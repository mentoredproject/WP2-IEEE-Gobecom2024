from pytest import mark


@mark.parametrize("length, expected", [(60, 66), (66, 66), (67, 102), (202, 253), (1237, 1514)])
def test_nearest_pad(create_nearest_padding, length, expected):
    actual: int = create_nearest_padding.pad(length)
    assert expected == actual
