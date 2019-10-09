## Kines
[![PyPI version](https://img.shields.io/pypi/v/kines.svg)](https://badge.fury.io/py/kines) [![Build Status](https://travis-ci.org/dinsaw/kines.svg?branch=master)](https://travis-ci.org/dinsaw/kines)

Friendly Command Line Interface for [Amazon Kinesis Data Streams](https://aws.amazon.com/kinesis/data-streams/)

![Kines Demo](https://raw.githubusercontent.com/dinsaw/kines/master/demo/kines-demo.gif)

#### Install
- `pip install kines`

#### Setup 
- `aws configure`

#### Commands 
##### List all Kinesis Stream
- `kines ls`

![Kines ls](https://raw.githubusercontent.com/dinsaw/kines/master/demo/kines-ls.png)

##### List Kinesis Stream Shards
- `kines lss <stream-name>`
- For detailed output Run `kines lss <stream-name> -d`

![Kines lss](https://raw.githubusercontent.com/dinsaw/kines/master/demo/kines-lss-and-d.png)

##### Find shard for partition key
- `kines find prod-clickstream -p 123455 -p 8900`

![Kines find](https://raw.githubusercontent.com/dinsaw/kines/master/demo/kines-find.png)

#### Walk through kinesis records
- `kines walk <stream-name> <shard-id> -s <sequence-number> -n <number-of-records-per-call>`

![Kines Walk](https://raw.githubusercontent.com/dinsaw/kines/master/demo/kines-walk-demo.gif)

- Get report for last 60 hours with 6 hour metric period

![Kines Report 60 hours 6 hours](https://raw.githubusercontent.com/dinsaw/kines/master/demo/kines-report-h-60-p-60.png)

#### View all short forms and legends
- `kines legends`

![Kines Legends](https://raw.githubusercontent.com/dinsaw/kines/master/demo/kines-legends.png)

#### How to build in Dev?
- `pip install --editable .`

#### How to publish to pypi?
- `python3 setup.py sdist bdist_wheel`
- `twine upload --skip-existing dist/*`
