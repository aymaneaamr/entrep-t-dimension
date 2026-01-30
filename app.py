import streamlit as st
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np
from io import BytesIO
import base64

st.set_page_config(
    page_title="Générateur d'Entrepôt",
    page_icon="🏭",
    layout="wide"
)

# CSS personnalisé
st.markdown("""
<style>
    .main-header {
        text-align: center;
        color: #2c3e50;
        padding: 20px 0;
    }
    .stButton>button {
        background-color: #4CAF50;
        color: white;
        font-weight: bold;
        width: 100%;
    }
    .info-box {
        background-color: #e8f4fd;
        padding: 15px;
        border-radius: 10px;
        margin: 10px 0;
    }
    .rack-config {
        background-color: #f9f9f9;
        padding: 15px;
        border-radius: 10px;
        margin: 10px 0;
    }
</style>
""", unsafe_allow_html=True)

# Titre
st.markdown("<h1 class='main-header'>🏭 Générateur de Configuration d'Entrepôt</h1>", unsafe_allow_html=True)

# Sidebar pour les paramètres
with st.sidebar:
    st.header("⚙️ Paramètres de configuration")
    
    col1, col2 = st.columns(2)
    with col1:
        largeur_entrepot = st.number_input("Largeur entrepôt (m)", 10, 200, 50)
        largeur_rack = st.number_input("Largeur rack (m)", 0.5, 5.0, 2.0, 0.5)
        hauteur_rack = st.number_input("Hauteur racks (m)", 2.0, 20.0, 4.0, 0.5)
    with col2:
        longueur_entrepot = st.number_input("Longueur entrepôt (m)", 10, 200, 30)
        longueur_rack = st.number_input("Longueur rack (m)", 1.0, 15.0, 5.0, 0.5)
        nb_rangees = st.number_input("Nombre de rangées", 1, 20, 4)
    
    largeur_allee = st.slider("Largeur allée (m)", 2.0, 15.0, 4.0, 0.5)
    config_type = st.selectbox("Type de configuration", 
                              ["Simple (2 rangées)", "Double (4 rangées)", "Compact (max)"])
    
    # Calculs automatiques
    if st.button("🔄 Calculer automatiquement", use_container_width=True):
        # Logique de calcul automatique (à adapter)
        st.session_state.auto_calc = True
    
    st.markdown("---")
    st.markdown("### 📊 Statistiques estimées")
    
    # Calculs préliminaires
    nb_racks_par_rangee = 4 if "Double" in config_type else 2
    nb_racks_total = nb_rangees * nb_racks_par_rangee * 2  # 2 côtés
    
    st.metric("Nombre total de racks", nb_racks_total)
    surface_stockage = nb_racks_total * largeur_rack * longueur_rack
    st.metric("Surface de stockage (m²)", f"{surface_stockage:.1f}")
    st.metric("Surface totale (m²)", largeur_entrepot * longueur_entrepot)

