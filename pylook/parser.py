import argparse
import logging
from .logger import start_logger
from .data.data_store import DataStore

logger = logging.getLogger("pylook")


class GenericParser(argparse.ArgumentParser):
    def __init__(self, *args, **kwargs):
        self.groups = dict()
        super().__init__(*args, **kwargs)
        self.logger = start_logger()
        self.standard_argument()

    def standard_argument(self):
        self.add_argument(
            "-v",
            "--verbose",
            default="WARNING",
            choices=("TRACE", "DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"),
        )
        group = self.add_argument_group("Data")
        group.add_argument("filenames", nargs="*")
        group.add_argument("--demo_datasets", action="store_true")

    def add_argument_group(self, group_name, *args, **kwargs):
        group = super().add_argument_group(group_name, *args, **kwargs)
        self.groups[group_name] = group
        return group

    def parse_args(self, *args, **kwargs):
        args = super().parse_args(*args, **kwargs)
        self.logger.setLevel(logging.getLevelName(args.verbose.upper()))
        d = DataStore()
        d.add_paths(args.filenames)
        if args.demo_datasets:
            d.add_demo_datasets()
        return args
