import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

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
    "APC": (660, "633 nm"),
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

# Přibližná spektrální data (vlnová délka, relativní intenzita)
# Poznámka: Tato data lze nahradit přesnějšími spektry z FPbase, Thermo Fisher apod.
SPECTRA_DB = {
    "FITC": [(480, 0.1), (500, 0.5), (519, 1.0), (540, 0.5), (560, 0.2), (580, 0.05)],
    "PE": [(540, 0.1), (560, 0.4), (578, 1.0), (600, 0.6), (620, 0.3), (650, 0.1)],
    "PerCP": [(640, 0.1), (660, 0.5), (677, 1.0), (700, 0.4), (720, 0.1)],
    "APC": [(620, 0.1), (640, 0.5), (660, 1.0), (680, 0.5), (700, 0.2)],
    "Pacific Blue": [(420, 0.1), (440, 0.6), (455, 1.0), (470, 0.5), (490, 0.1)],
    "Alexa Fluor 700": [(680, 0.1), (700, 0.5), (723, 1.0), (740, 0.4), (760, 0.1)],
    "BV421": [(400, 0.1), (410, 0.5), (421, 1.0), (440, 0.5), (460, 0.2)],
    "BV510": [(470, 0.1), (490, 0.5), (510, 1.0), (530, 0.5), (550, 0.2)],
    "BV605": [(570, 0.1), (590, 0.5), (605, 1.0), (620, 0.5), (640, 0.2)],
    "BV711": [(670, 0.1), (690, 0.5), (711, 1.0), (730, 0.5), (750, 0.2)],
    "PE-Cy5.5": [(660, 0.1), (680, 0.5), (695, 1.0), (710, 0.5), (730, 0.2)],
    "PE-Cy7": [(740, 0.1), (760, 0.5), (780, 1.0), (800, 0.4), (820, 0.1)],
    "APC-Cy7": [(740, 0.1), (760, 0.5), (785, 1.0), (800, 0.4), (820, 0.1)],
    "ECD": [(580, 0.1), (600, 0.5), (610, 1.0), (630, 0.5), (650, 0.2)],
    "Pacific Orange": [(520, 0.1), (540, 0.5), (551, 1.0), (570, 0.5), (590, 0.2)],
    "BV650": [(620, 0.1), (640, 0.5), (650, 1.0), (670, 0.5), (690, 0.2)],
    "Alexa Fluor 647": [(630, 0.1), (650, 0.5), (668, 1.0), (690, 0.5), (710, 0.2)],
    "PE-CF594": [(580, 0.1), (600, 0.5), (617, 1.0), (640, 0.5), (660, 0.2)],
    "AmCyan": [(460, 0.1), (480, 0.5), (491, 1.0), (510, 0.5), (530, 0.2)],
    "VioGreen": [(480, 0.1), (500, 0.5), (520, 1.0), (540, 0.5), (560, 0.2)]
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

def generuj_spektra(fluora):
    # Vytvoření grafu emisních spekter
    fig, ax = plt.subplots(figsize=(6, 4))
    vlnove_delky = np.linspace(400, 800, 400)  # Rozsah vlnových délek (nm)
    
    for fluor in set(fluora):  # Použijeme set pro odstranění duplikátů
        laser = FLUOROCHROM_DB[fluor][1]
        barva = LASER_BARVY.get(laser, "gray")
        # Získání spektrálních dat
        spektrum = SPECTRA_DB[fluor]
        vlnove_delky_spektra, intenzity = zip(*spektrum)  # Rozbalení tuple
        # Interpolace pro hladkou křivku
        intenzity_interpol = np.interp(vlnove_delky, vlnove_delky_spektra, intenzity)
        ax.plot(vlnove_delky, intenzity_interpol, label=fluor, color=barva, linewidth=2)
    
    ax.set_xlabel("Vlnová délka (nm)")
    ax.set_ylabel("Relativní intenzita")
    ax.set_title("Emisní spektra vybraných fluorochromů")
    ax.legend()
    ax.grid(True, alpha=0.3)
    plt.tight_layout()
    return fig

st.title("AI nástroj: Návrh panelu a spektrální kompenzace")

scenar = st.selectbox("Vyberte klinický scénář:", list(MARKER_DB.keys()))
navrzeno = MARKER_DB[scenar]
st.write(f"**Navržené markery:** {', '.join(navrzeno)}")

st.write("**Zvolte fluorochromy pro každý marker:**")
fluoro_volby = {}
for marker in navrzeno:
    # Zobrazení názvu markeru
    st.markdown(f"**{marker}:**")
    # Selectbox s prostými názvy fluorochromů
    selected_fluoro = st.selectbox(
        "",
        list(FLUOROCHROM_DB.keys()),
        key=marker,
        label_visibility="collapsed"
    )
    fluoro_volby[marker] = selected_fluoro
    # Zobrazení barevné tečky podle vybraného fluorochromu
    laser = FLUOROCHROM_DB[selected_fluoro][1]
    color = LASER_BARVY.get(laser, "white")
    st.markdown(
        f"<span style='display: inline-flex; align-items: center; font-size: 0.9em; color: #666;'>"
        f"Vybraný laser: <span style='width: 12px; height: 12px; border-radius: 50%; background-color: {color}; margin-left: 8px; margin-right: 8px;'></span>{laser}</span>",
        unsafe_allow_html=True
    )

zvolene_fluora = list(fluoro_volby.values())
konflikty = kontroluj_spektralni_konflikt(zvolene_fluora)

if konflikty:
    st.warning("Nalezeny spektrální konflikty mezi:")
    for k in konflikty:
        st.write(f"- {k[0]} a {k[1]}")
else:
    st.success("Bez spektrálních konfliktů. Panel je v pořádku.")

# Rozdělení layoutu na dva sloupce
col1, col2 = st.columns([1, 1])

with col1:
    st.write("**Předpokládaná kompenzační matice (%):**")
    kompenzace_df = generuj_kompenzaci(zvolene_fluora)

    # Barevné zvýraznění laserů
    def zbarvi_bunky(val):
        laser = FLUOROCHROM_DB[val.name][1] if val.name in FLUOROCHROM_DB else None
        color = LASER_BARVY.get(laser, "white")
        return [f"background-color: {color}" for _ in val]

    st.dataframe(kompenzace_df.style.apply(zbarvi_bunky, axis=1))

with col2:
    st.write("**Emisní spektra vybraných fluorochromů:**")
    fig = generuj_spektra(zvolene_fluora)
    st.pyplot(fig)
