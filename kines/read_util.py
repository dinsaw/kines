import boto3
from kines import constants
import click
from terminaltables import SingleTable
import base64
from textwrap import wrap


def walk(stream_name, shard_id, sequence_number=None, get_records_limit=5, timestamp=None):
    kinesis_client = boto3.client('kinesis')

    if not shard_id.startswith(constants.SHARD_ID_PREFIX):
        shard_id = constants.SHARD_ID_PREFIX + shard_id

    shard_iterator_type = 'AT_SEQUENCE_NUMBER' if sequence_number else 'TRIM_HORIZON'

    get_shard_iterator_args = {
        'StreamName': stream_name,
        'ShardId': shard_id,
        'ShardIteratorType': shard_iterator_type,
    }

    if sequence_number:
        get_shard_iterator_args['StartingSequenceNumber'] = sequence_number

    click.echo(f"Creating shard iterator with arguments = {get_shard_iterator_args}")
    response = kinesis_client.get_shard_iterator(**get_shard_iterator_args)

    shard_iterator = response['ShardIterator']
    while True:

        records_response = kinesis_client.get_records(
            ShardIterator=shard_iterator,
            Limit=get_records_limit
        )

        for record in records_response['Records']:
            parsed_data = base64.b64decode(record['Data']).decode('utf-8')
            table_data = [
                ['SequenceNumber', record['SequenceNumber']],
                ['ApproximateArrivalTimestamp', record['ApproximateArrivalTimestamp']],
                ['PartitionKey', record['PartitionKey']],
                ['EncryptionType', record.get('EncryptionType')],
                ['Decoded Data', parsed_data]
            ]

            table = SingleTable(table_data)
            max_width = table.column_max_width(1)
            wrapped_string = '\n'.join(wrap(parsed_data, max_width))
            table.table_data[4][1] = wrapped_string
            print(table.table)

        if not records_response['Records']:
            print("No records found for this api call 😔")

        click.confirm('Fetch more records?', abort=True, default=True)
        shard_iterator = records_response['NextShardIterator']
