from pylook.exchange_object import (
    FigureSet,
    Figure,
    GeoSubplot,
    SimpleSubplot,
    Method,
    Data,
    Legend,
)


s = FigureSet()

f1 = Figure()
f2 = Figure()
s.appends(f1, f2)
s1 = GeoSubplot()
# s2 = GeoSubplot()
s4 = SimpleSubplot()
# s5 = GeoSubplot()
f1.appends(s1)
# f1.appends(s1, s2)
f2.appends(s4)
m1, m2, m3 = Method(), Method(), Method()
s1.appends(m1, m3)
s4.appends(m2)
d1 = Data()
d2 = Data()
l1 = Legend()
m1.appends(d1, l1)
m3.appends(d2)
print(s.summary())
print(s.summary(compress=True))
