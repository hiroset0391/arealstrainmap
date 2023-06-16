import streamlit as st
import pydeck as pdk
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib as mpl
from PIL import Image
import datetime

strain_min, strain_max = -4e-6, 4e-6


cmap_strain = plt.cm.viridis


norm = mpl.colors.Normalize(vmin=-4, vmax=4)
fig, ax = plt.subplots(figsize=(8, 1))
fig.patch.set_facecolor('#313131') 
cbar = mpl.colorbar.ColorbarBase(
    ax=ax,
    cmap=cmap_strain,
    norm=norm,
    orientation="horizontal"
)
cbar.set_label(label=r"areal strain ($\times$10$^{-6}$)", size=24, color='white')
cbar.ax.tick_params(labelsize=20, color='white') 
cbar.ax.xaxis.set_tick_params(color='white')


# set colorbar edgecolor 
cbar.outline.set_edgecolor('white')
ax.xaxis.label.set_color('white')
plt.setp(plt.getp(cbar.ax.axes, 'xticklabels'), color='white')

plt.savefig("strain.png", bbox_inches="tight",) # transparent=True
plt.close()


st.write("# Areal Strain Map")

refday = st.date_input('Select Reference',
        min_value=datetime.date(2015, 1, 1),
        max_value=datetime.date(2023, 1, 1),
        value=datetime.date(2015, 1, 1),
        )
st.write('Reference: ', refday)

dfin = pd.read_csv('area/area'+refday.strftime("%Y%m%d")+'.csv')
lons = np.array(dfin['lon'])
lats = np.array(dfin['lat'])
area_ref = np.array(dfin['area'])

col1, col2 = st.columns(2)
year = col1.selectbox('target year', [2015,2016,2017,2018,2019,2020,2021,2022,2023], label_visibility="hidden")

initialdate = datetime.datetime(year,1,1)
enddate = datetime.datetime(year,12,31)

currdate = st.slider('target day', min_value=initialdate, max_value=enddate, value=datetime.datetime(year,1,1), format="YY-MM-DD", label_visibility="hidden")

# dfin = pd.read_csv('arealstrain/arealstrain'+currdate.strftime("%Y%m%d")+'.csv')
# lons = np.array(dfin['lon'])
# lats = np.array(dfin['lat'])
# strains = np.array(dfin['arealstrain'])

dfin = pd.read_csv('area/area'+currdate.strftime("%Y%m%d")+'.csv')
area = np.array(dfin['area'])

strains = (area-area_ref)/area_ref

idx = np.where(strains==strains)
lons = lons[idx]
lats = lats[idx]
strains = strains[idx]

print(dfin)

Layers = list()
r_list = list() 
g_list = list() 
b_list = list() 

for i in range(len(lons)):
    lon, lat = lons[i], lats[i]
    df = pd.DataFrame({'lon': [lon], 'lat': [lat]})
    if strains[i]==strains[i]:
        idx = (strains[i]-strain_min)/(strain_max-strain_min) 
        
        temp = cmap_strain(idx, bytes=True)[0:3]
        r_list.append(temp[0])
        g_list.append(temp[1])
        b_list.append(temp[2])
        
        
Layers = list()
df = pd.DataFrame(
{
        'lon': lons,
        'lat': lats,
        'r': r_list,
        'g': g_list,
        'b': b_list
    }
)

color=strains
color_min = strain_min
color_max = strain_max
scat_layer = pdk.Layer(
        type='ScatterplotLayer',
        data=df,
        get_position='[lon, lat]',
        get_fill_color=['r', 'g', 'b'],
        get_radius=2000,
        get_line_color=[0, 0, 0],
        filled=True,
        line_width_min_pixels=10,
        opacity=2,
    )
Layers.append(scat_layer)

#st.write("### "+currdate.strftime("%Y-%m-%d"))
st.pydeck_chart(pdk.Deck(
    map_style='mapbox://styles/mapbox/dark-v10',
    initial_view_state=pdk.ViewState(
        latitude=36.381093,
        longitude=138.116365,
        zoom=3.7,
        pitch=0,
    ),
    layers=Layers,
    ))


col1, col2 = st.columns(2)
original = Image.open("strain.png")
col1.image(original, use_column_width=True)