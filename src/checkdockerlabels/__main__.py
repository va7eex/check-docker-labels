from optparse import OptionParser

from .labelcheck import CheckLabelConfig, ValidPattern, find_files


def app():
    defaultConfig = CheckLabelConfig(glob_patterns=["*compose.*y*ml", "**/*compose.*y*ml"])
    optparse = OptionParser()
    optparse.add_option(
        "-r",
        "--regex",
        action="store",
        dest="regex",
        default=defaultConfig.valid_pattern.pattern,
        help=f"Regex pattern to check labels against, default: {defaultConfig.valid_pattern.pattern}",
    )
    optparse.add_option(
        "-u",
        "--uppercase",
        action="store_true",
        dest="uppercase",
        default=defaultConfig.valid_pattern.key_is_uppercase,
        help=f"Check if keys should be uppercase, default {defaultConfig.valid_pattern.key_is_uppercase}",
    )
    optparse.add_option(
        "-i",
        "--ignore-prefix",
        action="append",
        dest="ignore_prefix",
        default=defaultConfig.valid_pattern.ignore_prefix,
        help=f"Ignore keys that start with the following, multiple prefixes can be specifid by repeating '-i' (ex: {' '.join([f'-i {_pat}' for _pat in defaultConfig.valid_pattern.ignore_prefix])}), default: {defaultConfig.valid_pattern.ignore_prefix}",
    )
    optparse.add_option(
        "-f",
        "--file",
        action="append",
        dest="files",
        default=defaultConfig.glob_patterns,
        help=f"Filepath or glob pattern to use to detect docker-compose files, multiple paths/patterns can be specifid by repeating '-f' (ex: {' '.join([f'-f {_pat}' for _pat in defaultConfig.glob_patterns])}), default: {defaultConfig.glob_patterns}",
    )
    optparse.add_option(
        "-q",
        "--quiet",
        action="store_false",
        dest="verbose",
        default=defaultConfig.verbose,
        help="Suppress output to console, default: False",
    )
    optparse.add_option(
        "-v", "--verbose", action="store_true", dest="verbose", help="Display output on console, default: True"
    )
    _opts, _ = optparse.parse_args()

    valid_pattern = ValidPattern(
        pattern=_opts.regex, key_is_uppercase=_opts.uppercase, ignore_prefix=_opts.ignore_prefix
    )
    config = CheckLabelConfig(glob_patterns=_opts.files, valid_pattern=valid_pattern, verbose=_opts.verbose)

    find_files(config=config)


if __name__ == "__main__":
    app()
