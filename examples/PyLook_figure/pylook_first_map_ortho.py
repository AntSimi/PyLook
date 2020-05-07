"""
Orthographic map
================

"""
from matplotlib import pyplot as plt
import pylook

fig = plt.figure()
ax = fig.add_subplot(111, projection='ortho')
ax.grid(True)
