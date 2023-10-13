import streamlit as st
from folium.plugins import MarkerCluster
from folium.plugins import HeatMap
from folium.features import GeoJsonTooltip
from datetime import datetime as dt
from branca.colormap import linear
import branca
from functools import partial
import geopandas as gpd
import pandas as pd
import calendar
import folium
import json

data_folder ="./data/"
csv_accidents_path = f'{data_folder}2023_Accidentalidad_c_g_s_d.csv'
geojson_path = f'{data_folder}Distritos_de_Madrid.geojson'

map_type_list = ["Mapa General", "Mapa Cluserizado" ,  "Mapa de calor"]
map_style_list = ["CartoDB Positron" ,  "OpenStreetMap"  , "Stamen Terrain" ]
l_id_distr=0
l_id_date=1
madrid_location = (40.4168, -3.7038)
madrid_zone="Madrid"


##################################################################################################
#This function is responsible to feed the LOVs for the sidebar
##################################################################################################
def get_data_lov(l_id):
    with open(f'{data_folder}LOV.json', 'r') as json_file:
        loaded_data = json.load(json_file)
        lov_date_data = loaded_data[l_id]['data']
        return lov_date_data

##################################################################################################
#This function is responsible to display the options on the sidebar
##################################################################################################
def sidebar_options():
    with st.sidebar:
        #Tipo de mapa
        map_type = st.selectbox("Tipo de mapa:", map_type_list)
        map_style = st.selectbox("Estilo del mapa:", map_style_list)

        if map_type == map_type_list[0]:
            dis_select = {'cod_dist': None}
        else:
            if st.toggle("Información global" , value= True ):
                dis_select = {'cod_dist':None}
            else:
                dl = get_data_lov(l_id_distr)
                dis_select = st.selectbox( 'Seleccione el distrito', options=dl, format_func=lambda x: f'{x["nombre"]}')


        l=[d['min']  for d in  get_data_lov(l_id_date) ]
        start_date, end_date = st.select_slider( 'Seleccionar mes', options=[d for d in l] , format_func=lambda date_string: dt.strptime(date_string, "%Y-%m-%d").strftime("%b") if date_string else None ,  value=(l[0], l[-1] ))
        end_date = last_day_of_month(end_date)

        params = {
            "map_type" : map_type,
            "map_style" : map_style,
            "start_date" : start_date,
            "end_date":  end_date.strftime("%Y-%m-%d"),
            "cod_distr" : int(dis_select.get('cod_distr')) if dis_select.get('cod_distr') is not None else None,
            "zone_name": dis_select.get('nombre') if dis_select.get('nombre') is not None else madrid_zone
        }

        with st.expander("Parámetros utilizados"):
            st.write(params)
    return params

##################################################################################################
#This function is responsible to get the last day of the month from a given date
##################################################################################################
def last_day_of_month(d):
    d = dt.strptime(d, "%Y-%m-%d")
    last_day = calendar.monthrange(d.year, d.month)[1]
    d = dt.strptime(f"{d.year}-{d.month}-{last_day}", "%Y-%m-%d")
    return d

##################################################################################################
#This function is responsible to retrieve agregated GeoJSON dataframe with the total accidents from a given date range
#And invidual dataframe from all accidents with the criteria selected
##################################################################################################
def buid_staging_data(start_date, end_date, cod_dist):
    query = f"('{start_date}' <= fecha <= '{end_date}')"
    #if cod_dist is not None:
    #    query += f" & cod_distrito == {cod_dist} "

    base_df = (
        pd.read_csv(csv_accidents_path, sep=";")
        .astype({'cod_distrito': int})
        .query(query)
        .groupby(['num_expediente', 'fecha', 'cod_distrito', 'latitude', 'longitude', 'tipo_accidente',
                  'formatted', 'latitude_api', 'longitude_api'])
        .agg({'numero': 'count'})
        .reset_index()
    )

    if cod_dist:
        df = base_df[base_df['cod_distrito']== int(cod_dist)]
    else:
        df = base_df

    geo_dist_df = (
        gpd.read_file(geojson_path)
        .rename(columns={'NOMBRE': 'nom_distrito'})
        .assign(cod_distrito=lambda x: x['cod_distrito'].astype(int))
    )

    dist_df = base_df.groupby(['cod_distrito'])['num_expediente'].agg(['count']).rename(columns={'count': 'count_accidents'}).reset_index()

    gdf = geo_dist_df.merge(dist_df, on='cod_distrito' )
    return df, gdf


