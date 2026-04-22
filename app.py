import streamlit as st
import pandas as pd

# 1. Configuración Estética
st.set_page_config(page_title="Oferta de Lenguas 2026", layout="wide")

# CSS Personalizado para darle el "toque Anáhuac"
st.markdown("""
    <style>
    .main { background-color: #f5f5f5; }
    .stMetric { background-color: #ffffff; padding: 15px; border-radius: 10px; box-shadow: 2px 2px 5px rgba(0,0,0,0.1); }
    .nrc-badge { background-color: #ff6600; color: white; padding: 2px 8px; border-radius: 5px; font-weight: bold; margin-right: 5px; }
    </style>
    """, unsafe_allow_html=True)

# 2. Gestión de Estado para Reset
if 'idioma_key' not in st.session_state: st.session_state.idioma_key = 0
if 'asignatura_key' not in st.session_state: st.session_state.asignatura_key = 0
if 'horario_key' not in st.session_state: st.session_state.horario_key = 0

def restablecer_filtros():
    st.session_state.idioma_key += 1
    st.session_state.asignatura_key += 1
    st.session_state.horario_key += 1

# 3. Carga de Datos
@st.cache_data
def cargar_datos():
    archivo = "202640_UAX_OfertaLenguas.xlsx"
    df = pd.read_excel(archivo)
    df.columns = [c.strip() for c in df.columns]
    return df

try:
    df = cargar_datos()
    
    # Banner llamativo
    st.markdown("<h1 style='text-align: center; color: #ff6600;'>🏛️ Portal Académico Centro de Lenguas</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; font-size: 1.2em;'>Gestión Inteligente de la Oferta Académica 2026</p>", unsafe_allow_html=True)

    tab_explorar, tab_buscar = st.tabs(["📊 Panorama General", "🔍 Buscador Inteligente"])

    with tab_explorar:
        st.subheader("Estadísticas de la Coordinación")
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Idiomas", df['Lengua'].nunique())
        m2.metric("Total Grupos", df['NRC'].count())
        m3.metric("Docentes", df['Docente'].nunique())
        m4.metric("Inscritos Est.", "600+")

        st.divider()
        col_a, col_b = st.columns(2)
        with col_a:
            st.write("**Oferta por Idioma**")
            st.bar_chart(df['Lengua'].value_counts(), color="#ff6600")
        with col_b:
            st.write("**Distribución de Modalidades**")
            st.bar_chart(df['MetodoInstruccion'].value_counts(), color="#ffb380")

    with tab_buscar:
        st.sidebar.header("Configuración de Búsqueda")
        
        idiomas = sorted(df['Lengua'].unique().tolist())
        sel_idioma = st.sidebar.selectbox("1. Idioma", [""] + idiomas, key=f"i_{st.session_state.idioma_key}")
        
        if sel_idioma:
            df_i = df[df['Lengua'] == sel_idioma]
            asignaturas = sorted(df_i['NombreMateria'].unique().tolist())
            sel_asignatura = st.sidebar.selectbox("2. Asignatura", [""] + asignaturas, key=f"a_{st.session_state.asignatura_key}")
            
            if sel_asignatura:
                df_a = df_i[df_i['NombreMateria'] == sel_asignatura]
                horarios = sorted(df_a['HoraInicio'].astype(str).unique().tolist())
                sel_horario = st.sidebar.selectbox("3. Horario", [""] + horarios, key=f"h_{st.session_state.horario_key}")
                
                if sel_horario:
                    # FILTRADO Y AGRUPACIÓN PARA LISTAS CRUZADAS
                    resultados = df_a[df_a['HoraInicio'].astype(str) == sel_horario]
                    
                    st.success(f"Se han encontrado opciones para {sel_asignatura}")
                    
                    # Agrupamos por Docente y Horario para detectar listas cruzadas
                    # Si varios NRC comparten docente, horario y método, son una "clase conjunta"
                    grupos = resultados.groupby(['Docente', 'HoraInicio', 'HoraFin', 'MetodoInstruccion', 'PartePeriodo'])
                    
                    for (docente, inicio, fin, metodo, periodo), datos_grupo in grupos:
                        with st.container():
                            # Diseño de tarjeta para el curso
                            st.markdown(f"""
                            <div style="border: 1px solid #ddd; padding: 20px; border-radius: 10px; background-color: white; margin-bottom: 15px;">
                                <h3 style="margin-top:0; color: #ff6600;">{sel_asignatura}</h3>
                                <p><strong>Catedrático:</strong> {docente}</p>
                                <p><strong>Horario:</strong> {inicio} - {fin} | <strong>Modalidad:</strong> {metodo}</p>
                                <hr>
                                <p><strong>NRC(s) Disponibles para Inscripción:</strong></p>
                            </div>
                            """, unsafe_allow_html=True)
                            
                            # Desplegamos los NRC juntos (Lista Cruzada)
                            cols_nrc = st.columns(len(datos_grupo) if len(datos_grupo) < 5 else 4)
                            for i, (_, fila) in enumerate(datos_grupo.iterrows()):
                                with cols_nrc[i % 4]:
                                    st.markdown(f"<span class='nrc-badge'>NRC {fila['NRC']}</span>", unsafe_allow_html=True)
                                    st.caption(f"Banner: {fila['Clave Banner']}")
                            
                            with st.expander("Ver notas y detalles adicionales"):
                                st.write(f"**Periodo:** {periodo}")
                                st.info(f"**Observaciones:** {fila['Notas'] if pd.notna(fila['Notas']) else 'Sin observaciones.'}")

        st.sidebar.divider()
        if st.sidebar.button("🔄 Restablecer Filtros", on_click=restablecer_filtros):
            st.rerun()

except Exception as e:
    st.error(f"⚠️ Error en la plataforma: {e}")
