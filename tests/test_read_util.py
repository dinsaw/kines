import datetime
from dateutil.tz import tzutc, tzlocal
from kines import read_util


def test_get_parsed_data_base64_encoded():
    record = {
        "SequenceNumber": "49600282682944895786267660693075522538255370376250918498",
        "ApproximateArrivalTimestamp": datetime.datetime(
            2019, 10, 10, 16, 22, 41, 761000, tzinfo=tzlocal()
        ),
        "Data": b"eyJldmVudCI6ICIxIn0K",
        "PartitionKey": "4439109",
    }
    assert '{"event": "1"}\n' == read_util.get_parsed_data(record)


def test_get_parsed_data_non_base64():
    record = {
        "SequenceNumber": "49600282682944895786267660693075522538255370376250918498",
        "ApproximateArrivalTimestamp": datetime.datetime(
            2019, 10, 10, 16, 22, 41, 761000, tzinfo=tzlocal()
        ),
        "Data": b'{"event": "2"}',
        "PartitionKey": "4439109",
    }
    assert '{"event": "2"}' == read_util.get_parsed_data(record)