def run_maps_app():
    params = sidebar_options()

    cod_distr = int(params.get('cod_distr')) if params.get('cod_distr') is not None  else None

    st.markdown(f'## Visualización de mapa de {params.get("zone_name")} ')
    df, gdf = buid_staging_data(params['start_date'], params['end_date'], cod_distr)

    display_map(df,gdf,params)

    st.write(f"Número total de accidentes: {len(df)}")

    st.markdown('### Dataset utilizado')
    st.write(df)

def display_map(df, gdf, params):
    cod_distr = params.get('cod_distr')
    if cod_distr is None:
        map_center = madrid_location
        map_zoom = 10
        #dist_data = get_all_dist_data(params)
    else:
        map_zoom = 12
        #dist_data = get_dist_data(cod_dist,params)
        x=gdf[gdf['cod_distrito']== 1 ]['geometry'].centroid.x
        y=gdf[gdf['cod_distrito']== 1 ]['geometry'].centroid.y
        map_center = [y,x ]

    map = folium.Map(location=map_center, zoom_start=map_zoom, tiles=params["map_style"] )

    if params["map_type"] == map_type_list[0]:
        map_add_colormap(map,gdf)
    elif params["map_type"] == map_type_list[1]:
        map_add_cluster(map,gdf,df,cod_distr)
    elif params["map_type"] == map_type_list[2]:
        map_add_heatmap(map, df)

    st.components.v1.html(map._repr_html_(), width=800, height=500)

def define_tooltip():
    return GeoJsonTooltip(fields=['cod_distrito', 'nom_distrito', 'count_accidents'],labels=True, localize=True,aliases=['Código de distrito', 'nombre', 'Número de accidentes'])

def map_add_cluster(map , gdf, df, cod_distr):
    def style_function(feature, cod_distr):
        if feature['properties']['cod_distrito'] == cod_distr:
            return { 'fillColor': 'green',  'color': 'black',  'weight': 1, 'fillOpacity': 0.5}
        else:
            return {'fillColor': 'blue' ,'color': 'black', 'weight': 1, 'fillOpacity': 0.1}

    def build_pop_up(row):
        return f"""<div style="width: 300; ">
                <b>Número de Expediente:</b> {row['num_expediente']}<br>
                <b>Fecha:</b> {row['fecha']}<br>
                <b>Tipo de accidente:</b> {row['tipo_accidente']}<br>
                <b>Dirección:</b> {row['formatted']}<br>
                <b>Número de afectados:</b> {row['numero']}<br> </div>"""

    #Transform dataframe to dictionary for speed
    d = df.to_dict(orient='records')
    marker_cluster = MarkerCluster().add_to(map)
    for row in d:
        popup_html = build_pop_up(row)
        folium.Marker(location=[row['latitude'], row['longitude']],
                      icon=folium.Icon(color="black", icon="fa-solid fa-car-burst", prefix='fa'),
                      popup=folium.Popup(popup_html, max_width=300)).add_to(marker_cluster)

    dist_figure = folium.GeoJson(gdf, name='mapa_distrito', style_function=partial(style_function, cod_distr=cod_distr),
                                 tooltip=define_tooltip())
    dist_figure.add_to(map)

def map_add_colormap(map, gdf):
    colormap = branca.colormap.LinearColormap(
        vmin=gdf["count_accidents"].quantile(0.0),
        vmax=gdf["count_accidents"].quantile(1),
        colors=['yellow', 'orange', 'red', 'black'],
        caption="Trips Forcast",
    )
    colormap.add_to(map)

    dist_figure = folium.GeoJson(gdf, name='mapa_distrito', style_function=lambda x: {
        "fillColor": colormap(x['properties']['count_accidents']),
        "color": "black",
        "weight": 0.5,
        "fillOpacity": 0.6,
    },
    tooltip=define_tooltip())
    dist_figure.add_to(map)

def map_add_heatmap(map, df):
    df["Latitude"] = df["latitude"].astype(float)
    df["Longitude"] = df["longitude"].astype(float)
    heatDF = df[["latitude", "longitude"]]

    heatdata = [[row["latitude"], row["longitude"]] for index, row in heatDF.iterrows()]
    HeatMap(heatdata, min_opacity=0.1, max_zoom=10, radius=6, blur=4, max_val=0.9).add_to(map)

