from dataclasses import dataclass, field
from typing import List, Dict

from adaptive_padding.padding.nearest.external_integration import ExternalIntegration
from adaptive_padding.padding.padding_strategy import PaddingStrategy, pad_length_equal_to_or_greater_than_mtu


@dataclass
class NearestPadding(PaddingStrategy):
    external_integration: ExternalIntegration
    __memory: Dict[int, int] = field(default_factory=dict)

    def __post_init__(self):
        self.lengths: List[int] = self.external_integration.execute()

    @pad_length_equal_to_or_greater_than_mtu
    def pad(self, length: int) -> int:
        if length in self.__memory:
            return self.__memory.get(length)

        extra_bytes = 0
        for l in self.lengths:
            if l >= length:
                extra_bytes = l - length
                break
        self.__memory[length] = length + extra_bytes
        return self.__memory.get(length)
