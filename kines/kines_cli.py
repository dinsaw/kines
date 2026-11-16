import click
from botocore.exceptions import (
    BotoCoreError,
    ClientError,
    CredentialRetrievalError,
    EndpointConnectionError,
    NoCredentialsError,
    NoRegionError,
    PartialCredentialsError,
)
from kines import (
    partition_key_util,
    metrics,
    stream_util,
    shard_util,
    read_util,
    put_util,
)


def format_aws_error(error: Exception) -> str:
    if isinstance(error, NoRegionError):
        return (
            "AWS region not configured. Please set the AWS_DEFAULT_REGION environment "
            "variable or configure a default region in ~/.aws/config."
        )
    if isinstance(error, NoCredentialsError):
        return (
            "AWS credentials not found. Please configure ~/.aws/credentials or "
            "set AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY environment variables."
        )
    if isinstance(error, PartialCredentialsError):
        return f"Partial AWS credentials found: {error}"
    if isinstance(error, CredentialRetrievalError):
        return f"Failed to retrieve AWS credentials: {error}"
    if isinstance(error, EndpointConnectionError):
        return f"Could not connect to AWS endpoint: {error}"
    if isinstance(error, ClientError):
        error_code = error.response.get("Error", {}).get("Code", "ClientError")
        error_message = error.response.get("Error", {}).get("Message", str(error))
        if error_code == "ResourceNotFoundException":
            return f"Resource not found: {error_message}"
        if error_code == "AccessDeniedException":
            return f"Access denied: {error_message}"
        if error_code == "ResourceInUseException":
            return f"Resource in use: {error_message}"
        if error_code == "InvalidArgumentException":
            return f"Invalid argument: {error_message}"
        if error_code == "ProvisionedThroughputExceededException":
            return f"Provisioned throughput exceeded: {error_message}"
        return f"AWS Error ({error_code}): {error_message}"
    if isinstance(error, BotoCoreError):
        return f"AWS Error: {error}"
    return str(error)


class KinesGroup(click.Group):
    def invoke(self, ctx):
        try:
            return super().invoke(ctx)
        except (BotoCoreError, ClientError) as e:
            raise click.ClickException(format_aws_error(e))


@click.group(cls=KinesGroup)
def kines():
    """Friendly Command Line Interface for Amazon Kinesis Data Streams"""


@kines.command()
def ls():
    """List streams"""
    stream_util.list_streams()


@click.argument("stream-name", required=True)
@click.option(
    "-o", "--only-open-shards", is_flag=True, help="Only show results for Open Shards"
)
@click.option(
    "-d",
    "--detailed",
    is_flag=True,
    help="Show extra details eg. Starting-Ending hash key",
)
@kines.command()
def lss(stream_name: str, only_open_shards: bool, detailed: bool):
    """List stream shards"""
    shard_util.display_shard_table(stream_name, only_open_shards, detailed)


@click.argument("stream-name", required=True)
@click.option(
    "-p", "--partition-key", required=True, multiple=True, help="Partition Key"
)
@click.option(
    "-o", "--open-shards", is_flag=True, help="Only show results for Open Shards"
)
@kines.command()
def find(stream_name: str, partition_key: str, open_shards: bool):
    """Find shard for Partition Keys"""
    partition_key_util.find_shard(stream_name, partition_key, open_shards)


@click.argument("stream-name", required=True)
@click.option("-p", "--period", default=15, type=int, help="Metric Period in Minutes")
@click.option("-h", "--hours", default=12, type=int, help="Report for how many hours")
@kines.command()
def report(stream_name: str, period: int, hours: int):
    """Get report for a Kinesis stream"""
    metrics.display_report(stream_name, period * 60, hours)


@click.option(
    "-n",
    "--number-of-records",
    default=5,
    type=int,
    help="Max Number of records to be retrieved per call",
)
@click.option(
    "-s",
    "--sequence-number",
    default=None,
    type=str,
    help="Start from this Sequence Number. Creates AT_SEQUENCE_NUMBER shard iterator.",
)
@click.option(
    "-f",
    "--follow",
    default=False,
    is_flag=True,
    help="Poll records repeatedly after 2 seconds",
)
@click.option(
    "-l",
    "--latest",
    default=False,
    is_flag=True,
    help="Start from latest records. Creates LATEST shard iterator",
)
@click.option(
    "-t",
    "--timestamp",
    help="Start from this timestamp. Creates AT_TIMESTAMP shard iterator. You can specify timestamp as '2016-04-04T19:58:46.480-00:00' or with short hand as '1h10m' i.e. 1 hour 10 minutes ago, '10m' i.e. 10 minutes ago, '1h' i.e. 1 hour ago.",
)
@click.option(
    "-r",
    "--raw",
    default=False,
    is_flag=True,
    help="Print raw decoded record data without table formatting",
)
@click.argument("shard-id", required=True)
@click.argument("stream-name", required=True)
@kines.command()
def walk(
    stream_name: str,
    shard_id: str,
    sequence_number: str,
    number_of_records: int,
    follow: bool,
    latest: bool,
    timestamp: str,
    raw: bool,
):
    """Walk through Kinesis Records. By default creates TRIM_HORIZON iterator."""
    read_util.walk(
        stream_name,
        shard_id,
        sequence_number,
        number_of_records,
        follow,
        latest,
        timestamp,
        raw,
    )


@click.argument("stream-name", required=True)
@click.option(
    "-p",
    "--partition-key",
    multiple=True,
    help="Partition key. Can be specified multiple times for multiple records.",
)
@click.option(
    "-d",
    "--data",
    multiple=True,
    help="Record data. Can be specified multiple times for multiple records.",
)
@click.option(
    "-f",
    "--file",
    type=click.Path(exists=True),
    help="Path to file containing record data or a JSON array of records.",
)
@click.option(
    "-a",
    "--aggregate",
    is_flag=True,
    default=False,
    help="Aggregate multiple records into a single KPL-compatible aggregated record.",
)
@click.option(
    "-k",
    "--explicit-hash-key",
    default=None,
    help="Explicit hash key to override partition key hash.",
)
@kines.command()
def put(
    stream_name: str,
    partition_key: tuple,
    data: tuple,
    file: str,
    aggregate: bool,
    explicit_hash_key: str,
):
    """Put single or aggregated records into a Kinesis stream"""
    put_util.put(
        stream_name,
        partition_keys=partition_key,
        data_list=data,
        file_path=file,
        aggregate=aggregate,
        explicit_hash_key=explicit_hash_key,
    )


@kines.command()
def legends():
    """View all legends / short forms used"""
    for m in [metrics, stream_util, shard_util]:
        m.print_legends("\n")


if __name__ == "__main__":
    kines(prog_name="kines")
