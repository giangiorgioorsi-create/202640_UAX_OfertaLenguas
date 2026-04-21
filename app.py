import streamlit as st
import pandas as pd

# Configurazione Pagina
st.set_page_config(page_title="Offerta Lingue 2026", layout="wide")

st.title("🔍 Ricerca Corsi - Centro Linguistico")
st.write("Seleziona i criteri per visualizzare i dettagli del corso.")

# 1. Caricamento Dati
@st.cache_data
def load_data():
    # NOTA: Assicurati che il nome file su GitHub sia esattamente questo (inclusa estensione)
    file_name = "202640_UAX_OfertaLenguas.xlsx"
    df = pd.read_excel(file_name)
    # Pulizia nomi colonne per sicurezza
    df.columns = [c.strip() for c in df.columns]
    return df

try:
    df = load_data()

    # --- SIDEBAR PER FILTRI ---
    st.sidebar.header("Filtri di Ricerca")

    # Filtro 1: Lingua
    lingue = sorted(df['Lengua'].unique().tolist())
    selected_lengua = st.sidebar.selectbox("1. Scegli Lingua", [""] + lingue)

    if selected_lengua:
        # Filtro 2: Materia
        df_l = df[df['Lengua'] == selected_lengua]
        materie = sorted(df_l['NombreMateria'].unique().tolist())
        selected_materia = st.sidebar.selectbox("2. Scegli Materia", [""] + materie)
        
        if selected_materia:
            # Filtro 3: Orario
            df_m = df_l[df_l['NombreMateria'] == selected_materia]
            orari = sorted(df_m['HoraInicio'].astype(str).unique().tolist())
            selected_horario = st.sidebar.selectbox("3. Scegli Orario", [""] + orari)

            # --- VISUALIZZAZIONE RISULTATI ---
            if selected_horario:
                risultato = df_m[df_m['HoraInicio'].astype(str) == selected_horario]

                st.subheader(f"Risultati per {selected_materia}")
                
                # Tabella principale
                st.dataframe(risultato[['NRC', 'Docente', 'HoraInicio', 'HoraFin', 'Status']], use_container_width=True)

                # Dettagli del corso selezionato
                st.divider()
                st.subheader("📋 Dettagli Completi")
                for _, row in risultato.iterrows():
                    with st.expander(f"Dettagli NRC: {row['NRC']}"):
                        col1, col2 = st.columns(2)
                        with col1:
                            st.write(f"**Docente:** {row['Docente']}")
                            # CORREZIONE: 'MetodoInstruccion' senza accento
                            st.write(f"**Metodo:** {row['MetodoInstruccion']}")
                        with col2:
                            # CORREZIONE: 'PartePeriodo' invece di 'Parte del periodo'
                            st.write(f"**Periodo:** {row['PartePeriodo']}")
                            st.write(f"**Note:** {row['Notas'] if pd.notna(row['Notas']) else 'Nessuna nota'}")

    if st.sidebar.button("Reset Filtri"):
        st.rerun()

except Exception as e:
    st.error(f"Errore tecnico: {e}")
    st.info("Controlla che il nome del file su GitHub corrisponda a quello nel codice.")
