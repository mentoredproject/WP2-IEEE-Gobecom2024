from abc import ABC, abstractmethod
from typing import Callable


class PaddingStrategy(ABC):
    @abstractmethod
    def pad(self, length: int) -> int:
        """
        Returns the new packet length.
        """
        ...


def pad_length_equal_to_or_greater_than_mtu(function: Callable):
    mtu: int = 1500

    def wrapper(*args, **kwargs):
        length = args[1]
        if length >= mtu:
            return length
        return function(*args, **kwargs)
    return wrapper
