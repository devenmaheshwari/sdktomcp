# Kubernetes MCP Server

Auto-generated MCP server for kubernetes SDK operations.

## Installation

1. Install the SDK:
   ```bash
   pip install kubernetes
   ```

2. Install MCP dependencies:
   ```bash
   pip install mcp
   ```

## Setup

### Environment Variables

Set the required environment variables for authentication:


- For in-cluster: No additional setup required
- For local development: Ensure kubeconfig is properly configured

```bash
# Verify kubectl access
kubectl cluster-info
```


## Available Tools (15 total)

### Create Operations
- **create_namespaced_controller_revision**: create_namespaced_controller_revision  # noqa: E501

create a ControllerRevision  # noqa: E501
This ...
- **create_namespaced_daemon_set**: create_namespaced_daemon_set  # noqa: E501

create a DaemonSet  # noqa: E501
This method makes a syn...
- **create_namespaced_deployment**: create_namespaced_deployment  # noqa: E501

create a Deployment  # noqa: E501
This method makes a sy...
- **create_namespaced_replica_set**: create_namespaced_replica_set  # noqa: E501

create a ReplicaSet  # noqa: E501
This method makes a s...
- **create_namespaced_stateful_set**: create_namespaced_stateful_set  # noqa: E501

create a StatefulSet  # noqa: E501
This method makes a...

### Delete Operations
- **delete_namespaced_controller_revision**: delete_namespaced_controller_revision  # noqa: E501

delete a ControllerRevision  # noqa: E501
This ...
- **delete_namespaced_daemon_set**: delete_namespaced_daemon_set  # noqa: E501

delete a DaemonSet  # noqa: E501
This method makes a syn...
- **delete_namespaced_deployment**: delete_namespaced_deployment  # noqa: E501

delete a Deployment  # noqa: E501
This method makes a sy...
- **delete_namespaced_replica_set**: delete_namespaced_replica_set  # noqa: E501

delete a ReplicaSet  # noqa: E501
This method makes a s...
- **delete_namespaced_stateful_set**: delete_namespaced_stateful_set  # noqa: E501

delete a StatefulSet  # noqa: E501
This method makes a...

### Read Operations
- **list_deployment_for_all_namespaces**: list_deployment_for_all_namespaces  # noqa: E501

list or watch objects of kind Deployment  # noqa: ...
- **list_namespaced_controller_revision**: list_namespaced_controller_revision  # noqa: E501

list or watch objects of kind ControllerRevision ...
- **list_namespaced_daemon_set**: list_namespaced_daemon_set  # noqa: E501

list or watch objects of kind DaemonSet  # noqa: E501
This...
- **list_namespaced_deployment**: list_namespaced_deployment  # noqa: E501

list or watch objects of kind Deployment  # noqa: E501
Thi...
- **list_namespaced_replica_set**: list_namespaced_replica_set  # noqa: E501

list or watch objects of kind ReplicaSet  # noqa: E501
Th...


## Usage

1. Start the MCP server:
   ```bash
   python kubernetes_mcp_server.py
   ```

2. Configure your MCP client to use this server by adding the configuration from `kubernetes_mcp_config.json`.

## Notes

- This is an auto-generated server based on SDK introspection
- All methods include proper error handling and response formatting
- Authentication is handled automatically using environment variables
- Responses are JSON-formatted for easy parsing
