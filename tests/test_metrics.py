from kines import metrics

TEST_PERIOD = 5
TEST_STREAM_NAME = "test_stream_name"
TEST_METRIC_NAME = "test_metric"
METRIC_ID = "metric_id"


def test_get_metric_data_query():
    query = metrics.get_metric_data_query(
        TEST_STREAM_NAME, TEST_METRIC_NAME, METRIC_ID, TEST_PERIOD
    )
    assert query["Id"] == METRIC_ID
    assert query["MetricStat"]["Metric"]["MetricName"] == TEST_METRIC_NAME
    assert query["MetricStat"]["Metric"]["Dimensions"][0]["Value"] == TEST_STREAM_NAME
    assert query["MetricStat"]["Stat"] == "Sum"
    assert query["MetricStat"]["Period"] == TEST_PERIOD
