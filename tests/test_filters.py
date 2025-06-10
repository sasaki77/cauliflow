from cauliflow.filters import dict2item, dict_keys, dict_values, join


def test_dict_keys():
    item = dict_keys({"key1": 1, "key2": 2})
    assert item == ["key1", "key2"]


def test_dict_values():
    item = dict_values({"key1": 1, "key2": 2})
    assert item == [1, 2]


def test_dict2item():
    item = dict_values({"key1": 1, "key2": 2})
    item = dict2item("k", "v", {"key1": 1, "key2": 2})
    assert item == [{"k": "key1", "v": 1}, {"k": "key2", "v": 2}]


def test_join():
    item = join(", ", ["Hello", "world"])
    assert item == "Hello, world"
