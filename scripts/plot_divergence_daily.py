import xarray as xr
import matplotlib.pyplot as plt
import matplotlib.colors as colors
import cv2
from matplotlib.ticker import LogFormatter 
from matplotlib import cm

import numpy as np
import pandas as pd
import geopandas as gpd
import copy
import os
import time

import sys; sys.path.append("..")
import settings



minmax = lambda x: (x - x.min()) / (x.max() - x.min())

cat = sys.argv[1]
fn =f'{cat}.nc'
data_dir_pol = settings.data_dir_pol
sub_dirs_pol = os.listdir(data_dir_pol)
if "agg" in sub_dirs_pol:
    sub_dirs_pol.remove("agg")
path_pol = os.path.join(data_dir_pol, sub_dirs_pol[0], fn)
pol = xr.open_dataset(path_pol)
prev = pol[cat][0].data[..., None]

prev = minmax(prev) * 255
prev = prev.astype(np.uint8)

color = np.random.randint(0, 255, (100000, 3))
mask = np.zeros_like(prev)

pols = []
for i in range(len(sub_dirs_pol)):
    path_pol = os.path.join(data_dir_pol, sub_dirs_pol[i], fn)
    pol = xr.open_dataset(path_pol)
    pols.append(pol)

def divergence(f):
    return np.ufunc.reduce(np.add, np.gradient(f, 15))

data_dir_pop = settings.data_dir_pop

days = list(range(len(pols)))[::-1]
hours = list(range(24))[::-1]
for i in days:
    pol = pols[i]
    # import pdb; pdb.set_trace();
    for j in hours:
        cur = pol[cat][j].data#[..., None]

        cur = cur.astype(np.uint8)
        
        g = divergence(cur)

        # fig, ax = plt.subplots()

        pop = xr.open_dataset(os.path.join(data_dir_pop, "pop.nc"))
        pop = pop.sortby(["lat", "lon"])
        wmap = gpd.read_file(gpd.datasets.get_path("naturalearth_lowres"))
 
        pol['divergence'] = (('lat', 'lon'), g)
        fig, ax = plt.subplots()
        cmap_ = copy.copy(cm.Blues)
        cmap_.set_under((1, 1, 1, 0.0))
        ax_pop = pop['population'].fillna(0.0).plot(
            ax=ax,
            alpha=1.0,
            cmap=cmap_,
            norm=colors.PowerNorm(0.25),
            cbar_kwargs={"shrink": 0.5})

        cmap = cm.CMRmap.reversed()
        cmap.set_under("white")
        bounds = np.concatenate([
            #np.arange(pol['divergence'].min(), 0, 5),
            np.arange(1, 20, 1),
            np.arange(20, pol['divergence'].max(), 10)]) 
        norm = colors.BoundaryNorm(bounds, ncolors=len(bounds))
        ax_pol = pol['divergence'].plot(
            ax=ax,
            alpha=0.5,
            cmap=cmap,
            norm=norm,
            cbar_kwargs={"shrink": 0.5})

        wmap.plot(color="lightgrey", ax=ax, alpha=0.25)
        # xm, ym = np.meshgrid(pol['lat'], pol['lon'])
        # plt.pcolormesh(xm, ym, g)
        # plt.colorbar()
        plt.show()
        # import pdb; pdb.set_trace();

        spots = np.argwhere(g>50)
        # img = cv2.add(grad, mask)

        # cv2.imshow('frame',img)
        # k = cv2.waitKey(30) & 0xff
        # if k == 27:
        #     break

        # Now update the previous frame and previous points
        prev = cur.copy()
        print(i, j)

