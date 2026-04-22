import streamlit as st
import pandas as pd

# 1. Configuración Institucional
st.set_page_config(page_title="Portal de Oferta Académica 2026", layout="wide")

# CSS para un diseño limpio y profesional
st.markdown("""
    <style>
    .card { 
        border: 1px solid #e0e0e0; padding: 25px; border-radius: 12px; 
        background-color: #ffffff; margin-bottom: 20px; box-shadow: 0 4px 6px rgba(0,0,0,0.05); 
    }
    .nrc-box { 
        background-color: #ff6600; color: white; padding: 6px 12px; 
        border-radius: 6px; font-weight: bold; display: inline-block; margin: 5px 0;
    }
    .banner-text { color: #444; font-size: 0.9em; font-weight: 700; display: block; }
    </style>
    """, unsafe_allow_html=True)

if 'reset_key' not in st.session_state: st.session_state.reset_key = 0
def restablecer(): st.session_state.reset_key += 1

@st.cache_data
def cargar_datos():
    archivo = "202640_UAX_OfertaLenguas.xlsx"
    df = pd.read_excel(archivo)
    df.columns = [c.strip() for c in df.columns]
    df['Hora_Ref'] = df['HoraInicio'].astype(str)
    return df

try:
    df_full = cargar_datos()
    st.markdown("<h1 style='color: #ff6600;'>🏛️ Portal de Consulta Académica</h1>", unsafe_allow_html=True)

    tab_explorar, tab_buscar = st.tabs(["📊 Panorama General", "🔍 Buscador de Asignaturas"])

    with tab_explorar:
        # (Se mantiene igual que la versión anterior para estadísticas)
        c1, c2, c3 = st.columns(3)
        c1.metric("Idiomas", df_full['Lengua'].nunique())
        c2.metric("Grupos Totales", df_full['NRC'].count())
        c3.metric("Docentes", df_full['Docente'].nunique())
        st.divider()
        col_graf1, col_graf2 = st.columns(2)
        with col_graf1: st.bar_chart(df_full['Lengua'].value_counts(), color="#ff6600")
        with col_graf2: st.bar_chart(df_full['MetodoInstruccion'].value_counts(), color="#ffb380")

    with tab_buscar:
        st.sidebar.header("Filtros de Inscripción")
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
                    target_cursos = df_m[df_m['Hora_Ref'] == sel_horario]
                    st.success(f"Resultados para: **{sel_materia}**")
                    
                    for _, row in target_cursos.iterrows():
                        # LÓGICA DE LISTA CRUZADA
                        lista_cruzada = df_full[
                            (df_full['Docente'] == row['Docente']) & 
                            (df_full['Hora_Ref'] == row['Hora_Ref']) & 
                            (df_full['PartePeriodo'] == row['PartePeriodo'])
                        ]
                        
                        es_lista_cruzada = len(lista_cruzada) > 1

                        # Diseño de Tarjeta
                        st.markdown(f"""
                        <div class="card">
                            <h3 style="color: #ff6600; margin-bottom: 5px;">{sel_materia}</h3>
                            <p style="margin: 0;"><strong>Catedrático:</strong> {row['Docente']}</p>
                            <p style="margin: 0;"><strong>Horario:</strong> {row['HoraInicio']} - {row['HoraFin']} | <strong>Modalidad:</strong> {row['MetodoInstruccion']}</p>
                            <hr style="margin: 15px 0; border: 0; border-top: 1px solid #eee;">
                            <p style="font-weight: bold; margin-bottom: 10px;">
                                {"Grupos vinculados en esta sesión (Lista Cruzada):" if es_lista_cruzada else "Información de inscripción:"}
                            </p>
                        """, unsafe_allow_html=True)
                        
                        cols = st.columns(len(lista_cruzada) if len(lista_cruzada) < 5 else 4)
                        for i, (_, item) in enumerate(lista_cruzada.iterrows()):
                            with cols[i % 4]:
                                st.markdown(f"<div class='nrc-box'>NRC {item['NRC']}</div>", unsafe_allow_html=True)
                                st.markdown(f"<span class='banner-text'>{item['Clave Banner']}</span>", unsafe_allow_html=True)
                                
                                # CAMBIO CLAVE: Solo muestra el nombre de la materia si es una lista cruzada
                                if es_lista_cruzada:
                                    st.caption(item['NombreMateria'])
                        
                        st.markdown("</div>", unsafe_allow_html=True)
                        
                        with st.expander("Detalles Académicos"):
                            st.write(f"**Periodo:** {row['PartePeriodo']}")
                            st.info(f"**Notas:** {row['Notas'] if pd.notna(row['Notas']) else 'Sin observaciones.'}")

        st.sidebar.divider()
        if st.sidebar.button("🔄 Restablecer Filtros", on_click=restablecer): st.rerun()

except Exception as e:
    st.error(f"⚠️ Error: {e}")