# Fonction pour générer le schéma
def generate_warehouse_schema(largeur_entrepot, longueur_entrepot, largeur_rack, 
                             longueur_rack, hauteur_rack, nb_rangees, largeur_allee, config_type):
    fig, ax = plt.subplots(figsize=(12, 8))
    
    # Dessiner l'entrepôt
    ax.add_patch(patches.Rectangle((0, 0), largeur_entrepot, longueur_entrepot,
                                   linewidth=2, edgecolor='black', facecolor='none'))
    
    # Configuration selon le type
    if "Simple" in config_type:
        racks_per_side = 2
    elif "Double" in config_type:
        racks_per_side = 4
    else:  # Compact
        racks_per_side = int((largeur_entrepot - largeur_allee - 4) / (largeur_rack + 1) / 2)
    
    # Dessiner les racks
    rack_positions = []
    for r in range(nb_rangees):
        # Côté gauche
        for c in range(racks_per_side):
            x = 2 + c * (largeur_rack + 1)
            y = 2 + r * (longueur_rack + 2)
            rack_positions.append((x, y, 'left'))
        
        # Côté droit
        for c in range(racks_per_side):
            x = 2 + racks_per_side * (largeur_rack + 1) + largeur_allee + c * (largeur_rack + 1)
            y = 2 + r * (longueur_rack + 2)
            rack_positions.append((x, y, 'right'))
    
    # Ajouter les racks
    for idx, (x, y, side) in enumerate(rack_positions):
        color = '#3498db' if side == 'left' else '#2ecc71'
        ax.add_patch(patches.Rectangle((x, y), largeur_rack, longueur_rack,
                                       facecolor=color, edgecolor='darkblue',
                                       alpha=0.8))
        
        # Ajouter les dimensions sur le rack
        ax.text(x + largeur_rack/2, y + longueur_rack/2,
                f'{largeur_rack}m\n×\n{longueur_rack}m',
                ha='center', va='center', fontsize=7, color='white')
    
    # Allée
    alley_x = 2 + racks_per_side * (largeur_rack + 1)
    ax.add_patch(patches.Rectangle((alley_x, 0), largeur_allee, longueur_entrepot,
                                   facecolor='lightgray', alpha=0.5))
    
    # Annotations de dimensions
    # Dimension de l'allée
    ax.annotate(f'{largeur_allee}m', 
                xy=(alley_x + largeur_allee/2, longueur_entrepot - 2),
                ha='center', va='center',
                fontsize=10, color='red',
                arrowprops=dict(arrowstyle='<->', color='red'))
    
    # Dimension totale
    ax.annotate(f'{largeur_entrepot}m',
                xy=(largeur_entrepot/2, -2),
                ha='center', va='center',
                fontsize=12, fontweight='bold')
    
    ax.set_xlim(-5, largeur_entrepot + 5)
    ax.set_ylim(-5, longueur_entrepot + 5)
    ax.set_aspect('equal')
    ax.set_xlabel('Largeur (m)')
    ax.set_ylabel('Longueur (m)')
    ax.set_title(f'Schéma de configuration - {len(rack_positions)} racks')
    ax.grid(True, linestyle='--', alpha=0.3)
    
    return fig, len(rack_positions)

# Bouton de génération
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    if st.button("🚀 Générer le schéma", use_container_width=True):
        with st.spinner("Génération du schéma..."):
            fig, nb_racks = generate_warehouse_schema(
                largeur_entrepot, longueur_entrepot, largeur_rack,
                longueur_rack, hauteur_rack, nb_rangees, largeur_allee, config_type
            )
            
            # Afficher le schéma
            st.pyplot(fig)
            
            # Téléchargement
            buf = BytesIO()
            fig.savefig(buf, format="png", dpi=150)
            st.download_button(
                label="📥 Télécharger l'image",
                data=buf.getvalue(),
                file_name="schema_entrepot.png",
                mime="image/png",
                use_container_width=True
            )
            
            # Informations supplémentaires
            with st.expander("📋 Détails de la configuration"):
                st.write(f"**Nombre de racks générés :** {nb_racks}")
                st.write(f"**Surface par rack :** {largeur_rack} × {longueur_rack} = {largeur_rack * longueur_rack}m²")
                st.write(f"**Surface totale de stockage :** {nb_racks * largeur_rack * longueur_rack:.1f}m²")
                st.write(f"**Utilisation de l'espace :** {(nb_racks * largeur_rack * longueur_rack) / (largeur_entrepot * longueur_entrepot) * 100:.1f}%")
            
            # Prompt pour IA
            st.markdown("---")
            st.markdown("### 🎨 Générer une image réaliste avec IA")
            prompt = f"""Photorealistic warehouse storage layout with {nb_racks} metal racks, {hauteur_rack}m height, {largeur_rack}m x {longueur_rack}m rack size, {largeur_allee}m wide aisles, pallet storage system, forklift in operation, dimension markers, professional lighting, wide-angle view"""
            
            st.code(prompt, language="text")
            st.info("Copiez ce prompt dans DALL·E, Midjourney ou ChatGPT pour générer une image réaliste.")

# Section d'aide
with st.expander("❓ Comment utiliser cette application"):
    st.markdown("""
    1. **Configurez les dimensions** dans la sidebar à gauche
    2. **Cliquez sur 'Générer le schéma'** pour visualiser
    3. **Téléchargez l'image** pour l'utiliser dans vos plans
    4. **Copiez le prompt IA** pour générer une image réaliste
    
    **Conseils :**
    - Allée ≥ 3m pour chariot élévateur
    - Hauteur standard : 6-12m
    - Prévoyez des zones de manœuvre
    """)

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: gray;'>
    <p>Générateur d'entrepôt • Compatible Streamlit Cloud • v1.0</p>
</div>
""", unsafe_allow_html=True)
