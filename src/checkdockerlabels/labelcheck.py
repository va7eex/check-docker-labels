import re
from dataclasses import dataclass, field
from glob import glob
from typing import Any, Dict, Iterator, List, Set

import yaml


@dataclass
class ValidPattern:
    pattern: str = r"^[\"\']?[^\.][a-z]+(?:\.[a-z]+)*(?:=.+)?[\"\']?$"
    key_is_uppercase: bool = False
    ignore_prefix: List[str] = field(default_factory=list)


@dataclass
class CheckLabelConfig:
    glob_patterns: List[str] = field(default_factory=list)
    valid_pattern: ValidPattern = field(default_factory=ValidPattern)
    verbose: bool = True


@dataclass
class ServiceReport:
    service: str
    labels: List[str]

    def _get_filtered_labels(self, valid_pattern: ValidPattern) -> Iterator[str]:
        filter_labels = lambda _label: not any([_label.startswith(ignore) for ignore in valid_pattern.ignore_prefix])
        return filter(filter_labels, self.labels)

    def check_for_invalid_labels(self, valid_pattern: ValidPattern) -> List[str]:
        return [
            label
            for label in self._get_filtered_labels(valid_pattern=valid_pattern)
            if not re.match(valid_pattern.pattern, label)
        ]


def check_labels(file_name: str, yamlfile: Dict[str, Any], valid_pattern: ValidPattern, verbose_output: bool) -> bool:
    services: List[ServiceReport] = []
    for service, keys in yamlfile.get("services", {}).items():
        srv = ServiceReport(service, keys.get("labels", []))
        services.append(srv)

    invalid_labels: Dict[str, List[str]] = {
        srv.service: srv.check_for_invalid_labels(valid_pattern=valid_pattern) for srv in services
    }
    filter_for_invalid_Services = lambda kv: len(kv[1]) > 0
    srv_with_invalid_labels = [item for item in filter(filter_for_invalid_Services, invalid_labels.items())]

    if len(srv_with_invalid_labels) > 0:
        if verbose_output:
            print(f"The following invalid service labels were discovered in {file_name}:")
            for i, (key, items) in enumerate(srv_with_invalid_labels):
                print(f"{' ' * 2} {i:03}: {key}:")
                for item in items:
                    print(f"{' ' * 4} - {item}")
        return False
    return True


def find_files(
    config: CheckLabelConfig = CheckLabelConfig(glob_patterns=["*compose.y?ml", "**/*compose.*y?ml"]),
):
    error_present: bool = False
    fileset: Set[str] = set()
    for _glob in [glob(globpat) for globpat in config.glob_patterns]:
        for _file in _glob:
            fileset.add(_file)
    files: List[str] = list(fileset)
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
            result = check_labels(
                file_name=file,
                yamlfile=compose,
                valid_pattern=config.valid_pattern,
                verbose_output=config.verbose,
            )
            if not result:
                error_present = True

    if error_present:
        exit(1)
    exit(0)
