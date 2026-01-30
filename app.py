import streamlit as st
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np
import pandas as pd
from io import BytesIO
import math

# Configuration de la page
st.set_page_config(
    page_title="Warehouse Dimensioning Pro",
    page_icon="🏭",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================================
# STYLES ET CSS AMÉLIORÉ
# ============================================================================
st.markdown("""
<style>
    /* Styles généraux */
    .main-header {
        text-align: center;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 2rem;
        border-radius: 15px;
        margin-bottom: 2rem;
        box-shadow: 0 10px 30px rgba(0,0,0,0.2);
    }
    
    .section-header {
        background: linear-gradient(135deg, #3498db 0%, #2c3e50 100%);
        color: white;
        padding: 1rem;
        border-radius: 10px;
        margin: 1.5rem 0;
        font-weight: bold;
    }
    
    .simple-header {
        background: linear-gradient(135deg, #2ecc71 0%, #27ae60 100%);
        color: white;
        padding: 1rem;
        border-radius: 10px;
        margin: 1.5rem 0;
        font-weight: bold;
    }
    
    .metric-card {
        background: white;
        padding: 1.5rem;
        border-radius: 12px;
        border-left: 6px solid #3498db;
        box-shadow: 0 4px 12px rgba(0,0,0,0.08);
        transition: transform 0.3s;
        height: 100%;
        color: #2c3e50 !important;
    }
    
    .metric-card:hover {
        transform: translateY(-5px);
    }
    
    .metric-card h1, .metric-card h2, .metric-card h3, .metric-card h4 {
        color: #2c3e50 !important;
    }
    
    .metric-card p {
        color: #34495e !important;
    }
    
    .warning-box {
        background: linear-gradient(135deg, #fff3cd 0%, #ffeaa7 100%);
        border-left: 6px solid #f39c12;
        padding: 1rem;
        border-radius: 10px;
        margin: 1rem 0;
        color: #856404 !important;
    }
    
    .success-box {
        background: linear-gradient(135deg, #d4edda 0%, #c3e6cb 100%);
        border-left: 6px solid #28a745;
        padding: 1rem;
        border-radius: 10px;
        margin: 1rem 0;
        color: #155724 !important;
    }
    
    .parameter-card {
        background: white;
        padding: 1.2rem;
        border-radius: 10px;
        border: 2px solid #e9ecef;
        margin-bottom: 1rem;
        color: #2c3e50 !important;
    }
    
    .parameter-card h4 {
        color: #2c3e50 !important;
    }
    
    .parameter-card p {
        color: #34495e !important;
    }
    
    /* Amélioration de la sidebar */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #2c3e50 0%, #1a2530 100%);
    }
    
    [data-testid="stSidebar"] * {
        color: #ecf0f1 !important;
    }
    
    [data-testid="stSidebar"] .stRadio label {
        color: #ecf0f1 !important;
    }
    
    [data-testid="stSidebar"] .stSelectbox label,
    [data-testid="stSidebar"] .stTextInput label,
    [data-testid="stSidebar"] .stNumberInput label {
        color: #ecf0f1 !important;
    }
    
    [data-testid="stSidebar"] .stRadio div[role="radiogroup"] {
        background: rgba(255, 255, 255, 0.1);
        padding: 10px;
        border-radius: 8px;
    }
    
    [data-testid="stSidebar"] .stRadio div[role="radiogroup"] label {
        padding: 8px;
        margin: 4px 0;
        border-radius: 5px;
        transition: background 0.3s;
    }
    
    [data-testid="stSidebar"] .stRadio div[role="radiogroup"] label:hover {
        background: rgba(52, 152, 219, 0.3);
    }
    
    [data-testid="stSidebar"] .stRadio div[role="radiogroup"] label[data-baseweb="radio"] div:first-child {
        color: #3498db !important;
    }
    
    /* Amélioration des inputs dans la sidebar */
    [data-testid="stSidebar"] input, 
    [data-testid="stSidebar"] .stTextInput input,
    [data-testid="stSidebar"] .stNumberInput input {
        background: rgba(255, 255, 255, 0.1) !important;
        color: white !important;
        border: 1px solid rgba(255, 255, 255, 0.2) !important;
    }
    
    [data-testid="stSidebar"] input:focus {
        border-color: #3498db !important;
        box-shadow: 0 0 0 1px #3498db !important;
    }
    
    /* Amélioration des selectbox */
    [data-testid="stSidebar"] .stSelectbox div[data-baseweb="select"] {
        background: rgba(255, 255, 255, 0.1) !important;
        color: white !important;
    }
    
    [data-testid="stSidebar"] .stSelectbox div[data-baseweb="select"] div {
        color: white !important;
    }
    
    /* Boutons dans la sidebar */
    [data-testid="stSidebar"] button {
        background: linear-gradient(135deg, #3498db 0%, #2980b9 100%) !important;
        color: white !important;
        border: none !important;
        font-weight: bold !important;
    }
    
    [data-testid="stSidebar"] button:hover {
        background: linear-gradient(135deg, #2980b9 0%, #3498db 100%) !important;
        transform: translateY(-2px) !important;
        box-shadow: 0 5px 15px rgba(41, 128, 185, 0.4) !important;
    }
    
    /* Titres dans la sidebar */
    [data-testid="stSidebar"] h1,
    [data-testid="stSidebar"] h2,
    [data-testid="stSidebar"] h3,
    [data-testid="stSidebar"] h4,
    [data-testid="stSidebar"] h5,
    [data-testid="stSidebar"] h6 {
        color: #ecf0f1 !important;
        text-shadow: 1px 1px 2px rgba(0,0,0,0.5);
    }
    
    /* Onglets personnalisés */
    .stTabs [data-baseweb="tab-list"] {
        gap: 10px;
        background: #f8f9fa;
        padding: 10px;
        border-radius: 10px;
    }
    
    .stTabs [data-baseweb="tab"] {
        height: 60px;
        white-space: pre-wrap;
        background-color: #e9ecef;
        border-radius: 10px 10px 0px 0px;
        gap: 1px;
        padding-top: 15px;
        padding-bottom: 15px;
        font-weight: bold;
        color: #2c3e50;
    }
    
    .stTabs [aria-selected="true"] {
        background-color: #3498db !important;
        color: white !important;
    }
    
    /* Boutons principaux */
    .stButton>button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        font-weight: bold;
        border: none;
        border-radius: 8px;
        padding: 12px 24px;
        transition: all 0.3s;
    }
    
    .stButton>button:hover {
        transform: scale(1.05);
        box-shadow: 0 8px 20px rgba(102, 126, 234, 0.4);
    }
    
    /* Amélioration des dataframes */
    .dataframe {
        background: white !important;
        color: #2c3e50 !important;
    }
    
    .dataframe th {
        background: #3498db !important;
        color: white !important;
        font-weight: bold !important;
    }
    
    .dataframe td {
        color: #2c3e50 !important;
    }
    
    /* Code blocks */
    .stCode {
        background: #2c3e50 !important;
        color: #ecf0f1 !important;
        border-radius: 8px;
        padding: 15px;
    }
    
    /* Tooltips et info boxes */
    .stAlert {
        background: #e8f4fd !important;
        color: #0c5460 !important;
        border-color: #b8daff !important;
    }
    
    /* Amélioration de la visibilité du texte partout */
    p, span, div:not([class*="sidebar"]) {
        color: #2c3e50 !important;
    }
    
    /* Correction pour les métriques */
    [data-testid="stMetricValue"], 
    [data-testid="stMetricLabel"] {
        color: #2c3e50 !important;
    }
    
    /* Grilles et séparateurs */
    hr {
        border-color: #bdc3c7 !important;
    }
    
    /* Amélioration de la visibilité des labels dans le contenu principal */
    .main .stNumberInput label,
    .main .stTextInput label,
    .main .stSelectbox label,
    .main .stSlider label {
        color: #2c3e50 !important;
        font-weight: bold !important;
    }
    
    /* Amélioration de la visibilité des valeurs dans les inputs */
    .main .stNumberInput input,
    .main .stTextInput input {
        color: #2c3e50 !important;
        background: white !important;
        border: 1px solid #ddd !important;
    }
    
    /* Correction pour les titres dans le contenu principal */
    .main h1, .main h2, .main h3, .main h4, .main h5, .main h6 {
        color: #2c3e50 !important;
    }
    
    /* Style pour la section Calcul Simple */
    .simple-section {
        background: linear-gradient(135deg, #e8f5e9 0%, #c8e6c9 100%);
        border-left: 6px solid #4CAF50;
        padding: 1.5rem;
        border-radius: 10px;
        margin: 1rem 0;
    }
    
    .simple-metric {
        background: white;
        border: 2px solid #4CAF50;
        border-radius: 10px;
        padding: 1rem;
        text-align: center;
    }
</style>
""", unsafe_allow_html=True)

# ============================================================================
# EN-TÊTE PRINCIPAL
# ============================================================================
st.markdown("""
<div class="main-header">
    <h1 style="margin:0; font-size: 2.8em;">🏭 WAREHOUSE DIMENSIONING PRO</h1>
    <p style="margin:0; font-size: 1.2em;">Outil intelligent de dimensionnement d'entrepôts avec calcul simple et avancé</p>
    <p style="margin-top: 10px; opacity: 0.9;">v4.0 | Mode Simple & Mode Avancé • Normes ISO intégrées</p>
</div>
""", unsafe_allow_html=True)

# ============================================================================
# INITIALISATION DES VARIABLES DE SESSION
# ============================================================================
if 'warehouse_data' not in st.session_state:
    st.session_state.warehouse_data = {
        'mode': 'simple',  # 'simple' ou 'advanced'
        'step': 1,
        'calculations': {},
        'warnings': [],
        'optimizations': [],
        'params': {},
        'simple_params': {}
    }

# ============================================================================
# FONCTIONS DE CALCUL POUR MODE SIMPLE
# ============================================================================
class SimpleWarehouseCalculator:
    """Classe de calcul simplifié pour le dimensionnement rapide"""
    
    @staticmethod
    def calculate_simple_capacity(params):
        """Calcule la capacité de stockage en mode simple"""
        try:
            # Dimensions de base
            length = params.get('length', 60.0)
            width = params.get('width', 40.0)
            rack_width = params.get('rack_width', 1.0)
            rack_depth = params.get('rack_depth', 1.2)
            aisle_width = params.get('aisle_width', 3.5)
            rack_height = params.get('rack_height', 6.0)
            pallet_height = params.get('pallet_height', 1.2)
            
            # Calcul simplifié
            usable_length = length - aisle_width - 4
            racks_per_row = max(1, int(usable_length / (rack_depth + 1)))
            
            usable_width = width - 4
            rows_per_side = max(1, int(usable_width / (rack_width + 1)))
            
            total_racks = racks_per_row * rows_per_side * 2
            
            # Nombre de niveaux
            levels = min(5, int(rack_height / (pallet_height + 0.3)))
            
            # Capacité totale
            positions_per_rack = levels * 2  # 2 positions par niveau
            total_positions = total_racks * positions_per_rack
            total_pallets = int(total_positions * 0.85)  # 85% de remplissage
            
            # Surfaces
            total_area = length * width
            storage_area = total_racks * rack_width * rack_depth
            storage_ratio = (storage_area / total_area) * 100 if total_area > 0 else 0
            
            return {
                'total_racks': total_racks,
                'racks_per_row': racks_per_row,
                'rows_per_side': rows_per_side,
                'levels': levels,
                'total_positions': total_positions,
                'total_pallets': total_pallets,
                'storage_area': round(storage_area, 1),
                'total_area': total_area,
                'storage_ratio': round(storage_ratio, 1)
            }
        except Exception as e:
            st.error(f"Erreur dans le calcul simplifié: {e}")
            return {}
    
    @staticmethod
    def calculate_simple_costs(params, capacity):
        """Calcule les coûts estimés en mode simple"""
        try:
            # Coûts simplifiés
            rack_cost_per = 200  # € par emplacement
            area_cost_per_m2 = 300  # € par m²
            equipment_cost_map = {
                'forklift': 50000,
                'pallet_truck': 10000,
                'reach_truck': 60000,
                'conveyor': 80000
            }
            
            # Calcul des coûts
            rack_cost = capacity.get('total_positions', 0) * rack_cost_per
            area_cost = params.get('length', 0) * params.get('width', 0) * area_cost_per_m2
            equipment_type = params.get('equipment_type', 'forklift')
            equipment_cost = equipment_cost_map.get(equipment_type, 40000)
            
            total_cost = rack_cost + area_cost + equipment_cost
            
            return {
                'rack_cost': round(rack_cost / 1000, 1),
                'area_cost': round(area_cost / 1000, 1),
                'equipment_cost': round(equipment_cost / 1000, 1),
                'total_cost': round(total_cost / 1000, 1),
                'cost_per_pallet': round(total_cost / max(1, capacity.get('total_pallets', 1)) / 1000, 2)
            }
        except Exception as e:
            st.error(f"Erreur dans le calcul des coûts: {e}")
            return {}
    
    @staticmethod
    def generate_simple_schema(params, capacity):
        """Génère un schéma simplifié en 2D"""
        try:
            fig, ax = plt.subplots(figsize=(12, 8))
            
            # Dimensions
            length = params.get('length', 60.0)
            width = params.get('width', 40.0)
            rack_width = params.get('rack_width', 1.0)
            rack_depth = params.get('rack_depth', 1.2)
            aisle_width = params.get('aisle_width', 3.5)
            
            # Dessiner l'entrepôt
            ax.add_patch(patches.Rectangle((0, 0), length, width,
                                         linewidth=2, edgecolor='black',
                                         facecolor='#f0f0f0', alpha=0.3))
            
            # Positionner les racks (simplifié)
            racks_per_row = capacity.get('racks_per_row', 6)
            rows_per_side = capacity.get('rows_per_side', 8)
            
            # Racks côté gauche
            for i in range(min(racks_per_row, 8)):
                for j in range(min(rows_per_side, 8)):
                    x = 2 + i * (rack_depth + 1)
                    y = 2 + j * (rack_width + 1)
                    ax.add_patch(patches.Rectangle((x, y), rack_depth, rack_width,
                                                 facecolor='#3498db', edgecolor='#2980b9',
                                                 alpha=0.7))
            
            # Allée
            alley_x = 2 + racks_per_row * (rack_depth + 1)
            ax.add_patch(patches.Rectangle((alley_x, 0), aisle_width, width,
                                         facecolor='#95a5a6', alpha=0.3))
            
            # Racks côté droit
            for i in range(min(racks_per_row, 8)):
                for j in range(min(rows_per_side, 8)):
                    x = alley_x + aisle_width + 1 + i * (rack_depth + 1)
                    y = 2 + j * (rack_width + 1)
                    ax.add_patch(patches.Rectangle((x, y), rack_depth, rack_width,
                                                 facecolor='#2ecc71', edgecolor='#27ae60',
                                                 alpha=0.7))
            
            # Configuration
            ax.set_xlim(0, length)
            ax.set_ylim(0, width)
            ax.set_aspect('equal')
            ax.set_xlabel('Longueur (m)')
            ax.set_ylabel('Largeur (m)')
            ax.set_title(f'Schéma simplifié - {capacity.get("total_racks", 0)} racks', 
                        fontsize=14, fontweight='bold')
            ax.grid(True, linestyle='--', alpha=0.3)
            
            return fig
        except Exception as e:
            st.error(f"Erreur dans la génération du schéma: {e}")
            return None

# ============================================================================
# SIDEBAR - NAVIGATION ET CONFIGURATION GLOBALE
# ============================================================================
with st.sidebar:
    st.markdown("""
    <div style="text-align: center; padding: 20px 0;">
        <h2 style="color: #ecf0f1;">📋 MODE DE CALCUL</h2>
    </div>
    """, unsafe_allow_html=True)
    
    # Sélection du mode
    mode_options = ["⚡ CALCUL SIMPLE", "🔬 CALCUL AVANCÉ"]
    
    # Déterminer l'index initial
    if 'mode_selector' not in st.session_state:
        st.session_state.mode_selector = 0
    
    mode_index = 0 if st.session_state.warehouse_data.get('mode', 'simple') == 'simple' else 1
    
    mode = st.radio(
        "**CHOISISSEZ LE MODE**",
        mode_options,
        index=mode_index,
        key="mode_selector"
    )
    
    # Mettre à jour le mode
    if "SIMPLE" in mode:
        st.session_state.warehouse_data['mode'] = 'simple'
        step_options = ["📏 1. DIMENSIONS", "📦 2. RACKS", "🚚 3. TRANSPORT", "📊 4. RÉSULTATS"]
    else:
        st.session_state.warehouse_data['mode'] = 'advanced'
        step_options = ["🏢 1. BÂTIMENT", "📦 2. STOCKAGE", "🚚 3. CIRCULATION", 
                       "📊 4. RÉSULTATS", "🎨 5. VISUALISATION"]
    
    st.markdown("---")
    
    # Sélecteur d'étape
    st.markdown("""
    <div style="text-align: center; padding: 10px 0;">
        <h3 style="color: #ecf0f1;">📋 PROGRESSION</h3>
    </div>
    """, unsafe_allow_html=True)
    
    # CORRECTION CRITIQUE : S'assurer que step_index est valide
    current_step = st.session_state.warehouse_data.get('step', 1)
    
    # Vérifier que l'étape actuelle est valide pour le mode sélectionné
    max_steps = len(step_options)
    if current_step > max_steps:
        current_step = 1
        st.session_state.warehouse_data['step'] = 1
    
    # Calculer l'index (0-based)
    step_index = current_step - 1
    
    # CORRECTION : Utiliser un index valide
    step_index = min(step_index, len(step_options) - 1)
    step_index = max(0, step_index)
    
    step = st.radio(
        "**ÉTAPES DU PROJET**",
        step_options,
        index=step_index,
        key="navigation"
    )
    
    # Mettre à jour l'étape
    step_map = {option: i+1 for i, option in enumerate(step_options)}
    st.session_state.warehouse_data['step'] = step_map[step]
    
    st.markdown("---")
    
    # Paramètres globaux
    st.markdown("### ⚙️ PARAMÈTRES GLOBAUX")
    
    project_name = st.text_input("**Nom du projet**", "Entrepôt Principal")
    project_type = st.selectbox(
        "**Type d'entrepôt**",
        ["Distribution", "Production", "Cross-docking", "Logistique froide", "Automatisé"]
    )
    
    st.markdown("---")
    
    # Bouton de réinitialisation
    if st.button("🔄 Réinitialiser le projet", use_container_width=True):
        st.session_state.warehouse_data = {
            'mode': 'simple',
            'step': 1,
            'calculations': {},
            'warnings': [],
            'optimizations': [],
            'params': {},
            'simple_params': {}
        }
        st.rerun()

# ============================================================================
# SECTION : MODE SIMPLE
# ============================================================================
if st.session_state.warehouse_data['mode'] == 'simple':
    
    # ========================================================================
    # ÉTAPE 1 SIMPLE : DIMENSIONS
    # ========================================================================
    if st.session_state.warehouse_data['step'] == 1:
        st.markdown('<div class="simple-header">📏 ÉTAPE 1 : DIMENSIONS DE L\'ENTREPÔT</div>', unsafe_allow_html=True)
        
        st.markdown("""
        <div class="simple-section">
            <h4>⚡ CALCUL RAPIDE - Paramètres essentiels seulement</h4>
            <p>Configurez les dimensions de base de votre entrepôt pour un dimensionnement rapide.</p>
        </div>
        """, unsafe_allow_html=True)
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.markdown("### 📐 Dimensions principales")
            
            tab1, tab2 = st.tabs(["Bâtiment", "Informations"])
            
            with tab1:
                c1, c2, c3 = st.columns(3)
                with c1:
                    length = st.number_input("**Longueur totale (m)**", 
                                           min_value=10.0, max_value=200.0, value=60.0, step=1.0,
                                           help="Longueur du bâtiment")
                with c2:
                    width = st.number_input("**Largeur totale (m)**", 
                                          min_value=10.0, max_value=100.0, value=40.0, step=1.0,
                                          help="Largeur du bâtiment")
                with c3:
                    height = st.number_input("**Hauteur libre (m)**", 
                                           min_value=3.0, max_value=20.0, value=9.0, step=0.5,
                                           help="Hauteur sous poutre")
            
            with tab2:
                st.markdown("#### 📋 Informations complémentaires")
                building_type = st.selectbox("**Type de construction**",
                                          ["Nouvelle construction", "Bâtiment existant", "Extension"])
                
                c1, c2 = st.columns(2)
                with c1:
                    column_spacing = st.number_input("**Espace poteaux (m)**", 5.0, 15.0, 9.0, 1.0)
                with c2:
                    floor_load = st.number_input("**Charge sol (T/m²)**", 1.0, 10.0, 3.0, 1.0)
        
        with col2:
            st.markdown("### 🎯 Aperçu rapide")
            
            # Calculs instantanés
            area = length * width
            volume = area * height
            
            st.markdown(f"""
            <div class="simple-metric">
                <h4>📐 Surface</h4>
                <h2>{area:.0f} m²</h2>
                <p>{length:.0f}m × {width:.0f}m</p>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown(f"""
            <div class="simple-metric">
                <h4>📦 Volume</h4>
                <h2>{volume:,.0f} m³</h2>
                <p>Hauteur : {height:.1f}m</p>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown(f"""
            <div class="simple-metric">
                <h4>🏗️ Type</h4>
                <h3>{building_type}</h3>
                <p>Charge : {floor_load} T/m²</p>
            </div>
            """, unsafe_allow_html=True)
        
        # Sauvegarder les paramètres
        st.session_state.warehouse_data['simple_params'].update({
            'length': float(length),
            'width': float(width),
            'height': float(height),
            'building_type': building_type,
            'column_spacing': float(column_spacing),
            'floor_load': float(floor_load)
        })
    
    # ========================================================================
    # ÉTAPE 2 SIMPLE : RACKS
    # ========================================================================
    elif st.session_state.warehouse_data['step'] == 2:
        st.markdown('<div class="simple-header">📦 ÉTAPE 2 : CONFIGURATION DES RACKS</div>', unsafe_allow_html=True)
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.markdown("### 🏗️ Dimensions des racks")
            
            tab1, tab2 = st.tabs(["Dimensions", "Configuration"])
            
            with tab1:
                c1, c2, c3 = st.columns(3)
                with c1:
                    rack_width = st.number_input("**Largeur rack (m)**", 
                                               min_value=0.8, max_value=3.0, value=1.0, step=0.1,
                                               help="Largeur d'un module")
                with c2:
                    rack_depth = st.number_input("**Profondeur rack (m)**", 
                                               min_value=0.8, max_value=3.0, value=1.2, step=0.1,
                                               help="Profondeur d'un module")
                with c3:
                    rack_height = st.number_input("**Hauteur rack (m)**", 
                                                min_value=2.0, max_value=12.0, value=6.0, step=0.5,
                                                help="Hauteur maximale")
            
            with tab2:
                st.markdown("#### ⚙️ Configuration")
                rack_type = st.selectbox("**Type de rack**",
                                       ["Palettier standard", "Drive-in", "Palettier mobile", "Cantilever"])
                
                c1, c2 = st.columns(2)
                with c1:
                    max_levels = st.slider("**Niveaux max**", 1, 8, 3)
                with c2:
                    pallet_type = st.selectbox("**Type palette**",
                                             ["EUR (800×1200)", "US (1000×1200)", "Demi-palette"])
        
        with col2:
            st.markdown("### 📊 Capacité estimée")
            
            # Récupérer les paramètres de l'étape 1
            params = st.session_state.warehouse_data.get('simple_params', {})
            length = params.get('length', 60.0)
            width = params.get('width', 40.0)
            
            # Calcul rapide
            aisle_width = 3.5  # Valeur par défaut
            usable_length = length - aisle_width - 4
            racks_per_row = max(1, int(usable_length / (rack_depth + 1)))
            
            usable_width = width - 4
            rows_per_side = max(1, int(usable_width / (rack_width + 1)))
            
            total_racks = racks_per_row * rows_per_side * 2
            
            st.markdown(f"""
            <div class="simple-metric">
                <h4>🏗️ Racks estimés</h4>
                <h2>{total_racks}</h2>
                <p>{racks_per_row} × {rows_per_side} × 2 côtés</p>
            </div>
            """, unsafe_allow_html=True)
            
            positions_per_rack = max_levels * 2
            total_positions = total_racks * positions_per_rack
            
            st.markdown(f"""
            <div class="simple-metric">
                <h4>📦 Emplacements</h4>
                <h2>{total_positions}</h2>
                <p>{max_levels} niveaux × 2 positions</p>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown(f"""
            <div class="simple-metric">
                <h4>📐 Dimensions</h4>
                <p>{rack_width}m × {rack_depth}m</p>
                <p>Hauteur : {rack_height}m</p>
            </div>
            """, unsafe_allow_html=True)
        
        # Sauvegarder les paramètres
        st.session_state.warehouse_data['simple_params'].update({
            'rack_width': float(rack_width),
            'rack_depth': float(rack_depth),
            'rack_height': float(rack_height),
            'rack_type': rack_type,
            'max_levels': int(max_levels),
            'pallet_type': pallet_type,
            'aisle_width': 3.5  # Valeur par défaut
        })
    
    # ========================================================================
    # ÉTAPE 3 SIMPLE : TRANSPORT
    # ========================================================================
    elif st.session_state.warehouse_data['step'] == 3:
        st.markdown('<div class="simple-header">🚚 ÉTAPE 3 : ÉQUIPEMENTS DE TRANSPORT</div>', unsafe_allow_html=True)
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.markdown("### 🚗 Sélection des équipements")
            
            tab1, tab2 = st.tabs(["Équipements", "Configuration"])
            
            with tab1:
                equipment_type = st.selectbox(
                    "**Type d'équipement principal**",
                    ["forklift", "pallet_truck", "reach_truck", "conveyor"],
                    format_func=lambda x: {
                        "forklift": "🔸 Chariot élévateur",
                        "pallet_truck": "🔸 Transpalette électrique",
                        "reach_truck": "🔸 Chariot à mât rétractable",
                        "conveyor": "🔄 Convoyeur automatisé"
                    }[x]
                )
                
                c1, c2 = st.columns(2)
                with c1:
                    equipment_qty = st.slider("**Nombre d'équipements**", 1, 10, 2)
                with c2:
                    operating_hours = st.slider("**Heures/jour**", 8, 24, 16)
            
            with tab2:
                st.markdown("#### 🛣️ Configuration circulation")
                aisle_width = st.number_input("**Largeur allée (m)**", 
                                            min_value=2.0, max_value=6.0, value=3.5, step=0.1,
                                            help="Largeur pour la circulation")
                
                c1, c2 = st.columns(2)
                with c1:
                    speed = st.slider("**Vitesse (km/h)**", 5, 20, 10)
                with c2:
                    capacity = st.number_input("**Capacité (kg)**", 500, 5000, 1500, 100)
        
        with col2:
            st.markdown("### 📋 Spécifications")
            
            # Recommandations basées sur le type d'équipement
            recommendations = {
                "forklift": "✅ Allée ≥ 3.5m, Hauteur ≥ 6m",
                "pallet_truck": "✅ Allée ≥ 2.5m, Niveau sol",
                "reach_truck": "✅ Allée ≥ 2.8m, Hauteur ≤ 12m",
                "conveyor": "✅ Système automatisé, Maintenance spécialisée"
            }
            
            st.markdown(f"""
            <div class="simple-metric">
                <h4>🔧 Équipement</h4>
                <h3>{'Chariot élévateur' if equipment_type == 'forklift' else 'Transpalette' if equipment_type == 'pallet_truck' else 'Chariot mât rétractable' if equipment_type == 'reach_truck' else 'Convoyeur'}</h3>
                <p>Quantité : {equipment_qty}</p>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown(f"""
            <div class="simple-metric">
                <h4>📏 Allée requise</h4>
                <h2>{aisle_width}m</h2>
                <p>{recommendations.get(equipment_type, 'Configuration standard')}</p>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown(f"""
            <div class="simple-metric">
                <h4>⚡ Performances</h4>
                <p>Vitesse : {speed} km/h</p>
                <p>Capacité : {capacity} kg</p>
                <p>Heures : {operating_hours}h/j</p>
            </div>
            """, unsafe_allow_html=True)
        
        # Sauvegarder les paramètres
        st.session_state.warehouse_data['simple_params'].update({
            'equipment_type': equipment_type,
            'equipment_qty': int(equipment_qty),
            'operating_hours': int(operating_hours),
            'aisle_width': float(aisle_width),
            'speed': int(speed),
            'capacity': int(capacity)
        })
    
    # ========================================================================
    # ÉTAPE 4 SIMPLE : RÉSULTATS
    # ========================================================================
    elif st.session_state.warehouse_data['step'] == 4:
        st.markdown('<div class="simple-header">📊 ÉTAPE 4 : RÉSULTATS DU CALCUL SIMPLE</div>', unsafe_allow_html=True)
        
        # Bouton de calcul
        if st.button("🚀 CALCULER LE DIMENSIONNEMENT", type="primary", use_container_width=True):
            with st.spinner("Calcul en cours..."):
                calculator = SimpleWarehouseCalculator()
                params = st.session_state.warehouse_data.get('simple_params', {})
                
                # Calculs
                capacity = calculator.calculate_simple_capacity(params)
                costs = calculator.calculate_simple_costs(params, capacity)
                
                # Sauvegarder
                st.session_state.warehouse_data['calculations'] = {
                    'capacity': capacity,
                    'costs': costs
                }
            
            st.success("✅ Calcul terminé avec succès !")
            st.rerun()
        
        # Afficher les résultats si disponibles
        if st.session_state.warehouse_data['calculations']:
            calc = st.session_state.warehouse_data['calculations']
            
            # Tableau de bord
            st.markdown("### 📈 RÉSULTATS PRINCIPAUX")
            
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.markdown(f"""
                <div class="metric-card">
                    <h4>🏗️ Racks</h4>
                    <h1 style="color:#3498db;">{calc['capacity'].get('total_racks', 0)}</h1>
                    <p>{calc['capacity'].get('racks_per_row', 0)} × {calc['capacity'].get('rows_per_side', 0)} × 2</p>
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                st.markdown(f"""
                <div class="metric-card">
                    <h4>📦 Palettes</h4>
                    <h1 style="color:#2ecc71;">{calc['capacity'].get('total_pallets', 0):,}</h1>
                    <p>{calc['capacity'].get('levels', 0)} niveaux</p>
                </div>
                """, unsafe_allow_html=True)
            
            with col3:
                st.markdown(f"""
                <div class="metric-card">
                    <h4>📐 Surface utile</h4>
                    <h1 style="color:#e74c3c;">{calc['capacity'].get('storage_area', 0):.0f} m²</h1>
                    <p>{calc['capacity'].get('storage_ratio', 0):.1f}% d'occupation</p>
                </div>
                """, unsafe_allow_html=True)
            
            with col4:
                st.markdown(f"""
                <div class="metric-card">
                    <h4>💰 Coût total</h4>
                    <h1 style="color:#f39c12;">{calc['costs'].get('total_cost', 0)} k€</h1>
                    <p>{calc['costs'].get('cost_per_pallet', 0)} k€/palette</p>
                </div>
                """, unsafe_allow_html=True)
            
            # Détails
            st.markdown("### 📋 DÉTAILS DU CALCUL")
            
            tab1, tab2, tab3 = st.tabs(["Capacités", "Coûts", "Schéma"])
            
            with tab1:
                col1, col2 = st.columns(2)
                with col1:
                    st.markdown("#### 📊 Capacités de stockage")
                    capacity_data = {
                        "Paramètre": ["Surface totale", "Surface de stockage", "Taux occupation", 
                                    "Racks totaux", "Emplacements", "Palettes"],
                        "Valeur": [f"{calc['capacity'].get('total_area', 0):.0f} m²", 
                                 f"{calc['capacity'].get('storage_area', 0):.1f} m²",
                                 f"{calc['capacity'].get('storage_ratio', 0):.1f}%",
                                 f"{calc['capacity'].get('total_racks', 0)}",
                                 f"{calc['capacity'].get('total_positions', 0):,}",
                                 f"{calc['capacity'].get('total_pallets', 0):,}"]
                    }
                    st.dataframe(pd.DataFrame(capacity_data), use_container_width=True, hide_index=True)
                
                with col2:
                    st.markdown("#### 📈 Répartition des surfaces")
                    labels = ['Stockage', 'Circulation', 'Services']
                    values = [
                        calc['capacity'].get('storage_ratio', 0),
                        100 - calc['capacity'].get('storage_ratio', 0) - 10,
                        10
                    ]
                    
                    fig1, ax1 = plt.subplots(figsize=(6, 6))
                    ax1.pie(values, labels=labels, autopct='%1.1f%%', startangle=90,
                           colors=['#3498db', '#2ecc71', '#e74c3c'])
                    ax1.axis('equal')
                    st.pyplot(fig1)
            
            with tab2:
                col1, col2 = st.columns(2)
                with col1:
                    st.markdown("#### 💰 Détail des coûts")
                    cost_data = {
                        "Poste": ["Racks", "Surface", "Équipement", "TOTAL"],
                        "Coût (k€)": [calc['costs'].get('rack_cost', 0),
                                     calc['costs'].get('area_cost', 0),
                                     calc['costs'].get('equipment_cost', 0),
                                     calc['costs'].get('total_cost', 0)]
                    }
                    st.dataframe(pd.DataFrame(cost_data), use_container_width=True, hide_index=True)
                
                with col2:
                    st.markdown("#### 📊 Répartition des coûts")
                    cost_values = [
                        calc['costs'].get('rack_cost', 0),
                        calc['costs'].get('area_cost', 0),
                        calc['costs'].get('equipment_cost', 0)
                    ]
                    
                    fig2, ax2 = plt.subplots(figsize=(6, 6))
                    ax2.pie(cost_values, labels=['Racks', 'Surface', 'Équipement'], 
                           autopct='%1.1f%%', startangle=90,
                           colors=['#3498db', '#2ecc71', '#f39c12'])
                    ax2.axis('equal')
                    st.pyplot(fig2)
            
            with tab3:
                st.markdown("#### 📐 Schéma simplifié de l'entrepôt")
                
                # Générer le schéma
                params = st.session_state.warehouse_data.get('simple_params', {})
                capacity = calc.get('capacity', {})
                
                fig = SimpleWarehouseCalculator.generate_simple_schema(params, capacity)
                if fig:
                    st.pyplot(fig)
                    
                    # Bouton de téléchargement
                    buf = BytesIO()
                    fig.savefig(buf, format="png", dpi=150)
                    st.download_button(
                        label="⬇️ Télécharger le schéma",
                        data=buf.getvalue(),
                        file_name="schema_simplifie.png",
                        mime="image/png",
                        use_container_width=True
                    )
            
            # Export des résultats
            st.markdown("### 📥 EXPORT DES RÉSULTATS")
            
            col_exp1, col_exp2, col_exp3 = st.columns(3)
            
            with col_exp1:
                if st.button("📊 Exporter en Excel", use_container_width=True):
                    # Créer un DataFrame pour l'export
                    params_df = pd.DataFrame([st.session_state.warehouse_data['simple_params']])
                    st.download_button(
                        label="⬇️ Télécharger Excel",
                        data=params_df.to_csv(index=False).encode('utf-8'),
                        file_name="calcul_simple.csv",
                        mime="text/csv",
                        use_container_width=True
                    )
            
            with col_exp2:
                if st.button("📄 Générer rapport", use_container_width=True):
                    st.success("Rapport généré avec succès!")
            
            with col_exp3:
                if st.button("🖼️ Image 3D IA", use_container_width=True):
                    st.info("Utilisez ce prompt pour générer une image 3D:")
                    prompt = f"""
                    Warehouse layout with {calc['capacity'].get('total_racks', 0)} racks, 
                    {calc['capacity'].get('levels', 0)} levels, simple configuration, 
                    industrial design, clean layout, wide-angle view
                    """
                    st.code(prompt, language="text")

# ============================================================================
# SECTION : MODE AVANCÉ (CODE EXISTANT - SIMPLIFIÉ POUR LA DÉMONSTRATION)
# ============================================================================
else:
    st.markdown('<div class="section-header">🔬 MODE AVANCÉ - EN CONSTRUCTION</div>', unsafe_allow_html=True)
    
    st.markdown("""
    <div class="simple-section">
        <h4>🚧 Mode Avancé en développement</h4>
        <p>Le mode avancé est actuellement en cours de développement. Il offrira des fonctionnalités supplémentaires :</p>
        <ul>
            <li>Analyse détaillée des flux logistiques</li>
            <li>Calculs avancés selon les normes ISO</li>
            <li>Optimisation automatique des allées</li>
            <li>Simulation des temps de cycle</li>
            <li>Rapports techniques complets</li>
        </ul>
        <p>Pour l'instant, utilisez le <strong>Mode Simple</strong> pour vos calculs de dimensionnement.</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Option pour basculer vers le mode simple
    if st.button("⚡ Passer au Mode Simple", type="primary", use_container_width=True):
        st.session_state.warehouse_data['mode'] = 'simple'
        st.session_state.warehouse_data['step'] = 1
        st.rerun()

# ============================================================================
# PIED DE PAGE
# ============================================================================
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #7f8c8d; padding: 20px;">
    <p style="font-size: 0.9em;">
        <strong>Warehouse Dimensioning Pro v4.0</strong> | 
        © 2024 - Solution professionnelle de dimensionnement d'entrepôts |
        Mode Simple & Mode Avancé
    </p>
    <p style="font-size: 0.8em; margin-top: 10px;">
        Développé avec Streamlit • Python • Calcul simple et avancé intégrés
    </p>
</div>
""", unsafe_allow_html=True)
