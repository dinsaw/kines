import boto3
from kines import constants, date_util
import click
from terminaltables import SingleTable
import base64
from textwrap import wrap
import time

UTF_8 = "utf-8"
WAIT_FOR_SECONDS = 2


def walk(
    stream_name,
    shard_id,
    sequence_number=None,
    get_records_limit=5,
    follow=False,
    latest=False,
    timestamp=None,
):
    kinesis_client = boto3.client("kinesis")

    if not shard_id.startswith(constants.SHARD_ID_PREFIX):
        shard_id = constants.SHARD_ID_PREFIX + shard_id

    get_shard_iterator_args = {"StreamName": stream_name, "ShardId": shard_id}

    if sequence_number:
        get_shard_iterator_args["ShardIteratorType"] = "AT_SEQUENCE_NUMBER"
        get_shard_iterator_args["StartingSequenceNumber"] = sequence_number
    elif latest:
        get_shard_iterator_args["ShardIteratorType"] = "LATEST"
    elif timestamp:
        get_shard_iterator_args["ShardIteratorType"] = "AT_TIMESTAMP"
        get_shard_iterator_args["Timestamp"] = date_util.to_iterator_timestamp(
            timestamp
        )
    else:
        get_shard_iterator_args["ShardIteratorType"] = "TRIM_HORIZON"

    click.echo(f"Creating shard iterator with arguments = {get_shard_iterator_args}")
    shard_iterator_response = kinesis_client.get_shard_iterator(
        **get_shard_iterator_args
    )

    shard_iterator = shard_iterator_response["ShardIterator"]
    fetch_more = True
    while fetch_more:

        records_response = kinesis_client.get_records(
            ShardIterator=shard_iterator, Limit=get_records_limit
        )

        for record in records_response["Records"]:
            parsed_data = get_parsed_data(record)
            table_data = [
                ["SequenceNumber", record["SequenceNumber"]],
                ["ApproximateArrivalTimestamp", record["ApproximateArrivalTimestamp"]],
                ["PartitionKey", record["PartitionKey"]],
                ["EncryptionType", record.get("EncryptionType")],
                ["Decoded Data", parsed_data],
            ]

            table = SingleTable(table_data)
            max_width = table.column_max_width(1)
            wrapped_string = "\n".join(wrap(parsed_data, max_width))
            table.table_data[4][1] = wrapped_string
            print(table.table)

        if not records_response["Records"]:
            click.echo("No records found for this api call 😔")

        if follow:
            click.echo(f"Waiting for {WAIT_FOR_SECONDS} seconds...")
            time.sleep(WAIT_FOR_SECONDS)
        else:
            fetch_more = click.confirm("Fetch more records?", default=True)

        shard_iterator = records_response["NextShardIterator"]


def get_parsed_data(kinesis_record):
    try:
        return base64.b64decode(kinesis_record["Data"]).decode(UTF_8)
    except:
        return kinesis_record["Data"].decode(UTF_8)
