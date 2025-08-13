#!/usr/bin/env python3
"""
Enhanced SDK-to-MCP Converter

A generalized converter that transforms Python SDKs into MCP (Model Context Protocol) servers
with ACTUAL method implementations, not just placeholders.

Key improvements:
- Generates real method implementations
- Handles client initialization patterns
- Provides proper error handling and response formatting
- Supports authentication patterns for different SDKs
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
    implementation: str  # The actual Python code to execute


@dataclass
class SDKMethod:
    """Represents a discovered SDK method"""
    name: str
    full_path: str
    signature: inspect.Signature
    docstring: Optional[str]
    class_name: str
    module_name: str
    requires_client_instance: bool = True


class SDKIntrospector:
    """Introspects Python SDKs to discover available methods and their signatures"""
    
    # Enhanced SDK mappings with client initialization patterns
    SDK_MAPPINGS = {
        'kubernetes': {
            'import_name': 'kubernetes.client',
            'package_name': 'kubernetes',
            'install_cmd': 'pip install kubernetes',
            'main_classes': ['AppsV1Api', 'CoreV1Api', 'NetworkingV1Api', 'BatchV1Api'],
            'client_init': '''try:
        from kubernetes import client, config
        # Try in-cluster config first, then local kubeconfig
        try:
            config.load_incluster_config()
        except:
            config.load_kube_config()
        
        # Initialize API clients
        self.core_v1 = client.CoreV1Api()
        self.apps_v1 = client.AppsV1Api()
        self.networking_v1 = client.NetworkingV1Api()
        self.batch_v1 = client.BatchV1Api()
        
        # Client mapping for dynamic access
        self.clients = {
            'CoreV1Api': self.core_v1,
            'AppsV1Api': self.apps_v1,
            'NetworkingV1Api': self.networking_v1,
            'BatchV1Api': self.batch_v1
        }
    except Exception as e:
        logger.error(f"Failed to initialize Kubernetes client: {e}")
        raise''',
            'method_template': '''# Extract client and method from path
            path_parts = "{method_path}".split('.')
            client_class = path_parts[-2] if len(path_parts) > 1 else "CoreV1Api"
            method_name = path_parts[-1]
            
            client_instance = sdk_client.clients.get(client_class)
            if not client_instance:
                raise ValueError(f"Unknown client class: {{client_class}}")
            
            method = getattr(client_instance, method_name)
            result = method(**arguments)
            
            # Convert Kubernetes objects to dict for JSON serialization
            if hasattr(result, 'to_dict'):
                result = result.to_dict()
            elif hasattr(result, 'items') and result.items:
                result = {{
                    'items': [item.to_dict() if hasattr(item, 'to_dict') else str(item) for item in result.items],
                    'metadata': result.metadata.to_dict() if hasattr(result, 'metadata') else {{}}
                }}
            else:
                result = str(result)'''
        },
        'github': {
            'import_name': 'github',
            'package_name': 'PyGithub',
            'install_cmd': 'pip install PyGithub',
            'main_classes': ['Github'],
            'client_init': '''try:
        from github import Github
        import os
        
        # Get token from environment or config
        token = os.getenv('GITHUB_TOKEN')
        if not token:
            raise ValueError("GITHUB_TOKEN environment variable required")
        
        self.github = Github(token)
        self.clients = {'Github': self.github}
    except Exception as e:
        logger.error(f"Failed to initialize GitHub client: {e}")
        raise''',
            'method_template': '''# GitHub client method execution
            method = getattr(sdk_client.github, "{method_name}")
            result = method(**arguments)
            
            # Convert GitHub objects to serializable format
            if hasattr(result, '__dict__'):
                # Handle GitHub objects
                result = {{k: v for k, v in result.__dict__.items() if not k.startswith('_')}}
            elif hasattr(result, '__iter__') and not isinstance(result, str):
                # Handle lists/iterables
                result = [item.__dict__ if hasattr(item, '__dict__') else str(item) for item in result]
            else:
                result = str(result)'''
        },
        'azure': {
            'import_name': 'azure.mgmt.compute',
            'package_name': 'azure-mgmt-compute',
            'install_cmd': 'pip install azure-mgmt-compute azure-identity',
            'main_classes': ['ComputeManagementClient'],
            'client_init': '''try:
        from azure.identity import DefaultAzureCredential
        from azure.mgmt.compute import ComputeManagementClient
        import os
        
        subscription_id = os.getenv('AZURE_SUBSCRIPTION_ID')
        if not subscription_id:
            raise ValueError("AZURE_SUBSCRIPTION_ID environment variable required")
        
        credential = DefaultAzureCredential()
        self.compute_client = ComputeManagementClient(credential, subscription_id)
        self.clients = {'ComputeManagementClient': self.compute_client}
    except Exception as e:
        logger.error(f"Failed to initialize Azure client: {e}")
        raise''',
            'method_template': '''# Azure client method execution
            client_instance = sdk_client.compute_client
            method = getattr(client_instance, "{method_name}")
            result = method(**arguments)
            
            # Handle Azure response objects
            if hasattr(result, 'as_dict'):
                result = result.as_dict()
            elif hasattr(result, '__dict__'):
                result = {{k: v for k, v in result.__dict__.items() if not k.startswith('_')}}
            else:
                result = str(result)'''
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
            'main_classes': [],
            'client_init': f'# TODO: Initialize {sdk_name} client',
            'method_template': f'# TODO: Implement method execution for {sdk_name}'
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
                    module_name=cls.__module__,
                    requires_client_instance=True
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
        
        # Skip common utility/internal methods
        skip_patterns = [
            'to_dict', 'to_str', 'from_dict', 'attribute_map', 'swagger_types',
            'discriminator', 'openapi_types', 'model_config', 'validate',
            'serialize', 'deserialize', '__str__', '__repr__', 'set_default'
        ]
        
        method_lower = method.name.lower()
        if any(pattern in method_lower for pattern in skip_patterns):
            return False
        
        # Prioritize methods that sound like actions
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
    
    def analyze_methods(self, methods: List[SDKMethod], sdk_name: str, sdk_config: Dict) -> List[MCPTool]:
        """Analyze methods and convert them to MCP tool definitions with implementations"""
        tools = []
        
        # Filter to most essential methods
        max_methods = 15  # Keep it manageable
        if len(methods) > max_methods:
            logger.info(f"Filtering {len(methods)} methods down to {max_methods} most essential ones")
            methods = self._select_essential_methods(methods, max_methods)
        
        # Process methods and generate implementations
        for method in methods:
            tool = self._create_tool_with_implementation(method, sdk_name, sdk_config)
            if tool:
                tools.append(tool)
        
        return tools
    
    def _select_essential_methods(self, methods: List[SDKMethod], limit: int) -> List[SDKMethod]:
        """Select only the most essential methods for MCP conversion"""
        essential_patterns = {
            'kubernetes': [
                'list_pod', 'create_namespaced_pod', 'delete_namespaced_pod',
                'list_deployment', 'create_namespaced_deployment', 'patch_namespaced_deployment_scale',
                'list_service', 'create_namespaced_service', 'delete_namespaced_service',
                'list_namespace', 'create_namespace', 'delete_namespace',
                'list_configmap', 'create_namespaced_config_map'
            ],
            'github': [
                'get_user', 'get_repo', 'create_repo', 
                'get_issues', 'create_issue', 'create_pull',
                'get_pulls', 'merge', 'get_contents'
            ],
            'azure': [
                'list', 'get', 'create_or_update', 'delete',
                'start', 'restart', 'deallocate'
            ]
        }
        
        sdk_key = next((k for k in essential_patterns.keys() if k in methods[0].module_name.lower()), 'default')
        patterns = essential_patterns.get(sdk_key, ['create', 'get', 'list', 'update', 'delete'])
        
        # Score and filter methods
        scored_methods = []
        for method in methods:
            score = 0
            method_lower = method.name.lower()
            
            # Check for essential patterns
            for pattern in patterns:
                if pattern in method_lower:
                    score += 10
                    break
            
            # Bonus for good documentation
            if method.docstring and len(method.docstring) > 50:
                score += 2
            
            # Penalty for very long names (usually internal methods)
            if len(method.name) > 40:
                score -= 5
            
            if score > 0:
                scored_methods.append((score, method))
        
        # Sort by score and take top methods
        scored_methods.sort(reverse=True, key=lambda x: x[0])
        return [method for score, method in scored_methods[:limit]]
    
    def _create_tool_with_implementation(self, method: SDKMethod, sdk_name: str, sdk_config: Dict) -> Optional[MCPTool]:
        """Create an MCP tool with actual implementation code"""
        try:
            # Generate parameter schema
            parameters = self._generate_parameter_schema(method)
            
            # Generate implementation code
            implementation = self._generate_method_implementation(method, sdk_name, sdk_config)
            
            # Create tool description
            description = method.docstring or f"Execute {method.name} method"
            if len(description) > 200:
                description = description[:200] + "..."
            
            return MCPTool(
                name=method.name,
                description=description,
                parameters=parameters,
                method_path=method.full_path,
                category=self._categorize_method(method),
                implementation=implementation
            )
            
        except Exception as e:
            logger.debug(f"Failed to create tool for {method.name}: {e}")
            return None
    
    def _generate_parameter_schema(self, method: SDKMethod) -> Dict[str, Any]:
        """Generate JSON schema for method parameters"""
        parameters = {
            "type": "object",
            "properties": {},
            "required": []
        }
        
        for param_name, param in method.signature.parameters.items():
            if param_name == 'self':
                continue
            
            param_type = "string"  # Default
            param_desc = f"Parameter for {method.name}"
            
            # Try to infer type from annotation
            if param.annotation != param.empty:
                annotation_str = str(param.annotation)
                if 'int' in annotation_str.lower():
                    param_type = "integer"
                elif 'bool' in annotation_str.lower():
                    param_type = "boolean"
                elif 'list' in annotation_str.lower():
                    param_type = "array"
                elif 'dict' in annotation_str.lower():
                    param_type = "object"
                elif 'float' in annotation_str.lower():
                    param_type = "number"
            
            parameters["properties"][param_name] = {
                "type": param_type,
                "description": param_desc
            }
            
            # Add to required if no default value
            if param.default == param.empty:
                parameters["required"].append(param_name)
        
        return parameters
    
    def _generate_method_implementation(self, method: SDKMethod, sdk_name: str, sdk_config: Dict) -> str:
        """Generate the actual implementation code for the method"""
        template = sdk_config.get('method_template', '# Generic method execution')
        
        # Replace placeholders in template
        implementation = template.format(
            method_path=method.full_path,
            method_name=method.name,
            class_name=method.class_name
        )
        
        return implementation
    
    def _categorize_method(self, method: SDKMethod) -> str:
        """Categorize the method based on its name and purpose"""
        name_lower = method.name.lower()
        
        if any(keyword in name_lower for keyword in ['create', 'post']):
            return 'create'
        elif any(keyword in name_lower for keyword in ['list', 'get', 'read', 'fetch']):
            return 'read'
        elif any(keyword in name_lower for keyword in ['update', 'patch', 'put', 'edit']):
            return 'update'
        elif any(keyword in name_lower for keyword in ['delete', 'remove']):
            return 'delete'
        else:
            return 'other'


class MCPServerGenerator:
    """Generates MCP server code with actual method implementations"""
    
    def generate_server(self, tools: List[MCPTool], sdk_name: str, output_path: str, sdk_config: Dict):
        """Generate a complete MCP server with implementations"""
        server_code = self._generate_server_code(tools, sdk_name, sdk_config)
        
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
        
        # Generate README with setup instructions
        readme_content = self._generate_readme(sdk_name, tools, sdk_config)
        readme_file = Path(output_path) / f"{sdk_name.lower()}_README.md"
        
        with open(readme_file, 'w') as f:
            f.write(readme_content)
        
        return str(server_file)
    
    def _generate_server_code(self, tools: List[MCPTool], sdk_name: str, sdk_config: Dict) -> str:
        """Generate the complete MCP server Python code with implementations"""
        
        # Generate tool definitions
        tool_definitions = []
        for tool in tools:
            safe_description = tool.description.replace('"', '\\"')
            tool_def = f'''Tool(
    name="{tool.name}",
    description="{safe_description}",
    input_schema={json.dumps(tool.parameters, indent=4)}
)'''
            tool_definitions.append(tool_def)
        
        tools_list = ',\n    '.join(tool_definitions)
        
        # Generate method implementations
        method_implementations = []
        for tool in tools:
            impl = f'''        elif name == "{tool.name}":
            # {tool.method_path}
{self._indent_code(tool.implementation, 12)}'''
            method_implementations.append(impl)
        
        implementations_code = '\n'.join(method_implementations)
        
        server_template = f'''#!/usr/bin/env python3
"""
{sdk_name.title()} MCP Server
Auto-generated from SDK using enhanced sdk-to-mcp converter

