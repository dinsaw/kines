## Kines
[![PyPI version](https://img.shields.io/pypi/v/kines.svg)](https://badge.fury.io/py/kines) [![PyPI downloads](https://img.shields.io/pypi/dm/kines.svg)](https://pypistats.org/packages/kines) [![Build Status](https://travis-ci.org/dinsaw/kines.svg?branch=master)](https://travis-ci.org/dinsaw/kines) [![codecov](https://codecov.io/gh/dinsaw/kines/branch/master/graph/badge.svg)](https://codecov.io/gh/dinsaw/kines)

Friendly Command Line Interface for [Amazon Kinesis Data Streams](https://aws.amazon.com/kinesis/data-streams/)

![Kines Demo](https://raw.githubusercontent.com/dinsaw/kines/master/demo/kines-demo.gif)

#### Install
- `pip install kines`

#### Setup 
- `aws configure`

#### Commands 
##### List all Kinesis Stream
- `kines ls`

This command lists streams with their open shard count, enhanced consumers count, retention period and encryption type. Internally this command calls `list-streams` and `describe_stream_summary` methods of [Boto3](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/kinesis.html#id34) Kinesis client.

![Kines ls](https://raw.githubusercontent.com/dinsaw/kines/master/demo/kines-ls.png)

##### List Kinesis Stream Shards
- `kines lss <stream-name>`

This command will show you open as well as closed shards of a Kinesis stream.

- For detailed output Run `kines lss <stream-name> -d`

![Kines lss](https://raw.githubusercontent.com/dinsaw/kines/master/demo/kines-lss-and-d.png)

##### Find shard for partition key
- `kines find prod-clickstream -p 123455 -p 8900`

From [Kinesis Docs](https://docs.aws.amazon.com/streams/latest/dev/key-concepts.html)
> A partition key is used to group data by shard within a stream. Kinesis Data Streams segregates the data records belonging to a stream into multiple shards. It uses the partition key that is associated with each data record to determine which shard a given data record belongs to. Partition keys are Unicode strings with a maximum length limit of 256 bytes. An MD5 hash function is used to map partition keys to 128-bit integer values and to map associated data records to shards. When an application puts data into a stream, it must specify a partition key.

This command comes handy when you want to determine shard for a partition key. This Command can accept multiple partition keys.

![Kines find](https://raw.githubusercontent.com/dinsaw/kines/master/demo/kines-find.png)

#### Walk through kinesis records
- `kines walk <stream-name> <shard-id> -s <sequence-number> -n <number-of-records-per-call>`

You can use this command to debug kinesis records. This command internally creates a [Shard Iterator](https://docs.aws.amazon.com/kinesis/latest/APIReference/API_GetShardIterator.html). If you don't specify `sequence-number` then a ShardIterator is created with type `TRIM_HORIZON`, which allows you to fetch from oldest Kinesis records in shard. When you specify `sequence-number` a ShardIterator is created with `AT_SEQUENCE_NUMBER` type, which fetches data from the specified sequence number.
The Kinesis record's data is decoded using `base64` decoder. You can press ⏎ to fetch more records or type `n` to abort.

![Kines Walk](https://raw.githubusercontent.com/dinsaw/kines/master/demo/kines-walk-demo.gif)

- Use `-t` option to get records from 1 hour 10 minutes ago. Example: `kines walk click-stream 000000000000 -t '1h10m'`

- Use `-l` option to start from latest records. Example: `kines walk click-stream 000000000000 -l`

- Use `-f` option to poll records repeatedly. Example: `kines walk click-stream 000000000000 -l -f`

#### Get report for Kinesis Stream

The report command gives you statistics about your Kinesis Stream. Internally, this command calls [`get_metric_data`](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/cloudwatch.html#CloudWatch.Client.get_metric_data) of Boto3 Cloudwatch client.

Please take a look at legends command for shortforms used in this report.

![Kines Report 60 hours 6 hours](https://raw.githubusercontent.com/dinsaw/kines/master/demo/kines-report-h-60-p-60.png)

#### View all short forms and legends
- `kines legends`

![Kines Legends](https://raw.githubusercontent.com/dinsaw/kines/master/demo/kines-legends.png)

#### How to build in Dev?
- `pip install --editable .`

#### How to publish to pypi?
- `python3 setup.py sdist bdist_wheel`
- `twine upload --skip-existing dist/*`
