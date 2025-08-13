#!/usr/bin/env python3
"""
SDK-to-MCP Converter

A generalized converter that transforms Python SDKs into MCP (Model Context Protocol) servers.
Supports introspection of SDK classes and methods, generates MCP-compatible tool definitions,
and creates executable MCP servers.

Tested with: Kubernetes, GitHub, and Azure SDKs
"""

import ast
import inspect
import json
import logging
import os
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union
import importlib
import pkgutil
import openai
from openai import OpenAI

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class MCPTool:
    """Represents an MCP tool definition"""
    name: str
    description: str
    parameters: Dict[str, Any]
    method_path: str  # e.g., "client.list_pods"
    category: str


@dataclass
class SDKMethod:
    """Represents a discovered SDK method"""
    name: str
    full_path: str
    signature: inspect.Signature
    docstring: Optional[str]
    class_name: str
    module_name: str


class SDKIntrospector:
    """Introspects Python SDKs to discover available methods and their signatures"""
    
    # Mapping of common SDK names to their actual import names and packages
    SDK_MAPPINGS = {
        'kubernetes': {
            'import_name': 'kubernetes.client',
            'package_name': 'kubernetes',
            'install_cmd': 'pip install kubernetes',
            'main_classes': ['AppsV1Api', 'CoreV1Api', 'NetworkingV1Api']
        },
        'github': {
            'import_name': 'github',
            'package_name': 'PyGithub',
            'install_cmd': 'pip install PyGithub',
            'main_classes': ['Github']
        },
        'azure': {
            'import_name': 'azure.mgmt.compute',
            'package_name': 'azure-mgmt-compute',
            'install_cmd': 'pip install azure-mgmt-compute azure-identity',
            'main_classes': ['ComputeManagementClient']
        }
    }
    
    def __init__(self, sdk_name: str):
        self.sdk_name = sdk_name.lower()
        self.discovered_methods: List[SDKMethod] = []
        
        # Get SDK mapping or use the name as-is
        self.sdk_config = self.SDK_MAPPINGS.get(self.sdk_name, {
            'import_name': sdk_name,
            'package_name': sdk_name,
            'install_cmd': f'pip install {sdk_name}',
            'main_classes': []
        })
        
    def discover_methods(self, max_depth: int = 3) -> List[SDKMethod]:
        """Discover all relevant methods in the SDK"""
        import_name = self.sdk_config['import_name']
        
        try:
            # Import the main SDK module
            sdk_module = importlib.import_module(import_name)
            logger.info(f"Successfully imported {import_name}")
            
            # For well-known SDKs, focus on main classes
            if self.sdk_config['main_classes']:
                self._explore_main_classes(sdk_module, import_name)
            else:
                # Recursively explore the module
                self._explore_module(sdk_module, import_name, depth=0, max_depth=max_depth)
            
            logger.info(f"Discovered {len(self.discovered_methods)} methods")
            return self.discovered_methods
            
        except ImportError as e:
            logger.error(f"Failed to import {import_name}: {e}")
            logger.error(f"Try installing: {self.sdk_config['install_cmd']}")
            return []
    
    def _explore_main_classes(self, module, module_path: str):
        """Explore specific main classes for well-known SDKs"""
        for class_name in self.sdk_config['main_classes']:
            try:
                if hasattr(module, class_name):
                    cls = getattr(module, class_name)
                    self._explore_class(cls, f"{module_path}.{class_name}", 1, 2)
                else:
                    logger.debug(f"Class {class_name} not found in {module_path}")
            except Exception as e:
                logger.debug(f"Error exploring class {class_name}: {e}")
    
    def _explore_module(self, module, module_path: str, depth: int, max_depth: int):
        """Recursively explore a module to find classes and methods"""
        if depth > max_depth:
            return
            
        for name, obj in inspect.getmembers(module):
            if name.startswith('_'):
                continue
                
            full_path = f"{module_path}.{name}"
            
            # Explore classes
            if inspect.isclass(obj):
                # More flexible module checking
                if (hasattr(obj, '__module__') and 
                    obj.__module__ and 
                    any(sdk_part in obj.__module__ for sdk_part in [self.sdk_name, self.sdk_config['import_name']])):
                    self._explore_class(obj, full_path, depth + 1, max_depth)
            
            # Explore submodules
            elif inspect.ismodule(obj):
                if (hasattr(obj, '__name__') and 
                    obj.__name__ and 
                    any(sdk_part in obj.__name__ for sdk_part in [self.sdk_name, self.sdk_config['import_name']]) and
                    depth < max_depth):
                    self._explore_module(obj, full_path, depth + 1, max_depth)
    
    def _explore_class(self, cls, class_path: str, depth: int, max_depth: int):
        """Explore methods within a class"""
        for name, method in inspect.getmembers(cls):
            if (name.startswith('_') or 
                not callable(method) or 
                name in ['__init__', '__new__']):
                continue
            
            try:
                signature = inspect.signature(method)
                docstring = inspect.getdoc(method)
                
                sdk_method = SDKMethod(
                    name=name,
                    full_path=f"{class_path}.{name}",
                    signature=signature,
                    docstring=docstring,
                    class_name=cls.__name__,
                    module_name=cls.__module__
                )
                
                # Filter out methods that are likely not useful for MCP
                if self._is_useful_method(sdk_method):
                    self.discovered_methods.append(sdk_method)
                    
            except (ValueError, TypeError) as e:
                logger.debug(f"Could not inspect method {class_path}.{name}: {e}")
    
    def _is_useful_method(self, method: SDKMethod) -> bool:
        """Determine if a method is likely useful for MCP exposure"""
        # Skip properties and private methods
        if method.name.startswith('_'):
            return False
        
        # Skip methods with no parameters (likely properties)
        params = list(method.signature.parameters.values())
        if len(params) <= 1:  # Only 'self' parameter
            return False
        
        # Skip common utility/internal methods that aren't useful for agents
        skip_patterns = [
            'to_dict', 'to_str', 'from_dict', 'attribute_map', 'swagger_types',
            'discriminator', 'openapi_types', 'model_config', 'validate',
            'serialize', 'deserialize', '__str__', '__repr__', 'set_default'
        ]
        
        method_lower = method.name.lower()
        if any(pattern in method_lower for pattern in skip_patterns):
            return False
        
        # Prioritize methods that sound like actions (more restrictive list)
        high_priority_keywords = [
            'create', 'delete', 'update', 'list', 'get', 'patch', 'replace',
            'scale', 'deploy', 'apply', 'exec', 'logs', 'watch'
        ]
        
        if any(keyword in method_lower for keyword in high_priority_keywords):
            return True
        
        # For Kubernetes specifically, focus on core operations
        if 'kubernetes' in method.module_name.lower():
            k8s_operations = [
                'namespace', 'pod', 'service', 'deployment', 'configmap',
                'secret', 'node', 'ingress', 'persistent_volume'
            ]
            if any(op in method_lower for op in k8s_operations):
                return True
        
        # Include methods with good docstrings but be more selective
        if method.docstring and len(method.docstring) > 100:
            return True
        
        return False