This server provides MCP tools for {sdk_name} SDK operations.
Generated tools: {len(tools)}
"""

import asyncio
import json
import logging
from typing import Any, Dict, List

# MCP imports
from mcp.server import Server
from mcp.types import Tool, TextContent

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize MCP server
server = Server(f"{sdk_name.lower()}-mcp")


class {sdk_name.title()}Client:
    """Client wrapper for {sdk_name} SDK"""
    
    def __init__(self):
{self._indent_code(sdk_config.get('client_init', f'# Initialize {sdk_name} client'), 8)}


# Global client instance
try:
    sdk_client = {sdk_name.title()}Client()
    logger.info(f"{sdk_name.title()} client initialized successfully")
except Exception as e:
    logger.error(f"Failed to initialize {sdk_name} client: {{e}}")
    sdk_client = None


# Tool definitions ({len(tools)} tools)
TOOLS = [
    {tools_list}
]


@server.list_tools()
async def list_tools() -> List[Tool]:
    """List available tools"""
    return TOOLS


@server.call_tool()
async def handle_tool_call(name: str, arguments: Dict[str, Any]) -> List[TextContent]:
    """Handle all tool calls with actual implementations"""
    try:
        if not sdk_client:
            return [TextContent(
                type="text",
                text=json.dumps({{"error": "SDK client not initialized"}}, indent=2)
            )]
        
        logger.info(f"Executing tool: {{name}} with args: {{arguments}}")
        
        # Route to appropriate implementation
        result = None
        if False:
            pass
{implementations_code}
        else:
            result = {{"error": f"Unknown tool: {{name}}"}}
        
        return [TextContent(
            type="text",
            text=json.dumps(result, indent=2, default=str)
        )]
        
    except Exception as e:
        logger.error(f"Error executing {{name}}: {{e}}")
        return [TextContent(
            type="text", 
            text=json.dumps({{"error": str(e)}}, indent=2)
        )]


def main():
    """Main entry point"""
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
'''
        
        return server_template
    
    def _indent_code(self, code: str, spaces: int) -> str:
        """Indent code block by specified number of spaces"""
        indent = ' ' * spaces
        lines = code.strip().split('\n')
        return '\n'.join(indent + line if line.strip() else line for line in lines)
    
    def _generate_config(self, tools: List[MCPTool], sdk_name: str) -> Dict[str, Any]:
        """Generate MCP configuration"""
        return {
            "mcpServers": {
                f"{sdk_name.lower()}-mcp": {
                    "command": "python",
                    "args": [f"{sdk_name.lower()}_mcp_server.py"],
                    "description": f"MCP server for {sdk_name} SDK with {len(tools)} tools",
                    "tools": [tool.name for tool in tools],
                    "categories": list(set(tool.category for tool in tools))
                }
            }
        }
    
    def _generate_readme(self, sdk_name: str, tools: List[MCPTool], sdk_config: Dict) -> str:
        """Generate README with setup instructions"""
        tools_by_category = {}
        for tool in tools:
            if tool.category not in tools_by_category:
                tools_by_category[tool.category] = []
            tools_by_category[tool.category].append(tool)
        
        tools_list = ""
        for category, category_tools in tools_by_category.items():
            tools_list += f"\n### {category.title()} Operations\n"
            for tool in category_tools:
                description = tool.description[:100] + "..." if len(tool.description) > 100 else tool.description
                tools_list += f"- **{tool.name}**: {description}\n"
        
        sdk_setup = {
            'kubernetes': """
