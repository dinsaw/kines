from kines import util


def test_convert_size():
    assert "0B" == util.convert_size(0)
    assert "2.0 GB" == util.convert_size(2147483648)
