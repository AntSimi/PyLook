from ..parser import GenericParser
from ..data.data_store import DataStore


def data_header():
    parser = GenericParser("DataHeader, give a summary of data file")
    parser.add_argument("--full", action="store_true")
    args = parser.parse_args()
    d = DataStore()
    print(d.summary(color_bash=True, full=args.full))
