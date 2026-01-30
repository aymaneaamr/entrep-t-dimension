import streamlit as st
import pandas as pd

st.set_page_config(
    page_title="Warehouse Optimizer",
    page_icon="🏭",
    layout="wide"
)

st.title("🏭 Entrepôt Dimension Optimizer")
st.markdown("### Configuration pour chariots élévateurs")

with st.sidebar:
    st.header("📐 Dimensions")
    
    col1, col2 = st.columns(2)
    with col1:
        longueur = st.number_input("Longueur (m)", 50.0)
    with col2:
        largeur = st.number_input("Largeur (m)", 30.0)
    
    hauteur = st.number_input("Hauteur (m)", 12.0)
    
    st.divider()
    st.header("📦 Racks")
    
    rack_longueur = st.number_input("L rack (m)", 2.4)
    rack_largeur = st.number_input("l rack (m)", 1.0)
    rack_hauteur = st.number_input("H rack (m)", 10.0)
    
    st.divider()
    st.header("🚜 Chariots élévateurs")
    
    allee = st.slider("Allée chariots (m)", 3.0, 6.0, 4.0)
    type_chariot = st.selectbox("Type chariot", ["Contrebalance", "Télescopique", "Transpalette"])
    
    st.divider()
    st.header("⚙️ Options")
    
    etages = st.slider("Étages par rack", 1, 10, 6)
    palettes = st.number_input("Palettes/emplacement", 1, 4, 2)

# Calculs simples
if st.button("🚀 Calculer la configuration", type="primary"):
    
    # Calculs basiques
    surface = longueur * largeur
    surface_rack = rack_longueur * rack_largeur
    
    # Estimation nombre de racks (formule simplifiée)
    nb_racks = int((longueur * 0.8 / rack_longueur) * (largeur * 0.6 / (rack_largeur + 1)))
    capacite = nb_racks * etages * palettes
    
    # Résultats
    st.success(f"### 📊 Résultats de la configuration")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("🏢 Surface totale", f"{surface:.0f} m²")
        st.metric("📦 Surface rack", f"{surface_rack:.1f} m²")
    
    with col2:
        st.metric("🔢 Nombre de racks", f"{nb_racks}")
        st.metric("🔄 Étages/rack", f"{etages}")
    
    with col3:
        st.metric("📈 Capacité totale", f"{capacite} palettes")
        st.metric("🚜 Type chariot", type_chariot)
    
    with col4:
        st.metric("📏 Allée chariots", f"{allee} m")
        st.metric("✅ Conformité", "✅" if allee >= 3.0 else "⚠️")
    
    # Tableau récapitulatif
    st.divider()
    st.subheader("📋 Configuration générée")
    
    data = {
        'Paramètre': ['Entrepôt', 'Rack', 'Chariots', 'Capacité'],
        'Dimensions': [
            f"{longueur}m × {largeur}m × {hauteur}m",
            f"{rack_longueur}m × {rack_largeur}m × {rack_hauteur}m",
            f"{type_chariot} - Allée {allee}m",
            f"{nb_racks} racks × {etages} étages"
        ],
        'Valeurs': [
            f"{surface:.0f} m²",
            f"{surface_rack:.1f} m² par rack",
            "Conforme" if allee >= 3.0 else "À vérifier",
            f"{capacite} palettes totales"
        ]
    }
    
    df = pd.DataFrame(data)
    st.table(df)
    
    # Export simple
    st.divider()
    st.subheader("💾 Exporter la configuration")
    
    rapport = f"""CONFIGURATION ENTREPÔT
    ====================
    
    ENTREPÔT:
    - Dimensions: {longueur}m × {largeur}m × {hauteur}m
    - Surface: {surface:.0f} m²
    
    RACKS:
    - Dimensions: {rack_longueur}m × {rack_largeur}m × {rack_hauteur}m
    - Nombre: {nb_racks} racks
    - Étages: {etages} par rack
    - Palettes/emplacement: {palettes}
    
    CHARIOTS:
    - Type: {type_chariot}
    - Allée: {allee}m
    - Conformité: {'CONFORME' if allee >= 3.0 else 'À VÉRIFIER'}
    
    CAPACITÉ:
    - Palettes totales: {capacite}
    - Emplacements: {nb_racks * etages}
    
    GÉNÉRÉ LE: {pd.Timestamp.now().strftime('%d/%m/%Y %H:%M')}
    """
    
    st.download_button(
        label="📄 Télécharger le rapport",
        data=rapport,
        file_name="configuration_entrepot.txt",
        mime="text/plain"
    )

# Instructions
with st.expander("ℹ️ Instructions"):
    st.markdown("""
    ### Comment utiliser :
    
    1. **Réglez les dimensions** de votre entrepôt
    2. **Configurez les racks** selon vos palettes
    3. **Choisissez le type de chariot** et l'allée
    4. **Cliquez sur Calculer**
    5. **Exportez** le rapport
    
    ### Normes chariots élévateurs :
    - Allée minimum : **3.0 mètres**
    - Chariots contrebalance : **3.5m recommandé**
    - Hauteur libre : +0.5m au-dessus des charges
    """)

st.caption("🏭 Version simplifiée | Streamlit Cloud Compatible")
