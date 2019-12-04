import boto3
from click.testing import CliRunner

from kines import kines_cli
from tests.aws_client_mocks import MockKinesisClient, MockCloudWatchClient


def test_kines_help():
    runner = CliRunner()
    result = runner.invoke(kines_cli.kines)
    assert result.exit_code == 0


def test_kines_legends():
    runner = CliRunner()
    result = runner.invoke(kines_cli.kines, ["legends"])
    assert result.exit_code == 0
    assert (
        """Time = Converted Local Time
IR = IncomingRecords
IS = IncomingSize
IR/Sec = IncomingRecords Per Sec
GR = GetRecords.Records
GR/Sec = GetRecords.Records/Sec
GR/IR = GetRecords/IncomingRecords
WPTE = WriteProvisionedThroughputExceeded
RPTE = ReadProvisionedThroughputExceeded
MAX(IAGM) = MAX(IteratorAgeMilliSeconds)

Status - Stream = Stream with Status
# = OpenShardCount
👥 = EnhancedConsumerCount
🕑 = RetentionPeriod
🔑 = EncryptionType

⛏  = CREATING Stream Status
❌  = DELETING Stream Status
⛹  = ACTIVE Stream Status
🛠️  = UPDATING Stream Status

📕 = Closed Shard
📖 = Open Shard
"""
        == result.output
    )


def boto3_init():
    print("mock boto3 init")


def mock_get_cloudwatch_client(*args, **kwargs):
    return MockCloudWatchClient()


def mock_get_kinesis_client(*args, **kwargs):
    return MockKinesisClient()


def test_kines_ls(monkeypatch):
    runner = CliRunner()

    monkeypatch.setattr(boto3, "client", mock_get_kinesis_client)

    result = runner.invoke(kines_cli.kines, ["ls"])
    assert result.exit_code == 0

    print(result.output)
    assert (
        "Found 2 streams.\n\x1b(0lqqqqqqqqqqqqqqqqqqwqqqwqqqqwqqqqwqqqqqqk\x1b(B\n\x1b(0x\x1b(B Status - Stream  "
        "\x1b(0x\x1b(B # \x1b(0x\x1b(B 👥 \x1b(0x\x1b(B 🕑 \x1b(0x\x1b(B 🔑   \x1b(0x\x1b(B\n\x1b("
        "0tqqqqqqqqqqqqqqqqqqnqqqnqqqqnqqqqnqqqqqqu\x1b(B\n\x1b(0x\x1b(B ⛏  test-stream-1 \x1b(0x\x1b(B 3 \x1b("
        "0x\x1b(B 0  \x1b(0x\x1b(B 24 \x1b(0x\x1b(B NONE \x1b(0x\x1b(B\n\x1b(0x\x1b(B ⛹  test-stream-2 \x1b("
        "0x\x1b(B 3 \x1b(0x\x1b(B 0  \x1b(0x\x1b(B 24 \x1b(0x\x1b(B NONE \x1b(0x\x1b(B\n\x1b("
        "0mqqqqqqqqqqqqqqqqqqvqqqvqqqqvqqqqvqqqqqqj\x1b(B\n" == result.output
    )
    assert result.output.startswith("Found 2 streams.")


def test_kines_lss(monkeypatch):
    monkeypatch.setattr(boto3, "client", mock_get_kinesis_client)

    runner = CliRunner()
    result = runner.invoke(kines_cli.kines, ["lss", "test-stream-1"])
    assert result.exit_code == 0

    print(result.output)
    assert (
        "\x1b(0lqqqqqqqqqqqqqqqqqwqqqqqqqqqqqqqqqwqqqqqqqqqqqqqqqqqqqqqqqwqqqqqqqqqqqqqqqqk\x1b(B\n\x1b(0x\x1b(B "
        "ShardId         \x1b(0x\x1b(B ParentShardId \x1b(0x\x1b(B AdjacentParentShardId \x1b(0x\x1b(B % "
        "HashKeyRange \x1b(0x\x1b(B\n\x1b("
        "0tqqqqqqqqqqqqqqqqqnqqqqqqqqqqqqqqqnqqqqqqqqqqqqqqqqqqqqqqqnqqqqqqqqqqqqqqqqu\x1b(B\n\x1b(0x\x1b(B 📖 "
        "000000000102 \x1b(0x\x1b(B 000000000100  \x1b(0x\x1b(B 000000000101          \x1b(0x\x1b(B 100.0%         "
        "\x1b(0x\x1b(B\n\x1b(0mqqqqqqqqqqqqqqqqqvqqqqqqqqqqqqqqqvqqqqqqqqqqqqqqqqqqqqqqqvqqqqqqqqqqqqqqqqj\x1b("
        "B\n" == result.output
    )


