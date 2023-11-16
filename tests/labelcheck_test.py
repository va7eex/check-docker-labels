from pathlib import Path
from typing import Any

import pytest
import yaml

from labelcheck.labelcheck import CheckLabelConfig, check_labels, find_files


@pytest.fixture(params=['"', "'", ""], ids=["double quote", "single quote", "no quote"])
def string_pattern(request: pytest.FixtureRequest) -> str:
    return request.param


@pytest.fixture(params=["foo", "foo.bar", "foo.bar.baz"])
def valid_compose_dict(request: pytest.FixtureRequest, string_pattern: str) -> dict[str, Any]:
    return {
        "services": {
            "myservice": {
                "labels": [
                    f"{string_pattern}{request.param}=baz{string_pattern}",
                ]
            }
        }
    }


@pytest.fixture(params=[".foo", "foo..bar", "foo.BAR", "foo.bar."])
def invalid_compose_dict(request: pytest.FixtureRequest, string_pattern: str) -> dict[str, Any]:
    return {
        "services": {
            "myservice": {
                "labels": [
                    f"{string_pattern}{request.param}=baz{string_pattern}",
                ]
            }
        }
    }


@pytest.fixture(params=["docker_compose.yml", "docker_compose.yaml", "compose.yml", "docker_compose.override.yml"])
def valid_compose_file(
    request: pytest.FixtureRequest, tmp_path: Path, valid_compose_dict: pytest.FixtureRequest
) -> Path:
    compose_file = tmp_path / request.param
    with open(compose_file, mode="w", encoding="utf-8") as f:
        yaml.safe_dump(valid_compose_dict, f)
    return compose_file


@pytest.fixture(params=["docker_compose.yml", "docker_compose.yaml", "compose.yml", "docker_compose.override.yml"])
def invalid_compose_file(
    request: pytest.FixtureRequest, tmp_path: Path, invalid_compose_dict: pytest.FixtureRequest
) -> Path:
    compose_file = tmp_path / request.param
    with open(compose_file, mode="w", encoding="utf-8") as f:
        yaml.safe_dump(invalid_compose_dict, f)
    return compose_file


def test_check_valid_labels(valid_compose_dict: dict[str, Any]):
    config = CheckLabelConfig()
    with pytest.raises(SystemExit) as pytest_wrapped_e:
        check_labels(valid_compose_dict, valid_pattern=config.valid_pattern, verbose_output=True)
    assert pytest_wrapped_e.type == SystemExit
    assert pytest_wrapped_e.value.code == 0


def test_check_invalid_labels(invalid_compose_dict: dict[str, Any]):
    config = CheckLabelConfig()
    with pytest.raises(SystemExit) as pytest_wrapped_e:
        check_labels(invalid_compose_dict, valid_pattern=config.valid_pattern, verbose_output=True)
    assert pytest_wrapped_e.type == SystemExit
    assert pytest_wrapped_e.value.code == 1


def test_check_valid_file(valid_compose_file: Path):
    config = CheckLabelConfig(glob_patterns=[str(valid_compose_file)], verbose=True)
    with pytest.raises(SystemExit) as pytest_wrapped_e:
        find_files(config)
    assert pytest_wrapped_e.type == SystemExit
    assert pytest_wrapped_e.value.code == 0


def test_check_invalid_file(invalid_compose_file: Path):
    config = CheckLabelConfig(glob_patterns=[str(invalid_compose_file)], verbose=True)
    with pytest.raises(SystemExit) as pytest_wrapped_e:
        find_files(config)
    assert pytest_wrapped_e.type == SystemExit
    assert pytest_wrapped_e.value.code == 1


def test_raise_if_no_files_found(tmp_path: pytest.FixtureRequest):
    config = CheckLabelConfig(glob_patterns=[f"{tmp_path}/*"], verbose=True)
    with pytest.raises(FileNotFoundError):
        find_files(config)
