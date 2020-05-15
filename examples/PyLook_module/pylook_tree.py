"""
Display tree
============
"""
from pylook.pylook_object.plot_object import FigureSet, Figure, GeoSubplot

s = FigureSet()
f = Figure()
s.appends(f)
g = GeoSubplot()
f.appends(g)
s