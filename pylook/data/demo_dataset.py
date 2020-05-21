from .data_store import MemoryDataset, MemoryVariable
import numpy


def fake_sat(time_step=10, altitude=1340, inclination=66, longitude0=0):
    r = altitude + 6371
    mu = 398600.4418
    v = (mu / r) ** 0.5
    p = 2 * numpy.pi * r / v
    t = numpy.arange(0, 86400 * 2, time_step, dtype="f4")
    i = numpy.radians(inclination)
    lat = numpy.degrees(numpy.arcsin(numpy.sin(i) * numpy.sin(2 * numpy.pi * t / p)))
    lon = t / 35
    lon += longitude0
    lon %= 360
    return MemoryDataset(
        "fake_sat",
        MemoryVariable("time", t, ("t",)),
        MemoryVariable("longitude", lon, ("t",)),
        MemoryVariable("latitude", lat, ("t",)),
    )


def grid():
    N = 0.125
    x, y = numpy.arange(0, 360, N), numpy.arange(-80, 80, N)
    x_, y_ = numpy.meshgrid(x, y)
    z = numpy.sin(4 * numpy.radians(x_)) * numpy.cos(4 * numpy.radians(y_))
    return MemoryDataset(
        "2D_wave_global",
        MemoryVariable("lon", x.astype('f4'), ("longitude",)),
        MemoryVariable("lat", y.astype('f4'), ("latitude",)),
        MemoryVariable("z", z.astype('f4'), ("latitude", "longitude")),
    )
