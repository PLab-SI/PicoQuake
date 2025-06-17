from itertools import permutations
from collections import deque
from typing import List, Any, Optional
import os


def get_axis_combinations(axis: str) -> set:
    return set(''.join(p) for i in range(1, len(axis) + 1) for p in permutations(axis, i))


def deque_get_last_n(data: deque, n: int) -> List[Any]:
    """
    Get the last n elements from a deque. Does not remove the elements from the deque.

    Args:
    data: Deque with data.
    n: Number of elements to get.

    Returns:
    List with the last n elements from the deque. If n is greater than the length of the deque, all elements are returned.
    """
    start_idx = max(0, len(data) - n)
    
    return [data[i] for i in range(start_idx, len(data))]

def remove_first_n_elements(data: deque, n: int) -> None:
    """
    Remove the first n elements from a deque.
    
    Args:
    data: Deque with data.
    n: Number of elements to remove.    
    """
    for i in range(n):
        data.pop()    

def deque_slice(dq: deque, start: Optional[int], end: Optional[int] = None) -> List[Any]:
    """
    Return a slice from the deque. Behaves like the list slice method.
    
    Args:
    dq: The deque to slice.
    start: The starting index of the slice.
    end : The ending index of the slice.
    
    Returns:
    deque: A deque containing the specified slice.
    """
    if start is None:
        start = 0
    if end is None:
        end = len(dq)
    if start < 0:
        start = len(dq) + start
    if end < 0:
        end = len(dq) + end
    if start < 0:
        start = 0
    if end > len(dq):
        end = len(dq)
    return [dq[i] for i in range(start, end)]


def get_unique_filename(path: str):
    """
    Returns a unique filename by appending a sequential number if the file already exists.
    
    Args:
        path: The path to the original file.
    
    Returns:
        A unique filename.
    """
    if not os.path.isfile(path):
        return path
    
    base, extension = os.path.splitext(path)
    counter = 1
    new_path = f"{base}_{counter}{extension}"
    
    while os.path.isfile(new_path):
        counter += 1
        new_path = f"{base}_{counter}{extension}"
    
    return new_path
