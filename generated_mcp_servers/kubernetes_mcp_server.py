#!/usr/bin/env python3
"""
Kubernetes MCP Server
Auto-generated from SDK using enhanced sdk-to-mcp converter

This server provides MCP tools for kubernetes SDK operations.
Generated tools: 15
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
server = Server(f"kubernetes-mcp")


class KubernetesClient:
    """Client wrapper for kubernetes SDK"""
    
    def __init__(self):
        try:
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
                raise


# Global client instance
try:
    sdk_client = KubernetesClient()
    logger.info(f"Kubernetes client initialized successfully")
except Exception as e:
    logger.error(f"Failed to initialize kubernetes client: {e}")
    sdk_client = None


# Tool definitions (15 tools)
TOOLS = [
    Tool(
    name="create_namespaced_controller_revision",
    description="create_namespaced_controller_revision  # noqa: E501

create a ControllerRevision  # noqa: E501
This method makes a synchronous HTTP request by default. To make an
asynchronous HTTP request, please pas...",
    input_schema={
    "type": "object",
    "properties": {
        "namespace": {
            "type": "string",
            "description": "Parameter for create_namespaced_controller_revision"
        },
        "body": {
            "type": "string",
            "description": "Parameter for create_namespaced_controller_revision"
        },
        "kwargs": {
            "type": "string",
            "description": "Parameter for create_namespaced_controller_revision"
        }
    },
    "required": [
        "namespace",
        "body",
        "kwargs"
    ]
}
),
    Tool(
    name="create_namespaced_daemon_set",
    description="create_namespaced_daemon_set  # noqa: E501

create a DaemonSet  # noqa: E501
This method makes a synchronous HTTP request by default. To make an
asynchronous HTTP request, please pass async_req=True
>...",
    input_schema={
    "type": "object",
    "properties": {
        "namespace": {
            "type": "string",
            "description": "Parameter for create_namespaced_daemon_set"
        },
        "body": {
            "type": "string",
            "description": "Parameter for create_namespaced_daemon_set"
        },
        "kwargs": {
            "type": "string",
            "description": "Parameter for create_namespaced_daemon_set"
        }
    },
    "required": [
        "namespace",
        "body",
        "kwargs"
    ]
}
),
    Tool(
    name="create_namespaced_deployment",
    description="create_namespaced_deployment  # noqa: E501

create a Deployment  # noqa: E501
This method makes a synchronous HTTP request by default. To make an
asynchronous HTTP request, please pass async_req=True
...",
    input_schema={
    "type": "object",
    "properties": {
        "namespace": {
            "type": "string",
            "description": "Parameter for create_namespaced_deployment"
        },
        "body": {
            "type": "string",
            "description": "Parameter for create_namespaced_deployment"
        },
        "kwargs": {
            "type": "string",
            "description": "Parameter for create_namespaced_deployment"
        }
    },
    "required": [
        "namespace",
        "body",
        "kwargs"
    ]
}
),
    Tool(
    name="create_namespaced_replica_set",
    description="create_namespaced_replica_set  # noqa: E501

create a ReplicaSet  # noqa: E501
This method makes a synchronous HTTP request by default. To make an
asynchronous HTTP request, please pass async_req=True...",
    input_schema={
    "type": "object",
    "properties": {
        "namespace": {
            "type": "string",
            "description": "Parameter for create_namespaced_replica_set"
        },
        "body": {
            "type": "string",
            "description": "Parameter for create_namespaced_replica_set"
        },
        "kwargs": {
            "type": "string",
            "description": "Parameter for create_namespaced_replica_set"
        }
    },
    "required": [
        "namespace",
        "body",
        "kwargs"
    ]
}
),
    Tool(
    name="create_namespaced_stateful_set",
    description="create_namespaced_stateful_set  # noqa: E501

create a StatefulSet  # noqa: E501
This method makes a synchronous HTTP request by default. To make an
asynchronous HTTP request, please pass async_req=Tr...",
    input_schema={
    "type": "object",
    "properties": {
        "namespace": {
            "type": "string",
            "description": "Parameter for create_namespaced_stateful_set"
        },
        "body": {
            "type": "string",
            "description": "Parameter for create_namespaced_stateful_set"
        },
        "kwargs": {
            "type": "string",
            "description": "Parameter for create_namespaced_stateful_set"
        }
    },
    "required": [
        "namespace",
        "body",
        "kwargs"
    ]
}
),
    Tool(
    name="delete_namespaced_controller_revision",
    description="delete_namespaced_controller_revision  # noqa: E501

delete a ControllerRevision  # noqa: E501
This method makes a synchronous HTTP request by default. To make an
asynchronous HTTP request, please pas...",
    input_schema={
    "type": "object",
    "properties": {
        "name": {
            "type": "string",
            "description": "Parameter for delete_namespaced_controller_revision"
        },
        "namespace": {
            "type": "string",
            "description": "Parameter for delete_namespaced_controller_revision"
        },
        "kwargs": {
            "type": "string",
            "description": "Parameter for delete_namespaced_controller_revision"
        }
    },
    "required": [
        "name",
        "namespace",
        "kwargs"
    ]
}
),
    Tool(
    name="delete_namespaced_daemon_set",
    description="delete_namespaced_daemon_set  # noqa: E501

delete a DaemonSet  # noqa: E501
This method makes a synchronous HTTP request by default. To make an
asynchronous HTTP request, please pass async_req=True
>...",
    input_schema={
    "type": "object",
    "properties": {
        "name": {
            "type": "string",
            "description": "Parameter for delete_namespaced_daemon_set"
        },
        "namespace": {
            "type": "string",
            "description": "Parameter for delete_namespaced_daemon_set"
        },
        "kwargs": {
            "type": "string",
            "description": "Parameter for delete_namespaced_daemon_set"
        }
    },
    "required": [
        "name",
        "namespace",
        "kwargs"
    ]
}
),
    Tool(
    name="delete_namespaced_deployment",
    description="delete_namespaced_deployment  # noqa: E501

delete a Deployment  # noqa: E501
This method makes a synchronous HTTP request by default. To make an
asynchronous HTTP request, please pass async_req=True
...",
    input_schema={
    "type": "object",
    "properties": {
        "name": {
            "type": "string",
            "description": "Parameter for delete_namespaced_deployment"
        },
        "namespace": {
            "type": "string",
            "description": "Parameter for delete_namespaced_deployment"
        },
        "kwargs": {
            "type": "string",
            "description": "Parameter for delete_namespaced_deployment"
        }
    },
    "required": [
        "name",
        "namespace",
        "kwargs"
    ]
}
),
    Tool(
    name="delete_namespaced_replica_set",
    description="delete_namespaced_replica_set  # noqa: E501

delete a ReplicaSet  # noqa: E501
This method makes a synchronous HTTP request by default. To make an
asynchronous HTTP request, please pass async_req=True...",
    input_schema={
    "type": "object",
    "properties": {
        "name": {
            "type": "string",
            "description": "Parameter for delete_namespaced_replica_set"
        },
        "namespace": {
            "type": "string",
            "description": "Parameter for delete_namespaced_replica_set"
        },
        "kwargs": {
            "type": "string",
            "description": "Parameter for delete_namespaced_replica_set"
        }
    },
    "required": [
        "name",
        "namespace",
        "kwargs"
    ]
}
),
    Tool(
    name="delete_namespaced_stateful_set",
    description="delete_namespaced_stateful_set  # noqa: E501

delete a StatefulSet  # noqa: E501
This method makes a synchronous HTTP request by default. To make an
asynchronous HTTP request, please pass async_req=Tr...",
    input_schema={
    "type": "object",
    "properties": {
        "name": {
            "type": "string",
            "description": "Parameter for delete_namespaced_stateful_set"
        },
        "namespace": {
            "type": "string",
            "description": "Parameter for delete_namespaced_stateful_set"
        },
        "kwargs": {
            "type": "string",
            "description": "Parameter for delete_namespaced_stateful_set"
        }
    },
    "required": [
        "name",
        "namespace",
        "kwargs"
    ]
}
),
    Tool(
    name="list_deployment_for_all_namespaces",
    description="list_deployment_for_all_namespaces  # noqa: E501

list or watch objects of kind Deployment  # noqa: E501
This method makes a synchronous HTTP request by default. To make an
asynchronous HTTP request, ...",
    input_schema={
    "type": "object",
    "properties": {
        "kwargs": {
            "type": "string",
            "description": "Parameter for list_deployment_for_all_namespaces"
        }
    },
    "required": [
        "kwargs"
    ]
}
),
    Tool(
    name="list_namespaced_controller_revision",
    description="list_namespaced_controller_revision  # noqa: E501

list or watch objects of kind ControllerRevision  # noqa: E501
This method makes a synchronous HTTP request by default. To make an
asynchronous HTTP ...",
    input_schema={
    "type": "object",
    "properties": {
        "namespace": {
            "type": "string",
            "description": "Parameter for list_namespaced_controller_revision"
        },
        "kwargs": {
            "type": "string",
            "description": "Parameter for list_namespaced_controller_revision"
        }
    },
    "required": [
        "namespace",
        "kwargs"
    ]
}
),
    Tool(
    name="list_namespaced_daemon_set",
    description="list_namespaced_daemon_set  # noqa: E501

list or watch objects of kind DaemonSet  # noqa: E501
This method makes a synchronous HTTP request by default. To make an
asynchronous HTTP request, please pa...",
    input_schema={
    "type": "object",
    "properties": {
        "namespace": {
            "type": "string",
            "description": "Parameter for list_namespaced_daemon_set"
        },
        "kwargs": {
            "type": "string",
            "description": "Parameter for list_namespaced_daemon_set"
        }
    },
    "required": [
        "namespace",
        "kwargs"
    ]
}
),
    Tool(
    name="list_namespaced_deployment",
    description="list_namespaced_deployment  # noqa: E501

list or watch objects of kind Deployment  # noqa: E501
This method makes a synchronous HTTP request by default. To make an
asynchronous HTTP request, please p...",
    input_schema={
    "type": "object",
    "properties": {
        "namespace": {
            "type": "string",
            "description": "Parameter for list_namespaced_deployment"
        },
        "kwargs": {
            "type": "string",
            "description": "Parameter for list_namespaced_deployment"
        }
    },
    "required": [
        "namespace",
        "kwargs"
    ]
}
),
    Tool(
    name="list_namespaced_replica_set",
    description="list_namespaced_replica_set  # noqa: E501

list or watch objects of kind ReplicaSet  # noqa: E501
This method makes a synchronous HTTP request by default. To make an
asynchronous HTTP request, please ...",
    input_schema={
    "type": "object",
    "properties": {
        "namespace": {
            "type": "string",
            "description": "Parameter for list_namespaced_replica_set"
        },
        "kwargs": {
            "type": "string",
            "description": "Parameter for list_namespaced_replica_set"
        }
    },
    "required": [
        "namespace",
        "kwargs"
    ]
}
)
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
                text=json.dumps({"error": "SDK client not initialized"}, indent=2)
            )]
        
        logger.info(f"Executing tool: {name} with args: {arguments}")
        
        # Route to appropriate implementation
        result = None
        if False:
            pass
        elif name == "create_namespaced_controller_revision":
            # kubernetes.client.AppsV1Api.create_namespaced_controller_revision
            # Extract client and method from path
                        path_parts = "kubernetes.client.AppsV1Api.create_namespaced_controller_revision".split('.')
                        client_class = path_parts[-2] if len(path_parts) > 1 else "CoreV1Api"
                        method_name = path_parts[-1]
            
                        client_instance = sdk_client.clients.get(client_class)
                        if not client_instance:
                            raise ValueError(f"Unknown client class: {client_class}")
            
                        method = getattr(client_instance, method_name)
                        result = method(**arguments)
            
                        # Convert Kubernetes objects to dict for JSON serialization
                        if hasattr(result, 'to_dict'):
                            result = result.to_dict()
                        elif hasattr(result, 'items') and result.items:
                            result = {
                                'items': [item.to_dict() if hasattr(item, 'to_dict') else str(item) for item in result.items],
                                'metadata': result.metadata.to_dict() if hasattr(result, 'metadata') else {}
                            }
                        else:
                            result = str(result)
        elif name == "create_namespaced_daemon_set":
            # kubernetes.client.AppsV1Api.create_namespaced_daemon_set
            # Extract client and method from path
                        path_parts = "kubernetes.client.AppsV1Api.create_namespaced_daemon_set".split('.')
                        client_class = path_parts[-2] if len(path_parts) > 1 else "CoreV1Api"
                        method_name = path_parts[-1]
            
                        client_instance = sdk_client.clients.get(client_class)
                        if not client_instance:
                            raise ValueError(f"Unknown client class: {client_class}")
            
                        method = getattr(client_instance, method_name)
                        result = method(**arguments)
            
                        # Convert Kubernetes objects to dict for JSON serialization
                        if hasattr(result, 'to_dict'):
                            result = result.to_dict()
                        elif hasattr(result, 'items') and result.items:
                            result = {
                                'items': [item.to_dict() if hasattr(item, 'to_dict') else str(item) for item in result.items],
                                'metadata': result.metadata.to_dict() if hasattr(result, 'metadata') else {}
                            }
                        else:
                            result = str(result)
        elif name == "create_namespaced_deployment":
            # kubernetes.client.AppsV1Api.create_namespaced_deployment
            # Extract client and method from path
                        path_parts = "kubernetes.client.AppsV1Api.create_namespaced_deployment".split('.')
                        client_class = path_parts[-2] if len(path_parts) > 1 else "CoreV1Api"
                        method_name = path_parts[-1]
            
                        client_instance = sdk_client.clients.get(client_class)
                        if not client_instance:
                            raise ValueError(f"Unknown client class: {client_class}")
            
                        method = getattr(client_instance, method_name)
                        result = method(**arguments)
            
                        # Convert Kubernetes objects to dict for JSON serialization
                        if hasattr(result, 'to_dict'):
                            result = result.to_dict()
                        elif hasattr(result, 'items') and result.items:
                            result = {
                                'items': [item.to_dict() if hasattr(item, 'to_dict') else str(item) for item in result.items],
                                'metadata': result.metadata.to_dict() if hasattr(result, 'metadata') else {}
                            }
                        else:
                            result = str(result)
        elif name == "create_namespaced_replica_set":
            # kubernetes.client.AppsV1Api.create_namespaced_replica_set
            # Extract client and method from path
                        path_parts = "kubernetes.client.AppsV1Api.create_namespaced_replica_set".split('.')
                        client_class = path_parts[-2] if len(path_parts) > 1 else "CoreV1Api"
                        method_name = path_parts[-1]
            
                        client_instance = sdk_client.clients.get(client_class)
                        if not client_instance:
                            raise ValueError(f"Unknown client class: {client_class}")
            
                        method = getattr(client_instance, method_name)
                        result = method(**arguments)
            
                        # Convert Kubernetes objects to dict for JSON serialization
                        if hasattr(result, 'to_dict'):
                            result = result.to_dict()
                        elif hasattr(result, 'items') and result.items:
                            result = {
                                'items': [item.to_dict() if hasattr(item, 'to_dict') else str(item) for item in result.items],
                                'metadata': result.metadata.to_dict() if hasattr(result, 'metadata') else {}
                            }
                        else:
                            result = str(result)
        elif name == "create_namespaced_stateful_set":
            # kubernetes.client.AppsV1Api.create_namespaced_stateful_set
            # Extract client and method from path
                        path_parts = "kubernetes.client.AppsV1Api.create_namespaced_stateful_set".split('.')
                        client_class = path_parts[-2] if len(path_parts) > 1 else "CoreV1Api"
                        method_name = path_parts[-1]
            
                        client_instance = sdk_client.clients.get(client_class)
                        if not client_instance:
                            raise ValueError(f"Unknown client class: {client_class}")
            
                        method = getattr(client_instance, method_name)
                        result = method(**arguments)
            
                        # Convert Kubernetes objects to dict for JSON serialization
                        if hasattr(result, 'to_dict'):
                            result = result.to_dict()
                        elif hasattr(result, 'items') and result.items:
                            result = {
                                'items': [item.to_dict() if hasattr(item, 'to_dict') else str(item) for item in result.items],
                                'metadata': result.metadata.to_dict() if hasattr(result, 'metadata') else {}
                            }
                        else:
                            result = str(result)
        elif name == "delete_namespaced_controller_revision":
            # kubernetes.client.AppsV1Api.delete_namespaced_controller_revision
            # Extract client and method from path
                        path_parts = "kubernetes.client.AppsV1Api.delete_namespaced_controller_revision".split('.')
                        client_class = path_parts[-2] if len(path_parts) > 1 else "CoreV1Api"
                        method_name = path_parts[-1]
            
                        client_instance = sdk_client.clients.get(client_class)
                        if not client_instance:
                            raise ValueError(f"Unknown client class: {client_class}")
            
                        method = getattr(client_instance, method_name)
                        result = method(**arguments)
            
                        # Convert Kubernetes objects to dict for JSON serialization
                        if hasattr(result, 'to_dict'):
                            result = result.to_dict()
                        elif hasattr(result, 'items') and result.items:
                            result = {
                                'items': [item.to_dict() if hasattr(item, 'to_dict') else str(item) for item in result.items],
                                'metadata': result.metadata.to_dict() if hasattr(result, 'metadata') else {}
                            }
                        else:
                            result = str(result)
        elif name == "delete_namespaced_daemon_set":
            # kubernetes.client.AppsV1Api.delete_namespaced_daemon_set
            # Extract client and method from path
                        path_parts = "kubernetes.client.AppsV1Api.delete_namespaced_daemon_set".split('.')
                        client_class = path_parts[-2] if len(path_parts) > 1 else "CoreV1Api"
                        method_name = path_parts[-1]
            
                        client_instance = sdk_client.clients.get(client_class)
                        if not client_instance:
                            raise ValueError(f"Unknown client class: {client_class}")
            
                        method = getattr(client_instance, method_name)
                        result = method(**arguments)
            
                        # Convert Kubernetes objects to dict for JSON serialization
                        if hasattr(result, 'to_dict'):
                            result = result.to_dict()
                        elif hasattr(result, 'items') and result.items:
                            result = {
                                'items': [item.to_dict() if hasattr(item, 'to_dict') else str(item) for item in result.items],
                                'metadata': result.metadata.to_dict() if hasattr(result, 'metadata') else {}
                            }
                        else:
                            result = str(result)
        elif name == "delete_namespaced_deployment":
            # kubernetes.client.AppsV1Api.delete_namespaced_deployment
            # Extract client and method from path
                        path_parts = "kubernetes.client.AppsV1Api.delete_namespaced_deployment".split('.')
                        client_class = path_parts[-2] if len(path_parts) > 1 else "CoreV1Api"
                        method_name = path_parts[-1]
            
                        client_instance = sdk_client.clients.get(client_class)
                        if not client_instance:
                            raise ValueError(f"Unknown client class: {client_class}")
            
                        method = getattr(client_instance, method_name)
                        result = method(**arguments)
            
                        # Convert Kubernetes objects to dict for JSON serialization
                        if hasattr(result, 'to_dict'):
                            result = result.to_dict()
                        elif hasattr(result, 'items') and result.items:
                            result = {
                                'items': [item.to_dict() if hasattr(item, 'to_dict') else str(item) for item in result.items],
                                'metadata': result.metadata.to_dict() if hasattr(result, 'metadata') else {}
                            }
                        else:
                            result = str(result)
        elif name == "delete_namespaced_replica_set":
            # kubernetes.client.AppsV1Api.delete_namespaced_replica_set
            # Extract client and method from path
                        path_parts = "kubernetes.client.AppsV1Api.delete_namespaced_replica_set".split('.')
                        client_class = path_parts[-2] if len(path_parts) > 1 else "CoreV1Api"
                        method_name = path_parts[-1]
            
                        client_instance = sdk_client.clients.get(client_class)
                        if not client_instance:
                            raise ValueError(f"Unknown client class: {client_class}")
            
                        method = getattr(client_instance, method_name)
                        result = method(**arguments)
            
                        # Convert Kubernetes objects to dict for JSON serialization
                        if hasattr(result, 'to_dict'):
                            result = result.to_dict()
                        elif hasattr(result, 'items') and result.items:
                            result = {
                                'items': [item.to_dict() if hasattr(item, 'to_dict') else str(item) for item in result.items],
                                'metadata': result.metadata.to_dict() if hasattr(result, 'metadata') else {}
                            }
                        else:
                            result = str(result)
        elif name == "delete_namespaced_stateful_set":
            # kubernetes.client.AppsV1Api.delete_namespaced_stateful_set
            # Extract client and method from path
                        path_parts = "kubernetes.client.AppsV1Api.delete_namespaced_stateful_set".split('.')
                        client_class = path_parts[-2] if len(path_parts) > 1 else "CoreV1Api"
                        method_name = path_parts[-1]
            
                        client_instance = sdk_client.clients.get(client_class)
                        if not client_instance:
                            raise ValueError(f"Unknown client class: {client_class}")
            
                        method = getattr(client_instance, method_name)
                        result = method(**arguments)
            
                        # Convert Kubernetes objects to dict for JSON serialization
                        if hasattr(result, 'to_dict'):
                            result = result.to_dict()
                        elif hasattr(result, 'items') and result.items:
                            result = {
                                'items': [item.to_dict() if hasattr(item, 'to_dict') else str(item) for item in result.items],
                                'metadata': result.metadata.to_dict() if hasattr(result, 'metadata') else {}
                            }
                        else:
                            result = str(result)
        elif name == "list_deployment_for_all_namespaces":
            # kubernetes.client.AppsV1Api.list_deployment_for_all_namespaces
            # Extract client and method from path
                        path_parts = "kubernetes.client.AppsV1Api.list_deployment_for_all_namespaces".split('.')
                        client_class = path_parts[-2] if len(path_parts) > 1 else "CoreV1Api"
                        method_name = path_parts[-1]
            
                        client_instance = sdk_client.clients.get(client_class)
                        if not client_instance:
                            raise ValueError(f"Unknown client class: {client_class}")
            
                        method = getattr(client_instance, method_name)
                        result = method(**arguments)
            
                        # Convert Kubernetes objects to dict for JSON serialization
                        if hasattr(result, 'to_dict'):
                            result = result.to_dict()
                        elif hasattr(result, 'items') and result.items:
                            result = {
                                'items': [item.to_dict() if hasattr(item, 'to_dict') else str(item) for item in result.items],
                                'metadata': result.metadata.to_dict() if hasattr(result, 'metadata') else {}
                            }
                        else:
                            result = str(result)
        elif name == "list_namespaced_controller_revision":
            # kubernetes.client.AppsV1Api.list_namespaced_controller_revision
            # Extract client and method from path
                        path_parts = "kubernetes.client.AppsV1Api.list_namespaced_controller_revision".split('.')
                        client_class = path_parts[-2] if len(path_parts) > 1 else "CoreV1Api"
                        method_name = path_parts[-1]
            
                        client_instance = sdk_client.clients.get(client_class)
                        if not client_instance:
                            raise ValueError(f"Unknown client class: {client_class}")
            
                        method = getattr(client_instance, method_name)
                        result = method(**arguments)
            
                        # Convert Kubernetes objects to dict for JSON serialization
                        if hasattr(result, 'to_dict'):
                            result = result.to_dict()
                        elif hasattr(result, 'items') and result.items:
                            result = {
                                'items': [item.to_dict() if hasattr(item, 'to_dict') else str(item) for item in result.items],
                                'metadata': result.metadata.to_dict() if hasattr(result, 'metadata') else {}
                            }
                        else:
                            result = str(result)
        elif name == "list_namespaced_daemon_set":
            # kubernetes.client.AppsV1Api.list_namespaced_daemon_set
            # Extract client and method from path
                        path_parts = "kubernetes.client.AppsV1Api.list_namespaced_daemon_set".split('.')
                        client_class = path_parts[-2] if len(path_parts) > 1 else "CoreV1Api"
                        method_name = path_parts[-1]
            
                        client_instance = sdk_client.clients.get(client_class)
                        if not client_instance:
                            raise ValueError(f"Unknown client class: {client_class}")
            
                        method = getattr(client_instance, method_name)
                        result = method(**arguments)
            
                        # Convert Kubernetes objects to dict for JSON serialization
                        if hasattr(result, 'to_dict'):
                            result = result.to_dict()
                        elif hasattr(result, 'items') and result.items:
                            result = {
                                'items': [item.to_dict() if hasattr(item, 'to_dict') else str(item) for item in result.items],
                                'metadata': result.metadata.to_dict() if hasattr(result, 'metadata') else {}
                            }
                        else:
                            result = str(result)
        elif name == "list_namespaced_deployment":
            # kubernetes.client.AppsV1Api.list_namespaced_deployment
            # Extract client and method from path
                        path_parts = "kubernetes.client.AppsV1Api.list_namespaced_deployment".split('.')
                        client_class = path_parts[-2] if len(path_parts) > 1 else "CoreV1Api"
                        method_name = path_parts[-1]
            
                        client_instance = sdk_client.clients.get(client_class)
                        if not client_instance:
                            raise ValueError(f"Unknown client class: {client_class}")
            
                        method = getattr(client_instance, method_name)
                        result = method(**arguments)
            
                        # Convert Kubernetes objects to dict for JSON serialization
                        if hasattr(result, 'to_dict'):
                            result = result.to_dict()
                        elif hasattr(result, 'items') and result.items:
                            result = {
                                'items': [item.to_dict() if hasattr(item, 'to_dict') else str(item) for item in result.items],
                                'metadata': result.metadata.to_dict() if hasattr(result, 'metadata') else {}
                            }
                        else:
                            result = str(result)
        elif name == "list_namespaced_replica_set":
            # kubernetes.client.AppsV1Api.list_namespaced_replica_set
            # Extract client and method from path
                        path_parts = "kubernetes.client.AppsV1Api.list_namespaced_replica_set".split('.')
                        client_class = path_parts[-2] if len(path_parts) > 1 else "CoreV1Api"
                        method_name = path_parts[-1]
            
                        client_instance = sdk_client.clients.get(client_class)
                        if not client_instance:
                            raise ValueError(f"Unknown client class: {client_class}")
            
                        method = getattr(client_instance, method_name)
                        result = method(**arguments)
            
                        # Convert Kubernetes objects to dict for JSON serialization
                        if hasattr(result, 'to_dict'):
                            result = result.to_dict()
                        elif hasattr(result, 'items') and result.items:
                            result = {
                                'items': [item.to_dict() if hasattr(item, 'to_dict') else str(item) for item in result.items],
                                'metadata': result.metadata.to_dict() if hasattr(result, 'metadata') else {}
                            }
                        else:
                            result = str(result)
        else:
            result = {"error": f"Unknown tool: {name}"}
        
        return [TextContent(
            type="text",
            text=json.dumps(result, indent=2, default=str)
        )]
        
    except Exception as e:
        logger.error(f"Error executing {name}: {e}")
        return [TextContent(
            type="text", 
            text=json.dumps({"error": str(e)}, indent=2)
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
