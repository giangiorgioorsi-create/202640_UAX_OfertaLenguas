import streamlit as st
import pandas as pd

# 1. Configuración de la Interfaz
st.set_page_config(page_title="Portal de Oferta Académica 2026", layout="wide")

# 2. Gestión de Estado para el Restablecimiento
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

# --- INICIO DE LA LÓGICA VISUAL ---
try:
    df = cargar_datos()
    st.title("🏛️ Portal de Oferta Académica — Centro de Lenguas")

    # Creamos las pestañas para organizar la experiencia del alumno
    tab_explorar, tab_buscar = st.tabs(["📊 Explorar la Oferta", "🔍 Buscador de Cursos"])

    with tab_explorar:
with tab_explorar:
        st.header("Análisis General de la Oferta 2026")
        
        # Métricas de alto nivel
        m1, m2, m3 = st.columns(3)
        m1.metric("Idiomas", df['Lengua'].nunique())
        m2.metric("Total de Grupos", df['NRC'].count())
        m3.metric("Catedráticos", df['Docente'].nunique())

        st.divider()

        col_a, col_b = st.columns(2)
        with col_a:
            st.write("**Distribución por Idioma**")
            # Conteo simple por lengua
            conteo_lengua = df['Lengua'].value_counts()
            st.bar_chart(conteo_lengua)
            
        with col_b:
            st.write("**Distribución por Modalidad**")
            # Reemplazamos pie_chart por bar_chart para máxima compatibilidad
            conteo_metodo = df['MetodoInstruccion'].value_counts()
            st.bar_chart(conteo_metodo)

        st.info("""
        **Nota Académica:** Esta vista panorámica permite identificar la carga docente y la diversidad 
        de modalidades disponibles para el ciclo 2026.
        """)

    with tab_buscar:
        # TODA la lógica de búsqueda debe estar indentada aquí adentro
        st.subheader("Búsqueda Avanzada de Cursos")
        st.info("Utilice los filtros laterales para encontrar su NRC.")
        
        # --- Lógica de Filtros en Sidebar ---
        st.sidebar.header("Filtros de Búsqueda")
        
        idiomas = sorted(df['Lengua'].unique().tolist())
        sel_idioma = st.sidebar.selectbox(
            "1. Seleccione el Idioma", [""] + idiomas, 
            key=f"idioma_{st.session_state.idioma_key}"
        )
        
        if sel_idioma:
            df_i = df[df['Lengua'] == sel_idioma]
            asignaturas = sorted(df_i['NombreMateria'].unique().tolist())
            sel_asignatura = st.sidebar.selectbox(
                "2. Seleccione la Asignatura", [""] + asignaturas, 
                key=f"asignatura_{st.session_state.asignatura_key}"
            )
            
            if sel_asignatura:
                df_a = df_i[df_i['NombreMateria'] == sel_asignatura]
                horarios = sorted(df_a['HoraInicio'].astype(str).unique().tolist())
                sel_horario = st.sidebar.selectbox(
                    "3. Seleccione el Horario", [""] + horarios, 
                    key=f"horario_{st.session_state.horario_key}"
                )
                
                if sel_horario:
                    resultados = df_a[df_a['HoraInicio'].astype(str) == sel_horario]
                    
                    # Tabla de Resultados
                    st.dataframe(
                        resultados[['Clave Banner', 'NRC', 'Docente', 'HoraInicio', 'HoraFin', 'Status']], 
                        use_container_width=True
                    )
                    
                    st.divider()
                    for _, fila in resultados.iterrows():
                        with st.expander(f"Detalle Técnico — NRC: {fila['NRC']}"):
                            c1, c2 = st.columns(2)
                            with c1:
                                st.write(f"**Clave Banner:** {fila['Clave Banner']}")
                                st.write(f"**Catedrático:** {fila['Docente']}")
                                st.write(f"**Modalidad:** {fila['MetodoInstruccion']}")
                            with c2:
                                st.write(f"**Periodo:** {fila['PartePeriodo']}")
                                st.info(f"**Notas:** {fila['Notas'] if pd.notna(fila['Notas']) else 'Sin observaciones.'}")

        st.sidebar.divider()
        if st.sidebar.button("Restablecer Filtros", on_click=restablecer_filtros):
            st.rerun()

except Exception as e:
    st.error(f"⚠️ Error al cargar la plataforma: {e}")
