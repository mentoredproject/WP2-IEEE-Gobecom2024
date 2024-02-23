from pytest import fixture

from adaptive_padding.padding.nearest.nearest_padding import NearestPadding


@fixture(scope="function")
def create_nearest_padding():
    return NearestPadding()
