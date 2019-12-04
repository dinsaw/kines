import boto3
from kines import constants
from terminaltables import SingleTable

LIST_STREAM_SHORT_HEADERS = [
    "Status - Stream",
    constants.NUMBER_OF_SHARDS_ICON,
    constants.ENHANCED_CONSUMER_ICON,
    # 'ARN',
    constants.RETENTION_PERIOD_ICON,
    # 'Created At',
    constants.ENCRYPTION_TYPE_ICON,
]

LIST_STREAM_FULL_HEADERS = [
    "Stream with Status",
    "OpenShardCount",
    "EnhancedConsumerCount",
    # 'ARN',
    "RetentionPeriod",
    # 'Created At',
    "EncryptionType",
]


def list_streams(name_filter="", full_form=False):
    kinesis_client = boto3.client("kinesis")

    headers = LIST_STREAM_SHORT_HEADERS

    list_stream_response = kinesis_client.list_streams(Limit=100)

    stream_names = list_stream_response["StreamNames"]
    print(f"Found {len(stream_names)} streams.")

    if full_form:
        headers = LIST_STREAM_FULL_HEADERS

    table_data = [headers]

    for stream_name in stream_names:
        describe_stream_summary_response = kinesis_client.describe_stream_summary(
            StreamName=stream_name
        )
        describe_stream_summary = describe_stream_summary_response[
            "StreamDescriptionSummary"
        ]

        stream_status = describe_stream_summary["StreamStatus"]
        table_data.append(
            [
                constants.STREAM_STATUS_ICON_MAP[stream_status] + " " + stream_name,
                describe_stream_summary["OpenShardCount"],
                describe_stream_summary["ConsumerCount"],
                # describe_stream_summary['StreamARN'],
                describe_stream_summary["RetentionPeriodHours"],
                # describe_stream_summary['StreamCreationTimestamp'],
                describe_stream_summary["EncryptionType"],
            ]
        )

    table = SingleTable(table_data)
    print(table.table)


def print_legends(separator=". "):
    for idx, h in enumerate(LIST_STREAM_SHORT_HEADERS):
        print(f"{h} = {LIST_STREAM_FULL_HEADERS[idx]}", end=separator)
    print()

    for k, v in constants.STREAM_STATUS_ICON_MAP.items():
        print(f"{v} = {k} Stream Status", end=separator)
    print()
