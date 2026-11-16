import boto3
from kines import constants, date_util
import click
from terminaltables import SingleTable
import base64
from textwrap import wrap
import time
import aws_kinesis_agg.deaggregator as deagg

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
    raw=False,
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

    if not raw:
        click.echo(
            f"Creating shard iterator with arguments = {get_shard_iterator_args}"
        )
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
            records_to_display = [record]
            try:
                deaggs = list(
                    deagg.iter_deaggregate_records([record], data_format="Boto3")
                )
                if deaggs and deaggs[0].get("kinesis", {}).get("aggregated"):
                    records_to_display = deaggs
            except Exception:
                pass

            for item in records_to_display:
                if "kinesis" in item and item["kinesis"].get("aggregated"):
                    k = item["kinesis"]
                    parsed_data = get_parsed_data({"Data": k["data"]})
                    sub_seq = f" (sub: {k.get('subSequenceNumber', 0)})"
                    table_data = [
                        ["SequenceNumber", f"{k['sequenceNumber']}{sub_seq}"],
                        [
                            "ApproximateArrivalTimestamp",
                            k["approximateArrivalTimestamp"],
                        ],
                        ["PartitionKey", k["partitionKey"]],
                        ["EncryptionType", record.get("EncryptionType")],
                        ["Decoded Data", parsed_data],
                    ]
                else:
                    parsed_data = get_parsed_data(item)
                    table_data = [
                        ["SequenceNumber", item["SequenceNumber"]],
                        [
                            "ApproximateArrivalTimestamp",
                            item["ApproximateArrivalTimestamp"],
                        ],
                        ["PartitionKey", item["PartitionKey"]],
                        ["EncryptionType", item.get("EncryptionType")],
                        ["Decoded Data", parsed_data],
                    ]

                if raw:
                    click.echo(parsed_data.rstrip("\r\n"))
                else:
                    table = SingleTable(table_data)
                    max_width = table.column_max_width(1)
                    wrapped_string = "\n".join(wrap(parsed_data, max_width))
                    table.table_data[4][1] = wrapped_string
                    print(table.table)

        if not records_response["Records"]:
            if raw:
                click.echo("No records found for this api call 😔", err=True)
            else:
                click.echo("No records found for this api call 😔")

        if follow:
            if raw:
                click.echo(f"Waiting for {WAIT_FOR_SECONDS} seconds...", err=True)
            else:
                click.echo(f"Waiting for {WAIT_FOR_SECONDS} seconds...")
            time.sleep(WAIT_FOR_SECONDS)
        else:
            if raw:
                fetch_more = click.confirm(
                    "Fetch more records?", default=True, err=True
                )
            else:
                fetch_more = click.confirm("Fetch more records?", default=True)

        shard_iterator = records_response["NextShardIterator"]


def get_parsed_data(kinesis_record):
    data = kinesis_record.get("Data", b"")
    try:
        return base64.b64decode(data).decode(UTF_8)
    except Exception:
        try:
            return data.decode(UTF_8) if isinstance(data, bytes) else str(data)
        except Exception:
            return str(data)
