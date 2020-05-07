import argparse
import logging
import sys
import re
import copy
from PyQt5 import QtWidgets
from .parser import GenericParser
from .pylook_object.base import Choices
from .pylook_object.plot_object import FigureSet, Figure, SimpleSubplot, GeoSubplot
from .pylook_object.method import KNOWN_METHOD, best_geo_method, Method, Legend, Data
from .data.data_store import DataStore


logger = logging.getLogger("pylook")


def default_populate(x, *args, **kwargs):
    x = x()
    return dict(options=x.init_value, help_options=x.help)


def subplot_populate(x, namespace, label):
    x_types = getattr(namespace, x)
    if isinstance(x_types, dict):
        if label in x_types:
            return default_populate(x_types[label])
        else:
            return default_populate(x_types[":"])
    else:
        return default_populate(x_types)


def method_populate(x, namespace, label):
    method = getattr(namespace, "method")
    if method is None:
        data = getattr(namespace, "data")
        if isinstance(data, dict):
            if label in data:
                filenames = data[label]
            else:
                filenames = data[":"]
        else:
            filenames = data
        if filenames is None:
            return
        dataset = DataStore().get(filenames[0])
        variable = getattr(namespace, "variable")
        if variable is None:
            variable = dataset.first_geo_variable()
        else:
            variable = dataset[variable[0]]
        namespace.method = best_geo_method(variable.geo_datatype)().exchange_object()
        return default_populate(namespace.method)

    else:
        if isinstance(method, dict):
            if label in method:
                return default_populate(method[label])
        else:
            return default_populate(method)


class PyLookArgumentGroup(argparse._ArgumentGroup):
    def __init__(self, container, *args, **kwargs):
        super().__init__(container, *args, **kwargs)
        self.patterns = container.patterns
        self.known_subparser = container.known_subparser

    def add_argument(self, *args, **kwargs):
        obj = kwargs.pop("obj", None)
        populate = kwargs.pop("populate_kwargs", default_populate)
        dest = self._get_optional_kwargs(*args, **kwargs)["dest"]
        if isinstance(kwargs.get("help"), dict):
            kwargs["help"] = f"Could be : {', '.join(kwargs['help'].keys())}"
        patterns = set()
        for arg in args:
            patterns = patterns.union(self.patterns.get(arg.replace("-", ""), set()))
        if patterns:
            for pattern in patterns:
                kwargs = kwargs.copy()
                if isinstance(obj, str):
                    kwargs[
                        "help"
                    ] = f"Help couldn't be give without {obj} choose, after choose wrote {args[0]}[{pattern}] help "
                kwargs["dest"] = f"{dest}.{pattern}"
                action = super().add_argument(
                    *(f"{arg}[{pattern}]" for arg in args), **kwargs
                )
                if obj is not None:
                    self.known_subparser[kwargs["dest"]] = obj, populate
        else:
            if isinstance(obj, str):
                kwargs[
                    "help"
                ] = f"Help couldn't be give without {obj} choose, after choose wrote {args[0]} help "
            super().add_argument(*args, **kwargs)
            if obj is not None:
                self.known_subparser[dest] = obj, populate


class MultiItems(dict):
    """Class to know dict contains multi specifications, not for only one"""