def test_find(monkeypatch):
    monkeypatch.setattr(boto3, "client", mock_get_kinesis_client)

    runner = CliRunner()
    result = runner.invoke(
        kines_cli.kines,
        ["find", "test-stream-partition-key-1", "-p", "123", "-p", "abc"],
    )
    print(result.output)
    expected_output = "\x1b(0lqqqqqqqqqqqqqqwqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqwqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqwqqqqqqqqqqqqqqqqqk\x1b(B\n\x1b(0x\x1b(B PartitionKey \x1b(0x\x1b(B MD5PartitionKey                  \x1b(0x\x1b(B HashKey                                 \x1b(0x\x1b(B ShardId         \x1b(0x\x1b(B\n\x1b(0tqqqqqqqqqqqqqqnqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqnqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqnqqqqqqqqqqqqqqqqqu\x1b(B\n\x1b(0x\x1b(B 123          \x1b(0x\x1b(B 202cb962ac59075b964b07152d234b70 \x1b(0x\x1b(B 42767516990368493138776584305024125808  \x1b(0x\x1b(B 📖 000000000008 \x1b(0x\x1b(B\n\x1b(0x\x1b(B abc          \x1b(0x\x1b(B 900150983cd24fb0d6963f7d28e17f72 \x1b(0x\x1b(B 191415658344158766168031473277922803570 \x1b(0x\x1b(B 📖 000000000011 \x1b(0x\x1b(B\n\x1b(0mqqqqqqqqqqqqqqvqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqvqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqvqqqqqqqqqqqqqqqqqj\x1b(B\n"
    assert expected_output == result.output
    assert result.exit_code == 0


def test_report(monkeypatch):
    monkeypatch.setattr(boto3, "client", mock_get_cloudwatch_client)

    runner = CliRunner()
    result = runner.invoke(
        kines_cli.kines, ["report", "test-stream-report", "-h", "3", "-p", "30"]
    )
    print("report output", repr(result.output))
    expected_output = "\x1b(0lqqqqqqqqqqqqqqqqqqwqqqqqqqqqqwqqqqqqqqqqqwqqqqqqqqwqqqqqqqqqqqwqqqqqqqqqwqqqqqqqwqqqqqqwqqqqqqqqwqqqqqqqqqqqqk\x1b(B\n\x1b(0x\x1b(B Time             \x1b(0x\x1b(B IR       \x1b(0x\x1b(B IS        \x1b(0x\x1b(B IR/Sec \x1b(0x\x1b(B GR        \x1b(0x\x1b(B GR/Sec  \x1b(0x\x1b(B GR/IR \x1b(0x\x1b(B WPTE \x1b(0x\x1b(B RPTE   \x1b(0x\x1b(B MAX(IAGM)  \x1b(0x\x1b(B\n\x1b(0tqqqqqqqqqqqqqqqqqqnqqqqqqqqqqnqqqqqqqqqqqnqqqqqqqqnqqqqqqqqqqqnqqqqqqqqqnqqqqqqqnqqqqqqnqqqqqqqqnqqqqqqqqqqqqu\x1b(B\n\x1b(0x\x1b(B 2019-10-11 10:30 \x1b(0x\x1b(B 297200.0 \x1b(0x\x1b(B 926.48 MB \x1b(0x\x1b(B 165.11 \x1b(0x\x1b(B 2079782.0 \x1b(0x\x1b(B 1155.43 \x1b(0x\x1b(B 7.00  \x1b(0x\x1b(B 0.0  \x1b(0x\x1b(B 0.0    \x1b(0x\x1b(B 0.0        \x1b(0x\x1b(B\n\x1b(0x\x1b(B 2019-10-11 11:00 \x1b(0x\x1b(B 265471.0 \x1b(0x\x1b(B 837.15 MB \x1b(0x\x1b(B 147.48 \x1b(0x\x1b(B 1858115.0 \x1b(0x\x1b(B 1032.29 \x1b(0x\x1b(B 7.00  \x1b(0x\x1b(B 0.0  \x1b(0x\x1b(B 1.0 🔥 \x1b(0x\x1b(B 0.0        \x1b(0x\x1b(B\n\x1b(0x\x1b(B 2019-10-11 11:30 \x1b(0x\x1b(B 255861.0 \x1b(0x\x1b(B 807.8 MB  \x1b(0x\x1b(B 142.15 \x1b(0x\x1b(B 1791687.0 \x1b(0x\x1b(B 995.38  \x1b(0x\x1b(B 7.00  \x1b(0x\x1b(B 0.0  \x1b(0x\x1b(B 0.0    \x1b(0x\x1b(B 0.0        \x1b(0x\x1b(B\n\x1b(0x\x1b(B 2019-10-11 12:00 \x1b(0x\x1b(B 250698.0 \x1b(0x\x1b(B 792.29 MB \x1b(0x\x1b(B 139.28 \x1b(0x\x1b(B 1754570.0 \x1b(0x\x1b(B 974.76  \x1b(0x\x1b(B 7.00  \x1b(0x\x1b(B 0.0  \x1b(0x\x1b(B 3.0 🔥 \x1b(0x\x1b(B 0.0        \x1b(0x\x1b(B\n\x1b(0x\x1b(B 2019-10-11 12:30 \x1b(0x\x1b(B 241889.0 \x1b(0x\x1b(B 761.83 MB \x1b(0x\x1b(B 134.38 \x1b(0x\x1b(B 1693413.0 \x1b(0x\x1b(B 940.78  \x1b(0x\x1b(B 7.00  \x1b(0x\x1b(B 0.0  \x1b(0x\x1b(B 1.0 🔥 \x1b(0x\x1b(B 0.0        \x1b(0x\x1b(B\n\x1b(0x\x1b(B 2019-10-11 13:00 \x1b(0x\x1b(B 305792.0 \x1b(0x\x1b(B 953.44 MB \x1b(0x\x1b(B 169.88 \x1b(0x\x1b(B 2140395.0 \x1b(0x\x1b(B 1189.11 \x1b(0x\x1b(B 7.00  \x1b(0x\x1b(B 0.0  \x1b(0x\x1b(B 3.0 🔥 \x1b(0x\x1b(B 36000.0 🔥 \x1b(0x\x1b(B\n\x1b(0x\x1b(B 2019-10-11 13:30 \x1b(0x\x1b(B 189147.0 \x1b(0x\x1b(B 594.26 MB \x1b(0x\x1b(B 105.08 \x1b(0x\x1b(B 1323267.0 \x1b(0x\x1b(B 735.15  \x1b(0x\x1b(B 7.00  \x1b(0x\x1b(B 0.0  \x1b(0x\x1b(B 5.0 🔥 \x1b(0x\x1b(B 0.0        \x1b(0x\x1b(B\n\x1b(0mqqqqqqqqqqqqqqqqqqvqqqqqqqqqqvqqqqqqqqqqqvqqqqqqqqvqqqqqqqqqqqvqqqqqqqqqvqqqqqqqvqqqqqqvqqqqqqqqvqqqqqqqqqqqqj\x1b(B\n"
    assert expected_output == result.output
    assert result.exit_code == 0


