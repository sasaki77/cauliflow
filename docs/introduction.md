# Introduction

CauliFlow allows you to construct and run workflows by connecting multiple nodes.
It enables the creation of flexible, reusable workflows by utilising three types of variable: Flowdata, Blackboard and Macros.
Although CauliFlow is primarily designed to work with EPICS PVs, it can also be used for other purposes.

Below is an example of workflows.

```{image} _images/overview.drawio.svg
:alt: overview
:target: _images/overview.drawio.svg
```

These workflows run as follows:
First, `flow1` reads a CSV file and loads EPICS PV names along with their threshold values into the Blackboard.
Then, `flow2` monitors the specified PVs and passes the monitoring data downstream as Flowdata.
Only when the value of PV exceeds the threshold, the relevant information is written to a file.
The path to the CSV file can be specified at runtime using the macro.

## Flows

The example workflows consists of two separate flows: one responsible for reading the CSV file, and the other for monitoring the PVs and handling the data based on the defined thresholds.
CauliFlow can run multiple flows either sequentially or concurrently.

## Nodes

Each flow is composed of nodes. Each node performs a task corresponding to its type when it is processed. there are three categories of nodes:

| Node Categories                                  | Description                                                                                                                                                                                    |
| ------------------------------------------------ | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| [Trigger Nodes](overview/nodes.md#trigger-nodes) | These nodes enter an infinite loop when processed. Within this loop, whenever an event occurs, the node triggers the processing of its child node.                                             |
| [Process Nodes](overview/nodes.md#process-nodes) | These nodes immediately perform their task when processed. After the task finishes, the node triggers the processing of its child node.                                                        |
| [Control Nodes](overview/nodes.md#control-nodes) | These nodes act as control elements within a flow. They can have multiple child nodes and are used to manage the execution path of the flow — for example, to implement conditional branching. |

The nodes used in the example workflow are categorized as follows:

| Node Categories | Nodes                   |
| --------------- | ----------------------- |
| Trigger Nodes   | `camonitor`             |
| Process Nodes   | `input_csv`, `out_file` |
| Control Nodes   | `if`                    |


## Variables

CauliFlow supports three types of key-value variables:

| Variable type                                  | Description                                                    |
| ---------------------------------------------- | -------------------------------------------------------------- |
| [Flowdata](overview/variables.md#flowdata)     | Variable passed from upstream to downstream nodes.             |
| [Blackboard](overview/variables.md#blackboard) | Variable shared across the entire workflow.                    |
| [Macros](overview/variables.md/#macros)        | Variable that can be set at runtime when running the workflow. |

## Flow file

Below is the YAML-format file that defines the above workflows.
Variables can be referenced in the file by enclosing them in double curly braces (`{{ }}`).
Variables can be manipulated using filters. Filters follow the variable and separated by a pipe symbol (`|`).

```yaml
---
sequential:
  flows:
    - name: "flow1"
      flow:
        - in_csv:
            name: "csv"
            path: "{{ macro.csv_path }}"
            format: "key_value"
            out_bb: yes
    - name: "flow2"
      flow:
        - camonitor:
            name: "ca"
            pvname: "{{ bb.csv | dict_keys }}"
        - if:
            name: "if"
            condition: "fd.ca.value > bb.csv[fd.ca.name] | float"
        - out_file:
            name: "out"
            path: "out.txt"
            src: "{{ fd.ca.timestamp | str_pvts + ' ' + fd.ca.name + ' ' + fd.ca.value | str }}"
            parent: "if.child_if"
macros:
  csv_path: "test.csv"
```

## Run flow

To run the workflow, use the `cauliflow run` command in your terminal.

```bash
cauliflow run -m csv_path ./file1.csv ./flows.yml
```

The following is an example of the output written to `out.txt`.

```
2025-05-26 16:28:02.30860 pv1 101.0
2025-05-26 16:28:03.30767 pv1 102.0
2025-05-26 16:28:10.30760 pv2 220.0
2025-05-26 16:28:11.30771 pv2 230.0
```
