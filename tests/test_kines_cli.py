import datetime

import boto3
from click.testing import CliRunner
from dateutil.tz import tzlocal

from kines import kines_cli
import tests.test_boto3_client_responses

TEST_PARTITION_KEY_STREAM_NAME = 'test-stream-partition-key-1'


def test_kines_help():
    runner = CliRunner()
    result = runner.invoke(kines_cli.kines)
    assert result.exit_code == 0


def test_kines_legends():
    runner = CliRunner()
    result = runner.invoke(kines_cli.kines, ['legends'])
    assert result.exit_code == 0
    assert """Time = Converted Local Time
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
""" == result.output


def boto3_init():
    print("mock boto3 init")


class MockCloudWatchClient:
    @staticmethod
    def get_metric_data(*args, **kwargs):
        return tests.test_boto3_client_responses.CLOUDWATCH_RESPONSE_H3_P3


def mock_get_cloudwatch_client(*args, **kwargs):
    return MockCloudWatchClient()


class MockKinesisClient:
    @staticmethod
    def list_streams(*args, **kwargs):
        return {'StreamNames': ['test-stream-1', 'test-stream-2'], 'HasMoreStreams': False, " \
               "'ResponseMetadata': {'RequestId': 'fc11d7e4-6b7d-f442-aa43-3049e19b80e5', " \
               "'HTTPStatusCode': 200, 'HTTPHeaders': {'x-amzn-requestid': " \
               "'fc5bd7e4-6b7d-1111-aa43-3049e19b80e5', 'x-amz-id-2': " \
               "'yhU937PwchDLgTnJCxz+CX0z1u+hbl" \
               "+zDgDIf5yLf0SdfoETI8Ovai8Nj1ctKTCrPrvmQrRvOOy7F9eKOlVQyfmf1xES560M', 'date': 'Thu, " \
               "10 Oct 2019 08:01:49 GMT', 'content-type': 'application/x-amz-json-1.1', " \
               "'content-length': '453'}, 'RetryAttempts': 0}}

    @staticmethod
    def describe_stream_summary(*args, **kwargs):
        status = 'ACTIVE'
        if kwargs['StreamName'] == 'test-stream-1':
            status = 'CREATING'
        return {'StreamDescriptionSummary':
                    {'StreamName': kwargs['StreamName'],
                     'StreamARN': 'arn:aws:kinesis:ap-south-1:622212315795:stream/test-stream-1',
                     'StreamStatus': status, 'RetentionPeriodHours': 24,
                     'StreamCreationTimestamp': datetime.datetime(2017, 10, 12, 15, 1, 10, tzinfo=tzlocal()),
                     'EnhancedMonitoring': [{'ShardLevelMetrics': []}],
                     'EncryptionType': 'NONE', 'OpenShardCount': 3, 'ConsumerCount': 0},
                'ResponseMetadata': {'RequestId': 'f65c5191-b0a2-89db-a044-bc766e1035f2', 'HTTPStatusCode': 200,
                                     'HTTPHeaders': {'x-amzn-requestid': 'f65c5111-b0a2-89db-a044-bc766e1035f2',
                                                     'x-amz-id-2': 'iPhP5twFKYQUl9EVR+o9ofwuWS8IR8Gei8eQQcz'
                                                                   '+I11111pCfoSGDecx4VBgggDbTt7VxsGYUyHlePx'
                                                                   'd1ZYedxqrQBrq2Wpj',
                                                     'date': 'Thu, 10 Oct 2019 08:28:23 GMT',
                                                     'content-type': 'application/x-amz-json-1.1',
                                                     'content-length': '338'}, 'RetryAttempts': 0}}

    @staticmethod
    def list_shards(*args, **kwargs):
        if kwargs['StreamName'] == TEST_PARTITION_KEY_STREAM_NAME:
            return tests.test_boto3_client_responses.LIST_SHARDS_8_RESPONSE
        return {'Shards': [{'ShardId': 'shardId-000000000102', 'ParentShardId': 'shardId-000000000100',
                            'AdjacentParentShardId': 'shardId-000000000101',
                            'HashKeyRange': {'StartingHashKey': '0',
                                             'EndingHashKey': '340282366920938463463374607431768211455'},
                            'SequenceNumberRange': {
                                'StartingSequenceNumber': '49599466347575149145100714296670755717216365327595603554'}}],
                'ResponseMetadata':
                    {'RequestId': 'dd758b71-d791-b743-8b6c-96309a98f4c5', 'HTTPStatusCode': 200,
                     'HTTPHeaders': {'x-amzn-requestid': 'dd75ab71-d791-b743-8b6c-96309a98f4c5',
                                     'x-amz-id-2': 'Zh+M47thCzh5ATqzrmWjcZior+cBvowfewFEZNN7zYmeQ2lJ8U1fyVGao'
                                                   '+TayscjTKhRDTbMNzCOj11quBawNGQaHl7x/IiTu',
                                     'date': 'Thu, 10 Oct 2019 11:50:25 GMT',
                                     'content-type': 'application/x-amz-json-1.1',
                                     'content-length': '338'},
                     'RetryAttempts': 0}}


