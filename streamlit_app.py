# Streamlit demo: Výběr markerů a fluorochromů

import streamlit as st

# Ukázková databáze markerů a typických diagnóz
MARKER_DB = {
    "Leukémie": ["CD45", "CD34", "CD117", "CD13", "CD33"],
    "Imunodeficience": ["CD3", "CD4", "CD8", "CD19", "CD56"],
    "Lymfomy": ["CD20", "CD5", "CD10", "BCL2", "Ki67"]
}

# Ukázková databáze fluorochromů s emisními maximy (nm)
FLUOROCHROM_DB = {
    "FITC": 519,
    "PE": 578,
    "PerCP": 677,
    "APC": 660,
    "Pacific Blue": 455,
    "Alexa Fluor 700": 723
}

def kontroluj_spektralni_konflikt(vybrane):
    konflikt = []
    hodnoty = list(FLUOROCHROM_DB.items())
    for i in range(len(vybrane)):
        for j in range(i+1, len(vybrane)):
            rozdil = abs(hodnoty[i][1] - hodnoty[j][1])
            if rozdil < 40:
                konflikt.append((hodnoty[i][0], hodnoty[j][0]))
    return konflikt

st.title("AI nástroj: Návrh markerů a fluorochromů")

# Výběr klinického scénáře
scenar = st.selectbox("Vyberte klinický scénář:", list(MARKER_DB.keys()))

# Návrh markerů
navrzeno = MARKER_DB[scenar]
st.write(f"**Navržené markery:** {', '.join(navrzeno)}")

# Výběr fluorochromů
st.write("**Zvolte fluorochromy pro každý marker:**")
fluoro_volby = {}
for marker in navrzeno:
    fluoro_volby[marker] = st.selectbox(f"{marker}:", list(FLUOROCHROM_DB.keys()), key=marker)

# Detekce spektrálních konfliktů
zvolene_fluora = list(fluoro_volby.values())
konflikty = kontroluj_spektralni_konflikt(zvolene_fluora)

if konflikty:
    st.warning("Nalezeny spektrální konflikty mezi:")
    for k in konflikty:
        st.write(f"- {k[0]} a {k[1]}")
else:
    st.success("Bez spektrálních konfliktů. Panel je v pořádku.")