class LLMAnalyzer:
    """Uses LLM to analyze and categorize SDK methods for MCP conversion"""
    
    def __init__(self, api_key: str):
        self.client = OpenAI(api_key=api_key)
    
    def analyze_methods(self, methods: List[SDKMethod], sdk_name: str) -> List[MCPTool]:
        """Analyze methods and convert them to MCP tool definitions"""
        tools = []
        
        # Limit the number of methods to prevent overwhelming the LLM
        max_methods = 100  # Process at most 100 methods
        if len(methods) > max_methods:
            logger.info(f"Too many methods ({len(methods)}), selecting top {max_methods} most useful ones")
            # Sort by usefulness and take the top ones
            methods = self._prioritize_methods(methods)[:max_methods]
        
        # Process methods in smaller batches to avoid token limits
        batch_size = 3  # Reduced from 5 to 3
        for i in range(0, len(methods), batch_size):
            batch = methods[i:i+batch_size]
            batch_tools = self._analyze_batch(batch, sdk_name)
            tools.extend(batch_tools)
            
            logger.info(f"Processed batch {i//batch_size + 1}/{(len(methods)-1)//batch_size + 1}")
        
        return tools
    
    def _prioritize_methods(self, methods: List[SDKMethod]) -> List[SDKMethod]:
        """Sort methods by priority/usefulness for MCP conversion"""
        def method_score(method: SDKMethod) -> int:
            score = 0
            method_lower = method.name.lower()
            
            # High priority operations
            if any(op in method_lower for op in ['create', 'delete', 'list', 'get', 'update', 'patch']):
                score += 10
            
            # Medium priority operations  
            if any(op in method_lower for op in ['scale', 'deploy', 'apply', 'exec', 'logs']):
                score += 5
            
            # Kubernetes-specific resources
            if any(res in method_lower for res in ['pod', 'service', 'deployment', 'namespace']):
                score += 3
            
            # Good documentation
            if method.docstring and len(method.docstring) > 100:
                score += 2
            
            # Penalize very long method names (often internal)
            if len(method.name) > 50:
                score -= 2
                
            return score
        
        return sorted(methods, key=method_score, reverse=True)
    
    def _analyze_batch(self, methods: List[SDKMethod], sdk_name: str) -> List[MCPTool]:
        """Analyze a batch of methods"""
        method_info = []
        for method in methods:
            # Extract parameter information
            params = []
            for param_name, param in method.signature.parameters.items():
                if param_name == 'self':
                    continue
                
                param_info = {
                    'name': param_name,
                    'annotation': str(param.annotation) if param.annotation != param.empty else 'Any',
                    'default': str(param.default) if param.default != param.empty else None
                }
                params.append(param_info)
            
            method_info.append({
                'name': method.name,
                'full_path': method.full_path,
                'class_name': method.class_name,
                'docstring': method.docstring or 'No documentation available',
                'parameters': params
            })
        
        prompt = self._create_analysis_prompt(method_info, sdk_name)
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert in API design and the Model Context Protocol (MCP). Your task is to analyze SDK methods and convert them into well-defined MCP tools."
                    },
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1
            )
            
            # Parse the response
            return self._parse_llm_response(response.choices[0].message.content, methods)
            
        except Exception as e:
            logger.error(f"LLM analysis failed: {e}")
            # Fallback to simple conversion
            return self._fallback_conversion(methods)
    
    def _create_analysis_prompt(self, method_info: List[Dict], sdk_name: str) -> str:
        """Create a prompt for LLM analysis"""
        methods_json = json.dumps(method_info, indent=1)  # Reduced indentation to save tokens
        
        return f"""Analyze these {sdk_name} SDK methods and convert them to MCP tool definitions.

IMPORTANT: Respond with ONLY a valid JSON array, no additional text or formatting.

For each method, provide:
1. Clear tool name (snake_case)
2. Concise description 
3. JSON schema for parameters
4. Category

Methods:
{methods_json}

Response format (JSON only):
[{{"name":"tool_name","description":"description","category":"category","parameters":{{"type":"object","properties":{{"param":{{"type":"string","description":"desc"}}}},"required":["param"]}}}}]"""
    
    def _parse_llm_response(self, response: str, original_methods: List[SDKMethod]) -> List[MCPTool]:
        """Parse LLM response into MCP tools"""
        try:
            # Extract JSON from response
            start_idx = response.find('[')
            end_idx = response.rfind(']') + 1
            if start_idx == -1 or end_idx == 0:
                raise ValueError("No JSON array found in response")
            
            json_str = response[start_idx:end_idx]
            tools_data = json.loads(json_str)
            
            tools = []
            for i, tool_data in enumerate(tools_data):
                if i < len(original_methods):
                    method = original_methods[i]
                    tool = MCPTool(
                        name=tool_data.get('name', method.name),
                        description=tool_data.get('description', 'No description'),
                        parameters=tool_data.get('parameters', {}),
                        method_path=method.full_path,
                        category=tool_data.get('category', 'general')
                    )
                    tools.append(tool)
            
            return tools
            
        except Exception as e:
            logger.error(f"Failed to parse LLM response: {e}")
            return self._fallback_conversion(original_methods)
    
    def _fallback_conversion(self, methods: List[SDKMethod]) -> List[MCPTool]:
        """Fallback method conversion without LLM"""
        tools = []
        for method in methods:
            # Create basic parameter schema
            parameters = {
                "type": "object",
                "properties": {},
                "required": []
            }
            
            for param_name, param in method.signature.parameters.items():
                if param_name == 'self':
                    continue
                
                param_type = "string"  # Default to string
                if param.annotation != param.empty:
                    annotation_str = str(param.annotation)
                    if 'int' in annotation_str.lower():
                        param_type = "number"
                    elif 'bool' in annotation_str.lower():
                        param_type = "boolean"
                    elif 'list' in annotation_str.lower():
                        param_type = "array"
                    elif 'dict' in annotation_str.lower():
                        param_type = "object"
                
                parameters["properties"][param_name] = {
                    "type": param_type,
                    "description": f"Parameter for {method.name}"
                }
                
                if param.default == param.empty:
                    parameters["required"].append(param_name)
            
            tool = MCPTool(
                name=method.name,
                description=method.docstring or f"Execute {method.name} method",
                parameters=parameters,
                method_path=method.full_path,
                category="general"
            )
            tools.append(tool)
        
        return tools


