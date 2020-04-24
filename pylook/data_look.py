import argparse
import logging
from .parser import GenericParser
from .exchange_object import FigureSet, Figure, GeoSubplot, Choices


class DataLookParser(GenericParser):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.known_subparser = dict()
        self.add_figure_set_argument()
        self.add_figure_argument()
        self.add_subplot_argument()
        # self.add_method_argument()
        # self.add_data_argument()
        # self.add_legend_argument()

    def add_figure_set_argument(self):
        group = self.add_argument_group(
            "Figure set", description="Options for a whole set of figure"
        )
        opt = group.add_argument("--figure_set_options", nargs="*")
        obj = FigureSet()
        self.known_subparser[opt.dest] = SubParser(
            options=obj.init_value, help_options=obj.help
        )

    def add_figure_argument(self):
        group = self.add_argument_group("Figure", description="Options for figure")
        opt = group.add_argument("--figure_options", nargs="*")
        obj = Figure()
        self.known_subparser[opt.dest] = SubParser(
            options=obj.init_value, help_options=obj.help
        )

    def add_subplot_argument(self):
        group = self.add_argument_group("Subplot", description="Options for subplot")
        opt = group.add_argument("--subplot_options", nargs="*")
        obj = GeoSubplot()
        self.known_subparser[opt.dest] = SubParser(
            options=obj.init_value, help_options=obj.help
        )

    def parse_args(self, *args, **kwargs):
        args = super().parse_args(*args, **kwargs)
        for name, parser in self.known_subparser.items():
            sub_args = getattr(args, name)
            sub_args = [
                f"--{item}" for item in (tuple() if sub_args is None else sub_args)
            ]
            setattr(args, name, parser.parse_args(sub_args))
        return args


class SubParserFormatter(argparse.HelpFormatter):
    def __init__(self, *args, **kwargs):
        kwargs["width"] = 120
        super().__init__(*args, **kwargs)

    def _split_lines(self, text, width):
        import textwrap

        lines = textwrap.wrap(text, width)
        for pattern in ["Default :", "Examples of value :"]:
            new_lines = list()
            for line in lines:
                res = line.split(pattern)
                if len(res) == 2:
                    if len(res[0]):
                        new_lines.append(res[0])
                    new_lines.append(pattern + res[1])
                else:
                    new_lines.append(line)
            lines = new_lines.copy()
        return new_lines


class SubParser(argparse.ArgumentParser):
    def __init__(self, *args, **kwargs):
        opts = kwargs.pop("options")
        help_opts = kwargs.pop("help_options")
        kwargs["formatter_class"] = SubParserFormatter
        self.sub_parser = dict()
        super().__init__(*args, **kwargs)
        for k, v in opts.items():
            if isinstance(v, dict):
                self.add_argument(f"--{k}",)
                self.sub_parser[k] = self.__class__(options=v, help_options=help_opts.get(k, dict()))
            else:
                if isinstance(v, Choices):
                    v_ = v.default
                    choices = f"Examples of value : {v.summary(shorten=True)}"

                else:
                    v_ = v
                    choices = ""
                doc = help_opts.get(k, dict()).get("doc", "")
                help_ = f"{doc}Default : {v_}{choices}"
                self.add_argument(f"--{k}", default=v_, help=help_)

    def parse_args(self, *args, **kwargs):
        args = super().parse_args(*args, **kwargs)
        for name, parser in self.sub_parser.items():
            sub_args = getattr(args, name)
            # sub_args = [
                # f"--{item}" for item in (tuple() if sub_args is None else sub_args)
            # ]
            print(sub_args)
            print(type(sub_args))
            if sub_args is None:
                setattr(args, name, parser.parse_args(list()))
            else:
                print(parser.parse_args(sub_args))
                # setattr(args, name, parser.parse_args(sub_args))
        return args


def data_look(args=None):
    parser = DataLookParser("DataLook allow to create pylook figures with sh command")
    args = parser.parse_args(args)
    print(args)
