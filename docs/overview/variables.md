# Variables

CauliFlow supports three types of key-value variables:

- [Flowdata](#flowdata)
- [Blackboard](#blackboard)
- [Macros](#macros)

Variables can be referenced in the [flows file](file.md) by enclosing them in double curly braces. For more details, please refer to [this page](file.md#variables).

## Flowdata

Flowdata is a variable passed from upstream to downstream nodes.
Nodes can update Flowdata with either their own node name or an arbitrary key. However, they are not allowed to overwrite existing values associated with the same key in Flowdata.

## Blackboard

Blackboard is a variable shared across the entire workflow.
Nodes can update Blackboard with either their own node name or an arbitrary key.
they can overwrite existing values associated with the same key in Blackboard.

## Macros

Macros is a variable that can be set at runtime when running the workflow.
A macro value can be defined with a default value in the flows file.
