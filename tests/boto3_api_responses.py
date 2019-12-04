import datetime

from dateutil.tz import tzutc, tzlocal

LIST_SHARDS_8_RESPONSE = {
    "Shards": [
        {
            "ShardId": "shardId-000000000007",
            "ParentShardId": "shardId-000000000003",
            "HashKeyRange": {
                "StartingHashKey": "0",
                "EndingHashKey": "42535295865117307932921825928971026431",
            },
            "SequenceNumberRange": {
                "StartingSequenceNumber": "49599683191123462322666423956522487359138715784273985650"
            },
        },
        {
            "ShardId": "shardId-000000000008",
            "ParentShardId": "shardId-000000000003",
            "HashKeyRange": {
                "StartingHashKey": "42535295865117307932921825928971026432",
                "EndingHashKey": "85070591730234615865843651857942052863",
            },
            "SequenceNumberRange": {
                "StartingSequenceNumber": "49599683191145763067864954579664023077411364145779966082"
            },
        },
        {
            "ShardId": "shardId-000000000009",
            "ParentShardId": "shardId-000000000004",
            "HashKeyRange": {
                "StartingHashKey": "85070591730234615865843651857942052864",
                "EndingHashKey": "127605887595351923798765477786913079295",
            },
            "SequenceNumberRange": {
                "StartingSequenceNumber": "49599683201872421508358184310742703566555228091740848274"
            },
        },
        {
            "ShardId": "shardId-000000000010",
            "ParentShardId": "shardId-000000000004",
            "HashKeyRange": {
                "StartingHashKey": "127605887595351923798765477786913079296",
                "EndingHashKey": "170141183460469231731687303715884105727",
            },
            "SequenceNumberRange": {
                "StartingSequenceNumber": "49599683201894722253556714933884239284827876453246828706"
            },
        },
        {
            "ShardId": "shardId-000000000011",
            "ParentShardId": "shardId-000000000005",
            "HashKeyRange": {
                "StartingHashKey": "170141183460469231731687303715884105728",
                "EndingHashKey": "212676479325586539664609129644855132159",
            },
            "SequenceNumberRange": {
                "StartingSequenceNumber": "49599683204057894537814185378613203957274767931643789490"
            },
        },
        {
            "ShardId": "shardId-000000000012",
            "ParentShardId": "shardId-000000000005",
            "HashKeyRange": {
                "StartingHashKey": "212676479325586539664609129644855132160",
                "EndingHashKey": "255211775190703847597530955573826158591",
            },
            "SequenceNumberRange": {
                "StartingSequenceNumber": "49599683204080195283012716001754739675547416293149769922"
            },
        },
        {
            "ShardId": "shardId-000000000013",
            "ParentShardId": "shardId-000000000006",
            "HashKeyRange": {
                "StartingHashKey": "255211775190703847597530955573826158592",
                "EndingHashKey": "297747071055821155530452781502797185023",
            },
            "SequenceNumberRange": {
                "StartingSequenceNumber": "49599683205886555644093696476219132855631933918731567314"
            },
        },
        {
            "ShardId": "shardId-000000000014",
            "ParentShardId": "shardId-000000000006",
            "HashKeyRange": {
                "StartingHashKey": "297747071055821155530452781502797185024",
                "EndingHashKey": "340282366920938463463374607431768211455",
            },
            "SequenceNumberRange": {
                "StartingSequenceNumber": "49599683205908856389292227099360668573904582280237547746"
            },
        },
    ]
}

