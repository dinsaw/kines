import json
import uuid
import boto3
import click
from terminaltables import SingleTable
import aws_kinesis_agg.aggregator as agg

UTF_8 = "utf-8"


def put(
    stream_name,
    partition_keys=(),
    data_list=(),
    file_path=None,
    aggregate=False,
    explicit_hash_key=None,
):
    records = parse_records(partition_keys, data_list, file_path)
    if not records:
        raise click.UsageError(
            "No record data provided. Use -d/--data or -f/--file to specify data."
        )

    if aggregate or len(records) > 1:
        if aggregate:
            return put_aggregated_record(
                stream_name, records, explicit_hash_key=explicit_hash_key
            )

    # Single record put
    record = records[0]
    return put_single_record(
        stream_name,
        partition_key=record["partition_key"],
        data=record["data"],
        explicit_hash_key=explicit_hash_key or record.get("explicit_hash_key"),
    )


def parse_records(partition_keys, data_list, file_path):
    records = []

    # Parse from file if provided
    if file_path:
        with open(file_path, "r", encoding=UTF_8) as f:
            content = f.read().strip()
            try:
                parsed_json = json.loads(content)
                if isinstance(parsed_json, list):
                    for item in parsed_json:
                        if isinstance(item, dict):
                            pk = str(
                                item.get("partition_key")
                                or item.get("PartitionKey")
                                or uuid.uuid4().hex
                            )
                            dt = item.get("data") or item.get("Data") or ""
                            if not isinstance(dt, str):
                                dt = json.dumps(dt)
                            records.append({"partition_key": pk, "data": dt})
                        else:
                            records.append(
                                {"partition_key": uuid.uuid4().hex, "data": str(item)}
                            )
                elif isinstance(parsed_json, dict):
                    pk = str(
                        parsed_json.get("partition_key")
                        or parsed_json.get("PartitionKey")
                        or uuid.uuid4().hex
                    )
                    dt = parsed_json.get("data") or parsed_json.get("Data") or content
                    if not isinstance(dt, str):
                        dt = json.dumps(dt)
                    records.append({"partition_key": pk, "data": dt})
                else:
                    records.append({"partition_key": uuid.uuid4().hex, "data": content})
            except (json.JSONDecodeError, ValueError):
                records.append({"partition_key": uuid.uuid4().hex, "data": content})

    # Parse from CLI options
    pks = list(partition_keys)
    datas = list(data_list)

    if datas:
        for idx, d in enumerate(datas):
            if idx < len(pks):
                pk = pks[idx]
            elif pks:
                pk = pks[0]
            else:
                pk = uuid.uuid4().hex
            records.append({"partition_key": pk, "data": d})

    return records


def put_single_record(stream_name, partition_key, data, explicit_hash_key=None):
    kinesis_client = boto3.client("kinesis")

    payload_bytes = data.encode(UTF_8) if isinstance(data, str) else data

    put_args = {
        "StreamName": stream_name,
        "PartitionKey": partition_key,
        "Data": payload_bytes,
    }
    if explicit_hash_key:
        put_args["ExplicitHashKey"] = explicit_hash_key

    response = kinesis_client.put_record(**put_args)

    data_display = data if isinstance(data, str) else str(data)
    if len(data_display) > 80:
        data_display = data_display[:77] + "..."

    table_data = [
        ["StreamName", stream_name],
        ["ShardId", response.get("ShardId", "")],
        ["SequenceNumber", response.get("SequenceNumber", "")],
        ["PartitionKey", partition_key],
        ["EncryptionType", response.get("EncryptionType", "NONE")],
        ["Data", data_display],
    ]
    table = SingleTable(table_data)
    click.echo(table.table)
    click.echo(
        f"Successfully put 1 record into shard {response.get('ShardId')} of stream '{stream_name}'."
    )
    return response


def put_aggregated_record(stream_name, records, explicit_hash_key=None):
    kinesis_client = boto3.client("kinesis")

    aggregator = agg.RecordAggregator()
    for rec in records:
        pk = rec["partition_key"]
        data_str = rec["data"]
        ehk = rec.get("explicit_hash_key") or explicit_hash_key
        aggregator.add_user_record(pk, data_str, ehk)

    agg_record = aggregator.clear_and_get()
    if not agg_record:
        raise click.ClickException("Failed to aggregate records.")

    agg_pk, agg_ehk, agg_data = agg_record.get_contents()

    put_args = {
        "StreamName": stream_name,
        "PartitionKey": agg_pk,
        "Data": agg_data,
    }
    if agg_ehk:
        put_args["ExplicitHashKey"] = agg_ehk

    response = kinesis_client.put_record(**put_args)

    table_data = [
        ["StreamName", stream_name],
        ["RecordType", "Aggregated (KPL)"],
        ["UserRecordsCount", len(records)],
        ["ShardId", response.get("ShardId", "")],
        ["SequenceNumber", response.get("SequenceNumber", "")],
        ["AggregatedPartitionKey", agg_pk],
        ["EncryptionType", response.get("EncryptionType", "NONE")],
    ]
    table = SingleTable(table_data)
    click.echo(table.table)
    click.echo(
        f"Successfully put 1 aggregated record ({len(records)} user records) into shard {response.get('ShardId')} of stream '{stream_name}'."
    )
    return response
