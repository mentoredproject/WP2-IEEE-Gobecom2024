from typing import List

from adaptive_padding.padding.nearest.external_integration import ExternalIntegration


class ExternalIntegrationMock(ExternalIntegration):
    def execute(self) -> List[int]:
        return [66, 102, 253, 1236, 1514]
