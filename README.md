## Kines
Friendly Amazon Kinesis Stream Command Line Interface

![Kines Demo](demo/kines-demo.gif)

#### Install
- `pip install kines`

#### Setup 
- `aws configure`

#### Commands 
##### List all Kinesis Stream
- `kines ls`
![Kines ls](demo/kines-ls.png)

##### List Kinesis Stream Shards
- `kines lss <stream-name>`
- For detailed output Run `kines lss <stream-name> -d`
![Kines lss](demo/kines-lss-and-d.png)

##### Find shard for partition key
- `kines find prod-clickstream -p 123455 -p 8900`
![Kines find](demo/kines-find.png)

#### Get report for your Kinesis Stream
- `kines report <stream-name> -h <number-of-hours> -p <metric-period-in-minutes>`
![Kines Report](demo/kines-report.png)

#### View all short forms and legends
- `kines legends`
![Kines Legends](demo/kines-legends.png)

#### How to build in Dev?
- `pip install --editable .`

#### How to publish to pypi?
- `python3 setup.py sdist bdist_wheel`
- `twine upload --skip-existing dist/*`
