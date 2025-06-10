import time
from typing import Any


def _str(target: Any) -> str:
    """
    description:
      - Convert the value into a string.
    """
    return str(target)


def _int(target: Any) -> int:
    """
    description:
      - Convert the value into an integer.
    """
    return int(target)


def _float(target: Any) -> float:
    """
    description:
      - Convert the value into a float.
    """
    return float(target)


def _bool(target: Any) -> bool:
    """
    description:
      - Convert the value into a boolean.
    """
    return bool(target)


def dict_keys(target: dict) -> list:
    """
    description:
      - Return a list of all the keys from the dictionary.
    example: |-
      # item: ["key1", "key2"]
      item: "{{ {'key1': 1, 'key2': 2} | dict_keys }}"
    """
    return list(target.keys())


def dict_values(target: dict) -> list:
    """
    description:
      - Return a list of all the values from the dictionary.
    example: |-
      # item: [1, 2]
      item: "{{ {'key1': 1, 'key2': 2} | dict_values }}"
    """
    return list(target.values())


def dict2item(key_name: str, val_name: str, target: dict | None = None) -> list[dict]:
    """
    description:
      - Return a list of dictionaries from the dictionary.
    parameters:
      key_name:
        description: The name of the dictionary’s keys.
      val_name:
        description: The name of the dictionary’s values.
    example: |-
      # item: [{"k": "key1", "v": 1}, {"k": "key2", "v": 2}]
      item: "{{ {'key1': 1, 'key2': 2} | dict2item('k','v') }}"
    """
    if not isinstance(target, dict):
        raise ValueError
    dictlist = []
    for k, v in target.items():
        dictlist.append({key_name: k, val_name: v})
    return dictlist


def str_pvts(tstamp: float) -> str:
    """
    description:
      - Return a string of formated timestamp from the float value of pyepics timestamp.
    example: |-
      # item: "2025-05-26 14:48:29.99555"
      item: "{{ 1748238509.995554 | str_pvts }}"
    """
    tstamp, frac = divmod(tstamp, 1)
    return "%s.%5.5i" % (
        time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(tstamp)),
        round(1.0e5 * frac),
    )


def join(separator: str, target: list[str] | None = None) -> str:
    """
    description:
      - Join a list of string with separator.
    parameters:
      separator:
        description: Separator for the concatenation of the strings.
    example: |-
      # item: "Hello, world"
      item: "{{ ["Hello", "world"] | join(', ') }}"
    """
    if not isinstance(target, list):
        raise ValueError
    return separator.join(target)


FILTERS = {
    "str": _str,
    "int": _int,
    "float": _float,
    "bool": _bool,
    "str_pvts": str_pvts,
    "dict_keys": dict_keys,
    "dict_values": dict_values,
    "dict2item": dict2item,
    "join": join,
}
