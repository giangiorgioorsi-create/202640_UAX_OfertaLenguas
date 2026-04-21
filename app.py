import streamlit as st
import pandas as pd

# 1. Configuración de la Interfaz
st.set_page_config(page_title="Oferta Académica de Lenguas 2026", layout="wide")

# 2. Gestión de Estado para el Restablecimiento (Reset)
if 'idioma_key' not in st.session_state:
    st.session_state.idioma_key = 0
if 'asignatura_key' not in st.session_state:
    st.session_state.asignatura_key = 0
if 'horario_key' not in st.session_state:
    st.session_state.horario_key = 0

def restablecer_filtros():
    st.session_state.idioma_key += 1
    st.session_state.asignatura_key += 1
    st.session_state.horario_key += 1

# 3. Carga de Base de Datos
@st.cache_data
def cargar_datos():
    archivo = "202640_UAX_OfertaLenguas.xlsx"
    df = pd.read_excel(archivo)
    df.columns = [c.strip() for c in df.columns]
    return df

try:
    df = cargar_datos()
    st.title("🏛️ Portal de Oferta Académica — Centro de Lenguas")

    # Creamos dos pestañas: una para explorar y otra para buscar
    tab_explorar, tab_buscar = st.tabs(["📊 Explorar la Oferta", "🔍 Buscador de Cursos"])

    with tab_explorar:
        st.header("Radiografía de Idiomas 2026")
        
        # Métricas rápidas (High-level metrics)
        c1, c2, c3 = st.columns(3)
        c1.metric("Idiomas Disponibles", df['Lengua'].nunique())
        c2.metric("Total de Grupos (NRC)", df['NRC'].count())
        c3.metric("Modalidades", df['MetodoInstruccion'].nunique())

        st.divider()

        # Gráficos de exploración
        col_graf1, col_graf2 = st.columns(2)
        
        with col_graf1:
            st.write("**Distribución por Idioma**")
            # Conteo de grupos por lengua
            conteo_lenguas = df['Lengua'].value_counts()
            st.bar_chart(conteo_lenguas)

        with col_graf2:
            st.write("**Modalidades de Instrucción**")
            conteo_metodo = df['MetodoInstruccion'].value_counts()
            st.pie_chart(conteo_metodo)

        st.info("""
        **Tip Académico:** Recuerda que los niveles siguen el Marco Común Europeo (A1-C1). 
        Explora la diversidad de horarios para planear mejor tu semestre.
        """)

    with tab_buscar:
        # Aquí va todo tu código anterior de filtros (selectbox, etc.)
        # ... (copia aquí la lógica de sel_idioma, sel_asignatura, etc.)

try:
    df = cargar_datos()
    st.title("🏛️ Buscador de Oferta Académica — Centro de Lenguas")
    st.markdown("""
    Siga el orden de los filtros en la barra lateral para consultar la disponibilidad de cursos, 
    horarios y la **Clave Banner** correspondiente para su proceso de inscripción.
    """)

    # --- Barra Lateral (Sidebar) ---
    st.sidebar.header("Criterios de Selección")
    
    # Filtro 1: Idioma
    idiomas = sorted(df['Lengua'].unique().tolist())
    sel_idioma = st.sidebar.selectbox(
        "1. Seleccione el Idioma", 
        [""] + idiomas, 
        key=f"idioma_{st.session_state.idioma_key}"
    )
    
    if sel_idioma:
        # Filtro 2: Asignatura
        df_i = df[df['Lengua'] == sel_idioma]
        asignaturas = sorted(df_i['NombreMateria'].unique().tolist())
        sel_asignatura = st.sidebar.selectbox(
            "2. Seleccione la Asignatura", 
            [""] + asignaturas, 
            key=f"asignatura_{st.session_state.asignatura_key}"
        )
        
        if sel_asignatura:
            # Filtro 3: Horario
            df_a = df_i[df_i['NombreMateria'] == sel_asignatura]
            horarios = sorted(df_a['HoraInicio'].astype(str).unique().tolist())
            sel_horario = st.sidebar.selectbox(
                "3. Seleccione el Horario", 
                [""] + horarios, 
                key=f"horario_{st.session_state.horario_key}"
            )
            
            if sel_horario:
                # Filtrado Final de Resultados
                resultados = df_a[df_a['HoraInicio'].astype(str) == sel_horario]
                
                st.subheader(f"Cursos disponibles para: {sel_asignatura}")
                
                # Tabla de Resultados Institucionales
                st.dataframe(
                    resultados[['Clave Banner', 'NRC', 'Docente', 'HoraInicio', 'HoraFin', 'Status']], 
                    use_container_width=True
                )
                
                # Secciones de Información Detallada
                st.divider()
                st.subheader("📋 Ficha Técnica del Curso")
                for _, fila in resultados.iterrows():
                    with st.expander(f"Más información — NRC: {fila['NRC']}"):
                        col1, col2 = st.columns(2)
                        with col1:
                            st.write(f"**Clave Banner:** {fila['Clave Banner']}")
                            st.write(f"**Catedrático:** {fila['Docente']}")
                            st.write(f"**Modalidad de Instrucción:** {fila['MetodoInstruccion']}")
                        with col2:
                            st.write(f"**Periodo Académico:** {fila['PartePeriodo']}")
                            st.write(f"**Estatus:** {fila['Status']}")
                            st.info(f"**Observaciones:** {fila['Notas'] if pd.notna(fila['Notas']) else 'Sin observaciones adicionales.'}")

    # Botón de Restablecimiento
    st.sidebar.divider()
    if st.sidebar.button("Restablecer Filtros", on_click=restablecer_filtros):
        st.rerun()

except Exception as e:
    st.error(f"⚠️ Error en la consulta de datos: {e}")
    st.warning("Verifique que el archivo fuente mantenga la estructura de columnas requerida.")
