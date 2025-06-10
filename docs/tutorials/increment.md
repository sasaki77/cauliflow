# Increment the count

This tutorial demonstrates how to build a flow that periodically increments a value stored in the blackboard and outputs the updated value to the console.

Create a file named `increment.yml`, write the following content into it.

```yaml
---
sequential:
  flows:
    - name: "init"
      flow:
        - message:
            name: "increment"
            msg: 0
            out_bb: yes
    - name: "main"
      flow:
        - interval:
            name: "interval"
            interval: "{{ macro.interval | float }}"
        - message:
            name: "add"
            msg: "{{ bb.increment + 1 }}"
            out_bb: yes
            out_field: "increment"
        - message:
            name: "out_msg"
            msg: "{{ 'Count: ' + bb.increment | str }}"
        - stdout:
            name: "out"
            src: "{{ fd.out_msg }}"
macros:
  interval: "1"
```

In the above flows, two flows are executed sequentially.
The `init` flow runs first and sets the value of the `increment` key in the blackboard to `0`.
After that, the `main` flow is executed at regular intervals, controlled by an `interval` node. Each time it runs, the `add` node increments the value of `increment` key in the blackboard and updates the value. Next, the `out_msg` node creates a message string and writes it to the flowdata. This string is then passed and printed to the standard output by the `out` node.

The `interval` parameter of the `interval` node is configured using a macro.
Since the macro value is passed as a string, the [filter](../overview/file.md#filters) is used to convert it to a float.

To run the flows, use the cauliflow run command.
the incremented value is showed every second.

```bash
$ cauliflow run increment.yml
Count: 1
Count: 2
Count: 3
Count: 4
Count: 5
```

You can change the interval value by specifying the macro at runtime.

```bash
$ cauliflow run -m interval 5 increment.yml
Count: 1
Count: 2
Count: 3
Count: 4
Count: 5
```
