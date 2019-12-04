from kines import constants
import boto3
from terminaltables import SingleTable


def display_shard_table(stream_name, only_open_shards, detailed):
    kinesis_client = boto3.client("kinesis")

    shards = kinesis_client.list_shards(StreamName=stream_name)
    headers = [
        "ShardId",
        "ParentShardId",
        "AdjacentParentShardId",
        "% HashKeyRange",
        # 'StartingSequenceNumber'
    ]

    if detailed:
        headers.append("StartingHashKey")
        headers.append("EndingHashKey")

    table_data = [headers]

    for shard in shards["Shards"]:
        is_shard_closed = "EndingSequenceNumber" in shard["SequenceNumberRange"]
        if only_open_shards and is_shard_closed:
            continue

        state_icon = constants.CLOSED_ICON if is_shard_closed else constants.OPEN_ICON
        starting_hash_key = shard["HashKeyRange"]["StartingHashKey"]
        ending_hash_key = shard["HashKeyRange"]["EndingHashKey"]

        data_row = [
            state_icon + " " + shard["ShardId"].replace(constants.SHARD_ID_PREFIX, ""),
            shard.get("ParentShardId", "").replace(constants.SHARD_ID_PREFIX, ""),
            shard.get("AdjacentParentShardId", "").replace(
                constants.SHARD_ID_PREFIX, ""
            ),
            str(cal_range_percentage(starting_hash_key, ending_hash_key)) + "%",
            # shard['SequenceNumberRange']['StartingSequenceNumber']
        ]

        if detailed:
            data_row.append(starting_hash_key)
            data_row.append(ending_hash_key)

        table_data.append(data_row)

    table = SingleTable(table_data)
    print(table.table)


def cal_range_percentage(starting_hash_key, ending_hash_key):
    return ((int(ending_hash_key) - int(starting_hash_key)) / constants.MAX_RANGE) * 100


def print_legends(separator=". "):
    print(f"{constants.CLOSED_ICON} = Closed Shard", end=separator)
    print(f"{constants.OPEN_ICON} = Open Shard", end=separator)