def mock_get_kinesis_client(*args, **kwargs):
    return MockKinesisClient()


def test_kines_ls(monkeypatch):
    runner = CliRunner()

    monkeypatch.setattr(boto3, 'client', mock_get_kinesis_client)

    result = runner.invoke(kines_cli.kines, ['ls'])
    assert result.exit_code == 0

    print(result.output)
    assert 'Found 2 streams.\n\x1b(0lqqqqqqqqqqqqqqqqqqwqqqwqqqqwqqqqwqqqqqqk\x1b(B\n\x1b(0x\x1b(B Status - Stream  ' \
           '\x1b(0x\x1b(B # \x1b(0x\x1b(B 👥 \x1b(0x\x1b(B 🕑 \x1b(0x\x1b(B 🔑   \x1b(0x\x1b(B\n\x1b(' \
           '0tqqqqqqqqqqqqqqqqqqnqqqnqqqqnqqqqnqqqqqqu\x1b(B\n\x1b(0x\x1b(B ⛏  test-stream-1 \x1b(0x\x1b(B 3 \x1b(' \
           '0x\x1b(B 0  \x1b(0x\x1b(B 24 \x1b(0x\x1b(B NONE \x1b(0x\x1b(B\n\x1b(0x\x1b(B ⛹  test-stream-2 \x1b(' \
           '0x\x1b(B 3 \x1b(0x\x1b(B 0  \x1b(0x\x1b(B 24 \x1b(0x\x1b(B NONE \x1b(0x\x1b(B\n\x1b(' \
           '0mqqqqqqqqqqqqqqqqqqvqqqvqqqqvqqqqvqqqqqqj\x1b(B\n' == result.output
    assert result.output.startswith('Found 2 streams.')


def test_kines_lss(monkeypatch):
    monkeypatch.setattr(boto3, 'client', mock_get_kinesis_client)

    runner = CliRunner()
    result = runner.invoke(kines_cli.kines, ['lss', 'test-stream-1'])
    assert result.exit_code == 0

    print(result.output)
    assert '\x1b(0lqqqqqqqqqqqqqqqqqwqqqqqqqqqqqqqqqwqqqqqqqqqqqqqqqqqqqqqqqwqqqqqqqqqqqqqqqqk\x1b(B\n\x1b(0x\x1b(B ' \
           'ShardId         \x1b(0x\x1b(B ParentShardId \x1b(0x\x1b(B AdjacentParentShardId \x1b(0x\x1b(B % ' \
           'HashKeyRange \x1b(0x\x1b(B\n\x1b(' \
           '0tqqqqqqqqqqqqqqqqqnqqqqqqqqqqqqqqqnqqqqqqqqqqqqqqqqqqqqqqqnqqqqqqqqqqqqqqqqu\x1b(B\n\x1b(0x\x1b(B 📖 ' \
           '000000000102 \x1b(0x\x1b(B 000000000100  \x1b(0x\x1b(B 000000000101          \x1b(0x\x1b(B 100.0%         ' \
           '\x1b(0x\x1b(B\n\x1b(0mqqqqqqqqqqqqqqqqqvqqqqqqqqqqqqqqqvqqqqqqqqqqqqqqqqqqqqqqqvqqqqqqqqqqqqqqqqj\x1b(' \
           'B\n' == result.output


