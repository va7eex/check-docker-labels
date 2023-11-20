from pathlib import Path
from typing import Any, Dict, Tuple

import pytest
import yaml

from checkdockerlabels.labelcheck import CheckLabelConfig, check_labels, find_files


@pytest.fixture(params=[True, False], ids=["key-value", "string"])
def labeltype(request: pytest.FixtureRequest) -> bool:
    return request.param


@pytest.fixture(params=['"', "'", ""], ids=["double quote", "single quote", "no quote"])
def string_pattern(request: pytest.FixtureRequest) -> str:
    return request.param


@pytest.fixture(params=["docker_compose.yml", "docker_compose.yaml", "compose.yml", "docker_compose.override.yml"])
def file_name(request: pytest.FixtureRequest) -> str:
    return request.param


@pytest.fixture(params=["foo", "foo.bar", "foo.bar.baz"])
def valid_compose_dict(request: pytest.FixtureRequest, string_pattern: str, labeltype: bool) -> Dict[str, Any]:
    if labeltype:
        return {
            "services": {
                "myservice": {
                    "labels": {
                        f"{request.param}": "baz",
                    }
                }
            }
        }
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
def invalid_compose_dict(request: pytest.FixtureRequest, string_pattern: str, labeltype: bool) -> Dict[str, Any]:
    if labeltype:
        return {
            "services": {
                "myservice": {
                    "labels": {
                        f"{request.param}": "baz",
                    }
                }
            }
        }
    return {
        "services": {
            "myservice": {
                "labels": [
                    f"{string_pattern}{request.param}=baz{string_pattern}",
                ]
            }
        }
    }


@pytest.fixture(
    params=[
        # int(True) -> Exit(1)
        # int(False) -> Exit(0)
        [True, [".foo", "foo..bar", "foo.BAR", "foo.bar."]],
        [False, ["foo", "foo.bar", "foo.bar.baz"]],
        [True, ["foo", "foo.bar", "foo.bar.baz", "foo.bar."]],
    ]
)
def complex_compose_dict(
    request: pytest.FixtureRequest, string_pattern: str, labeltype: bool
) -> Tuple[bool, Dict[str, Any]]:
    if labeltype:
        return (request.param[0], {"services": {"myservice": {"labels": {k: "baz" for k in request.param[1]}}}})
    return (
        request.param[0],
        {"services": {"myservice": {"labels": [f"{string_pattern}{k}=baz{string_pattern}" for k in request.param[1]]}}},
    )


@pytest.fixture
def valid_compose_file(file_name: str, tmp_path: Path, valid_compose_dict: Dict[str, Any]) -> Path:
    compose_file = tmp_path / file_name
    with open(compose_file, mode="w", encoding="utf-8") as f:
        yaml.safe_dump(valid_compose_dict, f)
    return compose_file


@pytest.fixture
def invalid_compose_file(file_name: str, tmp_path: Path, invalid_compose_dict: Dict[str, Any]) -> Path:
    compose_file = tmp_path / file_name
    with open(compose_file, mode="w", encoding="utf-8") as f:
        yaml.safe_dump(invalid_compose_dict, f)
    return compose_file


@pytest.fixture
def complex_compose_file(
    file_name: str, tmp_path: Path, complex_compose_dict: Tuple[bool, Dict[str, Any]]
) -> Tuple[bool, Path]:
    compose_file = tmp_path / file_name
    with open(compose_file, mode="w", encoding="utf-8") as f:
        yaml.safe_dump(complex_compose_dict[1], f)
    return complex_compose_dict[0], compose_file


def test_check_valid_labels(valid_compose_dict: Dict[str, Any]):
    config = CheckLabelConfig()
    result = check_labels("", valid_compose_dict, valid_pattern=config.valid_pattern, verbose_output=True)
    assert result == True


def test_check_invalid_labels(invalid_compose_dict: Dict[str, Any]):
    config = CheckLabelConfig()
    result = check_labels("", invalid_compose_dict, valid_pattern=config.valid_pattern, verbose_output=True)
    assert result == False


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


def test_check_complex_labels(complex_compose_dict: Tuple[bool, Dict[str, Any]]):
    config = CheckLabelConfig()
    result = check_labels("", complex_compose_dict[1], valid_pattern=config.valid_pattern, verbose_output=True)
    assert result != complex_compose_dict[0]


def test_check_complex_file(complex_compose_file: Tuple[bool, Path]):
    config = CheckLabelConfig(glob_patterns=[str(complex_compose_file[1])], verbose=True)
    with pytest.raises(SystemExit) as pytest_wrapped_e:
        find_files(config)
    assert pytest_wrapped_e.type == SystemExit
    assert pytest_wrapped_e.value.code == int(complex_compose_file[0])