def test_walk(monkeypatch):
    monkeypatch.setattr(boto3, "client", mock_get_kinesis_client)
    runner = CliRunner()
    result = runner.invoke(
        kines_cli.kines, ["walk", "test-stream-walk", "000000000102"], input="n\n"
    )
    print("walk output", result.output)
    expected_output = 'Creating shard iterator with arguments = {\'StreamName\': \'test-stream-walk\', \'ShardId\': \'shardId-000000000102\', \'ShardIteratorType\': \'TRIM_HORIZON\'}\n\x1b(0lqqqqqqqqqqqqqqqqqqqqqqqqqqqqqwqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqk\x1b(B\n\x1b(0x\x1b(B SequenceNumber              \x1b(0x\x1b(B 49600282682944895786267660693075522538255370376250918498 \x1b(0x\x1b(B\n\x1b(0tqqqqqqqqqqqqqqqqqqqqqqqqqqqqqnqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqu\x1b(B\n\x1b(0x\x1b(B ApproximateArrivalTimestamp \x1b(0x\x1b(B 2019-10-10 16:22:41.761000+05:30                         \x1b(0x\x1b(B\n\x1b(0x\x1b(B PartitionKey                \x1b(0x\x1b(B 4439109                                                  \x1b(0x\x1b(B\n\x1b(0x\x1b(B EncryptionType              \x1b(0x\x1b(B None                                                     \x1b(0x\x1b(B\n\x1b(0x\x1b(B Decoded Data                \x1b(0x\x1b(B {"event": "1"}                                           \x1b(0x\x1b(B\n\x1b(0mqqqqqqqqqqqqqqqqqqqqqqqqqqqqqvqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqj\x1b(B\n\x1b(0lqqqqqqqqqqqqqqqqqqqqqqqqqqqqqwqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqk\x1b(B\n\x1b(0x\x1b(B SequenceNumber              \x1b(0x\x1b(B 49600282682944895786267660697997059549906526021357667938 \x1b(0x\x1b(B\n\x1b(0tqqqqqqqqqqqqqqqqqqqqqqqqqqqqqnqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqu\x1b(B\n\x1b(0x\x1b(B ApproximateArrivalTimestamp \x1b(0x\x1b(B 2019-10-10 16:22:45.180000+05:30                         \x1b(0x\x1b(B\n\x1b(0x\x1b(B PartitionKey                \x1b(0x\x1b(B 4439109                                                  \x1b(0x\x1b(B\n\x1b(0x\x1b(B EncryptionType              \x1b(0x\x1b(B None                                                     \x1b(0x\x1b(B\n\x1b(0x\x1b(B Decoded Data                \x1b(0x\x1b(B {"event": "2"}                                           \x1b(0x\x1b(B\n\x1b(0mqqqqqqqqqqqqqqqqqqqqqqqqqqqqqvqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqj\x1b(B\n\x1b(0lqqqqqqqqqqqqqqqqqqqqqqqqqqqqqwqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqk\x1b(B\n\x1b(0x\x1b(B SequenceNumber              \x1b(0x\x1b(B 49600282682944895786267660702176316108314299215755871842 \x1b(0x\x1b(B\n\x1b(0tqqqqqqqqqqqqqqqqqqqqqqqqqqqqqnqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqu\x1b(B\n\x1b(0x\x1b(B ApproximateArrivalTimestamp \x1b(0x\x1b(B 2019-10-10 16:22:48.083000+05:30                         \x1b(0x\x1b(B\n\x1b(0x\x1b(B PartitionKey                \x1b(0x\x1b(B 4439109                                                  \x1b(0x\x1b(B\n\x1b(0x\x1b(B EncryptionType              \x1b(0x\x1b(B None                                                     \x1b(0x\x1b(B\n\x1b(0x\x1b(B Decoded Data                \x1b(0x\x1b(B {"event": "3"}                                           \x1b(0x\x1b(B\n\x1b(0mqqqqqqqqqqqqqqqqqqqqqqqqqqqqqvqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqj\x1b(B\n\x1b(0lqqqqqqqqqqqqqqqqqqqqqqqqqqqqqwqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqk\x1b(B\n\x1b(0x\x1b(B SequenceNumber              \x1b(0x\x1b(B 49600282682944895786267660702634498993948243810408466018 \x1b(0x\x1b(B\n\x1b(0tqqqqqqqqqqqqqqqqqqqqqqqqqqqqqnqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqu\x1b(B\n\x1b(0x\x1b(B ApproximateArrivalTimestamp \x1b(0x\x1b(B 2019-10-10 16:22:48.407000+05:30                         \x1b(0x\x1b(B\n\x1b(0x\x1b(B PartitionKey                \x1b(0x\x1b(B 4439109                                                  \x1b(0x\x1b(B\n\x1b(0x\x1b(B EncryptionType              \x1b(0x\x1b(B None                                                     \x1b(0x\x1b(B\n\x1b(0x\x1b(B Decoded Data                \x1b(0x\x1b(B {"event": "4"}                                           \x1b(0x\x1b(B\n\x1b(0mqqqqqqqqqqqqqqqqqqqqqqqqqqqqqvqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqj\x1b(B\n\x1b(0lqqqqqqqqqqqqqqqqqqqqqqqqqqqqqwqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqk\x1b(B\n\x1b(0x\x1b(B SequenceNumber              \x1b(0x\x1b(B 49600282682944895786267660705672529578639807063884039778 \x1b(0x\x1b(B\n\x1b(0tqqqqqqqqqqqqqqqqqqqqqqqqqqqqqnqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqu\x1b(B\n\x1b(0x\x1b(B ApproximateArrivalTimestamp \x1b(0x\x1b(B 2019-10-10 16:22:50.666000+05:30                         \x1b(0x\x1b(B\n\x1b(0x\x1b(B PartitionKey                \x1b(0x\x1b(B 4439109                                                  \x1b(0x\x1b(B\n\x1b(0x\x1b(B EncryptionType              \x1b(0x\x1b(B None                                                     \x1b(0x\x1b(B\n\x1b(0x\x1b(B Decoded Data                \x1b(0x\x1b(B {"event": "5"}                                           \x1b(0x\x1b(B\n\x1b(0mqqqqqqqqqqqqqqqqqqqqqqqqqqqqqvqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqj\x1b(B\nFetch more records? [Y/n]: n\n'
    assert expected_output == result.output
    assert 0 == result.exit_code
