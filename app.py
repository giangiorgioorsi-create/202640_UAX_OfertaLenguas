import streamlit as st
import pandas as pd

# 1. Configurazione Iniziale
st.set_page_config(page_title="Offerta Linguistica 2026", layout="wide")

# 2. Gestione del Reset tramite Session State
# Inizializziamo le chiavi dei filtri se non esistono
if 'lingua_key' not in st.session_state:
    st.session_state.lingua_key = 0
if 'materia_key' not in st.session_state:
    st.session_state.materia_key = 0
if 'orario_key' not in st.session_state:
    st.session_state.orario_key = 0

def reset_filters():
    st.session_state.lingua_key += 1
    st.session_state.materia_key += 1
    st.session_state.orario_key += 1

# 3. Funzione Caricamento Dati
@st.cache_data
def load_data():
    file_name = "202640_UAX_OfertaLenguas.xlsx"
    df = pd.read_excel(file_name)
    df.columns = [c.strip() for c in df.columns]
    return df

try:
    df = load_data()
    st.title("🎓 Offerta Formativa - Centro Linguistico")

    # --- Sidebar ---
    st.sidebar.header("Filtri di Ricerca")
    
    # Filtro 1: Lingua
    lingue = sorted(df['Lengua'].unique().tolist())
    sel_lingua = st.sidebar.selectbox(
        "1. Scegli Lingua", 
        [""] + lingue, 
        key=f"lingua_{st.session_state.lingua_key}"
    )
    
    if sel_lingua:
        # Filtro 2: Materia
        df_l = df[df['Lengua'] == sel_lingua]
        materie = sorted(df_l['NombreMateria'].unique().tolist())
        sel_materia = st.sidebar.selectbox(
            "2. Scegli Materia", 
            [""] + materie, 
            key=f"materia_{st.session_state.materia_key}"
        )
        
        if sel_materia:
            # Filtro 3: Orario
            df_m = df_l[df_l['NombreMateria'] == sel_materia]
            orari = sorted(df_m['HoraInicio'].astype(str).unique().tolist())
            sel_orario = st.sidebar.selectbox(
                "3. Scegli Orario", 
                [""] + orari, 
                key=f"orario_{st.session_state.orario_key}"
            )
            
            if sel_orario:
                # Filtro Finale
                risultato = df_m[df_m['HoraInicio'].astype(str) == sel_orario]
                
                st.subheader(f"Corsi disponibili: {sel_materia}")
                
                # CORREZIONE: Inserita la 'Clave Banner' nella visualizzazione
                st.dataframe(
                    risultato[['Clave Banner', 'NRC', 'Docente', 'HoraInicio', 'HoraFin', 'Status']], 
                    use_container_width=True
                )
                
                # Dettagli espandibili
                st.divider()
                for _, row in risultato.iterrows():
                    with st.expander(f"Dettagli completi NRC: {row['NRC']}"):
                        st.write(f"**Clave Banner:** {row['Clave Banner']}")
                        st.write(f"**Docente:** {row['Docente']}")
                        st.write(f"**Metodo:** {row['MetodoInstruccion']}")
                        st.write(f"**Periodo:** {row['PartePeriodo']}")
                        st.write(f"**Note:** {row['Notas'] if pd.notna(row['Notas']) else 'Nessuna nota'}")

    # Bottone di Reset (Utilizza la funzione definita sopra)
    st.sidebar.divider()
    if st.sidebar.button("Azzera Ricerca", on_click=reset_filters):
        st.rerun()

except Exception as e:
    st.error(f"⚠️ Errore tecnico: {e}")
    st.info("Assicurati che il file Excel nel repository abbia le colonne 'Clave Banner', 'NRC', 'Lengua', 'NombreMateria'.")
