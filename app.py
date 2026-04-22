import streamlit as st
import pandas as pd

# 1. Configuración Institucional
st.set_page_config(page_title="Portal de Oferta Académica 2026", layout="wide")

# Estilos CSS (Estética Anáhuac)
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
    .legend-box { 
        background-color: #f0f2f6; padding: 12px; border-radius: 8px; 
        font-size: 0.85em; color: #444; border-left: 5px solid #ff6600; 
    }
    </style>
    """, unsafe_allow_html=True)

# 2. Gestión de Estado (Reset)
filtros = ['idioma', 'asignatura', 'metodo', 'fechas', 'horario']
for f in filtros:
    if f"{f}_key" not in st.session_state:
        st.session_state[f"{f}_key"] = 0

def restablecer_filtros():
    for f in filtros:
        st.session_state[f"{f}_key"] += 1

@st.cache_data
def cargar_datos():
    archivo = "202640_UAX_OfertaLenguas.xlsx"
    df = pd.read_excel(archivo, dtype={'Weekdays': str})
    df.columns = [c.strip() for c in df.columns]
    df['Hora_Ref'] = df['HoraInicio'].astype(str)
    return df

try:
    df_full = cargar_datos()
    st.markdown("<h1 style='color: #ff6600;'>🏛️ Portal de Consulta Académica</h1>", unsafe_allow_html=True)

    tab_explorar, tab_buscar = st.tabs(["📊 Panorama General", "🔍 Buscador de Asignaturas"])

    with tab_explorar:
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
        
        # Filtro 1: Idioma
        idiomas = sorted(df_full['Lengua'].unique().tolist())
        sel_idioma = st.sidebar.selectbox("1. Idioma", [""] + idiomas, key=f"id_{st.session_state.idioma_key}")
        
        if sel_idioma:
            df_f = df_full[df_full['Lengua'] == sel_idioma]
            
            # Filtro 2: Asignatura
            materias = sorted(df_f['NombreMateria'].unique().tolist())
            sel_materia = st.sidebar.selectbox("2. Asignatura", [""] + materias, key=f"mat_{st.session_state.asignatura_key}")
            
            if sel_materia:
                df_f = df_f[df_f['NombreMateria'] == sel_materia]
                
                # Filtro 3: Modalidad
                metodos = sorted(df_f['MetodoInstruccion'].unique().tolist())
                sel_metodo = st.sidebar.selectbox("3. Modalidad", [""] + metodos, key=f"met_{st.session_state.metodo_key}")
                
                if sel_metodo:
                    df_f = df_f[df_f['MetodoInstruccion'] == sel_metodo]
                    
                    # Filtro 4: Fechas
                    periodos = sorted(df_f['Fechas'].unique().tolist())
                    sel_fecha = st.sidebar.selectbox("4. Periodo / Fechas", [""] + periodos, key=f"fec_{st.session_state.fechas_key}")
                    
                    if sel_fecha:
                        df_f = df_f[df_f['Fechas'] == sel_fecha]
                        
                        # Filtro 5: Horario
                        horarios = sorted(df_f['Hora_Ref'].unique().tolist())
                        sel_horario = st.sidebar.selectbox("5. Horario", [""] + horarios, key=f"hr_{st.session_state.horario_key}")
                        
                        if sel_horario:
                            target_cursos = df_f[df_f['Hora_Ref'] == sel_horario]
                            st.success(f"Resultados para: **{sel_materia}**")
                            
                            # Evitamos duplicados en las tarjetas de resultados
                            for idx, row in target_cursos.drop_duplicates(subset=['Docente', 'Hora_Ref', 'Fechas']).iterrows():
                                
                                # CORRECCIÓN: Filtramos la lista cruzada por NombreMateria para separar A de B
                                lista_cruzada = df_full[
                                    (df_full['Docente'] == row['Docente']) & 
                                    (df_full['Hora_Ref'] == row['Hora_Ref']) & 
                                    (df_full['Fechas'] == row['Fechas']) &
                                    (df_full['NombreMateria'] == row['NombreMateria'])
                                ]
                                
                                es_lista_cruzada = len(lista_cruzada) > 1

                                st.markdown(f"""
                                <div class="card">
                                    <h3 style="color: #ff6600; margin-bottom: 5px;">{sel_materia}</h3>
                                    <p style="margin: 0;"><strong>Catedrático:</strong> {row['Docente']}</p>
                                    <p style="margin: 0;"><strong>Horario:</strong> {row['HoraInicio']} - {row['HoraFin']}</p>
                                    <p style="margin: 0;"><strong>Modalidad:</strong> {row['MetodoInstruccion']} | <strong>Fechas:</strong> {row['Fechas']}</p>
                                    <hr style="margin: 15px 0; border: 0; border-top: 1px solid #eee;">
                                    <p style="font-weight: bold; margin-bottom: 10px;">
                                        {"Grupos vinculados (Lista Cruzada):" if es_lista_cruzada else "Información de inscripción:"}
                                    </p>
                                """, unsafe_allow_html=True)
                                
                                cols = st.columns(len(lista_cruzada) if len(lista_cruzada) < 5 else 4)
                                for i, (_, item) in enumerate(lista_cruzada.iterrows()):
                                    with cols[i % 4]:
                                        st.markdown(f"<div class='nrc-box'>NRC {item['NRC']}</div>", unsafe_allow_html=True)
                                        st.markdown(f"<span class='banner-text'>{item['ClaveBanner']}</span>", unsafe_allow_html=True)
                                
                                st.markdown("</div>", unsafe_allow_html=True)
                                
                                with st.expander("📚 Detalles Académicos Completos"):
                                    col_d1, col_d2 = st.columns(2)
                                    with col_d1:
                                        st.write(f"**Créditos:** {row['CreditosAcademicos']}")
                                        st.write(f"**Estatus:** {row['Status']}")
                                        st.write(f"**ID Banner:** {row['ClaveBanner']}")
                                    
                                    with col_d2:
                                        dias_raw = str(row['Weekdays']) if pd.notna(row['Weekdays']) else "No especificado"
                                        st.write(f"**Días (1-7):** `{dias_raw}`")
                                        st.markdown("<div class='legend-box'>1: Lun | 2: Mar | 3: Mié | 4: Jue | 5: Vie | 6: Sáb | 7: Dom</div>", unsafe_allow_html=True)
                                        
                                    st.divider()
                                    st.info(f"**Notas:** {row['Notas'] if pd.notna(row['Notas']) else 'Sin observaciones.'}")

        st.sidebar.divider()
        if st.sidebar.button("🔄 Restablecer Filtros", on_click=restablecer_filtros):
            st.rerun()

except Exception as e:
    st.error(f"⚠️ Error en la plataforma: {e}")
