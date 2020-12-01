from kines import date_util
from freezegun import freeze_time
import datetime as dt


@freeze_time("2020-11-01 7:00:00", tz_offset=+dt.timedelta(hours=5, minutes=30))
def test_to_iterator_timestamp():
    print("now = ", dt.datetime.now())
    assert dt.datetime(2020, 11, 1, 5, 55) == date_util.to_iterator_timestamp("1h5m")
    assert dt.datetime(2020, 11, 1, 6, 55) == date_util.to_iterator_timestamp("5m")
    assert dt.datetime(2020, 11, 1, 6, 00) == date_util.to_iterator_timestamp("1h")
    assert "2016-04-04T19:58:46.480-00:00" == date_util.to_iterator_timestamp(
        "2016-04-04T19:58:46.480-00:00"
    )