def test_find(monkeypatch):
    monkeypatch.setattr(boto3, 'client', mock_get_kinesis_client)

    runner = CliRunner()
    result = runner.invoke(kines_cli.kines, ['find', 'test-stream-partition-key-1', '-p', '123', '-p', 'abc'])
    print(result.output)
    expected_output = "\x1b(0lqqqqqqqqqqqqqqwqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqwqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqwqqqqqqqqqqqqqqqqqk\x1b(B\n\x1b(0x\x1b(B PartitionKey \x1b(0x\x1b(B MD5PartitionKey                  \x1b(0x\x1b(B HashKey                                 \x1b(0x\x1b(B ShardId         \x1b(0x\x1b(B\n\x1b(0tqqqqqqqqqqqqqqnqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqnqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqnqqqqqqqqqqqqqqqqqu\x1b(B\n\x1b(0x\x1b(B 123          \x1b(0x\x1b(B 202cb962ac59075b964b07152d234b70 \x1b(0x\x1b(B 42767516990368493138776584305024125808  \x1b(0x\x1b(B 📖 000000000008 \x1b(0x\x1b(B\n\x1b(0x\x1b(B abc          \x1b(0x\x1b(B 900150983cd24fb0d6963f7d28e17f72 \x1b(0x\x1b(B 191415658344158766168031473277922803570 \x1b(0x\x1b(B 📖 000000000011 \x1b(0x\x1b(B\n\x1b(0mqqqqqqqqqqqqqqvqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqvqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqvqqqqqqqqqqqqqqqqqj\x1b(B\n"
    assert expected_output == result.output
    assert result.exit_code == 0


