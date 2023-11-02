import streamlit as st
import base64
import maps
import ml
import eda
import file_aux

##################################################################################################
#Constants Declaration
##################################################################################################
st.set_page_config(page_title = "Detección de Accidentes en Madrid", page_icon=":🚦:" )
st.sidebar.info("Menú de opciones")
font="sans serif"

PAGE_HOME = "🚘 HOME"
PAGE_EDA = "📊 Análisis Gráfico"
PAGE_MAPS = "🌎 Visualización con Mapas"
PAGE_ML = "🤖 Predicción con níveles de lesividad"
PAGE_SELECT=[PAGE_HOME,PAGE_EDA ,PAGE_MAPS, PAGE_ML ]

IMG_HEADER ='TrafficBW.jpeg'
IMG_PORTADA= "accidente_portada.jpg"

##################################################################################################
#Main program to activate the App and the sidebar menu
##################################################################################################
def main():
	#page selector
	ps = st.sidebar.selectbox("Seleccióne una opcion",(PAGE_SELECT))

	if ps== PAGE_HOME:
		home_app()
	elif ps == PAGE_EDA:
		eda.run_eda_app()
	elif ps == PAGE_ML:
		ml.run_mlapp()
	else:
		maps.run_maps_app()

#########################################################
#################		HOMEPAGE		#################
#########################################################
def home_app():
	try:
		st.image(file_aux.get_image(IMG_PORTADA), use_column_width=True)
	except:
		st.empty()

	st.write('A día de hoy, el numero de vehículos asegurados en España se situó en 33.231.237 en el segundo semestre de 2023 según Unespa, Unión Española de Entidades Aseguradoras y Reaseguradoras.')
	st.write('En el año 2022, se registraron 1.042 accidentes mortales en las carreteras de España, con un saldo de 1.145 personas fallecidas y 4.008 personas heridas de gravedad. Estas estadísticas reflejan un aumento de 44 víctimas fatales (+4 %) en comparación con el año 2019, que sirve como punto de referencia antes de la pandemia, aunque se registró una disminución de 425 heridos graves (-10 %) en ese mismo período.')
	st.write('En los primeros siete meses del año 2023, 620 personas han fallecido en siniestros de tráfico.')
	st.write('Este proyecto se basa en el análisis de accidentes de transito de la comunidad de Madrid.')

#########################################################
#################		APP HEADER 		#################
#########################################################
def header():
	try:
		encoded_image = file_aux.get_image(IMG_HEADER)
		# Encode the image data as base64
		encoded_image = base64.b64encode(encoded_image).decode('utf-8')
	except:
		encoded_image = None

	html = f"""
		<div style="background-image: url(data:image/jpeg;base64,{encoded_image}); background-size: 100% 100%; border-radius: 30px; padding: 10px; text-align: center; color: orange;">
		<h1 style="font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif; font-weight: bold; font-size: 55px;
					-webkit-text-stroke: 2px black; color:orange;
					text-stroke: 23px black;">
			Detección de Accidentes
		</h1>
		<p style="font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;font-weight: bold;font-size: 36px;-webkit-text-stroke: 2px black;
					text-stroke: 2px black;">Ciudad de Madrid</p>
	</div>
	"""
	st.markdown(html, unsafe_allow_html=True)

if __name__ == '__main__':
	header()
	st.write("")
	st.write("")
	main()
