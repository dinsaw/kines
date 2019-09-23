import boto3
import click
import time


def scale_up(stream_name):
    print(f'Using boto3 version {boto3.__version__}')
    kinesis_client = boto3.client('kinesis')

    open_shards = get_open_shards(kinesis_client, stream_name)

    open_shard_count = len(open_shards)
    click.secho(f'You have {open_shard_count} open shards. '
                f'You will have {open_shard_count * 2} open shards after this operation.', fg='blue')
    click.confirm('Do you want to continue?', abort=True)

    for shard in open_shards:
        starting_hash_key = int(shard['HashKeyRange']['StartingHashKey'])
        ending_hash_key = int(shard['HashKeyRange']['EndingHashKey'])
        new_hash_key = int((starting_hash_key + ending_hash_key) / 2)
        shard_id = shard["ShardId"]
        click.secho(f'Splitting {shard_id} ...', fg='yellow', nl=False)

        response = kinesis_client.split_shard(
            StreamName=stream_name,
            ShardToSplit=shard_id,
            NewStartingHashKey=str(new_hash_key)
        )

        loop_till_active(kinesis_client, stream_name)

        click.secho(f' done.', fg='blue')


def get_open_shards(kinesis_client, stream_name):
    shards = kinesis_client.list_shards(StreamName=stream_name)
    open_shards = []
    for shard in shards['Shards']:
        is_shard_closed = 'EndingSequenceNumber' in shard['SequenceNumberRange']
        if not is_shard_closed:
            open_shards.append(shard)
    return open_shards


def scale_down(stream_name):
    print(f'Using boto3 version {boto3.__version__}')
    kinesis_client = boto3.client('kinesis')

    open_shards = get_open_shards(kinesis_client, stream_name)

    open_shards = sorted(open_shards, key=lambda x: x['HashKeyRange']['StartingHashKey'])

    open_shard_count = len(open_shards)
    click.secho(f'You have {open_shard_count} open shards. '
                f'You will have {int(open_shard_count / 2)} open shards after this operation.', fg='red')
    click.confirm('Do you want to continue?', abort=True)

    for idx in range(len(open_shards)):
        if idx % 2 != 0:
            print('idx', idx)

        # starting_hash_key = int(shard['HashKeyRange']['StartingHashKey'])
        # ending_hash_key = int(shard['HashKeyRange']['EndingHashKey'])
        # new_hash_key = int((starting_hash_key + ending_hash_key) / 2)
        # shard_id = shard["ShardId"]
        # click.secho(f'Splitting {shard_id} ...', fg='yellow', nl=False)

        # response = kinesis_client.split_shard(
        #     StreamName=stream_name,
        #     ShardToSplit=shard_id,
        #     NewStartingHashKey=new_hash_key
        # )

        loop_till_active(kinesis_client, stream_name)

        click.secho(f' done.', fg='blue')


def loop_till_active(kinesis_client, stream_name):
    click.secho(f'.', fg='yellow', nl=False)
    describe_stream_summary_response = kinesis_client.describe_stream_summary(StreamName=stream_name)
    describe_stream_summary = describe_stream_summary_response['StreamDescriptionSummary']
    stream_status = describe_stream_summary['StreamStatus']
    if stream_status != 'ACTIVE':
        time.sleep(1)
        loop_till_active(kinesis_client, stream_name)
