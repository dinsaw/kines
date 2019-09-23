import hashlib
import boto3
from kines import common
from terminaltables import SingleTable

kinesis_client = boto3.client('kinesis')


def find_shard(stream_name, partition_keys, only_open_shards):
    print(f'Using boto3 version {boto3.__version__}')
    table_data = [
        [
            'PartitionKey',
            'MD5PartitionKey',
            'HashKey',
            'ShardId',
            # 'StartingHashKey',
            # 'EndingHashKey',
            # 'StartingSequenceNumber'
        ]
    ]

    for partition_key in partition_keys:
        md5_partition_key = hashlib.md5(partition_key.encode('UTF-8')).hexdigest()
        hash_key = int(md5_partition_key, base=16)

        shards = kinesis_client.list_shards(StreamName=stream_name)
        for shard in shards['Shards']:

            is_shard_closed = 'EndingSequenceNumber' in shard['SequenceNumberRange']
            if only_open_shards and is_shard_closed:
                continue

            state_icon = common.CLOSED_ICON if is_shard_closed else common.OPEN_ICON
            starting_hash_key = int(shard['HashKeyRange']['StartingHashKey'])
            ending_hash_key = int(shard['HashKeyRange']['EndingHashKey'])

            if starting_hash_key <= hash_key <= ending_hash_key:
                table_data.append([
                    partition_key,
                    md5_partition_key,
                    hash_key,
                    state_icon + ' ' + shard['ShardId'].replace(common.SHARD_ID_PREFIX, ''),
                    # starting_hash_key,
                    # ending_hash_key
                ])

    table = SingleTable(table_data)
    print(table.table)
