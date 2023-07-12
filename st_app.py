import streamlit as st
import pydeck as pdk
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib as mpl
from PIL import Image
import datetime
import os

# データの準備
@st.cache_data
def read_poligonfile(file):
    return np.load(file).tolist()

polygon = read_poligonfile('polygon20150101.npy')
cmap_strain = plt.cm.viridis



if 'strain_min' not in st.session_state or 'strain_max' not in st.session_state:
    st.session_state['strain_min'] = -1e-6
    st.session_state['strain_max'] = 1e-6
    
    norm = mpl.colors.Normalize(vmin=-1, vmax=1)
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
        min_value=datetime.date(2005, 1, 1),
        max_value=datetime.date(2023, 1, 1),
        value=datetime.date(2015, 1, 1),
        )
st.write('Reference: ', refday)

dfin = pd.read_csv('triangle.csv')
lons = np.array(dfin['lon'])
lats = np.array(dfin['lat'])

dfin = pd.read_csv('area2/area'+refday.strftime("%Y%m%d")+'.csv')
area_ref = np.array(dfin['area'])


col1, col2 = st.columns(2)
year = col1.selectbox('target year', [2005,2006,2007,2008,2009,2010,2011,2012,2013,2014,2015,2016,2017,2018,2019,2020,2021,2022,2023], label_visibility="hidden", index=19)

initialdate = datetime.datetime(year,1,1)
enddate = datetime.datetime(year,12,31)
currdate = st.slider('target day', min_value=initialdate, max_value=enddate, value=datetime.datetime(year,1,1), format="YY-MM-DD", label_visibility="hidden")


dfin = pd.read_csv('area2/area'+currdate.strftime("%Y%m%d")+'.csv')
area = np.array(dfin['area'])


#st.write(len(polygon))


strains = (area-area_ref)/area_ref
#strains[strains!=strains] = 0.0

idx = np.where(strains==strains)
lons = lons[idx]
lats = lats[idx]
strains = strains[idx]
polygon_plot = list()
for i in range(len(polygon)):
    if i in idx[0]:
        polygon_plot.append(polygon[i])




r_list = list() 
g_list = list() 
b_list = list() 
color = list()

for i in range(len(lons)):
    #lon, lat = lons[i], lats[i]
    #df = pd.DataFrame({'lon': [lon], 'lat': [lat]})
    
    if currdate.strftime("%Y%m%d")=='20150101':
        if strains[i]==strains[i]:
            idx = (strains[i]-st.session_state['strain_min'])/(st.session_state['strain_max']-st.session_state['strain_min']) 
            
            temp = cmap_strain(idx, bytes=True)[0:3]
            r_list.append(temp[0])
            g_list.append(temp[1])
            b_list.append(temp[2])
            color.append([int(temp[0]), int(temp[1]), int(temp[2]), 150]) #'Alpha' は透過度を表す値で、0から255の範囲で指定します。0は完全に透明、255は完全に不透明を意味します。
    else:
        if strains[i]==strains[i] and strains[i]!=0:
            idx = (strains[i]-st.session_state['strain_min'])/(st.session_state['strain_max']-st.session_state['strain_min']) 
            
            temp = cmap_strain(idx, bytes=True)[0:3]
            r_list.append(temp[0])
            g_list.append(temp[1])
            b_list.append(temp[2])
            color.append([int(temp[0]), int(temp[1]), int(temp[2]), 150]) #'Alpha' は透過度を表す値で、0から255の範囲で指定します。0は完全に透明、255は完全に不透明を意味します。
        else:
            color.append([0,0,0,0])
            
    
#st.write(len(list(polygon_plot)), len(list(color)))
Layers = list()
df = pd.DataFrame({
    'polygon': list(polygon_plot),
    'color': list(color)
})


layer = pdk.Layer(
    'PolygonLayer',
    df,
    wireframe=True,
    get_polygon='polygon',
    get_fill_color='color',
    get_line_color=[255,255,255],
    get_line_width=1,  # 線の太さの基本値
    get_line_width_units='pixels',  # 線の太さの単位をピクセルに設定
    lineWidthScale=100,  # 線の太さに乗算されるスケーリング係数
    pickable=True,
    auto_highlight=False
)

# 地図のビューを設定
view_state = pdk.ViewState(latitude=36.381093, longitude=138.116365, zoom=3.7, bearing=0, pitch=0)

# レイヤーとビューを使用してdeckを作成
deck = pdk.Deck(
    map_style='mapbox://styles/mapbox/dark-v10',
    layers=[layer],
    initial_view_state=view_state
)

# Streamlitでレンダリング
st.pydeck_chart(deck)



col1, col2 = st.columns(2)
original = Image.open("strain.png")
col1.image(original, use_column_width=True)


with st.expander("change max. and min. values for the colorbar"):
    col1, col2 = st.columns(2)
    strain_max = float(col1.text_input('max.', '1e-6', label_visibility="hidden")) #col2.number_input('max.', value=4e-6)

    if col1.button('change'):
        

        st.session_state['strain_max'] = strain_max
        st.session_state['strain_min'] = -strain_max
        
        fmax_str = str(abs(st.session_state['strain_max']))
        if fmax_str[-4] == 'e':
            # 指数部の取得
            e = int(fmax_str[-2:])
            # 仮数部の桁数の取得
            m = fmax_str.index('e') - 1
            order_max = e + m
            amp_max = float( fmax_str[:fmax_str.index('e')] )
        else:
            order_max = np.sum(c.isdigit() for c in fmax_str)

        
        norm = mpl.colors.Normalize(vmin=-amp_max, vmax=amp_max)
        fig, ax = plt.subplots(figsize=(8, 1))
        fig.patch.set_facecolor('#313131') 
        cbar = mpl.colorbar.ColorbarBase(
            ax=ax,
            cmap=cmap_strain,
            norm=norm,
            orientation="horizontal"
        )
        cbar.set_label(label=r"areal strain ($\times$10$^{-"+str(int(order_max))+r"}$)", size=24, color='white')
        cbar.ax.tick_params(labelsize=20, color='white') 
        cbar.ax.xaxis.set_tick_params(color='white')


        # set colorbar edgecolor 
        cbar.outline.set_edgecolor('white')
        ax.xaxis.label.set_color('white')
        plt.setp(plt.getp(cbar.ax.axes, 'xticklabels'), color='white')

        plt.savefig("strain.png", bbox_inches="tight",) # transparent=True
        plt.close()


        
# Layers = list()
# df = pd.DataFrame(
# {
#         'lon': lons,
#         'lat': lats,
#         'r': r_list,
#         'g': g_list,
#         'b': b_list
#     }
# )

# color=strains
# color_min = strain_min
# color_max = strain_max
# scat_layer = pdk.Layer(
#         type='ScatterplotLayer',
#         data=df,
#         get_position='[lon, lat]',
#         get_fill_color=['r', 'g', 'b'],
#         get_radius=2000,
#         get_line_color=[0, 0, 0],
#         filled=True,
#         line_width_min_pixels=10,
#         opacity=2,
#     )
# Layers.append(scat_layer)

# #st.write("### "+currdate.strftime("%Y-%m-%d"))
# st.pydeck_chart(pdk.Deck(
#     map_style='mapbox://styles/mapbox/dark-v10',
#     initial_view_state=pdk.ViewState(
#         latitude=36.381093,
#         longitude=138.116365,
#         zoom=3.7,
#         pitch=0,
#     ),
#     layers=Layers,
#     ))


# col1, col2 = st.columns(2)
# original = Image.open("strain.png")
# col1.image(original, use_column_width=True)