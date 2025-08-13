# Requirements (requirements.txt)
openai>=1.0.0
mcp>=0.1.0

# For testing different SDKs:
kubernetes>=28.0.0
PyGithub>=1.59.0
azure-mgmt-core>=1.4.0
azure-mgmt-compute>=30.0.0
azure-identity>=1.15.0

# Development dependencies
pytest>=7.0.0
black>=22.0.0
mypy>=1.0.0

---

# Usage Examples

## Basic Usage

```bash
# Install dependencies
pip install -r requirements.txt

# Set OpenAI API key
export OPENAI_API_KEY="your-api-key-here"

# Convert Kubernetes SDK
python sdk4.py kubernetes

# Convert GitHub SDK  
python sdk4.py github

# Convert Azure SDK
python sdk4.py azure
```

## Python API Usage

```python
from sdk4.py import SDKToMCPConverter

# Initialize converter
converter = SDKToMCPConverter(api_key="your-openai-api-key")

# Convert an SDK
server_path = converter.convert("kubernetes", output_dir="./my_mcp_servers")

print(f"Generated MCP server at: {server_path}")
```

## Testing the Generated Server

```bash
# After generating a server, test it:
cd generated_mcp_servers
python kubernetes_mcp_server.py

# In another terminal, interact with it using MCP client tools
```

## Customization

1. Authentication: Add proper SDK client initialization
2. Error Handling: Enhance error handling for specific SDK quirks

## Architecture Overview

The converter works in three phases:

1. Introspection: Uses Python's `inspect` module to discover SDK methods
2. Analysis: Uses LLM to analyze methods and generate proper MCP tool definitions
3. Generation: Creates executable MCP server code and configuration

## Supported SDK Patterns

The converter is designed to work with SDKs that follow common patterns:
- Class based APIs with methods
- Good  documentation
- Standard Python module structure

## Known Behaviors/Errors

- Some of the generated servers have slight indentation issues that need to be reconsidered
- Batching is used to handle such large SDKs. Methods are chosen to be converted based on use cases. This number can be expanded upon.

## Extending the Converter

To support additional SDKs or customize behavior:

1. Custom Filters: Modify `_is_useful_method()` in `SDKIntrospector`
2. Enhanced Analysis: Customize the LLM prompts in `LLMAnalyzer`
3. Server Templates: Modify `_generate_server_code()` for different MCP patterns
4. SDK-Specific Logic: Add SDK-specific handling in the converter

