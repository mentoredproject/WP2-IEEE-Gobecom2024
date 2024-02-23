from pytest import mark


@mark.parametrize("length, expected", [(66, 100), (200, 300), (201, 300), (66, 100)])
def test_level100(create_level100_padding, length, expected):
    actual: int = create_level100_padding.pad(length)
    assert expected == actual


@mark.parametrize("length", [1500, 1501, 1502, 1510, 1514])
def test_level100_when_greater_than_or_equal_to_1500_return_same_length(create_level100_padding, length):
    actual: int = create_level100_padding.pad(length)
    assert length == actual