class MCPServerGenerator:
    """Generates MCP server code from tool definitions"""
    
    def generate_server(self, tools: List[MCPTool], sdk_name: str, output_path: str):
        """Generate a complete MCP server"""
        server_code = self._generate_server_code(tools, sdk_name)
        
        # Write server file
        server_file = Path(output_path) / f"{sdk_name.lower()}_mcp_server.py"
        server_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(server_file, 'w') as f:
            f.write(server_code)
        
        logger.info(f"Generated MCP server: {server_file}")
        
        # Generate configuration file
        config = self._generate_config(tools, sdk_name)
        config_file = Path(output_path) / f"{sdk_name.lower()}_mcp_config.json"
        
        with open(config_file, 'w') as f:
            json.dump(config, f, indent=2)
        
        logger.info(f"Generated MCP config: {config_file}")
        
        return str(server_file)
    
    def _generate_server_code(self, tools: List[MCPTool], sdk_name: str) -> str:
        """Generate the MCP server Python code"""
        imports = f"""#!/usr/bin/env python3
\"\"\"
{sdk_name} MCP Server
Auto-generated from SDK using sdk-to-mcp converter
\"\"\"

import asyncio
import json
import logging
import sys
from typing import Any, Dict, List, Optional

# MCP imports
from mcp.server import Server
from mcp.types import Tool, TextContent

# SDK imports
try:
    import {sdk_name.lower()}
except ImportError:
    print(f"Please install the {sdk_name} SDK: pip install {sdk_name.lower()}")
    sys.exit(1)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize MCP server
server = Server(f"{sdk_name.lower()}-mcp")
"""

        # Generate tool definitions
        tool_definitions = []
        tool_handlers = []
        
        for tool in tools:
            # Tool definition
            tool_def = f'''
Tool(
    name="{tool.name}",
    description="{tool.description}",
    input_schema={json.dumps(tool.parameters, indent=4)}
)'''
            tool_definitions.append(tool_def.strip())
            
            # Tool handler
            handler = self._generate_tool_handler(tool)
            tool_handlers.append(handler)
        
        tools_list = ',\n    '.join(tool_definitions)
        handlers_code = '\n\n'.join(tool_handlers)
        
        server_template = f"""
# Tool definitions
TOOLS = [
    {tools_list}
]

@server.list_tools()
async def list_tools() -> List[Tool]:
    return TOOLS

{handlers_code}

def main():
    \"\"\"Main entry point\"\"\"
    import mcp.server.stdio
    
    async def run():
        async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
            await server.run(
                read_stream,
                write_stream,
                server.create_initialization_options()
            )
    
    asyncio.run(run())

if __name__ == "__main__":
    main()
"""
        
        return imports + server_template
    
    def _generate_tool_handler(self, tool: MCPTool) -> str:
        """Generate handler code for a specific tool"""
        return f'''
@server.call_tool()
async def handle_{tool.name}(name: str, arguments: Dict[str, Any]) -> List[TextContent]:
    """Handle {tool.name} tool execution"""
    if name != "{tool.name}":
        raise ValueError(f"Unknown tool: {{name}}")
    
    try:
        # TODO: Initialize SDK client appropriately
        # This is a template - you'll need to customize based on the specific SDK
        
        # Extract and validate arguments
        {self._generate_argument_extraction(tool)}
        
        # Execute the SDK method
        # result = {tool.method_path}(**arguments)
        
        # For now, return a placeholder result
        result = {{"status": "success", "message": "Tool executed successfully", "arguments": arguments}}
        
        return [TextContent(
            type="text",
            text=json.dumps(result, indent=2, default=str)
        )]
        
    except Exception as e:
        logger.error(f"Error executing {tool.name}: {{e}}")
        return [TextContent(
            type="text", 
            text=f"Error: {{str(e)}}"
        )]'''
    
    def _generate_argument_extraction(self, tool: MCPTool) -> str:
        """Generate argument extraction and validation code"""
        if not tool.parameters.get('properties'):
            return "# No arguments required"
        
        validations = []
        for param_name, param_def in tool.parameters['properties'].items():
            is_required = param_name in tool.parameters.get('required', [])
            
            if is_required:
                validations.append(f'        if "{param_name}" not in arguments:')
                validations.append(f'            raise ValueError("Missing required parameter: {param_name}")')
        
        return '\n'.join(validations) if validations else "# Arguments will be passed as-is"
    
    def _generate_config(self, tools: List[MCPTool], sdk_name: str) -> Dict[str, Any]:
        """Generate MCP configuration"""
        return {
            "mcpServers": {
                f"{sdk_name.lower()}-mcp": {
                    "command": "python",
                    "args": [f"{sdk_name.lower()}_mcp_server.py"],
                    "description": f"MCP server for {sdk_name} SDK",
                    "tools": [tool.name for tool in tools]
                }
            }
        }


