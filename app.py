import streamlit as st
import maps


st.set_page_config(page_title = "Detección de Accidentes en Madrid", page_icon=":🚦:" )
st.sidebar.info("Menú Contextual")


font="sans serif"


PAGE_HOME = "🚘 Introducción"
PAGE_EDA = "📊 Analísis Exploratorio"
PAGE_MAPS = "🌎 Mapas y cuadro de mando"
PAGE_ML = "🤖 Sección de ML"
PAGE_INFO = "ℹ️ Información adicional"
PAGE_SELECT=[PAGE_HOME,PAGE_EDA ,PAGE_MAPS, PAGE_ML , PAGE_INFO]

def main():
	#page selector
	ps = st.sidebar.selectbox("",(PAGE_SELECT))

	if ps== PAGE_HOME:
		home_app()
	elif ps == PAGE_EDA:
		eda_app()
	elif ps == PAGE_INFO:
		info()
	elif ps == PAGE_ML:
		ml_app()
	else:
		maps.run_maps_app()


def home_app():
    st.write('Esta página consistirá de una portada. Se mostrarán un par de fotos chulas y se explicará el contexto del proyecto. No habrá necesidad de código, sólo texto plano')

def eda_app():
    st.write('Esta página consistira de una serie de datos explorarios sobre el dataset final.')
    st.write('Se pueden añadir gráficas para mostrar las distribuciones más comunes de los principales valores ( por ejempplo sexo,etc )')

def info():
    st.write('En esta página se puede mostrar información sobre el proyecto, las personas que han participado, herramientas utilizadas, links, etc...')

def maps_app():
    st.write('En esta pagina crearemos un cuadro de mando con los mapas y la información distribuida por sectores, pudiendo elegir distritos, etc y que la información filtre en función de la información')

def ml_app():
    st.write('En esta página se cargará el modelo de ML y permitirá realizar predicciones en base a los datos seleccionados')

def header():

	html = f'''
		<div style="background-image: url('https://github.com/mcclainej84/traffic_accident_detection/blob/main/TrafficBW.jpeg?raw=true'); background-size: 100% 100%; border-radius: 30px; padding: 10px; text-align: center; color: orange;">
		<h1 style="font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif; font-weight: bold; font-size: 55px; 
					-webkit-text-stroke: 2px black; color:orange;
					text-stroke: 23px black;">
			Detección de Accidentes
		</h1>
		<p style="font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;font-weight: bold;font-size: 36px;-webkit-text-stroke: 2px black; 
					text-stroke: 2px black;">Ciudad de Madrid</p>
	</div>
	'''

	st.markdown(html, unsafe_allow_html=True)

if __name__ == '__main__':
	header()
	st.text("")
	st.text("")
	main()
