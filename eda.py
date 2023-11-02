import streamlit as st
import pandas as pd
import plotly.express as px
import file_aux

st.set_option('deprecation.showPyplotGlobalUse', False)
graph_type_list = ["Gráfico de distribución por distrito", "Gráfico de Condiciones Climáticas" , "Gráfico de tipo de accidentes" , "Gráfico de distribución por sexo", "Grafico cantidad accidentes por distrito" ,"Gráfico de valores Nulos"]

csv_accidents_file = '2023_Accidentalidad_c_g_s_d_clean.csv'

def buid_staging_data():
    df = pd.read_csv(file_aux.get_file(csv_accidents_file), sep=";")
    return df

def sidebar_options():
    with st.sidebar:
        #Graph type
        grph_type = st.selectbox("Tipo de gráfico:", graph_type_list)

        return grph_type


def graph_distrito(Accidentes):
    # Gráfico de la distribución de la variable distrito
    umbral1 = 600
    umbral2 = 900

    recuento_distrito = Accidentes['distrito'].str.lower().value_counts()

    categorias = pd.cut(recuento_distrito, bins=[0, umbral1, umbral2, float('inf')],
                        labels=['Rango 1', 'Rango 2', 'Rango 3'])

    colores = {
        'Rango 1': 'lightcoral',
        'Rango 2': 'blue',
        'Rango 3': 'lightblue'
    }

    fig = px.bar(x=categorias.index, y=recuento_distrito, color=[colores[c] for c in categorias])

    fig.update_layout(
        title='Distribución de accidentes por distrito',
        xaxis_title='Distrito',
        yaxis_title='Número de accidentes',
        plot_bgcolor='black',
        paper_bgcolor='black',
        font=dict(color='white')
    )
    st.plotly_chart(fig)

def graph_meteorología(Accidentes):
    # Gráfico de la distribución de la variable Estado meteorológico
    colores = {
        'despejado': 'Skyblue',
        'nublado': 'gray',
        'lluvia débil': 'lightcoral'
    }

    recuento_estado = Accidentes['estado_meteorológico'].value_counts()

    fig_torta = px.pie(
        values=recuento_estado.values,
        names=recuento_estado.index,
        title='Distribución de Condiciones Climáticas'
    )
    st.plotly_chart(fig_torta)

def graph_tipo_accidentes(Accidentes):
    # Gráfico de la distribución de la variable tipo accidente
    recuento_tipo = Accidentes['tipo_accidente'].value_counts()

    fig = px.bar(x=recuento_tipo.index, y=recuento_tipo, color=recuento_tipo.index, color_continuous_scale='Viridis')

    fig.update_layout(
        title='Distribución de accidentes por su tipo',
        xaxis_title='Tipo de Accidente',
        yaxis_title='Número de accidentes',
        plot_bgcolor='black',  # Fondo negro
        paper_bgcolor='black',  # Fondo del papel negro
        font=dict(color='white')  # Texto en blanco
    )
    st.plotly_chart(fig)

def graph_sexo(Accidentes):
        # Gráfico de la distribución de la variable sexo
        recuento_sexo = Accidentes['sexo'].value_counts()
        fig = px.pie(
            values=recuento_sexo.values,
            names=recuento_sexo.index,
            title='Distribución de Género'
        )
        st.plotly_chart(fig)


def graph_top15(Accidentes):
    # Graficos distritos con mayor cantidad de accidentes
    Accidentes.drop_duplicates(
        subset='num_expediente').groupby('road_name_speed_api').size().nlargest(15)
    df_top15_accidentes = pd.DataFrame(top15_accidentes, columns=['Cantidad de Accidentes'])
    fig = px.bar(df_top15_accidentes, x=df_top15_accidentes.index, y='Cantidad de Accidentes',
                 color='Cantidad de Accidentes')
    fig.update_layout(
        title='Top 15 Ubicaciones de Carreteras con Mayor Cantidad de Accidentes',
        xaxis_title='Ubicación de la Carretera',
        yaxis_title='Cantidad de Accidentes',
    )
    st.plotly_chart(fig)