CLOUDWATCH_RESPONSE_H3_P3 = {
    "MetricDataResults": [
        {
            "Id": "ir",
            "Label": "IncomingRecords",
            "Timestamps": [
                datetime.datetime(2019, 10, 11, 5, 0, tzinfo=tzutc()),
                datetime.datetime(2019, 10, 11, 5, 30, tzinfo=tzutc()),
                datetime.datetime(2019, 10, 11, 6, 0, tzinfo=tzutc()),
                datetime.datetime(2019, 10, 11, 6, 30, tzinfo=tzutc()),
                datetime.datetime(2019, 10, 11, 7, 0, tzinfo=tzutc()),
                datetime.datetime(2019, 10, 11, 7, 30, tzinfo=tzutc()),
                datetime.datetime(2019, 10, 11, 8, 0, tzinfo=tzutc()),
            ],
            "Values": [
                297200.0,
                265471.0,
                255861.0,
                250698.0,
                241889.0,
                305792.0,
                189147.0,
            ],
            "StatusCode": "Complete",
        },
        {
            "Id": "ib",
            "Label": "IncomingBytes",
            "Timestamps": [
                datetime.datetime(2019, 10, 11, 5, 0, tzinfo=tzutc()),
                datetime.datetime(2019, 10, 11, 5, 30, tzinfo=tzutc()),
                datetime.datetime(2019, 10, 11, 6, 0, tzinfo=tzutc()),
                datetime.datetime(2019, 10, 11, 6, 30, tzinfo=tzutc()),
                datetime.datetime(2019, 10, 11, 7, 0, tzinfo=tzutc()),
                datetime.datetime(2019, 10, 11, 7, 30, tzinfo=tzutc()),
                datetime.datetime(2019, 10, 11, 8, 0, tzinfo=tzutc()),
            ],
            "Values": [
                971488736.0,
                877812818.0,
                847037776.0,
                830774392.0,
                798839755.0,
                999749339.0,
                623121754.0,
            ],
            "StatusCode": "Complete",
        },
        {
            "Id": "grr",
            "Label": "GetRecords.Records",
            "Timestamps": [
                datetime.datetime(2019, 10, 11, 5, 0, tzinfo=tzutc()),
                datetime.datetime(2019, 10, 11, 5, 30, tzinfo=tzutc()),
                datetime.datetime(2019, 10, 11, 6, 0, tzinfo=tzutc()),
                datetime.datetime(2019, 10, 11, 6, 30, tzinfo=tzutc()),
                datetime.datetime(2019, 10, 11, 7, 0, tzinfo=tzutc()),
                datetime.datetime(2019, 10, 11, 7, 30, tzinfo=tzutc()),
                datetime.datetime(2019, 10, 11, 8, 0, tzinfo=tzutc()),
            ],
            "Values": [
                2079782.0,
                1858115.0,
                1791687.0,
                1754570.0,
                1693413.0,
                2140395.0,
                1323267.0,
            ],
            "StatusCode": "Complete",
        },
        {
            "Id": "wpte",
            "Label": "WriteProvisionedThroughputExceeded",
            "Timestamps": [
                datetime.datetime(2019, 10, 11, 5, 0, tzinfo=tzutc()),
                datetime.datetime(2019, 10, 11, 5, 30, tzinfo=tzutc()),
                datetime.datetime(2019, 10, 11, 6, 0, tzinfo=tzutc()),
                datetime.datetime(2019, 10, 11, 6, 30, tzinfo=tzutc()),
                datetime.datetime(2019, 10, 11, 7, 0, tzinfo=tzutc()),
                datetime.datetime(2019, 10, 11, 7, 30, tzinfo=tzutc()),
                datetime.datetime(2019, 10, 11, 8, 0, tzinfo=tzutc()),
            ],
            "Values": [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
            "StatusCode": "Complete",
        },
        {
            "Id": "rpte",
            "Label": "ReadProvisionedThroughputExceeded",
            "Timestamps": [
                datetime.datetime(2019, 10, 11, 5, 0, tzinfo=tzutc()),
                datetime.datetime(2019, 10, 11, 5, 30, tzinfo=tzutc()),
                datetime.datetime(2019, 10, 11, 6, 0, tzinfo=tzutc()),
                datetime.datetime(2019, 10, 11, 6, 30, tzinfo=tzutc()),
                datetime.datetime(2019, 10, 11, 7, 0, tzinfo=tzutc()),
                datetime.datetime(2019, 10, 11, 7, 30, tzinfo=tzutc()),
                datetime.datetime(2019, 10, 11, 8, 0, tzinfo=tzutc()),
            ],
            "Values": [0.0, 1.0, 0.0, 3.0, 1.0, 3.0, 5.0],
            "StatusCode": "Complete",
        },
        {
            "Id": "giam",
            "Label": "GetRecords.IteratorAgeMilliseconds",
            "Timestamps": [
                datetime.datetime(2019, 10, 11, 5, 0, tzinfo=tzutc()),
                datetime.datetime(2019, 10, 11, 5, 30, tzinfo=tzutc()),
                datetime.datetime(2019, 10, 11, 6, 0, tzinfo=tzutc()),
                datetime.datetime(2019, 10, 11, 6, 30, tzinfo=tzutc()),
                datetime.datetime(2019, 10, 11, 7, 0, tzinfo=tzutc()),
                datetime.datetime(2019, 10, 11, 7, 30, tzinfo=tzutc()),
                datetime.datetime(2019, 10, 11, 8, 0, tzinfo=tzutc()),
            ],
            "Values": [0.0, 0.0, 0.0, 0.0, 0.0, 36000.0, 0.0],
            "StatusCode": "Complete",
        },
    ],
    "Messages": [],
}

KINESIS_RECORDS_ITERATOR_1_RESPONSE = {
    "Records": [
        {
            "SequenceNumber": "49600282682944895786267660693075522538255370376250918498",
            "ApproximateArrivalTimestamp": datetime.datetime(
                2019, 10, 10, 16, 22, 41, 761000, tzinfo=tzlocal()
            ),
            "Data": b"eyJldmVudCI6ICIxIn0K",
            "PartitionKey": "4439109",
        },
        {
            "SequenceNumber": "49600282682944895786267660697997059549906526021357667938",
            "ApproximateArrivalTimestamp": datetime.datetime(
                2019, 10, 10, 16, 22, 45, 180000, tzinfo=tzlocal()
            ),
            "Data": b"eyJldmVudCI6ICIyIn0K",
            "PartitionKey": "4439109",
        },
        {
            "SequenceNumber": "49600282682944895786267660702176316108314299215755871842",
            "ApproximateArrivalTimestamp": datetime.datetime(
                2019, 10, 10, 16, 22, 48, 83000, tzinfo=tzlocal()
            ),
            "Data": b"eyJldmVudCI6ICIzIn0K",
            "PartitionKey": "4439109",
        },
        {
            "SequenceNumber": "49600282682944895786267660702634498993948243810408466018",
            "ApproximateArrivalTimestamp": datetime.datetime(
                2019, 10, 10, 16, 22, 48, 407000, tzinfo=tzlocal()
            ),
            "Data": b"eyJldmVudCI6ICI0In0K",
            "PartitionKey": "4439109",
        },
        {
            "SequenceNumber": "49600282682944895786267660705672529578639807063884039778",
            "ApproximateArrivalTimestamp": datetime.datetime(
                2019, 10, 10, 16, 22, 50, 666000, tzinfo=tzlocal()
            ),
            "Data": b"eyJldmVudCI6ICI1In0K",
            "PartitionKey": "4439109",
        },
    ],
    "NextShardIterator": "AAAA-Shard-Iterator-2",
    "MillisBehindLatest": 86346000,
    "ResponseMetadata": {
        "RequestId": "f66ad0f9-3ade-3f3e-a070-b1f5c9043ac3",
        "HTTPStatusCode": 200,
        "HTTPHeaders": {
            "x-amzn-requestid": "f66ad0f9-3ade-3f3e-a070-b1f5c9043ac3",
            "x-amz-id-2": "y6rEwcgmg3F05eSo8bEqr2OMvkyFQwc8vCjClMZRRfU0fEq2vbR1lD2FC7v0rp43b1LY1acrEaQWjnjOXgBq/DkW39Fbznto",
            "date": "Fri, 11 Oct 2019 10:51:56 GMT",
            "content-type": "application/x-amz-json-1.1",
            "content-length": "91441",
        },
        "RetryAttempts": 0,
    },
}
