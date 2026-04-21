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