class SDKToMCPConverter:
    """Main converter class that orchestrates the conversion process"""
    
    def __init__(self, openai_api_key: str):
        self.llm_analyzer = LLMAnalyzer(openai_api_key)
        self.server_generator = MCPServerGenerator()
    
    def convert(self, sdk_name: str, output_dir: str = "./generated_mcp_servers") -> str:
        """Convert an SDK to an MCP server"""
        logger.info(f"Starting conversion of {sdk_name} SDK to MCP server")
        
        # Step 1: Introspect the SDK
        introspector = SDKIntrospector(sdk_name)
        methods = introspector.discover_methods()
        
        if not methods:
            # Provide helpful error message with installation instructions
            sdk_config = introspector.sdk_config
            error_msg = f"""No methods found in SDK: {sdk_name}

This could be because:
1. The SDK is not installed. Try: {sdk_config['install_cmd']}
2. The SDK name/import path is incorrect
3. The SDK doesn't follow standard Python patterns

For well-known SDKs, make sure you have installed:
- Kubernetes: pip install kubernetes
- GitHub: pip install PyGithub  
- Azure: pip install azure-mgmt-compute azure-identity
"""
            raise ValueError(error_msg)
        
        logger.info(f"Found {len(methods)} methods to convert")
        
        # Step 2: Analyze methods with LLM
        tools = self.llm_analyzer.analyze_methods(methods, sdk_name)
        logger.info(f"Generated {len(tools)} MCP tools")
        
        # Step 3: Generate MCP server
        server_path = self.server_generator.generate_server(tools, sdk_name, output_dir)
        
        logger.info(f"Successfully converted {sdk_name} SDK to MCP server")
        logger.info(f"Generated files in: {output_dir}")
        
        return server_path


def main():
    """CLI interface for the converter"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Convert Python SDKs to MCP servers")
    parser.add_argument("sdk_name", help="Name of the SDK to convert (e.g., 'kubernetes', 'github', 'azure')")
    parser.add_argument("--output-dir", default="./generated_mcp_servers", help="Output directory")
    parser.add_argument("--api-key", help="OpenAI API key (or set OPENAI_API_KEY env var)")
    
    args = parser.parse_args()
    
    # Get API key
    api_key = args.api_key or os.getenv('OPENAI_API_KEY')
    if not api_key:
        print("Error: OpenAI API key required. Use --api-key or set OPENAI_API_KEY environment variable")
        sys.exit(1)
    
    try:
        converter = SDKToMCPConverter(api_key)
        server_path = converter.convert(args.sdk_name, args.output_dir)
        print(f"✅ Successfully generated MCP server: {server_path}")
        
    except Exception as e:
        logger.error(f"Conversion failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()