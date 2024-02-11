from pytest import mark


@mark.parametrize("length, expected", [(66, 100), (200, 300), (201, 300), (66, 100)])
def test_level100(create_level100_padding, length, expected):
    actual: int = create_level100_padding.pad(length)
    assert expected == actual