def graph_nulos(Accidentes):
    st.write(
        'Luego analizamos los datos faltantes, ya que nos pareció importante entender cuan completo estaba el dataset.')
    st.write(
        'Analizamos los datos faltantes, ya que nos pareció importante entender cuan completo estaba el dataset.')
    st.write(
        'Primero, vimos la cantidad de datos faltantes por columna que teníamos. Luego hicimos la suma total de los datos faltantes. Posteriormente vimos cual era el porcentaje total de datos faltantes.Hemos visto que teníamos un 10.96% de datos faltantes totales.')
    st.write('Realizamos dos tratamientos distintos para los valores faltantes.')
    st.write(
        'En primer lugar, analizando los datos faltantes por columna, hemos observado que la columna positiva_droga tiene solo dos valores, Null y 1. En este caso entendimos que el valor null representa un negativo y el valor 1 representa un valor positivo. Procedimos a reemplazar los valores null por ceros para que así nos quedaran dos valores en dicha columna y podríamos utilizarla posteriormente en nuestro análisis.')
    st.write(
        'En este momento, hemos verificado nuevamente el porcentaje de datos faltantes y vemos que se ha reducido a un un 5.72%. Estos, se reparten entre las siguientes columnas: estado_meteorológico, tipo_vehiculo, rango_edad, sexo, cod_lesividad, lesividad, coordenada_x_utm, coordenada_y_utm y positiva_alcohol.')
    st.write(
        'En segundo lugar, reemplazamos los valores faltantes de las variables categóricas por su moda. Previamente cual era la moda de algunas de estas variables categóricas. Los reemplazamos por la moda ya que consideramos que si los eliminábamos o reemplazábamos por un valor “no asignado” perdíamos una cantidad de datos significante para luego realizar el modelo de predicción.')
    st.write('De esta manera, nos ha quedado un dataset completo sin apenas valores faltantes.')

    # Gráfico de los valores nulos por columna
    valores_nulos = Accidentes.isnull().sum()
    df_valores_nulos = pd.DataFrame({'Columna': valores_nulos.index, 'Valores Nulos': valores_nulos.values})
    fig = px.bar(df_valores_nulos, x='Columna', y='Valores Nulos', title='Cantidad de Valores Nulos por Columna')
    st.plotly_chart(fig)

def run_eda_app():
    # Accidentes = Accidentes.apply(lambda x: x.astype(str).str.lower()) ojo porque me saca los nulos cuando transformo el dataset a lower
    st.markdown(f'## Análisis Gráfico')

    # Get dataset
    Accidentes = buid_staging_data()

    st.write(
        'En este apartado comentaremos como hemos realizado el análisis exploratorio de nuestro dataset principal de accidentalidad.')
    st.write('Importamos el dataset y leemos las primeras 25 filas para ver su contenido.')
    st.write(
        'Observamos las diferentes columnas para entender el dataset. Vemos que tenemos una columna denominada num_expediente que es el numero de expendiente tomado por la policía al momento de ocurrir el accidente. Vemos también que tenemos información sobre la fecha y hora en la que ocurre el accidente, el tipo de vehículo involucrado, el rango de edad de las personas que participaron del accidente, las coordenadas donde ocurrió el accidente, entre otras.')
    st.write(
        'Comprobamos su dimensión y el tipo de datos que contiene cada columna. Vemos que tenemos un dataset de gran tamaño, 16,217 filas y 19 columnas. Todas las variables son categóricas a excepción de una, positivo_droga.')
    st.write('Comenzamos a ver la distribución de algunas variables que consideramos más interesantes.')

    grph_type = sidebar_options()

    if grph_type == graph_type_list[0]:
        graph_distrito(Accidentes)
    elif grph_type == graph_type_list[1]:
        graph_meteorología(Accidentes)
    elif grph_type == graph_type_list[2]:
        graph_tipo_accidentes(Accidentes)
    elif grph_type == graph_type_list[3]:
        graph_sexo(Accidentes)
    elif grph_type == graph_type_list[4]:
        graph_top15(Accidentes)
    elif grph_type == graph_type_list[5]:
        graph_nulos(Accidentes)
