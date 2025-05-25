# Streamlit demo: Výběr markerů, fluorochromů a interpretace (bez OpenAI, s kompenzací)

import streamlit as st
import pandas as pd

# Ukázková databáze markerů a typických diagnóz
MARKER_DB = {
    "Leukémie": ["CD45", "CD34", "CD117", "CD13", "CD33"],
    "Imunodeficience": ["CD3", "CD4", "CD8", "CD19", "CD56"],
    "Lymfomy": ["CD20", "CD5", "CD10", "BCL2", "Ki67"]
}

# Rozšířená databáze fluorochromů s emisními maximy (nm)
FLUOROCHROM_DB = {
    "FITC": 519,
    "PE": 578,
    "PerCP": 677,
    "APC": 660,
    "Pacific Blue": 455,
    "Alexa Fluor 700": 723,
    "BV421": 421,
    "BV510": 510,
    "BV605": 605,
    "BV711": 711,
    "PE-Cy7": 780,
    "APC-Cy7": 785
}

def kontroluj_spektralni_konflikt(vybrane):
    konflikt = []
    hodnoty = [(f, FLUOROCHROM_DB[f]) for f in vybrane]
    for i in range(len(hodnoty)):
        for j in range(i+1, len(hodnoty)):
            rozdil = abs(hodnoty[i][1] - hodnoty[j][1])
            if rozdil < 40:
                konflikt.append((hodnoty[i][0], hodnoty[j][0]))
    return konflikt

def generuj_kompenzaci(fluora):
    kanaly = list(dict.fromkeys(fluora))  # odstranění duplikátů
    data = []
    for r in kanaly:
        row = []
        for c in kanaly:
            if r == c:
                row.append(100.0)
            else:
                overlap = max(0.0, 100.0 - abs(FLUOROCHROM_DB[r] - FLUOROCHROM_DB[c])) / 2.5
                row.append(round(overlap, 1))
        data.append(row)
    return pd.DataFrame(data, index=kanaly, columns=kanaly)

st.title("AI nástroj: Návrh panelu a spektrální kompenzace")

scenar = st.selectbox("Vyberte klinický scénář:", list(MARKER_DB.keys()))
navrzeno = MARKER_DB[scenar]
st.write(f"**Navržené markery:** {', '.join(navrzeno)}")

st.write("**Zvolte fluorochromy pro každý marker:**")
fluoro_volby = {}
for marker in navrzeno:
    fluoro_volby[marker] = st.selectbox(f"{marker}:", list(FLUOROCHROM_DB.keys()), key=marker)

zvolene_fluora = list(fluoro_volby.values())
konflikty = kontroluj_spektralni_konflikt(zvolene_fluora)

if konflikty:
    st.warning("Nalezeny spektrální konflikty mezi:")
    for k in konflikty:
        st.write(f"- {k[0]} a {k[1]}")
else:
    st.success("Bez spektrálních konfliktů. Panel je v pořádku.")

st.write("**Předpokládaná kompenzační matice (%):**")
st.dataframe(generuj_kompenzaci(zvolene_fluora))
