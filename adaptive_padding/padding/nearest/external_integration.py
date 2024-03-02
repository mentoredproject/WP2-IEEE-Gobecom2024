from abc import ABC, abstractmethod
from dataclasses import dataclass
from subprocess import run, PIPE
from typing import List

import pdb


class ExternalIntegration(ABC):
    @abstractmethod
    def execute(self) -> List[int]:
        ...


@dataclass
class JuliaExternalIntegration(ExternalIntegration):
    julia_command: List[str]

    def execute(self) -> List[int]:
        command_output = run(self.julia_command, stdout=PIPE, stderr=PIPE, universal_newlines=True)
        return self.__get_packets_length(command_output.stdout)

    def __get_packets_length(self, command_output: str) -> List[int]:
        packet_sizes = command_output.split("\n")[1].split('[')[1].replace(
            '])',
            '').split(', ')
        breakpoint()
        return [int(x) for x in packet_sizes]
