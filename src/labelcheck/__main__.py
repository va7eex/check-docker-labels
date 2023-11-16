from optparse import OptionParser

from .labelcheck import CheckLabelConfig, find_files


def app():
    defaultConfig = CheckLabelConfig(glob_patterns=["*compose.*y*ml", "**/*compose.*y*ml"])
    optparse = OptionParser()
    optparse.add_option(
        "-r",
        "--regex",
        action="store",
        dest="regex",
        default=defaultConfig.valid_pattern,
        help=f"Regex pattern to check labels against, default: {defaultConfig.valid_pattern}",
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

    config = CheckLabelConfig(glob_patterns=_opts.files, valid_pattern=_opts.regex, verbose=_opts.verbose)

    find_files(config=config)


if __name__ == "__main__":
    app()
