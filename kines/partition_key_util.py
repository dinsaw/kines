import hashlib

import boto3
from terminaltables import SingleTable

from kines import constants


def find_shard(stream_name, partition_keys, only_open_shards):
    table_data = [
        [
            "PartitionKey",
            "MD5PartitionKey",
            "HashKey",
            "ShardId",
            # 'StartingHashKey',
            # 'EndingHashKey',
            # 'StartingSequenceNumber'
        ]
    ]

    kinesis_client = boto3.client("kinesis")
    shards_response = kinesis_client.list_shards(StreamName=stream_name)

    for partition_key in partition_keys:
        md5_partition_key = hashlib.md5(partition_key.encode("UTF-8")).hexdigest()
        hash_key = int(md5_partition_key, base=16)

        for shard in shards_response["Shards"]:
            is_shard_closed = "EndingSequenceNumber" in shard["SequenceNumberRange"]
            if only_open_shards and is_shard_closed:
                continue

            state_icon = (
                constants.CLOSED_ICON if is_shard_closed else constants.OPEN_ICON
            )
            starting_hash_key = int(shard["HashKeyRange"]["StartingHashKey"])
            ending_hash_key = int(shard["HashKeyRange"]["EndingHashKey"])

            if starting_hash_key <= hash_key <= ending_hash_key:
                table_data.append(
                    [
                        partition_key,
                        md5_partition_key,
                        hash_key,
                        state_icon
                        + " "
                        + shard["ShardId"].replace(constants.SHARD_ID_PREFIX, ""),
                        # starting_hash_key,
                        # ending_hash_key
                    ]
                )

    table = SingleTable(table_data)
    print(table.table)
