import streamlit as st
import pandas as pd

# Ukázková databáze markerů a typických diagnóz
MARKER_DB = {
    "Leukémie": ["CD45", "CD34", "CD117", "CD13", "CD33"],
    "Imunodeficience": ["CD45", "CD3", "CD4", "CD8", "CD19", "CD56"],
    "Lymfomy": ["CD45", "CD20", "CD5", "CD10", "BCL2", "Ki67"],
    "Monocyty - fenotypizace": ["CD45", "CD14", "CD16", "HLA-DR"],
    "B-lymfocyty - fenotypizace": ["CD45", "CD19", "CD20", "CD27", "IgD", "CD38"],
    "T-lymfocyty - fenotypizace": ["CD45", "CD3", "CD4", "CD8", "CD25", "CD127"]
}

# Fluorochromy s emisními maximy (nm) a laserem
FLUOROCHROM_DB = {
    "FITC": (519, "488 nm"),
    "PE": (578, "488 nm"),
    "PerCP": (677, "488 nm"),
    " APC": (660, "633 nm"),
    "Pacific Blue": (455, "405 nm"),
    "Alexa Fluor 700": (723, "633 nm"),
    "BV421": (421, "405 nm"),
    "BV510": (510, "405 nm"),
    "BV605": (605, "405 nm"),
    "BV711": (711, "405 nm"),
    "PE-Cy5.5": (695, "488 nm"),
    "PE-Cy7": (780, "488 nm"),
    "APC-Cy7": (785, "633 nm"),
    "ECD": (610, "488 nm"),
    "Pacific Orange": (551, "405 nm"),
    "BV650": (650, "405 nm"),
    "Alexa Fluor 647": (668, "633 nm"),
    "PE-CF594": (617, "488 nm"),
    "AmCyan": (491, "405 nm"),
    "VioGreen": (520, "405 nm")
}

LASER_BARVY = {
    "405 nm": "#D6BBF7",  # fialová
    "488 nm": "#A9CCE3",  # světle modrá
    "633 nm": "#F5B7B1"   # světle červená
}

def kontroluj_spektralni_konflikt(vybrane):
    konflikt = []
    hodnoty = [(f, FLUOROCHROM_DB[f][0]) for f in vybrane]
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
                overlap = max(0.0, 100.0 - abs(FLUOROCHROM_DB[r][0] - FLUOROCHROM_DB[c][0])) / 2.5
                row.append(round(overlap, 1))
        data.append(row)
    return pd.DataFrame(data, index=kanaly, columns=kanaly)

st.title("AI nástroj: Návrh panelu a spektrální kompenzace")

scenar = st.selectbox("Vyberte klinický scénář:", list(MARKER_DB.keys()))
navrzeno = MARKER_DB[scenar]
st.write(f"**Navržené markery:** {', '.join(navrzeno)}")

st.write("**Zvolte fluorochromy pro každý marker:**")
# Vytvoření seznamu fluorochromů s barevnými tečkami pro zobrazení
fluoro_display = [
    f"<span style='display: inline-flex; align-items: center;'><span style='width: 12px; height: 12px; border-radius: 50%; background-color: {LASER_BARVY[FLUOROCHROM_DB[f][1]]}; margin-right: 8px;'></span>{f}</span>"
    for f in FLUOROCHROM_DB.keys()
]
# Mapování zobrazených názvů na skutečné hodnoty fluorochromů
fluoro_map = dict(zip(fluoro_display, FLUOROCHROM_DB.keys()))

fluoro_volby = {}
for marker in navrzeno:
    st.markdown(f"**{marker}:**", unsafe_allow_html=True)
    selected_display = st.selectbox(
        "",
        fluoro_display,
        key=marker,
        label_visibility="collapsed"
    )
    fluoro_volby[marker] = fluoro_map[selected_display]

zvolene_fluora = list(fluoro_volby.values())
konflikty = kontroluj_spektralni_konflikt(zvolene_fluora)

if konflikty:
    st.warning("Nalezeny spektrální konflikty mezi:")
    for k in konflikty:
        st.write(f"- {k[0]} a {k[1]}")
else:
    st.success("Bez spektrálních konfliktů. Panel je v pořádku.")

st.write("**Předpokládaná kompenzační matice (%):**")
kompenzace_df = generuj_kompenzaci(zvolene_fluora)

# Barevné zvýraznění laserů
def zbarvi_bunky(val):
    laser = FLUOROCHROM_DB[val.name][1] if val.name in FLUOROCHROM_DB else None
    color = LASER_BARVY.get(laser, "white")
    return [f"background-color: {color}" for _ in val]

st.dataframe(kompenzace_df.style.apply(zbarvi_bunky, axis=1))
