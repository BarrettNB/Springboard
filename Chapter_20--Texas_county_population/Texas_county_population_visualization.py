# -*- coding: utf-8 -*-
"""
A data visualization tool for Texas counties' population growth, 2010-2019.

Source: https://www.census.gov/data/datasets/time-series/demo/popest/2010s-counties-total.html

Created on Tue Jul 20 11:23:48 2021

@author: Barrett
"""

import os
import geopandas as gpd
# import descartes
# from descartes.patch import PolygonPatch
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

#%% DATA COLLECTION

# Load the data
os.chdir(r'D:\Springboard_DataSci\Assignments' \
         + r'\Chapter_20--Texas_county_population\Data')
population_data = pd.read_excel('Texas county populations.xlsx')
shape_data = gpd.read_file('cb_2019_us_county_5m.shp')

#%% DATA CLEANING

# Clean up the Geographic Area (county) field
population_data['Geographic Area'] = population_data['Geographic Area']\
    .str.replace('.', '')\
    .str.replace(' County, Texas', '')
    
# Verify that the state population = sum of the county populations
print('Max population deviation:',
      (population_data.iloc[1:255, 1:].sum(axis=0)\
          - population_data.iloc[0, 1:]).max()) # Zero. All is well.
    
# Keep only the populations of all 254 Texas counties.
# Set the county names as the row index.
population_data = population_data.iloc[1:255]\
    .rename(columns = {'Geographic Area':'County'})
    
'''In July 2019, the nmost populous counties in Texas were Harris, Dallas,
Tarrant, Bexar, and Travis. These respectively have the cities of Houston,
Dallas, Fort Worth, San Antonio, and Austin.'''

# shape_data contains all US counties. Keep just Texas'.
shape_data = shape_data[shape_data.STATEFP == '48']
n_counties = shape_data.shape[0]
    
#%% EXPLORATORY DATA ANALYSIS

growth_columns = [2010, 2019]
GROWTH = 'Growth'
PCT_GROWTH = 'Pct Growth'

population_data[GROWTH] = population_data[growth_columns[1]]\
    - population_data[growth_columns[0]]
population_data[PCT_GROWTH] = population_data[GROWTH]\
    /population_data[growth_columns[1]] * 100
    
'''Harris County has by far the most growth, followed by Tarrant, Bexar,
Dallas, and Collin Counties. Collin County is just north of Dallas County.

Let's rank the counties in descending order by total growth, 2010-2019.'''
population_growth = population_data[['County', 'Growth']]\
    .sort_values('Growth', ascending=False, ignore_index=True)
population_growth['Cumulative'] = population_growth['Growth'].cumsum()

# Save these for later.
total_growth = population_growth['Cumulative'].iloc[-1]
max_growth = int(population_growth['Growth'].iloc[0])
#min_growth = int(population_growth['Growth'].iloc[-1])
    
'''Let's see how much the first few counties contributed to Texas' growth.'''
top_counties = [6, 10]
for i, n in enumerate(top_counties):
    fig, ax = plt.subplots()
    ax.set_xlabel('County')
    ax.set_ylabel('Growth')
    ax.plot(population_growth.index, population_growth['Cumulative'])
    # Show the top counties.
    x_top = population_growth.index[:n].to_numpy()
    y_top = population_growth['Cumulative'][:n]
    ax.scatter(x_top, y_top, c='k', zorder=4)
    text = pd.Series(population_growth['County'] + ': '\
        + (((500 + population_growth['Growth'])//1000).map(int).map(str)
           + 'k'))[:n]
    for j in range(n):
        ax.text(x_top[j]+3, y_top[j], s=text[j])
    ax.axhline([0.5, 0.7][i]*total_growth, 0, n_counties, c = '#aaaaaa')

'''Harris, Tarrant, Bexar, Dallas, Collin, and Travis counties accounted for
more than half of all of Texas' growth--just six out of 284 counties!

Next we need to make a graphic that visually shows where this growth is. We
first need to merge the population growth into the shape data.'''

Texas_data = shape_data.merge(population_growth, left_on='NAME',
                              right_on='County')

# https://jcutrer.com/python/learn-geopandas-plotting-usmaps

'''Now let's see the growth! Three distinct regions emerge: Houston
(southeast), Dallas/Fort Worth (north), and San Antonio/Austin (south-central).
We highlight them on the graph.'''
fig, ax = plt.subplots(figsize=(11, 11))
aspect = 1.2
ax.set_aspect(aspect)
ax = Texas_data.plot(
    'Growth', cmap='gray', ax=ax, vmax=1.2 * max_growth)
fig.patch.set_visible(False)
ax.axis('off')

lw = 0.2
r = 1.5
colors = ['#1177ff', '#44ff11', '#ff2222']
theta = np.linspace(0, 2*np.pi, 200)
for i in range(3): #D/FW, Houston, then San Antonio/Austin
    long = [-97, -98, -95.5][i]
    lat = [33, 30, 30][i]
    ax.plot(r*np.cos(theta) + long, r*np.sin(theta)/aspect + lat,
            color=colors[i], lw=2, zorder=5)
textsize = 20
textcolor = 'w' #Will be invisible here but visible on a dark background
ax.text(-97, 34.5, 'Dallas/\nFort Worth', horizontalalignment='center',
        fontsize=textsize, color=textcolor)
ax.text(-94.7, 28.4, 'Houston', fontsize=textsize, color=textcolor)
ax.text(-102.5, 27.5, 'San Antonio/\nAustin', horizontalalignment='center',
        fontsize=textsize, color=textcolor)
ax.arrow(-100.8, 28.3, 1.5, 1.0, color=colors[1], lw=2, head_width=0.2,
         length_includes_head=True)
