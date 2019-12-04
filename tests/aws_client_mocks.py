import datetime

from dateutil.tz import tzlocal

import tests.boto3_api_responses
from tests.test_constants import TEST_PARTITION_KEY_STREAM_NAME


class MockKinesisClient:
    @staticmethod
    def list_streams(*args, **kwargs):
        return {
            "StreamNames": ["test-stream-1", "test-stream-2"],
            "HasMoreStreams": False,
            " \
               "
            "ResponseMetadata": {
                "RequestId": "fc11d7e4-6b7d-f442-aa43-3049e19b80e5",
                " \
               "
                "HTTPStatusCode": 200,
                "HTTPHeaders": {
                    "x-amzn-requestid": " \
               "
                    "fc5bd7e4-6b7d-1111-aa43-3049e19b80e5",
                    "x-amz-id-2": " \
               "
                    'yhU937PwchDLgTnJCxz+CX0z1u+hbl" \
               "+zDgDIf5yLf0SdfoETI8Ovai8Nj1ctKTCrPrvmQrRvOOy7F9eKOlVQyfmf1xES560M',
                    "date": 'Thu, " \
               "10 Oct 2019 08:01:49 GMT',
                    "content-type": "application/x-amz-json-1.1",
                    " \
               "
                    "content-length": "453",
                },
                "RetryAttempts": 0,
            },
        }

    @staticmethod
    def describe_stream_summary(*args, **kwargs):
        status = "ACTIVE"
        if kwargs["StreamName"] == "test-stream-1":
            status = "CREATING"
        return {
            "StreamDescriptionSummary": {
                "StreamName": kwargs["StreamName"],
                "StreamARN": "arn:aws:kinesis:ap-south-1:622212315795:stream/test-stream-1",
                "StreamStatus": status,
                "RetentionPeriodHours": 24,
                "StreamCreationTimestamp": datetime.datetime(
                    2017, 10, 12, 15, 1, 10, tzinfo=tzlocal()
                ),
                "EnhancedMonitoring": [{"ShardLevelMetrics": []}],
                "EncryptionType": "NONE",
                "OpenShardCount": 3,
                "ConsumerCount": 0,
            },
            "ResponseMetadata": {
                "RequestId": "f65c5191-b0a2-89db-a044-bc766e1035f2",
                "HTTPStatusCode": 200,
                "HTTPHeaders": {
                    "x-amzn-requestid": "f65c5111-b0a2-89db-a044-bc766e1035f2",
                    "x-amz-id-2": "iPhP5twFKYQUl9EVR+o9ofwuWS8IR8Gei8eQQcz"
                    "+I11111pCfoSGDecx4VBgggDbTt7VxsGYUyHlePx"
                    "d1ZYedxqrQBrq2Wpj",
                    "date": "Thu, 10 Oct 2019 08:28:23 GMT",
                    "content-type": "application/x-amz-json-1.1",
                    "content-length": "338",
                },
                "RetryAttempts": 0,
            },
        }

    @staticmethod
    def list_shards(*args, **kwargs):
        if kwargs["StreamName"] == TEST_PARTITION_KEY_STREAM_NAME:
            return tests.boto3_api_responses.LIST_SHARDS_8_RESPONSE
        return {
            "Shards": [
                {
                    "ShardId": "shardId-000000000102",
                    "ParentShardId": "shardId-000000000100",
                    "AdjacentParentShardId": "shardId-000000000101",
                    "HashKeyRange": {
                        "StartingHashKey": "0",
                        "EndingHashKey": "340282366920938463463374607431768211455",
                    },
                    "SequenceNumberRange": {
                        "StartingSequenceNumber": "49599466347575149145100714296670755717216365327595603554"
                    },
                }
            ],
            "ResponseMetadata": {
                "RequestId": "dd758b71-d791-b743-8b6c-96309a98f4c5",
                "HTTPStatusCode": 200,
                "HTTPHeaders": {
                    "x-amzn-requestid": "dd75ab71-d791-b743-8b6c-96309a98f4c5",
                    "x-amz-id-2": "Zh+M47thCzh5ATqzrmWjcZior+cBvowfewFEZNN7zYmeQ2lJ8U1fyVGao"
                    "+TayscjTKhRDTbMNzCOj11quBawNGQaHl7x/IiTu",
                    "date": "Thu, 10 Oct 2019 11:50:25 GMT",
                    "content-type": "application/x-amz-json-1.1",
                    "content-length": "338",
                },
                "RetryAttempts": 0,
            },
        }

    @staticmethod
    def get_shard_iterator(*args, **kwargs):
        return {"ShardIterator": "AAAA-Shard-Iterator-1"}

    @staticmethod
    def get_records(*args, **kwargs):
        return tests.boto3_api_responses.KINESIS_RECORDS_ITERATOR_1_RESPONSE


class MockCloudWatchClient:
    @staticmethod
    def get_metric_data(*args, **kwargs):
        return tests.boto3_api_responses.CLOUDWATCH_RESPONSE_H3_P3
