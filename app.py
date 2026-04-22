import streamlit as st
import pandas as pd

# 1. Configuración Institucional y Estética
st.set_page_config(page_title="Portal de Oferta Académica — Centro de Lenguas", layout="wide")

# CSS personalizado para el estilo "Anáhuac" y tarjetas de cursos
st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    .card { 
        border: 1px solid #e0e0e0; 
        padding: 25px; 
        border-radius: 12px; 
        background-color: #ffffff; 
        margin-bottom: 25px; 
        box-shadow: 0 4px 6px rgba(0,0,0,0.05); 
    }
    .nrc-box { 
        background-color: #ff6600; 
        color: white; 
        padding: 6px 14px; 
        border-radius: 6px; 
        font-weight: bold; 
        display: inline-block; 
        margin: 5px 0;
    }
    .banner-text { 
        color: #444; 
        font-size: 0.9em; 
        font-weight: 700; 
        display: block;
    }
    .stTabs [data-baseweb="tab-list"] { gap: 24px; }
    .stTabs [data-baseweb="tab"] { height: 50px; white-space: pre-wrap; font-weight: 600; }
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
    # Columna auxiliar para comparaciones de tiempo sin errores de formato
    df['Hora_Ref'] = df['HoraInicio'].astype(str)
    return df

try:
    df_full = cargar_datos()
    
    # Encabezado Institucional
    st.markdown("<h1 style='color: #ff6600; margin-bottom: 0;'>🏛️ Portal de Consulta de Oferta Académica</h1>", unsafe_allow_html=True)
    st.markdown("<p style='font-size: 1.1em; color: #666;'>Coordinación del Centro de Lenguas — Ciclo 2026</p>", unsafe_allow_html=True)

    tab_explorar, tab_buscar = st.tabs(["📊 Panorama Institucional", "🔍 Buscador de Asignaturas"])

    with tab_explorar:
        st.subheader("Indicadores de Gestión Académica")
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Idiomas", df_full['Lengua'].nunique())
        c2.metric("Grupos Totales", df_full['NRC'].count())
        c3.metric("Cuerpo Docente", df_full['Docente'].nunique())
        c4.metric("Impacto Est.", "600+")
        
        st.divider()
        col_graf1, col_graf2 = st.columns(2)
        with col_graf1:
            st.write("**Distribución por Idioma**")
            st.bar_chart(df_full['Lengua'].value_counts(), color="#ff6600")
        with col_graf2:
            st.write("**Modalidades de Instrucción**")
            st.bar_chart(df_full['MetodoInstruccion'].value_counts(), color="#ffb380")

    with tab_buscar:
        st.sidebar.header("Criterios de Inscripción")
        
        # Filtros en cascada
        idiomas = sorted(df_full['Lengua'].unique().tolist())
        sel_idioma = st.sidebar.selectbox("1. Idioma", [""] + idiomas, key=f"id_{st.session_state.reset_key}")
        
        if sel_idioma:
            df_i = df_full[df_full['Lengua'] == sel_idioma]
            materias = sorted(df_i['NombreMateria'].unique().tolist())
            sel_materia = st.sidebar.selectbox("2. Asignatura", [""] + materias, key=f"mat_{st.session_state.reset_key}")
            
            if sel_materia:
                df_m = df_i[df_i['NombreMateria'] == sel_materia]
                horarios = sorted(df_m['Hora_Ref'].unique().tolist())
                sel_horario = st.sidebar.selectbox("3. Horario de Inicio", [""] + horarios, key=f"hr_{st.session_state.reset_key}")
                
                if sel_horario:
                    # Identificamos el curso base seleccionado
                    target_cursos = df_m[df_m['Hora_Ref'] == sel_horario]
                    
                    st.success(f"Se muestran los resultados para: **{sel_materia}**")
                    
                    # PROCESO DE LISTA CRUZADA
                    for _, row in target_cursos.iterrows():
                        # Buscamos todos los NRCs que compartan la misma 'huella' académica
                        lista_cruzada = df_full[
                            (df_full['Docente'] == row['Docente']) & 
                            (df_full['Hora_Ref'] == row['Hora_Ref']) & 
                            (df_full['PartePeriodo'] == row['PartePeriodo'])
                        ]
                        
                        # Diseño de Tarjeta de Resultado
                        st.markdown(f"""
                        <div class="card">
                            <h3 style="color: #ff6600; margin-bottom: 5px;">{sel_materia}</h3>
                            <p style="margin: 0;"><strong>Catedrático:</strong> {row['Docente']}</p>
                            <p style="margin: 0;"><strong>Horario:</strong> {row['HoraInicio']} - {row['HoraFin']} | <strong>Modalidad:</strong> {row['MetodoInstruccion']}</p>
                            <hr style="margin: 15px 0; border: 0; border-top: 1px solid #eee;">
                            <p style="font-weight: bold; margin-bottom: 10px;">Grupos disponibles en esta sesión (Lista Cruzada):</p>
                        """, unsafe_allow_html=True)
                        
                        # Desplegamos los NRCs vinculados en columnas
                        cols = st.columns(len(lista_cruzada) if len(lista_cruzada) < 5 else 4)
                        for i, (_, item) in enumerate(lista_cruzada.iterrows()):
                            with cols[i % 4]:
                                st.markdown(f"<div class='nrc-box'>NRC {item['NRC']}</div>", unsafe_allow_html=True)
                                st.markdown(f"<span class='banner-text'>{item['Clave Banner']}</span>", unsafe_allow_html=True)
                                # CAMBIO SOLICITADO: Se muestra la materia debajo del NRC
                                st.caption(item['NombreMateria']) 
                        
                        st.markdown("</div>", unsafe_allow_html=True)
                        
                        with st.expander("Información Académica Adicional"):
                            st.write(f"**Periodo Académico:** {row['PartePeriodo']}")
                            st.write(f"**Estatus Administrativo:** {row['Status']}")
                            st.info(f"**Observaciones:** {row['Notas'] if pd.notna(row['Notas']) else 'Sin comentarios adicionales.'}")

        st.sidebar.divider()
        if st.sidebar.button("🔄 Restablecer Filtros", on_click=restablecer):
            st.rerun()

except Exception as e:
    st.error(f"⚠️ Error en la plataforma: {e}")
