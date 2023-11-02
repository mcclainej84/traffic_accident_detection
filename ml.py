import geopandas as gpd
import streamlit as st
import pandas as pd
import folium
import file_aux

##################################################################################################
#Constants Declaration
##################################################################################################
geojson_file = 'Distritos_de_Madrid.geojson'
csv_predict_file = '2023_Accidentalidad_predicciones.csv'
madrid_location = (40.4168, -3.7038)
map_style_list = ["CartoDB Positron" ,  "OpenStreetMap"  , "Stamen Terrain" ]
lvl_lesividad_list = [ "Lesividad Grave" , "Lesividad Leve"]

##################################################################################################
#Main program to execute the ML section
##################################################################################################
def run_mlapp():
    st.markdown(f'## Predicción de puntos con grados de lesividad ')
    st.write("Mapa de predicción de puntos con mayor probabilidad de tener algún tipo de lesión")

    params = sidebar_options()

    df, gdf = build_staging_data(params)
    if not len(df)==0:
         display_map(df,gdf,params)
    else:
         st.warning('⚠️ No hay datos que mostrar')

##################################################################################################
#This function is responsible to display the options on the sidebar
##################################################################################################
def sidebar_options():
    with st.sidebar:
        #Map type
        map_style = st.selectbox("Estilo del mapa:", map_style_list)

        lesivity = st.selectbox("Tipo de lesividad:", lvl_lesividad_list)

        apply_cluster =  st.toggle("Agrupar por Clusteres", value=True)

        params = {
            "map_style" : map_style,
            "lesivity_levels" : lesivity,
            "cluster_group":  apply_cluster
        }

        with st.expander("Parámetros utilizados"):
            st.write(params)
    return params

##################################################################################################
#This function is reponsible to build the tooltip for the maps
##################################################################################################
def define_tooltip():
    return folium.features.GeoJsonTooltip(fields=['cod_distrito', 'nom_distrito'], labels=True,
                          localize=True, aliases=['Código de distrito', 'Nombre'])

##################################################################################################
#This function is reponsible for building the staging data to render the maps
##################################################################################################
def build_staging_data(params):
    lesivity_low = '(pred_lesividad_leve == 1)'
    lesivity_high = '(pred_lesividad_grave == 1)'

    query_lesivity = {
        lvl_lesividad_list[1]: lesivity_low,
        lvl_lesividad_list[0]: lesivity_high
    }

    query = query_lesivity.get(params['lesivity_levels'], '')

    df = (pd.read_csv(file_aux.get_file(csv_predict_file))
          .query(query)
           .assign(
                    pred_lesividad_leve=lambda x: x['pred_lesividad_leve'].fillna(0).astype(int) ,
                    pred_lesividad_grave=lambda x: x['pred_lesividad_grave'].fillna(0).astype(int)
            )).reset_index()

    geo_dist_df = gpd.read_file(file_aux.get_file(geojson_file)).rename(columns={'NOMBRE': 'nom_distrito'}).assign(cod_distrito=lambda x: x['cod_distrito'].astype(int))

    return df, geo_dist_df

##################################################################################################
#This function is reponsible to build the map and display on the screen
##################################################################################################
def display_map(df, gdf, params):
    def style_function(feature):
        return {'fillColor': 'blue' ,'color': 'black', 'weight': 1, 'fillOpacity': 0.1}

    def build_pop_up(row):
        return f"""<div style="width: 300; ">
                    <b>Dirección:</b> {row['formatted']}<br>
                    <b>Predicción de lesividad grave:</b> {row['pred_lesividad_grave']}<br>
                    <b>Predicción de lesividad leve:</b> {row['pred_lesividad_leve']}<br>
                """

    map_zoom = 11
    map = folium.Map(location=madrid_location, zoom_start=map_zoom, tiles=params["map_style"])
    #Transform dataframe to dictionary for speed
    d = df.to_dict(orient='records')

    if params['cluster_group']:
        marker_cluster = folium.plugins.MarkerCluster().add_to(map)
        fig = marker_cluster
    else:
        fig = map

    color = 'red' if params['lesivity_levels'] == lvl_lesividad_list[0] else 'orange'

    for row in d:
        popup_html = build_pop_up(row)
        folium.Marker(location=[row['latitude'], row['longitude']],
                      icon=folium.Icon(color=color, icon="fa-solid fa-car-burst", prefix='fa'),
                      popup=folium.Popup(popup_html, max_width=300) ).add_to(fig)

    dist_figure = folium.GeoJson(gdf, name='mapa_distrito',
                                 style_function=style_function,
                                 tooltip=define_tooltip() )
    dist_figure.add_to(map)

    st.components.v1.html(map._repr_html_(), width=800, height=500)
