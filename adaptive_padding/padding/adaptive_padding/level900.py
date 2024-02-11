from dataclasses import dataclass, field
from random import randint
from typing import Dict

from adaptive_padding.padding.padding_strategy import PaddingStrategy


@dataclass
class Level900(PaddingStrategy):
    extra_bytes: int = field(default=0)
    mtu_number_bytes: int = field(default=1500)
    __memory: Dict[int, int] = field(default_factory=dict)

    def __post_init__(self):
        self.__threshold = 900
        self.__extra_bytes = 0

    def pad(self, length: int) -> int:
        if length in self.__memory:
            return self.__memory.get(length)

        try:
            if length < self.mtu_number_bytes:
                if length < self.__threshold:
                    self.extra_bytes = self.__threshold - length
                    self.__memory[length] = length + self.__extra_bytes
                elif length > self.__threshold and length < 999:
                    upper_bound = 1000 - length
                    self.__extra_bytes = randint(1, upper_bound)
                elif length >= 999 and length <= 1399:
                    upper_bound = 1400 - length
                    self.__extra_bytes = randint(1, upper_bound)
                elif length >= 1400:
                    self.__extra_bytes = self.mtu_number_bytes - length
                    self.__memory[length] = length + self.__extra_bytes
                return length + self.__extra_bytes
        except ValueError as e:
            raise e
