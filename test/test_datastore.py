from pylook.data.data_store import DataStore
from glob import glob

d = DataStore()
print(d.add_files(glob("../py-eddy-tracker/share/*.nc")))
print(d.summary(color_bash=True))
