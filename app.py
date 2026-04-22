import streamlit as st
import pandas as pd

# 1. Configuración Institucional
st.set_page_config(page_title="Portal de Oferta Académica — Centro de Lenguas", layout="wide")

# Estilo para destacar los NRCs agrupados
st.markdown("""
    <style>
    .card { border: 1px solid #e6e6e6; padding: 20px; border-radius: 10px; background-color: #ffffff; margin-bottom: 20px; box-shadow: 2px 2px 10px rgba(0,0,0,0.05); }
    .nrc-box { background-color: #ff6600; color: white; padding: 5px 12px; border-radius: 4px; font-weight: bold; display: inline-block; margin: 5px; }
    .banner-text { color: #555; font-size: 0.85em; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

# 2. Gestión de Estado (Reset)
if 'reset_key' not in st.session_state: st.session_state.reset_key = 0

def restablecer():
    st.session_state.reset_key += 1

# 3. Carga de Datos
@st.cache_data
def cargar_datos():
    archivo = "202640_UAX_OfertaLenguas.xlsx"
    df = pd.read_excel(archivo)
    df.columns = [c.strip() for c in df.columns]
    # Asegurar que HoraInicio sea string para comparaciones precisas
    df['Hora_Ref'] = df['HoraInicio'].astype(str)
    return df

try:
    df_full = cargar_datos()
    st.title("🏛️ Buscador Inteligente de Cursos")
    
    tab_explorar, tab_buscar = st.tabs(["📊 Panorama de Oferta", "🔍 Búsqueda por Asignatura"])

    with tab_explorar:
        st.subheader("Estadísticas Generales")
        c1, c2, c3 = st.columns(3)
        c1.metric("Idiomas", df_full['Lengua'].nunique())
        c2.metric("Total Grupos", df_full['NRC'].count())
        c3.metric("Catedráticos", df_full['Docente'].nunique())
        
        col_graf1, col_graf2 = st.columns(2)
        with col_graf1:
            st.write("**Grupos por Idioma**")
            st.bar_chart(df_full['Lengua'].value_counts(), color="#ff6600")
        with col_graf2:
            st.write("**Modalidades**")
            st.bar_chart(df_full['MetodoInstruccion'].value_counts(), color="#ffb380")

    with tab_buscar:
        # --- FILTROS LATERALES (Sidebar) ---
        st.sidebar.header("Criterios de Inscripción")
        
        # Filtro 1: Idioma
        idiomas = sorted(df_full['Lengua'].unique().tolist())
        sel_idioma = st.sidebar.selectbox("1. Idioma", [""] + idiomas, key=f"id_{st.session_state.reset_key}")
        
        if sel_idioma:
            df_i = df_full[df_full['Lengua'] == sel_idioma]
            materias = sorted(df_i['NombreMateria'].unique().tolist())
            sel_materia = st.sidebar.selectbox("2. Asignatura", [""] + materias, key=f"mat_{st.session_state.reset_key}")
            
            if sel_materia:
                df_m = df_i[df_i['NombreMateria'] == sel_materia]
                horarios = sorted(df_m['Hora_Ref'].unique().tolist())
                sel_horario = st.sidebar.selectbox("3. Horario", [""] + horarios, key=f"hr_{st.session_state.reset_key}")
                
                if sel_horario:
                    # A. Encontramos la "materia objetivo" que el alumno buscó
                    target_cursos = df_m[df_m['Hora_Ref'] == sel_horario]
                    
                    st.success(f"Resultados para {sel_materia} en el horario {sel_horario}")
                    
                    # B. LÓGICA DE LISTA CRUZADA
                    # Para cada curso encontrado, buscamos todos los que compartan Docente, Hora y Periodo en TODA la base
                    for _, row in target_cursos.iterrows():
                        # Buscamos en el df_full original para traer los NRCs cruzados
                        lista_cruzada = df_full[
                            (df_full['Docente'] == row['Docente']) & 
                            (df_full['Hora_Ref'] == row['Hora_Ref']) & 
                            (df_full['PartePeriodo'] == row['PartePeriodo'])
                        ]
                        
                        # C. DESPLIEGUE VISUAL AGRUPADO
                        st.markdown(f"""
                        <div class="card">
                            <h3 style="color: #ff6600; margin-bottom: 5px;">{sel_materia}</h3>
                            <p style="margin: 0;"><strong>Catedrático:</strong> {row['Docente']}</p>
                            <p style="margin: 0;"><strong>Horario:</strong> {row['HoraInicio']} - {row['HoraFin']} | <strong>Modalidad:</strong> {row['MetodoInstruccion']}</p>
                            <hr style="margin: 15px 0;">
                            <p><strong>NRC disponibles en esta sesión (Lista Cruzada):</strong></p>
                        """, unsafe_allow_html=True)
                        
                        # Mostramos los NRCs de la lista cruzada lado a lado
                        cols = st.columns(len(lista_cruzada) if len(lista_cruzada) < 5 else 4)
                        for i, (_, item) in enumerate(lista_cruzada.iterrows()):
                            with cols[i % 4]:
                                st.markdown(f"<div class='nrc-box'>NRC {item['NRC']}</div>", unsafe_allow_html=True)
                                st.markdown(f"<span class='banner-text'>{item['Clave Banner']}</span>", unsafe_allow_html=True)
                                st.caption(item['Lengua'])
                        
                        st.markdown("</div>", unsafe_allow_html=True)
                        
                        with st.expander("Ver especificaciones académicas"):
                            st.write(f"**Estatus del grupo:** {row['Status']}")
                            st.write(f"**Periodo:** {row['PartePeriodo']}")
                            st.info(f"**Notas:** {row['Notas'] if pd.notna(row['Notas']) else 'Sin observaciones.'}")

        st.sidebar.divider()
        if st.sidebar.button("🔄 Restablecer Filtros", on_click=restablecer):
            st.rerun()

except Exception as e:
    st.error(f"⚠️ Error en la plataforma: {e}")
