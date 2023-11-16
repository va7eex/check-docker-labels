import re
from dataclasses import dataclass, field
from glob import glob
from typing import Any

import yaml


@dataclass
class CheckLabelConfig:
    glob_patterns: list[str] = field(default_factory=list)
    valid_pattern: str = r"^[\"\']?[^\.][a-z]+(?:\.[a-z]+)*=.+[\"\']?$"
    verbose: bool = False


def check_labels(yamlfile: dict[str, Any], valid_pattern: str, verbose_output: bool):
    invalid_keys: dict[str, list[str]] = {}
    for service, keys in yamlfile.get("services", {}).items():
        for label in keys.get("labels", []):
            if not re.match(valid_pattern, label):
                if service not in invalid_keys:
                    invalid_keys[service] = []
                invalid_keys[service].append(label)
    if len(invalid_keys) != 0:
        if verbose_output:
            print("The following invalid service labels were discovered:")
            for key, items in invalid_keys.items():
                print(f"\t{key}:")
                for item in items:
                    print(f"\t\t{item}")
        exit(1)
    exit(0)


def find_files(
    config: CheckLabelConfig = CheckLabelConfig(glob_patterns=["*compose.y?ml", "**/*compose.*y?ml"]),
):
    fileset: set[str] = set()
    for _glob in [glob(globpat) for globpat in config.glob_patterns]:
        for _file in _glob:
            fileset.add(_file)
    files: list[str] = list(fileset)
    files.sort()
    if len(files) == 0:
        raise FileNotFoundError("No files matching pattern found!")

    if config.verbose:
        print("Discovered files:")
        for file in files:
            print("-", file)
    for file in files:
        with open(file, mode="r", encoding="utf-8") as f:
            compose = yaml.safe_load(f)
            check_labels(
                yamlfile=compose,
                valid_pattern=config.valid_pattern,
                verbose_output=config.verbose,
            )
