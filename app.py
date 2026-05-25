# --- SECCIÓN DE FILTRADO OPTIMIZADA (UX PROGRESIVA) ---
st.sidebar.header("Filtros de Búsqueda")

nrc_input = st.sidebar.text_input("🔍 Buscar por NRC", key=f"nrc_{st.session_state.rk}")
st.sidebar.divider()

# Inicializamos el dataframe de resultados con una copia completa
df_res = df.copy()

if nrc_input:
    df_res = df_res[df_res['NRC'].str.contains(nrc_input.strip(), na=False)]
else:
    # 1. Filtro de Idioma (Sustituye el espacio vacío por "Todos")
    opciones_idioma = ["Todos"] + sorted(df['Lengua'].unique().tolist())
    idi = st.sidebar.selectbox("1. Idioma", opciones_idioma, key=f"i{st.session_state.rk}")
    
    if idi != "Todos":
        df_res = df_res[df_res['Lengua'] == idi]
        
        # 2. Filtro de Asignatura (Se habilita dinámicamente según el idioma)
        opciones_materia = ["Todas"] + sorted(df_res['NombreMateria'].unique().tolist())
        mat = st.sidebar.selectbox("2. Asignatura", opciones_materia, key=f"m{st.session_state.rk}")
        if mat != "Todas":
            df_res = df_res[df_res['NombreMateria'] == mat]
            
            # 3. Filtro de Modalidad
            opciones_metodo = ["Todas"] + sorted(df_res['MetodoInstruccion'].unique().tolist())
            met = st.sidebar.selectbox("3. Modalidad", opciones_metodo, key=f"e{st.session_state.rk}")
            if met != "Todas":
                df_res = df_res[df_res['MetodoInstruccion'] == met]
                
                # 4. Filtro de Periodo
                opciones_fechas = ["Todos"] + sorted(df_res['Fechas'].unique().tolist())
                fec = st.sidebar.selectbox("4. Periodo", opciones_fechas, key=f"f{st.session_state.rk}")
                if fec != "Todos":
                    df_res = df_res[df_res['Fechas'] == fec]
                    
                    # 5. Filtro de Horario
                    opciones_horario = ["Todos"] + sorted(df_res['Hora_Ref'].unique().tolist())
                    hor = st.sidebar.selectbox("5. Horario", opciones_horario, key=f"h{st.session_state.rk}")
                    if hor != "Todos":
                        df_res = df_res[df_res['Hora_Ref'] == hor]

# --- RENDERIZADO DINÁMICO DE RESULTADOS ---
# En lugar de evaluar 'show_results', mostramos los datos correspondientes al estado actual del dataframe
if df_res.empty:
    st.warning("No se encontraron cursos que coincidan con los filtros seleccionados.")
else:
    # Mostramos un contador de conveniencia para el usuario académico
    st.markdown(f"##### 📚 Se encontraron **{len(df_res.drop_duplicates(subset=['ListaCruzada', 'NRC']))}** cursos disponibles")
    
    # Preparación de la llave para Listas Cruzadas
    df_res['Key'] = df_res.apply(
        lambda r: r['ListaCruzada'] if es_valor_valido(r['ListaCruzada']) else r['NRC'],
        axis=1
    )

    for _, fila in df_res.drop_duplicates(subset=['Key']).iterrows():
        # [Tu lógica exacta de renderizado de tarjetas, recordatorios y st.expander continúa aquí...]
        if es_valor_valido(fila['ListaCruzada']):
            lc = df[df['ListaCruzada'] == fila['ListaCruzada']]
        else:
            lc = df[df['NRC'] == fila['NRC']]

        st.markdown(f"""
        <div class="course-card">
            <h3>{fila['NombreMateria']}</h3>
            <p>
                <b>Docente:</b> {fila['Docente']}<br>
                <b>Horario:</b> {fila['HoraInicio']} – {fila['HoraFin']}
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        # [... Mantén el resto de tu código de visualización intacto ...]