def test_report(monkeypatch):
    monkeypatch.setattr(boto3, 'client', mock_get_cloudwatch_client)

    runner = CliRunner()
    result = runner.invoke(kines_cli.kines, ['report', 'test-stream-report', '-h', '3', '-p', '30'])
    print("report output", repr(result.output))
    expected_output = '\x1b(0lqqqqqqqqqqqqqqqqqqwqqqqqqqqqqwqqqqqqqqqqqwqqqqqqqqwqqqqqqqqqqqwqqqqqqqqqwqqqqqqqwqqqqqqwqqqqqqqqwqqqqqqqqqqqqk\x1b(B\n\x1b(0x\x1b(B Time             \x1b(0x\x1b(B IR       \x1b(0x\x1b(B IS        \x1b(0x\x1b(B IR/Sec \x1b(0x\x1b(B GR        \x1b(0x\x1b(B GR/Sec  \x1b(0x\x1b(B GR/IR \x1b(0x\x1b(B WPTE \x1b(0x\x1b(B RPTE   \x1b(0x\x1b(B MAX(IAGM)  \x1b(0x\x1b(B\n\x1b(0tqqqqqqqqqqqqqqqqqqnqqqqqqqqqqnqqqqqqqqqqqnqqqqqqqqnqqqqqqqqqqqnqqqqqqqqqnqqqqqqqnqqqqqqnqqqqqqqqnqqqqqqqqqqqqu\x1b(B\n\x1b(0x\x1b(B 2019-10-11 10:30 \x1b(0x\x1b(B 297200.0 \x1b(0x\x1b(B 926.48 MB \x1b(0x\x1b(B 165.11 \x1b(0x\x1b(B 2079782.0 \x1b(0x\x1b(B 1155.43 \x1b(0x\x1b(B 7.00  \x1b(0x\x1b(B 0.0  \x1b(0x\x1b(B 0.0    \x1b(0x\x1b(B 0.0        \x1b(0x\x1b(B\n\x1b(0x\x1b(B 2019-10-11 11:00 \x1b(0x\x1b(B 265471.0 \x1b(0x\x1b(B 837.15 MB \x1b(0x\x1b(B 147.48 \x1b(0x\x1b(B 1858115.0 \x1b(0x\x1b(B 1032.29 \x1b(0x\x1b(B 7.00  \x1b(0x\x1b(B 0.0  \x1b(0x\x1b(B 1.0 🔥 \x1b(0x\x1b(B 0.0        \x1b(0x\x1b(B\n\x1b(0x\x1b(B 2019-10-11 11:30 \x1b(0x\x1b(B 255861.0 \x1b(0x\x1b(B 807.8 MB  \x1b(0x\x1b(B 142.15 \x1b(0x\x1b(B 1791687.0 \x1b(0x\x1b(B 995.38  \x1b(0x\x1b(B 7.00  \x1b(0x\x1b(B 0.0  \x1b(0x\x1b(B 0.0    \x1b(0x\x1b(B 0.0        \x1b(0x\x1b(B\n\x1b(0x\x1b(B 2019-10-11 12:00 \x1b(0x\x1b(B 250698.0 \x1b(0x\x1b(B 792.29 MB \x1b(0x\x1b(B 139.28 \x1b(0x\x1b(B 1754570.0 \x1b(0x\x1b(B 974.76  \x1b(0x\x1b(B 7.00  \x1b(0x\x1b(B 0.0  \x1b(0x\x1b(B 3.0 🔥 \x1b(0x\x1b(B 0.0        \x1b(0x\x1b(B\n\x1b(0x\x1b(B 2019-10-11 12:30 \x1b(0x\x1b(B 241889.0 \x1b(0x\x1b(B 761.83 MB \x1b(0x\x1b(B 134.38 \x1b(0x\x1b(B 1693413.0 \x1b(0x\x1b(B 940.78  \x1b(0x\x1b(B 7.00  \x1b(0x\x1b(B 0.0  \x1b(0x\x1b(B 1.0 🔥 \x1b(0x\x1b(B 0.0        \x1b(0x\x1b(B\n\x1b(0x\x1b(B 2019-10-11 13:00 \x1b(0x\x1b(B 305792.0 \x1b(0x\x1b(B 953.44 MB \x1b(0x\x1b(B 169.88 \x1b(0x\x1b(B 2140395.0 \x1b(0x\x1b(B 1189.11 \x1b(0x\x1b(B 7.00  \x1b(0x\x1b(B 0.0  \x1b(0x\x1b(B 3.0 🔥 \x1b(0x\x1b(B 36000.0 🔥 \x1b(0x\x1b(B\n\x1b(0x\x1b(B 2019-10-11 13:30 \x1b(0x\x1b(B 189147.0 \x1b(0x\x1b(B 594.26 MB \x1b(0x\x1b(B 105.08 \x1b(0x\x1b(B 1323267.0 \x1b(0x\x1b(B 735.15  \x1b(0x\x1b(B 7.00  \x1b(0x\x1b(B 0.0  \x1b(0x\x1b(B 5.0 🔥 \x1b(0x\x1b(B 0.0        \x1b(0x\x1b(B\n\x1b(0mqqqqqqqqqqqqqqqqqqvqqqqqqqqqqvqqqqqqqqqqqvqqqqqqqqvqqqqqqqqqqqvqqqqqqqqqvqqqqqqqvqqqqqqvqqqqqqqqvqqqqqqqqqqqqj\x1b(B\n'
    assert expected_output == result.output
    assert result.exit_code == 0
