import os
from tempfile import TemporaryDirectory

from picoquake.utils import *


def test_get_axis_combinations():
    assert get_axis_combinations("x") == {"x"}
    assert get_axis_combinations("xyz") == {"x", "y", "z",
                                            "xy", "xz", "yx", "yz", "zx", "zy",
                                            "xyz", "xzy", "yxz", "yzx", "zxy", "zyx"}
    assert get_axis_combinations("abcd") == {"a", "b", "c", "d",
                                            "ab", "ac", "ad", "ba", "bc", "bd", "ca", "cb", "cd", "da", "db", "dc",
                                            "abc", "abd", "acb", "acd", "adb", "adc", "bac", "bad", "bca", "bcd", "bda", "bdc",
                                            "cab", "cad", "cba", "cbd", "cda", "cdb", "dab", "dac", "dba", "dbc", "dca", "dcb",
                                            "abcd", "abdc", "acbd", "acdb", "adbc", "adcb", "bacd", "badc", "bcad", "bcda", "bdac", "bdca",
                                            "cabd", "cadb", "cbad", "cbda", "cdab", "cdba", "dabc", "dacb", "dbac", "dbca", "dcab", "dcba"}


def test_deque_get_last_n():
    d = deque([1, 2, 3, 4, 5])
    assert deque_get_last_n(d, 3) == [3, 4, 5]
    assert deque_get_last_n(d, 5) == [1, 2, 3, 4, 5]
    assert deque_get_last_n(d, 6) == [1, 2, 3, 4, 5]
    assert deque_get_last_n(d, 0) == []
    assert deque_get_last_n(d, -1) == []
    d = deque()
    assert deque_get_last_n(d, 3) == []
    assert deque_get_last_n(d, 0) == []
    assert deque_get_last_n(d, -1) == []


def test_deque_slice():
    dq = deque([1, 2, 3, 4, 5, 6, 7, 8, 9, 10])
    test_slices = [(None, None), (None, 3), (0, 3), (0, 10), (3, 7),
                   (None, -1), (-5, None), (-5, -3), (0, -3), (3, -3), (0, -10)]
    for start, end in test_slices:
        assert deque_slice(dq, start, end) == list(dq)[start:end]
    

def test_get_unique_filename():
    with TemporaryDirectory() as temp_dir:
        # Define a base filename
        base_filename = os.path.join(temp_dir, "file.csv")
        
        # Test when file does not exist
        assert get_unique_filename(base_filename) == base_filename
        
        # Create the base file
        with open(base_filename, 'w') as f:
            f.write('test content')

        # Test when file exists
        assert get_unique_filename(base_filename) == os.path.join(temp_dir, "file_1.csv")
        
        # Create the first unique file
        with open(os.path.join(temp_dir, "file_1.csv"), 'w') as f:
            f.write('test content')

        # Test when base file and first unique file exist
        assert get_unique_filename(base_filename) == os.path.join(temp_dir, "file_2.csv")
