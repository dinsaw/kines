import datetime
import math
import boto3
from terminaltables import SingleTable

from kines import common, date_util

REPORT_SHORT_HEADERS = [
    'Time',
    'IR',
    'IS',
    'IR/Sec',
    'GR',
    'GR/Sec',
    'GR/IR',
    'WPTE',
    'RPTE',
    'MAX(IAGM)',
]

REPORT_FULL_HEADERS = [
    'Converted Local Time',
    'IncomingRecords',
    'IncomingSize',
    'IncomingRecords Per Sec',
    'GetRecords.Records',
    'GetRecords.Records/Sec',
    'GetRecords/IncomingRecords',
    'WriteProvisionedThroughputExceeded',
    'ReadProvisionedThroughputExceeded',
    'MAX(IteratorAgeMilliSeconds)',
]

M_IB = 'ib'
M_GRR = 'grr'
M_IR = 'ir'
M_GIAM = 'giam'
M_RPTE = 'rpte'
M_WPTE = 'wpte'


def with_exceeded_icon(value):
    if value <= 0:
        return value
    return str(value) + ' ' + common.THROUGHPUT_EXCEEDED_ICON


def display_report(stream_name, period=(60 * 15), past_hours=12, full_form=False):
    start_time = (datetime.datetime.utcnow() - datetime.timedelta(hours=past_hours)).replace(minute=0, second=0)
    end_time = datetime.datetime.utcnow()

    print(f'Using boto3 version {boto3.__version__}')
    cloudwatch_client = boto3.client('cloudwatch')
    headers = REPORT_SHORT_HEADERS

    if full_form:
        headers = REPORT_FULL_HEADERS
    else:
        for idx, h in enumerate(headers):
            print(f'{h} = {REPORT_FULL_HEADERS[idx]}', end='. ')
        print()

    table_data = [headers]
    response = cloudwatch_client.get_metric_data(
        MetricDataQueries=[
            get_metric_data_query(stream_name, 'IncomingRecords', M_IR, period),
            get_metric_data_query(stream_name, 'IncomingBytes', M_IB, period),
            get_metric_data_query(stream_name, 'GetRecords.Records', M_GRR, period),
            get_metric_data_query(stream_name, 'WriteProvisionedThroughputExceeded', M_WPTE, period),
            get_metric_data_query(stream_name, 'ReadProvisionedThroughputExceeded', M_RPTE, period),
            get_metric_data_query(stream_name, 'GetRecords.IteratorAgeMilliseconds', M_GIAM, period, 'Maximum'),
        ],
        StartTime=start_time,
        # StartTime=datetime(2019, 9, 15),
        EndTime=end_time,
        # EndTime=datetime(2019, 9, 16),
        ScanBy='TimestampAscending',
        MaxDatapoints=288
    )
    result_map = {}
    for result in response['MetricDataResults']:
        result_map[result['Id']] = result

    if 0 == len(result_map[M_WPTE]['Timestamps']):
        print(f'No metrics found for past {past_hours} hours')
        return

    walk_through_count = 0
    step_time = datetime.timedelta(seconds=period)
    step_time_in_seconds = step_time.total_seconds()

    while walk_through_count < len(result_map[M_WPTE]['Timestamps']):
        ir_value = get_or_default(result_map[M_IR]['Values'], walk_through_count)
        grr_value = get_or_default(result_map[M_GRR]['Values'], walk_through_count)
        table_data.append(
            [
                date_util.utc_to_local(result_map[M_WPTE]['Timestamps'][walk_through_count]).strftime('%Y-%m-%d %H:%M'),
                ir_value,
                convert_size(get_or_default(result_map[M_IB]['Values'], walk_through_count)),
                "{0:.2f}".format(ir_value / step_time_in_seconds),
                grr_value,
                "{0:.2f}".format(grr_value / step_time_in_seconds),
                # Fraction(ir_value/grr_value).limit_denominator(),
                "{0:.2f}".format(grr_value / ir_value),
                with_exceeded_icon(get_or_default(result_map[M_WPTE]['Values'], walk_through_count)),
                with_exceeded_icon(get_or_default(result_map[M_RPTE]['Values'], walk_through_count)),
                with_exceeded_icon(get_or_default(result_map[M_GIAM]['Values'], walk_through_count)),
            ]
        )
        walk_through_count += 1

    table = SingleTable(table_data)
    print(table.table)


def get_or_default(array, walk_through_count, default_value=0):
    try:
        return array[walk_through_count]
    except IndexError:
        return default_value


def get_metric_data_query(stream_name, metric, metric_id, period, stat='Sum'):
    return {
        'Id': metric_id,
        'MetricStat': {
            'Metric': {
                'Namespace': 'AWS/Kinesis',
                'MetricName': metric,
                'Dimensions': [
                    {
                        'Name': 'StreamName',
                        'Value': stream_name
                    },
                ]
            },
            'Period': period,
            'Stat': stat
        }
    }


def convert_size(size_bytes):
    if size_bytes == 0:
        return "0B"
    size_name = ("B", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB")
    i = int(math.floor(math.log(size_bytes, 1024)))
    p = math.pow(1024, i)
    s = round(size_bytes / p, 2)
    return "%s %s" % (s, size_name[i])
