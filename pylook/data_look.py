import argparse
import logging
import sys
import re
from .parser import GenericParser
from .exchange_object import FigureSet, Figure, GeoSubplot, Choices


logger = logging.getLogger("pylook")


class PyLookArgumentGroup(argparse._ArgumentGroup):
    def __init__(self, container, *args, **kwargs):
        super().__init__(container, *args, **kwargs)
        self.patterns = container.patterns
        self.known_subparser = container.known_subparser

    def add_argument(self, *args, **kwargs):
        obj = kwargs.pop("obj", None)
        dest = self._get_optional_kwargs(*args, **kwargs)["dest"]
        patterns = self.patterns.get(dest, None)
        if patterns is not None:
            for pattern in patterns:
                kwargs = kwargs.copy()
                kwargs["dest"] = f"{dest}.{pattern}"
                super().add_argument(*(f"{args}[{pattern}]" for args in args), **kwargs)
                if obj is not None:
                    self.known_subparser[kwargs["dest"]] = SubParser(
                        options=obj.init_value, help_options=obj.help
                    )
        else:
            super().add_argument(*args, **kwargs)
            if obj is not None:
                self.known_subparser[dest] = SubParser(
                    options=obj.init_value, help_options=obj.help
                )


class MultiItems(dict):
    pass


class DataLookParser(GenericParser):
    def __init__(self, *args, **kwargs):
        argv = kwargs.pop("argv", sys.argv)
        if argv is None:
            argv = sys.argv
        self.patterns = dict()
        self.labels = dict()
        self.find_pattern(argv)
        super().__init__(*args, **kwargs)
        self.known_subparser = dict()
        self.add_figure_set_argument()
        self.add_figure_argument()
        self.add_subplot_argument()
        group = self.add_argument_group("General")
        group.add_argument(
            "--display_tree",
            help="Display a summary of the command",
            action="store_true",
        )

    def add_argument_group(self, *args, **kwargs):
        title = kwargs.get("title", args[0])
        if title in ["Figure set", "Figure", "Subplot"]:
            group = PyLookArgumentGroup(self, *args, **kwargs)
            self._action_groups.append(group)
        else:
            group = super().add_argument_group(*args, **kwargs)
        return group

    def find_pattern(self, argv):
        find_parent = re.compile(
            "--([a-z_]*)\[([a-zA-Z0-9_,:]*)\,parent=([a-zA-Z0-9_:,]*)]"
        )
        find_label = re.compile("--([a-z_]*)\[([a-zA-Z0-9_,:]*)\]")

        for i, item in enumerate(argv):
            if not item.startswith("--"):
                continue
            match = find_parent.match(item)
            if match:
                _, labels, parent = match.groups()
                print("parent", item, labels, parent)
                for label in labels.split(","):
                    self.labels[label] = parent.split(",")
                item = argv[i] = f"--{_}[{labels}]"
            match = find_label.match(item)
            if match:
                name, label = match.groups()
                print("label", item, name, label)
                if name not in self.patterns:
                    self.patterns[name] = list()
                self.patterns[name].append(label)

    def add_figure_set_argument(self):
        group = self.add_argument_group(
            "Figure set", description="Options for a whole set of figure"
        )
        group.add_argument("--figure_set_options", nargs="*", obj=FigureSet())

    def add_figure_argument(self):
        group = self.add_argument_group("Figure", description="Options for figure")
        group.add_argument("--figure_options", nargs="*", obj=Figure())

    def add_subplot_argument(self):
        group = self.add_argument_group("Subplot", description="Options for subplot")
        group.add_argument("--subplot_options", nargs="*", obj=GeoSubplot())

    def parse_args(self, *args, **kwargs):
        args = super().parse_args(*args, **kwargs)
        for name, parser in self.known_subparser.items():
            sub_args = getattr(args, name)
            sub_args = [
                f"--{item}" for item in (tuple() if sub_args is None else sub_args)
            ]
            setattr(args, name, vars(parser.parse_args(sub_args)))
        self.merge_options(args)
        return args

    def merge_options(self, args):
        for key, pattern in self.patterns.items():
            options = MultiItems()
            for label in self.get_labels(pattern):
                d = getattr(args, f"{key}.{label}", None)
                for k in pattern:
                    if "," in k and label in k:
                        self.update_if_default(d, getattr(args, f"{key}.{k}", None))
                self.update_if_default(d, getattr(args, f"{key}.:", None))
                options[label] = d
            setattr(args, key, options)

    @staticmethod
    def update_if_default(d_to_update, d):
        if d is None:
            return
        for k in d_to_update:
            if isinstance(d_to_update[k], Default):
                d_to_update[k] = d[k]

    @staticmethod
    def get_labels(labels):
        labels_ = list()
        for label in labels:
            labels_.extend(label.split(","))
        return set(labels_)


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


