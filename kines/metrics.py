import datetime
import boto3
from terminaltables import SingleTable

from kines import constants, date_util
from kines.util import convert_size, get_or_default

REPORT_SHORT_HEADERS = [
    "Time",
    "IR",
    "IS",
    "IR/Sec",
    "GR",
    "GR/Sec",
    "GR/IR",
    "WPTE",
    "RPTE",
    "MAX(IAGM)",
]

REPORT_FULL_HEADERS = [
    "Converted Local Time",
    "IncomingRecords",
    "IncomingSize",
    "IncomingRecords Per Sec",
    "GetRecords.Records",
    "GetRecords.Records/Sec",
    "GetRecords/IncomingRecords",
    "WriteProvisionedThroughputExceeded",
    "ReadProvisionedThroughputExceeded",
    "MAX(IteratorAgeMilliSeconds)",
]

M_IB = "ib"
M_GRR = "grr"
M_IR = "ir"
M_GIAM = "giam"
M_RPTE = "rpte"
M_WPTE = "wpte"


def with_exceeded_icon(value):
    if value <= 0:
        return value
    return str(value) + " " + constants.THROUGHPUT_EXCEEDED_ICON


def display_report(stream_name, period=(60 * 15), past_hours=12, full_form=False):
    start_time = calculate_start_time(past_hours)
    end_time = datetime.datetime.utcnow()

    cloudwatch_client = boto3.client("cloudwatch")
    headers = REPORT_SHORT_HEADERS

    if full_form:
        headers = REPORT_FULL_HEADERS

    table_data = [headers]
    response = cloudwatch_client.get_metric_data(
        MetricDataQueries=[
            get_metric_data_query(stream_name, "IncomingRecords", M_IR, period),
            get_metric_data_query(stream_name, "IncomingBytes", M_IB, period),
            get_metric_data_query(stream_name, "GetRecords.Records", M_GRR, period),
            get_metric_data_query(
                stream_name, "WriteProvisionedThroughputExceeded", M_WPTE, period
            ),
            get_metric_data_query(
                stream_name, "ReadProvisionedThroughputExceeded", M_RPTE, period
            ),
            get_metric_data_query(
                stream_name,
                "GetRecords.IteratorAgeMilliseconds",
                M_GIAM,
                period,
                "Maximum",
            ),
        ],
        StartTime=start_time,
        EndTime=end_time,
        ScanBy="TimestampAscending",
        MaxDatapoints=288,
    )
    result_map = {}
    for result in response["MetricDataResults"]:
        result_map[result["Id"]] = result

    if 0 == len(result_map[M_WPTE]["Timestamps"]):
        print(f"No metrics found for past {past_hours} hours")
        return

    walk_through_count = 0
    step_time = datetime.timedelta(seconds=period)
    step_time_in_seconds = step_time.total_seconds()

    while walk_through_count < len(result_map[M_WPTE]["Timestamps"]):
        ir_value = get_or_default(result_map[M_IR]["Values"], walk_through_count)
        grr_value = get_or_default(result_map[M_GRR]["Values"], walk_through_count)
        table_data.append(
            [
                get_timestamp(result_map, walk_through_count),
                ir_value,
                get_incoming_data_size(result_map, walk_through_count),
                get_value_per_second(ir_value, step_time_in_seconds),
                grr_value,
                get_value_per_second(grr_value, step_time_in_seconds),
                get_value_per_second(grr_value, ir_value),
                get_write_throughput_exceeded_count(result_map, walk_through_count),
                get_read_throughput_exceeded_count(result_map, walk_through_count),
                get_max_iterator_age_millis(result_map, walk_through_count),
            ]
        )
        walk_through_count += 1

    table = SingleTable(table_data)
    print(table.table)


def get_max_iterator_age_millis(result_map, walk_through_count):
    return with_exceeded_icon(
        get_or_default(result_map[M_GIAM]["Values"], walk_through_count)
    )


def get_read_throughput_exceeded_count(result_map, walk_through_count):
    return with_exceeded_icon(
        get_or_default(result_map[M_RPTE]["Values"], walk_through_count)
    )


def get_write_throughput_exceeded_count(result_map, walk_through_count):
    return with_exceeded_icon(
        get_or_default(result_map[M_WPTE]["Values"], walk_through_count)
    )


def get_value_per_second(value, step_time_in_seconds):
    return "{0:.2f}".format(value / step_time_in_seconds)


def get_incoming_data_size(result_map, walk_through_count):
    return convert_size(get_or_default(result_map[M_IB]["Values"], walk_through_count))


def get_timestamp(result_map, walk_through_count):
    return date_util.utc_to_local(
        result_map[M_WPTE]["Timestamps"][walk_through_count]
    ).strftime("%Y-%m-%d %H:%M")


def calculate_start_time(past_hours):
    start_time = datetime.datetime.utcnow() - datetime.timedelta(hours=past_hours)
    return start_time.replace(minute=0, second=0)


def print_legends(separator=". "):
    for idx, h in enumerate(REPORT_SHORT_HEADERS):
        print(f"{h} = {REPORT_FULL_HEADERS[idx]}", end=separator)
    print()


def get_metric_data_query(stream_name, metric, metric_id, period, stat="Sum"):
    return {
        "Id": metric_id,
        "MetricStat": {
            "Metric": {
                "Namespace": "AWS/Kinesis",
                "MetricName": metric,
                "Dimensions": [{"Name": "StreamName", "Value": stream_name},],
            },
            "Period": period,
            "Stat": stat,
        },
    }
