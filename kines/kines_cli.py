import click
from kines import partition_key_util, metric_util, stream_util, shard_util, read_util


@click.group()
def kines():
    """Friendly Command Line Interface for Amazon Kinesis Data Streams"""


@kines.command()
def ls():
    """List streams"""
    stream_util.list_streams()


@click.argument('stream-name', required=True)
@click.option('-o', '--only-open-shards', is_flag=True, help='Only show results for Open Shards')
@click.option('-d', '--detailed', is_flag=True, help='Show extra details eg. Starting-Ending hash key')
@kines.command()
def lss(stream_name: str, only_open_shards: bool, detailed: bool):
    """List stream shards"""
    shard_util.display_shard_table(stream_name, only_open_shards, detailed)


@click.argument('stream-name', required=True)
@click.option('-p', '--partition-key', required=True, multiple=True, help='Partition Key')
@click.option('-o', '--open-shards', is_flag=True, help='Only show results for Open Shards')
@kines.command()
def find(stream_name: str, partition_key: str, open_shards: bool):
    """Find shard for Partition Keys"""
    partition_key_util.find_shard(stream_name, partition_key, open_shards)


@click.argument('stream-name', required=True)
@click.option('-p', '--period', default=15, type=int, help='Metric Period in Minutes')
@click.option('-h', '--hours', default=12, type=int, help='Report for how many hours')
@kines.command()
def report(stream_name: str, period: int, hours: int):
    """Get report for a Kinesis stream"""
    metric_util.display_report(stream_name, period * 60, hours)


@click.option('-n', '--number-of-records', default=5, type=int, help='Max Number of records to be retrieved per call')
@click.option('-s', '--sequence-number', default=None, type=str, help='Sequence Number')
@click.argument('shard-id', required=True)
@click.argument('stream-name', required=True)
@kines.command()
def walk(stream_name: str, shard_id: str, sequence_number: str, number_of_records: int):
    """Walk through Kinesis Records"""
    read_util.walk(stream_name, shard_id, sequence_number, number_of_records)


@kines.command()
def legends():
    """View all legends / short forms used"""
    metric_util.print_legends('\n')
    stream_util.print_legends('\n')
    shard_util.print_legends('\n')


# @click.option('-s', '--stream-name', required=True, help='Kinesis Stream Name')
# @kines.command()
# def scaleup(stream_name: str):
#     """Splits all shards in the stream in equal parts."""
#     scaling_util.scale_up(stream_name)
#
#
# @click.option('-s', '--stream-name', required=True, help='Kinesis Stream Name')
# @kines.command()
# def scaledown(stream_name: str):
#     """Merge all shards in stream. Makes steam shards size of it's current size."""
#     scaling_util.scale_down(stream_name)


if __name__ == '__main__':
    kines(prog_name='kines')