class Default(str):
    pass


class SubParser(argparse.ArgumentParser):
    def __init__(self, *args, **kwargs):
        opts = kwargs.pop("options")
        help_opts = kwargs.pop("help_options")
        kwargs["formatter_class"] = SubParserFormatter
        self.sub_parser = dict()
        super().__init__(*args, **kwargs)
        for k, v in opts.items():
            if isinstance(v, dict):
                self.add_argument(
                    f"--{k}", help=f"For more help on this item write {k}=help"
                )
                self.sub_parser[k] = self.__class__(
                    options=v, help_options=help_opts.get(k, dict())
                )
            else:
                if isinstance(v, Choices):
                    v_ = v.default
                    choices = f"Examples of value : {v.summary(shorten=True)}"

                else:
                    v_ = v
                    choices = ""
                doc = help_opts.get(k, dict()).get("doc", "")
                help_ = f"{doc}Default : {v_}{choices}"
                self.add_argument(f"--{k}", default=Default(v_), help=help_)

    def parse_args(self, *args, **kwargs):
        args = super().parse_args(*args, **kwargs)
        for name, parser in self.sub_parser.items():
            sub_args = getattr(args, name)
            if sub_args is None:
                setattr(args, name, vars(parser.parse_args(list())))
            else:
                if sub_args.startswith("[") and sub_args.endswith("]"):
                    sub_args = sub_args[1:-1]
                if "[" not in sub_args:
                    sub_args = [f"--{item}" for item in sub_args.split(",")]
                else:
                    sub_args = [
                        f"--{item}" for item in split_(sub_args, ",") if len(item)
                    ]
                setattr(args, name, vars(parser.parse_args(sub_args)))
        return args


def split_(args, pattern):
    """split only if pattern are not between [ and ]
    """
    count = 0
    elts = list()
    i_previous = 0
    for i, c in enumerate(args):
        if c == "[":
            count += 1
        elif c == "]":
            count -= 1
        if count == 0 and c == pattern:
            elts.append(args[i_previous:i])
            i_previous = i + 1
    elts.append(args[i_previous:])
    return elts


def build_items_with_options(func, options):
    if isinstance(options, MultiItems):
        return {name: func(args_) for name, args_ in options.items() if name != ":"}
    return dict(noname=func(options))


def distribute_child(childs, parents, labels):
    all_parent_names = list(parents.keys())
    all_parent_names.sort()
    default_parent = [all_parent_names[0]]
    for name, child in childs.items():
        parent_names = labels.get(name, default_parent)
        if ":" in parent_names:
            for parent_name in all_parent_names:
                parents[parent_name].append(child)
        else:
            for parent_name in parent_names:
                parents[parent_name].append(child)


def data_look(args=None):
    parser = DataLookParser(
        "DataLook allow to create pylook figures with sh command", argv=args
    )
    args = parser.parse_args(args)
    all_fs = build_items_with_options(FigureSet.with_options, args.figure_set_options)
    all_f = build_items_with_options(Figure.with_options, args.figure_options)
    all_s = build_items_with_options(GeoSubplot.with_options, args.subplot_options)
    distribute_child(all_s, all_f, parser.labels)
    distribute_child(all_f, all_fs, parser.labels)

    if args.display_tree:
        for fs in all_fs.values():
            print(
                fs.summary(
                    compress=False
                    if logger.getEffectiveLevel() <= logging.DEBUG
                    else True
                )
            )
        return
    for fs in all_fs.values():
        fs.build()
