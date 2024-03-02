from pytest import fixture
from unittest.mock import patch

from adaptive_padding.padding.nearest.nearest_padding import NearestPadding
from tests.nearest.external_integration_mock import ExternalIntegrationMock


@fixture(scope="function")
def create_nearest_padding():
    external_integration_mock = ExternalIntegrationMock()
    return NearestPadding(external_integration_mock)
