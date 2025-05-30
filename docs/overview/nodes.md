# Nodes

Nodes are the fundamental building blocks of a flow.
when the node is processed, it performs a task corresponding to its type.

there are three categories of nodes:

- Trigger Nodes
- Process Nodes
- Control Nodes

## Trigger Nodes

The Trigger nodes enter an infinite loop when processed. Within this loop, whenever an event occurs, the node triggers the processing of its child node.

Please refer to the [trigger node plugins page](../nodes/trigger/index.rst) for details on the available trigger nodes.

## Process Nodes

The Process nodes immediately perform their task when processed. After the task finishes, the node triggers the processing of its child node.

Please refer to the [process node plugins page](../nodes/process/index.rst) for details on the available trigger nodes.


## Control Nodes

The Control nodes act as control elements within a flow. They can have multiple child nodes and are used to manage the execution path of the flow — for example, to implement conditional branching.

Please refer to the [control node plugins page](../nodes/control/index.rst) for details on the available trigger nodes.
