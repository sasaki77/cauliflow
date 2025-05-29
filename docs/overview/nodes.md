# Nodes

Nodes are the fundamental building blocks of a flow.
when the node is processed, it performs a task corresponding to its type.

there are three categories of nodes:

- Trigger Nodes
- Process Nodes
- Control Nodes

## Trigger Nodes

The Trigger nodes enter an infinite loop when processed. Within this loop, whenever an event occurs, the node triggers the processing of its child node.

## Process Nodes

The Process nodes immediately perform their task when processed. After the task finishes, the node triggers the processing of its child node.

## Control Nodes

The Control nodes act as control elements within a flow. They can have multiple child nodes and are used to manage the execution path of the flow — for example, to implement conditional branching.
