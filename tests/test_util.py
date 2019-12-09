from kines import util


def test_convert_size():
    assert "0B" == util.convert_size(0)
    assert "2.0 GB" == util.convert_size(2147483648)


def test_get_or_default():
    test_array = ["a", "b", "c"]
    assert "c" == util.get_or_default(test_array, 2)
    assert 0 == util.get_or_default(test_array, 3)
    assert "d" == util.get_or_default(test_array, 3, "d")
