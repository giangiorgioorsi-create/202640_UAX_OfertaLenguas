import streamlit as st
import pandas as pd

# Configurazione Pagina
st.set_page_config(page_title="Offerta Lingue 2026", layout="wide")

st.title("🔍 Ricerca Corsi - Centro Linguistico")
st.write("Seleziona i criteri per visualizzare i dettagli del corso.")

# 1. Caricamento Dati
@st.cache_data
def load_data():
    # Sostituisci con il percorso reale del tuo file
    df = pd.read_excel("Oferta_lenguas_202640.xlsx")
    return df

try:
    df = load_data()

    # --- SIDEBAR PER FILTRI A CASCATA ---
    st.sidebar.header("Filtri di Ricerca")

    # Filtro 1: Lingua
    lingue = sorted(df['Lengua'].unique())
    selected_lengua = st.sidebar.selectbox("1. Scegli Lingua", [""] + lingue)

    if selected_lengua:
        # Filtro 2: Materia (filtrata per lingua)
        materie = sorted(df[df['Lengua'] == selected_lengua]['NombreMateria'].unique())
        selected_materia = st.sidebar.selectbox("2. Scegli Materia", [""] + materie)
        
        if selected_materia:
            # Filtro 3: Orario (filtrato per lingua e materia)
            orari = sorted(df[(df['Lengua'] == selected_lengua) & 
                              (df['NombreMateria'] == selected_materia)]['HoraInicio'].unique())
            selected_horario = st.sidebar.selectbox("3. Scegli Orario", [""] + [str(h) for h in orari])

            # --- VISUALIZZAZIONE RISULTATI ---
            if selected_horario:
                # Filtro finale del dataframe
                risultato = df[(df['Lengua'] == selected_lengua) & 
                               (df['NombreMateria'] == selected_materia) & 
                               (df['HoraInicio'].astype(str) == selected_horario)]

                st.subheader(f"Risultati per {selected_materia}")
                
                # Tabella principale
                st.dataframe(risultato[['NRC', 'Docente', 'HoraInicio', 'HoraFin', 'Status']], use_container_width=True)

                # Dettagli del corso selezionato (se ce n'è più di uno, permette di scegliere l'NRC)
                if len(risultato) > 0:
                    st.divider()
                    st.subheader("📋 Dettagli Completi")
                    for _, row in risultato.iterrows():
                        with st.expander(f"Dettagli NRC: {row['NRC']}"):
                            col1, col2 = st.columns(2)
                            with col1:
                                st.write(f"**Docente:** {row['Docente']}")
                                st.write(f"**Metodo:** {row['MétodoInstruccion']}")
                            with col2:
                                st.write(f"**Periodo:** {row['Parte del periodo']}")
                                st.write(f"**Note:** {row['Notas'] if pd.notna(row['Notas']) else 'Nessuna nota'}")

    # Bottone Reset (Streamlit ricarica l'app)
    if st.sidebar.button("Reset Filtri"):
        st.rerun()

except Exception as e:
    st.error(f"Errore nel caricamento del file: {e}")
    st.info("Assicurati che il file 'Oferta_lenguas_202640.xlsx' sia nella stessa cartella dello script.")
streamlit
pandas
openpyxl
