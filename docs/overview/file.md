# Flows file

Flows file defines the flows to be run.
It specifies the structure and sequence of flows, including their associated nodes, parameters, and macros settings.

## Basic Syntax

Flows file is expressed in YAML format.
The basic syntax is as follows:

```yaml
---
<flows type| sequential or concurrent>:
  flows:
    - name: "flow name1"
      flow:
        - <node type>:
            name: "node name1"
            <node parameter1>: "param1"
            <node parameter2>: "param2"
    - name: "flow name2"
      flow:
        - <node type>:
            name: "node name2"
            <node parameter1>: "param1"
            <node parameter2>: "param2"
        - <node type>:
            name: "node name2"
            <node parameter1>: "param1"
            <node parameter2>: "param2"
macros:
  <macro name>: "macro data"
```

The flow type can be set to either `sequential` or `concurrent`.
Sequential flows run each flow in the order they are defined, from top to bottom.
Concurrent flows run multiple flows in parallel.

The elements that make up the flows are organized in the following hierarchical structure.

```
├── flows type
│   └── flows
│        ├── flow
│        │   ├── node
│        │   │   ├── parameter
│        │   │   └── parameter
│        │   └── node
│        │       ├── parameter
│        │       └── parameter
│        └── flow
│            ├── node
│            │   ├── parameter
│            │   └── parameter
│            └── node
│                ├── parameter
│                └── parameter
└── macros
     ├── macro
     └── macro
```

## Parent node

The nodes that constitute a flow are generally linked in a sequential manner.
By default, a node implicitly considers the previously defined node as its parent.

For example, consider the following flow file.

```yaml
- name: "flow"
  flow:
    - <node-A>:
        name: "A"
    - <node-B>:
        name: "B"
    - <node-C>:
        name: "C"
```

The structure of the flow in the above example is as follows.

```{mermaid}
flowchart LR
    A --> B --> C
```

Below is an example demonstrating how to explicitly define a parent node. `parent` parameter can be used to set a parent node.
Note that when specifying the parent node, the name in the `name` parameter must be used.

```yaml
- name: "flow"
  flow:
    - <node-A>:
        name: "A"
    - <node-B>:
        name: "B"
        parent: "A"
    - <node-C>:
        name: "C"
        parent: "B"
```

Almost all nodes implicitly have a parameter called `child`. When only the node name is specified in the `parent` parameter, the reference is assigned to the `child` parameter of that node. If you want to assign a node to a parameter other than `child` in the control nodes, use the format `<node name>.<parameter>`.

The following is an example that uses an `if` node, which is categorized as the control node.
`if` node supports two special child nodes: `child_if` and `child_else`. If the `condition` parameter evaluates to True, the `child_if` node is processed; otherwise, the `child_else` node is processed. Once either of these branches completes, the standard `child` node is subsequently processed.

```yaml
- name: "flow"
  flow:
    - <node-A>:
        name: "A"
    - if:
        name: "if-node"
        condition: "1 == 1"
    - <node-B>:
        name: "B"
        parent: "if-node.child_if"
    - <node-C>:
        name: "C"
    - <node-D>:
        name: "D"
        parent: "if-node.child_else"
    - <node-E>:
        name: "E"
    - <node-F>:
        name: "F"
        parent: "if-node"
    - <node-G>:
        name: "G"
```

The structure of the flow in the above example is as follows.

```{mermaid}
flowchart LR
    A --> if-node
    if-node -- child_if --> B --> C
    if-node -- child_else --> D --> E
    C --> F
    E --> F
    F --> G
```

## Expressions

Within the node parameters, segments of a string that are enclosed in double curly braces (`{{ }}`) are interpreted as expressions.
Expressions are generally evaluated before the execution of the node process.

### Variables

Variables can be used within these expressions.
The following table lists the names used to reference each variable within expressions.

| Variable type | Reference within expressions |
| ------------- | ---------------------------- |
| Flowdata      | `fd`                         |
| Blackboard    | `bb`                         |
| Macros        | `macro`                      |

Variables stores values of arbitrary data types in a key-value dictionary structure.
The following are examples of how to reference each variable.

```yaml
# Access the value of 'key1' from the flowdata with dot (.) access.
item: "{{ fd.key1 }}"

# Access the value of 'key1' from the flowdata with subscript syntax ([]).
item: "{{ fd['key1'] }}"

# Access the value of 'name' from the dictionary stored under the 'key2' in the blackboard.
item: "{{ bb.key2.name }}"

# Access the value of 'head' from the macros.
item: "{{ macro.head }}"
```

### Filters

Variables and data in expression can be manipulated using filters. Filters follow the variable and separated by a pipe symbol (`|`).
Some filters require optional arguments in parentheses.
Multiple filters can be chained together, where the output of one filter is passed as the input to the next.

For example, `{{ {"key1": 1, "key2": 2} | dict_keys }}` returns `["key1", "key2"]`.

For more information about each filter, see [Filters page](../filters.rst).

### Operators

The table below shows the operators that can be used within expressions, as well as their order of precedence.

| Operator                                                         | Description                                         |
| ---------------------------------------------------------------- | --------------------------------------------------- |
| `()`                                                             | Grouping                                            |
| `*`, `/`, `//`, `%`                                              | Multiplication, division, floor division, remainder |
| `+`, `-`                                                         | Addition and subtraction                            |
| `==`, `!=`, `>`, `<`, `>=`, `<=`, `is`, `is not`, `in`, `not in` | Comparison and identity/membership tests            |
| `not`                                                            | Boolean NOT                                         |
| `and`                                                            | Boolean AND                                         |
| `or`                                                             | Boolean OR                                          |

###  Data Types

The following data types are available for use within expressions. Most of them can be referenced in the same way as Python data types. However, list slicing is not supported.

- `str`
- `int`
- `float`
- `bool`
- `list`
- `dict`
