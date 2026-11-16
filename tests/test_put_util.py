import json
import boto3
import pytest
from click.testing import CliRunner

from kines import kines_cli, put_util


class MockPutKinesisClient:
    def __init__(self):
        self.calls = []

    def put_record(self, **kwargs):
        self.calls.append(kwargs)
        return {
            "ShardId": "shardId-000000000001",
            "SequenceNumber": "496123456789000000000000000000001",
            "EncryptionType": "NONE",
        }


def test_parse_records_from_options():
    records = put_util.parse_records(
        partition_keys=["pk1", "pk2"],
        data_list=['{"msg": 1}', '{"msg": 2}'],
        file_path=None,
    )
    assert len(records) == 2
    assert records[0]["partition_key"] == "pk1"
    assert records[0]["data"] == '{"msg": 1}'
    assert records[1]["partition_key"] == "pk2"
    assert records[1]["data"] == '{"msg": 2}'


def test_parse_records_single_pk_multiple_data():
    records = put_util.parse_records(
        partition_keys=["pk1"],
        data_list=["data1", "data2"],
        file_path=None,
    )
    assert len(records) == 2
    assert records[0]["partition_key"] == "pk1"
    assert records[1]["partition_key"] == "pk1"


def test_parse_records_from_json_array_file(tmp_path):
    json_file = tmp_path / "records.json"
    json_file.write_text(
        json.dumps(
            [
                {"partition_key": "user-1", "data": "event-1"},
                {"partition_key": "user-2", "data": "event-2"},
            ]
        )
    )
    records = put_util.parse_records((), (), str(json_file))
    assert len(records) == 2
    assert records[0]["partition_key"] == "user-1"
    assert records[0]["data"] == "event-1"
    assert records[1]["partition_key"] == "user-2"
    assert records[1]["data"] == "event-2"


def test_parse_records_from_text_file(tmp_path):
    txt_file = tmp_path / "raw_event.txt"
    txt_file.write_text("Hello plain text payload")
    records = put_util.parse_records(("my-pk",), (), str(txt_file))
    assert len(records) == 1
    assert records[0]["data"] == "Hello plain text payload"


def test_put_no_data_raises_error():
    with pytest.raises(Exception):
        put_util.put("my-stream", (), (), None)


def test_put_single_record(monkeypatch):
    mock_client = MockPutKinesisClient()
    monkeypatch.setattr(boto3, "client", lambda service: mock_client)

    resp = put_util.put_single_record(
        stream_name="test-stream",
        partition_key="pk-1",
        data="hello single",
        explicit_hash_key="12345",
    )
    assert resp["ShardId"] == "shardId-000000000001"
    assert len(mock_client.calls) == 1
    assert mock_client.calls[0]["StreamName"] == "test-stream"
    assert mock_client.calls[0]["PartitionKey"] == "pk-1"
    assert mock_client.calls[0]["Data"] == b"hello single"
    assert mock_client.calls[0]["ExplicitHashKey"] == "12345"


def test_put_aggregated_record(monkeypatch):
    mock_client = MockPutKinesisClient()
    monkeypatch.setattr(boto3, "client", lambda service: mock_client)

    records = [
        {"partition_key": "pk1", "data": "payload 1"},
        {"partition_key": "pk2", "data": "payload 2"},
    ]
    resp = put_util.put_aggregated_record("test-stream", records)
    assert resp["ShardId"] == "shardId-000000000001"
    assert len(mock_client.calls) == 1
    assert mock_client.calls[0]["StreamName"] == "test-stream"
    assert mock_client.calls[0]["PartitionKey"] == "pk1"
    # Starts with KPL magic header
    assert mock_client.calls[0]["Data"].startswith(b"\xf3\x89\x9a\xc2")


def test_kines_put_cli_single(monkeypatch):
    mock_client = MockPutKinesisClient()
    monkeypatch.setattr(boto3, "client", lambda service: mock_client)

    runner = CliRunner()
    result = runner.invoke(
        kines_cli.kines,
        ["put", "test-stream", "-p", "pk-cli", "-d", "cli message"],
    )
    assert result.exit_code == 0
    assert "Successfully put 1 record" in result.output
    assert "shardId-000000000001" in result.output


def test_kines_put_cli_aggregated(monkeypatch):
    mock_client = MockPutKinesisClient()
    monkeypatch.setattr(boto3, "client", lambda service: mock_client)

    runner = CliRunner()
    result = runner.invoke(
        kines_cli.kines,
        [
            "put",
            "test-stream",
            "-a",
            "-p",
            "pk-1",
            "-d",
            "msg-1",
            "-p",
            "pk-2",
            "-d",
            "msg-2",
        ],
    )
    assert result.exit_code == 0
    assert "Successfully put 1 aggregated record" in result.output
    assert "Aggregated (KPL)" in result.output