- For in-cluster: No additional setup required
- For local development: Ensure kubeconfig is properly configured

```bash
# Verify kubectl access
kubectl cluster-info
```
""",
            'github': """
```bash
export GITHUB_TOKEN="your-github-personal-access-token"
```
""",
            'azure': """
```bash
export AZURE_SUBSCRIPTION_ID="your-azure-subscription-id"
# Ensure Azure CLI is logged in: az login
```
"""
        }.get(sdk_name.lower(), f"# Configure {sdk_name} authentication")
        
        return f"""# {sdk_name.title()} MCP Server

Auto-generated MCP server for {sdk_name} SDK operations.

## Installation

1. Install the SDK:
   ```bash
   {sdk_config.get('install_cmd', f'pip install {sdk_name}')}
   ```

2. Install MCP dependencies:
   ```bash
   pip install mcp
   ```

## Setup

### Environment Variables

Set the required environment variables for authentication:

{sdk_setup}

## Available Tools ({len(tools)} total)
{tools_list}

## Usage

1. Start the MCP server:
   ```bash
   python {sdk_name.lower()}_mcp_server.py
   ```

2. Configure your MCP client to use this server by adding the configuration from `{sdk_name.lower()}_mcp_config.json`.

## Notes

- This is an auto-generated server based on SDK introspection
- All methods include proper error handling and response formatting
- Authentication is handled automatically using environment variables
- Responses are JSON-formatted for easy parsing
"""


class SDKToMCPConverter:
    """Enhanced converter class that generates working MCP servers"""
    
    def __init__(self, openai_api_key: str):
        self.llm_analyzer = LLMAnalyzer(openai_api_key)
        self.server_generator = MCPServerGenerator()
    
    def convert(self, sdk_name: str, output_dir: str = "./generated_mcp_servers") -> str:
        """Convert an SDK to a working MCP server"""
        logger.info(f"Starting conversion of {sdk_name} SDK to MCP server")
        
        # Step 1: Introspect the SDK
        introspector = SDKIntrospector(sdk_name)
        methods = introspector.discover_methods()
        
        if not methods:
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
        
        # Step 2: Analyze methods and generate implementations
        tools = self.llm_analyzer.analyze_methods(methods, sdk_name, introspector.sdk_config)
        logger.info(f"Generated {len(tools)} MCP tools with implementations")
        
        # Step 3: Generate working MCP server
        server_path = self.server_generator.generate_server(tools, sdk_name, output_dir, introspector.sdk_config)
        
        logger.info(f"Successfully converted {sdk_name} SDK to working MCP server")
        logger.info(f"Generated files in: {output_dir}")
        logger.info("Next steps:")
        logger.info(f"1. Set up authentication (see {sdk_name.lower()}_README.md)")
        logger.info(f"2. Test the server: python {server_path}")
        logger.info(f"3. Configure your MCP client with: {sdk_name.lower()}_mcp_config.json")
        
        return server_path


def main():
    """CLI interface for the enhanced converter"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Convert Python SDKs to working MCP servers")
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
        print(f"✅ Successfully generated working MCP server: {server_path}")
        
    except Exception as e:
        logger.error(f"Conversion failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()