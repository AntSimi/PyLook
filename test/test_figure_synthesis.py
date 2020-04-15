from pylook.exchange_object import FigureSet, Figure, Subplot

s = FigureSet()
f1 = Figure()
f2 = Figure()
s.appends(f1, f2)
s1 = Subplot()
s2 = Subplot()
s3 = Subplot()
s4 = Subplot()
s5 = Subplot()
f1.appends(s1, s2, s3)
f2.appends(s4, s5)
print(s.summary())