class DataLookParser(GenericParser):

    SUBPLOTS = dict(standard=SimpleSubplot, geo=GeoSubplot)

    def __init__(self, *args, **kwargs):
        argv = kwargs.pop("argv", sys.argv)
        if argv is None:
            argv = sys.argv
        self.patterns = dict()
        self.labels = dict()
        super().__init__(*args, **kwargs)
        self.find_pattern(argv)
        self.known_subparser = dict()
        self.add_figure_set_argument()
        self.add_figure_argument()
        self.add_subplot_argument()
        self.add_method_argument()
        group = self.add_argument_group("General")
        group.add_argument(
            "--display_tree",
            help="Display a summary of the command",
            action="store_true",
        )
        group.add_argument("--save_tree", help="Save command in json")
        group.add_argument("--gallery", help=argparse.SUPPRESS, action="store_true")

    def add_argument_group(self, *args, **kwargs):
        title = kwargs.get("title", args[0])
        if title in ["Figure set", "Figure", "Subplot", "Data/Method"]:
            group = PyLookArgumentGroup(self, *args, **kwargs)
            self._action_groups.append(group)
        else:
            group = super().add_argument_group(*args, **kwargs)
        return group

    def find_pattern(self, argv):
        """Found label in arguments
        """
        find_parent = re.compile(
            "--([a-z_]*)\[([a-zA-Z0-9_,:]*)\,parent=([a-zA-Z0-9_:,]*)]"
        )
        find_label = re.compile("--([a-z_]*)\[([a-zA-Z0-9_,:]*)\]")

        for i, item in enumerate(argv):
            if not item.startswith("--"):
                continue
            match = find_parent.match(item)
            if match:
                name, labels, parent = match.groups()
                for label in labels.split(","):
                    self.labels[label] = parent.split(",")
                item = argv[i] = f"--{name}[{labels}]"
            match = find_label.match(item)
            if match:
                name, labels = match.groups()
                if name not in self.patterns:
                    self.patterns[name] = list()
                self.patterns[name].append(labels)
        for values in self.patterns.values():
            if ":" not in values:
                values.append(":")
        logger.trace(f"Labels founds {self.labels}")
        logger.trace(f"Patterns founds {self.patterns}")

    def add_figure_set_argument(self):
        group = self.add_argument_group(
            "Figure set", description="Options for a whole set of figure"
        )
        group.add_argument("--figure_set_options", nargs="*", obj=FigureSet)

    def add_figure_argument(self):
        group = self.add_argument_group("Figure", description="Options for figure")
        group.add_argument("--figure_options", nargs="*", obj=Figure)

    @classmethod
    def subplot_class(cls, name):
        return cls.SUBPLOTS[name]

    @classmethod
    def subplot_obj_parser(cls, namespace, label):
        return getattr(namespace, "subplot_type")[label]

    def add_subplot_argument(self):
        group = self.add_argument_group("Subplot", description="Options for subplot")
        group.add_argument(
            "--subplot", default="geo", help=self.SUBPLOTS, type=self.subplot_class,
        )
        group.add_argument(
            "--subplot_options",
            nargs="*",
            obj="subplot",
            populate_kwargs=subplot_populate,
        )

    @classmethod
    def method_object(cls, name):
        found_keys = [k for k in KNOWN_METHOD.keys() if k.startswith(name)]
        if len(found_keys) == 1:
            return KNOWN_METHOD[found_keys[0]].exchange_object()
        elif len(found_keys) > 1:
            raise Exception(f"Method '{name}' could be '{', '.join(found_keys)}'")
        raise Exception(f"Method '{name}' are not declare")

    @classmethod
    def legend_object(cls, name):
        return "colorbar"

    def add_method_argument(self):
        group = self.add_argument_group(
            "Data/Method", description="Options to display data"
        )
        group.add_argument("--variable", "--var", nargs="*")
        group.add_argument("--data_index", nargs="*")
        group.add_argument("--data", nargs="*")
        group.add_argument("--method", type=self.method_object, help=KNOWN_METHOD)
        # group.add_argument("--legends", nargs="*", type=self.legend_object)
        group.add_argument(
            "--method_options", nargs="*", obj="", populate_kwargs=method_populate,
        )
        # group.add_argument(
        #     "--legend_options", nargs="*", obj="legends", populate_kwargs=None
        # )

    def data_check(self, namespace):
        if namespace.data is None and namespace.filenames:
            namespace.data = namespace.filenames
        elif isinstance(namespace.data, MultiItems) and ":" not in namespace.data:
            if namespace.filenames:
                namespace.data[":"] = namespace.filenames
            else:
                namespace.data[":"] = None

    def parse_args(self, *args, **kwargs):
        args = super().parse_args(*args, **kwargs)
        self.merge_target(args)
        self.data_check(args)
        for name, (obj, populate_kwargs) in self.known_subparser.items():
            sub_args = getattr(args, name)
            sub_args = [
                f"--{item}" for item in (tuple() if sub_args is None else sub_args)
            ]
            label = name.split(".")[1] if len(name.split(".")) > 1 else None
            logger.trace(f"Software will parse {name} keywords")
            kwargs_parser = populate_kwargs(obj, args, label)
            if kwargs_parser is None:
                pass
            else:
                setattr(args, name, SubParser(**kwargs_parser).parse_args(sub_args))
            logger.trace(f"{name} = {getattr(args,name)}")
        self.merge_options(args)
        return args

    def merge_target(self, args):
        for key, pattern in self.patterns.items():
            if key not in ("method", "subplot", "data"):
                continue
            options = MultiItems()
            for label in pattern:
                if "," in label:
                    v = getattr(args, f"{key}.{label}", None)
                    for label_ in label.split(","):
                        options[label_] = v
            for label in self.get_labels(pattern):
                d = getattr(args, f"{key}.{label}", None)
                if d is not None:
                    options[label] = d
            setattr(args, key, options)

    def merge_options(self, args):
        for key, pattern in self.patterns.items():
            if key in ("method", "subplot", "data"):
                continue
            options = MultiItems()
            for label in self.get_labels(pattern):
                logger.trace(f"{key}.{label} will be merge")
                default = getattr(args, f"{key}.:", None)
                d = getattr(args, f"{key}.{label}", copy.deepcopy(default))
                for k in pattern:
                    if "," in k and label in k:
                        self.update_if_default(d, getattr(args, f"{key}.{k}", None))
                self.update_if_default(d, default)
                options[label] = d
            setattr(args, key, options)

    @classmethod
    def update_if_default(cls, d_to_update, d):
        if d is None:
            return
        for k, v in d_to_update.items():
            if k not in d:
                continue
            if isinstance(v, dict):
                cls.update_if_default(v, d[k])
            elif isinstance(v, Default):
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
        self.add_argument("--stream_help", help=argparse.SUPPRESS, action="store_true")
        for k, v in opts.items():
            if isinstance(v, dict):
                self.add_argument(
                    f"--{k}", help=f"For more help on this item write {k}=help"
                )
                self.sub_parser[k] = dict(
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
        if args.stream_help:
            self.print_help()
        for name, parser_kwargs in self.sub_parser.items():
            parser = self.__class__(**parser_kwargs)
            sub_args = getattr(args, name)
            if sub_args is None:
                setattr(args, name, parser.parse_args(list()))
            else:
                if sub_args.startswith("[") and sub_args.endswith("]"):
                    sub_args = sub_args[1:-1]
                if "[" not in sub_args:
                    sub_args = [f"--{item}" for item in sub_args.split(",")]
                else:
                    sub_args = [
                        f"--{item}" for item in split_(sub_args, ",") if len(item)
                    ]
                setattr(args, name, parser.parse_args(sub_args))
        args = vars(args)
        args.pop("stream_help")
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


def build_items(cls, options):
    if options is None:
        return dict()
    keys = list()
    if isinstance(options, MultiItems):
        keys.extend(options.keys())
    if isinstance(cls, MultiItems):
        keys.extend(cls.keys())
    keys = set(keys)
    if len(keys):
        items = dict()
        for key in keys:
            if key == ":":
                continue
            class_ = cls.get(key, cls[":"]) if isinstance(cls, MultiItems) else cls
            options_ = (
                options.get(key, dict()) if isinstance(options, MultiItems) else options
            )
            items[key] = class_.with_options(options_)
        return items
    return {":": cls.with_options(options)}


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


def get_labels(items):
    labels_ = list()
    if items is None:
        return [":"]
    if isinstance(items, dict):
        labels_.extend(items.keys())
    else:
        labels_.append(":")
    return labels_


def merge_labels(methods, datas, variables):
    labels = list()
    labels.extend(get_labels(methods))
    labels.extend(get_labels(datas))
    labels.extend(get_labels(variables))
    labels = set(labels)
    if ":" in labels and len(labels) > 1:
        labels.remove(":")
    return set(labels)


def get_item(label, items):
    if not isinstance(items, dict):
        return items
    if label not in items:
        return items[":"]
    return items[label]


def add_data(methods, datas, variables):
    datastore = DataStore()
    labels = merge_labels(methods, datas, variables)
    for label in labels:
        methods[label] = get_item(label, methods).copy()
        m = methods[label].renderer_class
        d = Data()
        d.data.update(m.data_structure())
        datas_ = get_item(label, datas)
        for data in datas_:
            dataset = datastore.get(data)
            variable = dataset.first_geo_variable()
            d.data["x"].append((variable.geo_coordinates["x"], dataset.key))
            d.data["y"].append((variable.geo_coordinates["y"], dataset.key))
            d.data["z"].append((variable.name, dataset.key))
        methods[label].append(d)
    if len(labels) > 1 and ":" in methods:
        methods.pop(":")


def data_look(args=None):
    parser = DataLookParser(
        "DataLook allow to create pylook figures with sh command", argv=args
    )
    args = parser.parse_args(args)
    all_fs = build_items(FigureSet, args.figure_set_options)
    all_f = build_items(Figure, args.figure_options)
    all_s = build_items(args.subplot, args.subplot_options)
    all_m = build_items(args.method, args.method_options)
    add_data(all_m, args.data, args.variable)
    distribute_child(all_m, all_s, parser.labels)
    distribute_child(all_s, all_f, parser.labels)
    distribute_child(all_f, all_fs, parser.labels)

    if args.display_tree:
        level = logger.getEffectiveLevel()
        simplify = False if level <= logging.DEBUG else True
        compress = False if level <= logger.TRACE else True
        for fs in all_fs.values():
            print(fs.summary(compress=compress, only_modify=simplify))
        return

    if args.save_tree is not None:
        all_fs["noname"].save(args.save_tree)
        return

    if args.gallery:
        for fs in all_fs.values():
            fs.build(pyqt=False)
        return

    app = QtWidgets.QApplication(list())
    for fs in all_fs.values():
        fs.build()
    app.exec_()
