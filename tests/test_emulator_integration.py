import os
import time
import urllib.request
import ssl
import uuid
import boto3
import pytest
from click.testing import CliRunner

from kines import kines_cli

EMULATOR_PORT = 9297
EMULATOR_HEALTH_URL = f"https://127.0.0.1:{EMULATOR_PORT}/__admin/health"


def is_emulator_running():
    ca_cert = os.path.expanduser(f"~/.aws/emulator/{EMULATOR_PORT}/ca.pem")
    if not os.path.exists(ca_cert):
        return False
    try:
        ctx = ssl.create_default_context(cafile=ca_cert)
        with urllib.request.urlopen(
            EMULATOR_HEALTH_URL, context=ctx, timeout=2
        ) as resp:
            return resp.status == 200
    except Exception:
        return False


def setup_emulator_env():
    env_file = os.path.expanduser(f"~/.aws/emulator/{EMULATOR_PORT}.env")
    if os.path.exists(env_file):
        with open(env_file) as f:
            for line in f:
                line = line.strip()
                if line.startswith("export "):
                    key, val = line.replace("export ", "", 1).split("=", 1)
                    os.environ[key] = os.path.expandvars(val.strip("\"'"))
                elif line.startswith("unset "):
                    for var in line.replace("unset ", "", 1).split():
                        os.environ.pop(var, None)
    else:
        os.environ["AWS_ENDPOINT_URL"] = f"https://127.0.0.1:{EMULATOR_PORT}"
        os.environ["AWS_CA_BUNDLE"] = os.path.expanduser(
            f"~/.aws/emulator/{EMULATOR_PORT}/ca.pem"
        )
        os.environ["AWS_SHARED_CREDENTIALS_FILE"] = os.path.expanduser(
            f"~/.aws/emulator/{EMULATOR_PORT}/emulator_credentials"
        )
        os.environ["AWS_CONFIG_FILE"] = os.path.expanduser(
            f"~/.aws/emulator/{EMULATOR_PORT}/config"
        )
        os.environ["AWS_EC2_METADATA_DISABLED"] = "true"
        os.environ["AWS_DEFAULT_REGION"] = "us-east-1"
        os.environ["AWS_REGION"] = "us-east-1"
        for var in [
            "AWS_ACCESS_KEY_ID",
            "AWS_SECRET_ACCESS_KEY",
            "AWS_SESSION_TOKEN",
            "AWS_PROFILE",
            "AWS_DEFAULT_PROFILE",
        ]:
            os.environ.pop(var, None)


@pytest.fixture(scope="module")
def emulator_env():
    if not is_emulator_running():
        pytest.skip(f"AWS Emulator is not running on 127.0.0.1:{EMULATOR_PORT}")
    setup_emulator_env()
    return True


@pytest.fixture(scope="module")
def emulator_stream(emulator_env):
    stream_name = f"test-kines-{uuid.uuid4().hex[:8]}"
    client = boto3.client("kinesis")
    client.create_stream(StreamName=stream_name, ShardCount=2)

    # Wait for the stream to transition from CREATING to ACTIVE
    for _ in range(20):
        desc = client.describe_stream_summary(StreamName=stream_name)
        if desc["StreamDescriptionSummary"]["StreamStatus"] == "ACTIVE":
            break
        time.sleep(0.5)

    # Put a sample test record
    client.put_record(
        StreamName=stream_name,
        Data=b"Hello Emulator Test!",
        PartitionKey="test-partition-key",
    )

    yield stream_name

    # Teardown: Clean up test stream
    try:
        client.delete_stream(StreamName=stream_name)
    except Exception:
        pass


@pytest.mark.emulator
def test_emulator_kines_ls(emulator_stream):
    runner = CliRunner()
    result = runner.invoke(kines_cli.kines, ["ls"])
    assert result.exit_code == 0
    assert emulator_stream in result.output
    assert "Found" in result.output


@pytest.mark.emulator
def test_emulator_kines_lss(emulator_stream):
    runner = CliRunner()
    result = runner.invoke(kines_cli.kines, ["lss", emulator_stream])
    assert result.exit_code == 0
    assert "000000000000" in result.output
    assert "000000000001" in result.output
    assert "50.0%" in result.output


@pytest.mark.emulator
def test_emulator_kines_lss_detailed(emulator_stream):
    runner = CliRunner()
    result = runner.invoke(kines_cli.kines, ["lss", emulator_stream, "-d"])
    assert result.exit_code == 0
    assert "StartingHashKey" in result.output
    assert "EndingHashKey" in result.output
    assert "000000000000" in result.output


@pytest.mark.emulator
def test_emulator_kines_find(emulator_stream):
    runner = CliRunner()
    result = runner.invoke(
        kines_cli.kines,
        ["find", emulator_stream, "-p", "test-partition-key"],
    )
    assert result.exit_code == 0
    assert "test-partition-key" in result.output
    assert "PartitionKey" in result.output
    assert "HashKey" in result.output


@pytest.mark.emulator
def test_emulator_kines_walk(emulator_stream):
    runner = CliRunner()
    # Sending 'n\n' stops the interactive prompt after reading the first record batch
    result = runner.invoke(
        kines_cli.kines,
        ["walk", emulator_stream, "000000000000"],
        input="n\n",
    )
    assert result.exit_code == 0
    assert "Creating shard iterator" in result.output


@pytest.mark.emulator
def test_emulator_kines_report(emulator_stream):
    runner = CliRunner()
    result = runner.invoke(
        kines_cli.kines,
        ["report", emulator_stream, "-h", "1", "-p", "15"],
    )
    assert result.exit_code == 0


@pytest.mark.emulator
def test_emulator_kines_put_single(emulator_stream):
    runner = CliRunner()
    result = runner.invoke(
        kines_cli.kines,
        ["put", emulator_stream, "-p", "live-pk-single", "-d", "Live Single Payload"],
    )
    assert result.exit_code == 0
    assert "Successfully put 1 record" in result.output
    assert "Live Single Payload" in result.output


@pytest.mark.emulator
def test_emulator_kines_put_aggregated(emulator_stream):
    runner = CliRunner()
    result = runner.invoke(
        kines_cli.kines,
        [
            "put",
            emulator_stream,
            "-a",
            "-p",
            "live-agg-pk1",
            "-d",
            "Event payload 1",
            "-p",
            "live-agg-pk2",
            "-d",
            "Event payload 2",
        ],
    )
    assert result.exit_code == 0
    assert "Successfully put 1 aggregated record" in result.output
    assert "Aggregated (KPL)" in result.output
