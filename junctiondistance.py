#!/usr/bin/env python
# coding: utf-8

# In[1]:


# Parameters
pixel_width = 12
data_dir = "data"
output_dir = "output"
n_simulations = 1000

# Code
import os
from glob import iglob
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy import stats
from shapely.geometry import Point, Polygon
from random import random
get_ipython().run_line_magic('matplotlib', 'inline')

# make output directory if it doesn't exist
os.makedirs(output_dir, exist_ok=True)

# compile summary data for output to table
summarydata = []

# iterate through each cell file
for filename in iglob(os.path.join(data_dir, "*.txt")):
    # derive output file names from input filename
    basename = os.path.basename(filename)[:-4]
    # read coordinates
    df = pd.read_csv(filename, sep="\t", header=None)
    df.columns = ["x", "y"]
    df = df * pixel_width
    # create Shapely objects from coordinate data
    focus = Point(df.loc[0].values)
    cell = Polygon(df.loc[1:].values.tolist())
    # plot the shape of the cell with the focus point
    fig, ax = plt.subplots(figsize=[4,4])
    ax.plot(*cell.exterior.xy, color="darkblue")
    ax.scatter(*focus.xy, color="red")
    ax.set_aspect('equal', 'datalim')
    fig.savefig(os.path.join(output_dir, basename + "_shape.pdf"))
    # measure distance from focus to nearest edge
    distance = cell.exterior.distance(focus)
    # run simulations on random points
    simulated_distances = []
    while len(simulated_distances) < n_simulations:
        (minx, miny, maxx, maxy) = cell.bounds
        random_x = (maxx - minx) * random() + minx
        random_y = (maxy - miny) * random() + miny
        random_point = Point(random_x, random_y)
        if random_point.within(cell):
            simulated_distances.append(cell.exterior.distance(random_point))
            ax.scatter(*random_point.xy, color="grey", s=2)
    fig.savefig(os.path.join(output_dir, basename + "_shape_simulations.pdf")) # re-plot the cell with simulation points in grey
    plt.close(fig)
    
    # plot histogram of distances
    fig, ax = plt.subplots(figsize=[8,6])
    ax.hist(simulated_distances, bins=int(n_simulations/20), range=(0, max(simulated_distances)), color="grey")
    ax.axvline(distance, color="red")
    ax.set_xlabel("Distance to nearest junction")
    ax.set_ylabel("Frequency")
    fig.savefig(os.path.join(output_dir, basename + "_distances.pdf"))
    percentile = stats.percentileofscore(simulated_distances, distance) / 100
    summary = {"Cell name": basename, "Distance from Point to Nearest Junction": distance, "Percentile (0-1)": percentile}
    summarydata.append(pd.Series(summary))
summarydata = pd.DataFrame(summarydata)
summarydata.to_csv(os.path.join(output_dir, "summary.csv"))


# In[ ]:





# In[ ]:




