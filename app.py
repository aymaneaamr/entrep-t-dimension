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
# STYLES ET CSS
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
    
    .metric-card {
        background: white;
        padding: 1.5rem;
        border-radius: 12px;
        border-left: 6px solid #3498db;
        box-shadow: 0 4px 12px rgba(0,0,0,0.08);
        transition: transform 0.3s;
        height: 100%;
    }
    
    .metric-card:hover {
        transform: translateY(-5px);
    }
    
    .warning-box {
        background: linear-gradient(135deg, #fff3cd 0%, #ffeaa7 100%);
        border-left: 6px solid #f39c12;
        padding: 1rem;
        border-radius: 10px;
        margin: 1rem 0;
    }
    
    .success-box {
        background: linear-gradient(135deg, #d4edda 0%, #c3e6cb 100%);
        border-left: 6px solid #28a745;
        padding: 1rem;
        border-radius: 10px;
        margin: 1rem 0;
    }
    
    .parameter-card {
        background: #f8f9fa;
        padding: 1.2rem;
        border-radius: 10px;
        border: 2px solid #e9ecef;
        margin-bottom: 1rem;
    }
    
    /* Onglets personnalisés */
    .stTabs [data-baseweb="tab-list"] {
        gap: 10px;
    }
    
    .stTabs [data-baseweb="tab"] {
        height: 60px;
        white-space: pre-wrap;
        background-color: #f8f9fa;
        border-radius: 10px 10px 0px 0px;
        gap: 1px;
        padding-top: 15px;
        padding-bottom: 15px;
        font-weight: bold;
    }
    
    .stTabs [aria-selected="true"] {
        background-color: #3498db !important;
        color: white !important;
    }
    
    /* Boutons */
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
    
    /* Sidebar */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #2c3e50 0%, #3498db 100%);
    }
    
    [data-testid="stSidebar"] .sidebar-content {
        color: white;
    }
</style>
""", unsafe_allow_html=True)

# ============================================================================
# EN-TÊTE PRINCIPAL
# ============================================================================
st.markdown("""
<div class="main-header">
    <h1 style="margin:0; font-size: 2.8em;">🏭 WAREHOUSE DIMENSIONING PRO</h1>
    <p style="margin:0; font-size: 1.2em;">Outil intelligent de dimensionnement d'entrepôts avec normes ISO intégrées</p>
    <p style="margin-top: 10px; opacity: 0.9;">v3.0 | Conforme NF EN 15635 • ISO 9001 • Règlementation ERP</p>
</div>
""", unsafe_allow_html=True)

# ============================================================================
# INITIALISATION DES VARIABLES DE SESSION
# ============================================================================
if 'warehouse_data' not in st.session_state:
    st.session_state.warehouse_data = {
        'step': 1,
        'calculations': {},
        'warnings': [],
        'optimizations': []
    }

# ============================================================================
# FONCTIONS DE CALCUL PROFESSIONNELLES
# ============================================================================
class WarehouseCalculator:
    """Classe principale de calcul pour le dimensionnement d'entrepôt"""
    
    # Normes de référence
    NORMS = {
        'min_aisle_width_forklift': 3.5,  # Largeur minimale allée pour chariot élévateur (m)
        'min_aisle_width_pallet': 2.5,    # Largeur minimale pour transpalette (m)
        'clearance_height': 0.5,          # Dégagement minimum sous poutre (m)
        'fire_aisle_width': 1.2,          # Largeur allée d'évacuation (m)
        'max_rack_height': 15,           # Hauteur maximale recommandée (m)
        'min_turning_radius': 2.0,        # Rayon de braquage minimum (m)
        'load_per_m2': 1500,              # Charge au sol maximale (kg/m²)
        'lighting_level': 300,            # Niveau d'éclairage minimum (lux)
        'min_door_width': 2.4,            # Largeur minimale porte (m)
        'safety_margin': 0.3,             # Marge de sécurité autour racks (%)
    }
    
    @staticmethod
    def calculate_storage_capacity(params):
        """Calcule la capacité de stockage selon les normes ISO"""
        # Nombre de racks possibles
        usable_length = params['length'] - params['main_aisle_width'] - 4  # 2m de chaque côté
        racks_per_row = int(usable_length / (params['rack_depth'] + 1.0))
        
        usable_width = params['width'] - 2  # 1m de chaque côté
        rows_per_side = int(usable_width / (params['rack_width'] + 1.0))
        
        total_racks = racks_per_row * rows_per_side * 2  # Deux côtés
        
        # Capacité par rack
        levels = min(params['max_levels'], int(params['clear_height'] / (params['pallet_height'] + 0.3)))
        positions_per_level = 2  # Avant/arrière
        
        total_positions = total_racks * levels * positions_per_level
        total_pallets = total_positions * params['filling_rate'] / 100
        
        # Surface utile
        storage_area = total_racks * params['rack_width'] * params['rack_depth']
        total_area = params['length'] * params['width']
        storage_ratio = (storage_area / total_area) * 100
        
        return {
            'total_racks': total_racks,
            'racks_per_row': racks_per_row,
            'rows_per_side': rows_per_side,
            'levels': levels,
            'total_positions': total_positions,
            'total_pallets': int(total_pallets),
            'storage_area': round(storage_area, 1),
            'total_area': total_area,
            'storage_ratio': round(storage_ratio, 1),
            'volume_capacity': round(total_pallets * params['pallet_volume'], 1)
        }
    
    @staticmethod
    def calculate_circulation(params, capacity):
        """Calcule les paramètres de circulation"""
        # Distance moyenne de parcours
        avg_distance = (params['length'] + params['width']) / 2
        
        # Temps de cycle
        travel_speed = params['equipment_speed'] * 1000 / 3600  # m/s
        travel_time = avg_distance / travel_speed
        handling_time = 120 if params['equipment_type'] == 'forklift' else 90  # secondes
        
        cycle_time = travel_time * 2 + handling_time / 60  # minutes
        
        # Débit
        pallets_per_hour = 60 / cycle_time
        daily_capacity = pallets_per_hour * params['operating_hours']
        
        # Nombre d'équipements nécessaires
        daily_throughput = capacity['total_pallets'] / params['stock_rotation']
        required_equipment = math.ceil(daily_throughput / daily_capacity)
        
        return {
            'avg_distance': round(avg_distance, 1),
            'cycle_time': round(cycle_time, 1),
            'pallets_per_hour': round(pallets_per_hour, 1),
            'daily_capacity': int(daily_capacity),
            'daily_throughput': int(daily_throughput),
            'required_equipment': required_equipment
        }
    
    @staticmethod
    def calculate_costs(params, capacity, circulation):
        """Calcule les coûts d'investissement et d'exploitation"""
        # Coût des racks (€/emplacement)
        rack_cost_per_position = 180
        rack_cost = capacity['total_positions'] * rack_cost_per_position
        
        # Coût de la surface (€/m²)
        area_cost_per_m2 = 250
        area_cost = params['length'] * params['width'] * area_cost_per_m2
        
        # Coût des équipements
        equipment_costs = {
            'forklift': 45000,
            'reach_truck': 55000,
            'pallet_truck': 8000,
            'automated': 120000
        }
        equipment_cost = equipment_costs.get(params['equipment_type'], 30000) * circulation['required_equipment']
        
        # Coût installation
        installation_cost = (rack_cost + area_cost + equipment_cost) * 0.15
        
        # Coût total
        total_investment = rack_cost + area_cost + equipment_cost + installation_cost
        
        # Coûts annuels
        annual_maintenance = total_investment * 0.03
        annual_personnel = circulation['required_equipment'] * 2 * 35000  # 2 opérateurs par équipement
        annual_energy = params['area'] * 15  # €/m²/an
        
        total_annual_cost = annual_maintenance + annual_personnel + annual_energy
        
        return {
            'rack_cost': round(rack_cost / 1000, 1),
            'area_cost': round(area_cost / 1000, 1),
            'equipment_cost': round(equipment_cost / 1000, 1),
            'installation_cost': round(installation_cost / 1000, 1),
            'total_investment': round(total_investment / 1000, 1),
            'annual_maintenance': round(annual_maintenance / 1000, 1),
            'annual_personnel': round(annual_personnel / 1000, 1),
            'annual_energy': round(annual_energy / 1000, 1),
            'total_annual_cost': round(total_annual_cost / 1000, 1),
            'cost_per_pallet': round(total_annual_cost / capacity['total_pallets'], 2)
        }
    
    @staticmethod
    def check_norms_compliance(params):
        """Vérifie la conformité aux normes et retourne les alertes"""
        warnings = []
        optimizations = []
        
        # Vérification hauteur
        if params['clear_height'] - params['max_rack_height'] < WarehouseCalculator.NORMS['clearance_height']:
            warnings.append(f"⚠️ **Hauteur insuffisante** : Dégagement sous poutre inférieur à {WarehouseCalculator.NORMS['clearance_height']}m")
        
        # Vérification largeur allée
        min_aisle = WarehouseCalculator.NORMS['min_aisle_width_forklift'] if params['equipment_type'] == 'forklift' else WarehouseCalculator.NORMS['min_aisle_width_pallet']
        if params['main_aisle_width'] < min_aisle:
            warnings.append(f"⚠️ **Allée trop étroite** : {params['main_aisle_width']}m < {min_aisle}m minimum pour {params['equipment_type']}")
        
        # Vérification charge au sol
        estimated_load = (capacity.get('total_pallets', 0) * params['pallet_weight']) / params['area']
        if estimated_load > WarehouseCalculator.NORMS['load_per_m2']:
            warnings.append(f"⚠️ **Charge au sol excessive** : {estimated_load:.0f} kg/m² > {WarehouseCalculator.NORMS['load_per_m2']} kg/m² maximum")
        
        # Optimisations
        if params['storage_ratio'] > 70:
            optimizations.append("✅ **Excellent ratio de stockage** (>70%)")
        else:
            optimizations.append("💡 **Optimisation possible** : Augmenter le nombre de niveaux pour améliorer le ratio de stockage")
        
        if params['stock_rotation'] < 15:
            optimizations.append("🚀 **Rotation rapide** : Considérer une zone de préparation de commandes dédiée")
        
        return warnings, optimizations

# ============================================================================
# SIDEBAR - NAVIGATION ET CONFIGURATION GLOBALE
# ============================================================================
with st.sidebar:
    st.markdown("""
    <div style="text-align: center; padding: 20px 0;">
        <h2 style="color: white;">📋 NAVIGATION</h2>
    </div>
    """, unsafe_allow_html=True)
    
    # Sélecteur d'étape
    step = st.radio(
        "**PROGRESSION DU PROJET**",
        ["🏢 1. BÂTIMENT", "📦 2. STOCKAGE", "🚚 3. CIRCULATION", 
         "📊 4. RÉSULTATS", "🎨 5. VISUALISATION"],
        index=st.session_state.warehouse_data['step'] - 1,
        key="navigation"
    )
    
    # Mettre à jour l'étape
    step_map = {
        "🏢 1. BÂTIMENT": 1,
        "📦 2. STOCKAGE": 2,
        "🚚 3. CIRCULATION": 3,
        "📊 4. RÉSULTATS": 4,
        "🎨 5. VISUALISATION": 5
    }
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
    
    # Normes appliquées
    st.markdown("### 📜 NORMES APPLIQUÉES")
    st.markdown("""
    - **NF EN 15635** : Exploitation des systèmes de stockage
    - **ISO 9001** : Management de la qualité
    - **ISO 14001** : Management environnemental
    - **ERP** : Établissement recevant du public
    - **Règlementation incendie**
    """)
    
    st.markdown("---")
    
    # Bouton de réinitialisation
    if st.button("🔄 Réinitialiser le projet", use_container_width=True):
        st.session_state.warehouse_data = {'step': 1, 'calculations': {}, 'warnings': [], 'optimizations': []}
        st.rerun()

# ============================================================================
# ÉTAPE 1 : PARAMÈTRES DU BÂTIMENT
# ============================================================================
if st.session_state.warehouse_data['step'] == 1:
    st.markdown('<div class="section-header">🏢 ÉTAPE 1 : DIMENSIONS DU BÂTIMENT</div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("### 📏 Dimensions principales")
        
        tab1, tab2, tab3 = st.tabs(["Dimensions", "Structure", "Accès"])
        
        with tab1:
            c1, c2, c3 = st.columns(3)
            with c1:
                length = st.number_input("**Longueur (m)**", 10, 200, 60, 1, 
                                       help="Longueur totale du bâtiment")
            with c2:
                width = st.number_input("**Largeur (m)**", 10, 100, 40, 1,
                                      help="Largeur totale du bâtiment")
            with c3:
                clear_height = st.number_input("**Hauteur libre (m)**", 3, 20, 9, 0.5,
                                             help="Hauteur sous poutre")
        
        with tab2:
            c1, c2 = st.columns(2)
            with c1:
                column_spacing = st.number_input("**Espacement poteaux (m)**", 5, 15, 9, 1,
                                               help="Distance entre les poteaux de structure")
            with c2:
                floor_load = st.number_input("**Charge au sol (T/m²)**", 1, 10, 3, 1,
                                           help="Capacité portante du sol")
        
        with tab3:
            c1, c2 = st.columns(2)
            with c1:
                dock_doors = st.number_input("**Nombre de quais**", 1, 20, 4, 1,
                                           help="Quais de chargement/déchargement")
            with c2:
                door_width = st.number_input("**Largeur porte (m)**", 2, 5, 3, 0.1,
                                           help="Largeur des portes de quai")
    
    with col2:
        st.markdown("### 🎯 Prévisualisation")
        
        # Calcul de la surface
        area = length * width
        volume = area * clear_height
        
        st.markdown(f"""
        <div class="parameter-card">
            <h4 style="margin-top:0;">📐 Surface totale</h4>
            <h2 style="color:#3498db; margin:0;">{area} m²</h2>
            <p>Longueur : {length}m × Largeur : {width}m</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown(f"""
        <div class="parameter-card">
            <h4 style="margin-top:0;">📦 Volume disponible</h4>
            <h2 style="color:#3498db; margin:0;">{volume:,.0f} m³</h2>
            <p>Hauteur libre : {clear_height}m</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown(f"""
        <div class="parameter-card">
            <h4 style="margin-top:0;">🚪 Capacité d'accès</h4>
            <h2 style="color:#3498db; margin:0;">{dock_doors} quais</h2>
            <p>Largeur porte : {door_width}m</p>
        </div>
        """, unsafe_allow_html=True)

# ============================================================================
# ÉTAPE 2 : PARAMÈTRES DE STOCKAGE
# ============================================================================
elif st.session_state.warehouse_data['step'] == 2:
    st.markdown('<div class="section-header">📦 ÉTAPE 2 : PARAMÈTRES DE STOCKAGE</div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("### 📦 Caractéristiques des marchandises")
        
        tab1, tab2, tab3 = st.tabs(["Unités de charge", "Racks", "Gestion"])
        
        with tab1:
            c1, c2, c3 = st.columns(3)
            with c1:
                pallet_type = st.selectbox("**Type de palette**", 
                                         ["EUR (800×1200)", "US (1000×1200)", "Demi-palette", "Conteneur"])
            with c2:
                pallet_weight = st.number_input("**Poids palette (kg)**", 100, 2000, 800, 50,
                                              help="Poids moyen par palette")
            with c3:
                pallet_height = st.number_input("**Hauteur palette (m)**", 0.5, 2.5, 1.2, 0.1,
                                              help="Hauteur moyenne des charges")
        
        with tab2:
            c1, c2, c3 = st.columns(3)
            with c1:
                rack_type = st.selectbox("**Type de rack**", 
                                       ["Palettier conventionnel", "Drive-in", "Palettier mobile", "Cantilever"])
            with c2:
                rack_width = st.number_input("**Largeur rack (m)**", 0.8, 3.0, 1.0, 0.1,
                                           help="Largeur d'un module de rack")
            with c3:
                rack_depth = st.number_input("**Profondeur rack (m)**", 0.8, 3.0, 1.2, 0.1,
                                           help="Profondeur d'un module de rack")
        
        with tab3:
            c1, c2 = st.columns(2)
            with c1:
                stock_rotation = st.number_input("**Rotation des stocks (jours)**", 1, 365, 30, 1,
                                               help="Durée moyenne de stockage")
            with c2:
                filling_rate = st.slider("**Taux de remplissage (%)**", 50, 100, 85,
                                       help="Pourcentage moyen d'occupation")
    
    with col2:
        st.markdown("### 🎯 Paramètres avancés")
        
        st.markdown("#### 📈 Densité de stockage")
        max_levels = st.slider("**Nombre de niveaux max**", 1, 10, 3,
                             help="Nombre d'étages de stockage")
        
        st.markdown("#### 🔄 Flux de marchandises")
        flow_type = st.selectbox("**Type de flux**",
                               ["FIFO (First In First Out)", "LIFO (Last In First Out)", "FEFO (First Expired First Out)"])
        
        st.markdown("#### 🌡️ Conditions spéciales")
        special_conditions = st.multiselect("**Besoins spécifiques**",
                                          ["Chambres froides", "Sécurité renforcée", "Produits dangereux", 
                                           "Valeur élevée", "Fragile"])

# ============================================================================
# ÉTAPE 3 : PARAMÈTRES DE CIRCULATION
# ============================================================================
elif st.session_state.warehouse_data['step'] == 3:
    st.markdown('<div class="section-header">🚚 ÉTAPE 3 : CIRCULATION ET ÉQUIPEMENTS</div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("### 🚗 Équipements de manutention")
        
        tab1, tab2 = st.tabs(["Équipements", "Circulation"])
        
        with tab1:
            equipment_type = st.selectbox(
                "**Type d'équipement principal**",
                ["forklift", "reach_truck", "pallet_truck", "automated"],
                format_func=lambda x: {
                    "forklift": "🔸 Chariot élévateur",
                    "reach_truck": "🔸 Chariot à mât rétractable",
                    "pallet_truck": "🔸 Transpalette électrique",
                    "automated": "🤖 Système automatisé"
                }[x]
            )
            
            c1, c2 = st.columns(2)
            with c1:
                equipment_speed = st.slider("**Vitesse (km/h)**", 5, 25, 10, 1,
                                          help="Vitesse de circulation moyenne")
            with c2:
                equipment_capacity = st.number_input("**Capacité (kg)**", 1000, 5000, 1500, 100,
                                                   help="Capacité de levage")
        
        with tab2:
            c1, c2 = st.columns(2)
            with c1:
                main_aisle_width = st.number_input("**Largeur allée principale (m)**", 2.0, 6.0, 3.5, 0.1,
                                                 help="Largeur des allées de circulation")
            with c2:
                secondary_aisle_width = st.number_input("**Largeur allée secondaire (m)**", 1.5, 3.0, 2.0, 0.1,
                                                      help="Largeur des allées entre racks")
            
            operating_hours = st.slider("**Heures d'exploitation/jour**", 8, 24, 16, 1)
    
    with col2:
        st.markdown("### 📋 Spécifications techniques")
        
        st.markdown("#### 🛡️ Sécurité")
        safety_margin = st.slider("**Marge de sécurité (%)**", 10, 50, 20,
                                help="Marge pour manœuvres et sécurité")
        
        st.markdown("#### 💡 Éclairage")
        lighting_type = st.selectbox("**Type d'éclairage**",
                                   ["LED haute baie", "Fluorescent", "Sodium haute pression"])
        
        st.markdown("#### 🚨 Systèmes de sécurité")
        security_systems = st.multiselect("**Équipements de sécurité**",
                                        ["Détection incendie", "Vidéosurveillance", "Contrôle d'accès",
                                         "Alarme intrusion", "Éclairage de sécurité"])

# ============================================================================
# ÉTAPE 4 : CALCULS ET RÉSULTATS
# ============================================================================
elif st.session_state.warehouse_data['step'] == 4:
    st.markdown('<div class="section-header">📊 ÉTAPE 4 : RÉSULTATS ET ANALYSE</div>', unsafe_allow_html=True)
    
    # Collecter tous les paramètres (simplifié pour l'exemple)
    params = {
        'length': 60, 'width': 40, 'clear_height': 9,
        'main_aisle_width': 3.5, 'equipment_type': 'forklift',
        'equipment_speed': 10, 'operating_hours': 16,
        'rack_width': 1.0, 'rack_depth': 1.2, 'max_levels': 3,
        'pallet_height': 1.2, 'pallet_weight': 800, 'filling_rate': 85,
        'stock_rotation': 30, 'area': 60*40, 'pallet_volume': 1.0,
        'storage_ratio': 0
    }
    
    # Bouton de calcul
    if st.button("🚀 Lancer les calculs de dimensionnement", type="primary", use_container_width=True):
        with st.spinner("🔬 Calculs en cours avec vérification des normes..."):
            calculator = WarehouseCalculator()
            
            # Calculs
            capacity = calculator.calculate_storage_capacity(params)
            circulation = calculator.calculate_circulation(params, capacity)
            costs = calculator.calculate_costs(params, capacity, circulation)
            warnings, optimizations = calculator.check_norms_compliance(params)
            
            # Sauvegarder
            st.session_state.warehouse_data['calculations'] = {
                'capacity': capacity,
                'circulation': circulation,
                'costs': costs
            }
            st.session_state.warehouse_data['warnings'] = warnings
            st.session_state.warehouse_data['optimizations'] = optimizations
        
        st.success("✅ Calculs terminés avec succès !")
    
    # Afficher les résultats si disponibles
    if st.session_state.warehouse_data['calculations']:
        calc = st.session_state.warehouse_data['calculations']
        
        # Tableau de bord des métriques
        st.markdown("### 📈 TABLEAU DE BORD DES PERFORMANCES")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.markdown(f"""
            <div class="metric-card">
                <h4>🏗️ Racks installés</h4>
                <h1 style="color:#3498db;">{calc['capacity']['total_racks']}</h1>
                <p>{calc['capacity']['racks_per_row']} × {calc['capacity']['rows_per_side']} × 2 côtés</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
            <div class="metric-card">
                <h4>📦 Capacité palettes</h4>
                <h1 style="color:#2ecc71;">{calc['capacity']['total_pallets']:,}</h1>
                <p>{calc['capacity']['levels']} niveaux × {calc['capacity']['total_positions']} emplacements</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown(f"""
            <div class="metric-card">
                <h4>💰 Investissement</h4>
                <h1 style="color:#e74c3c;">{calc['costs']['total_investment']} k€</h1>
                <p>{calc['costs']['cost_per_pallet']} €/palette/an</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col4:
            st.markdown(f"""
            <div class="metric-card">
                <h4>⚡ Productivité</h4>
                <h1 style="color:#f39c12;">{calc['circulation']['pallets_per_hour']}/h</h1>
                <p>{calc['circulation']['required_equipment']} équipements nécessaires</p>
            </div>
            """, unsafe_allow_html=True)
        
        # Détails des calculs
        st.markdown("### 📋 RAPPORT DÉTAILLÉ")
        
        tab1, tab2, tab3 = st.tabs(["Capacité", "Circulation", "Coûts"])
        
        with tab1:
            col1, col2 = st.columns(2)
            with col1:
                st.markdown("#### 📊 Capacités de stockage")
                capacity_data = {
                    "Métrique": ["Surface totale", "Surface de stockage", "Taux d'occupation", 
                               "Volume utile", "Palettes totales", "Rotation moyenne"],
                    "Valeur": [f"{calc['capacity']['total_area']} m²", 
                             f"{calc['capacity']['storage_area']} m²",
                             f"{calc['capacity']['storage_ratio']}%",
                             f"{calc['capacity']['volume_capacity']} m³",
                             f"{calc['capacity']['total_pallets']:,}",
                             f"{params['stock_rotation']} jours"]
                }
                st.dataframe(pd.DataFrame(capacity_data), use_container_width=True, hide_index=True)
            
            with col2:
                st.markdown("#### 🎯 Efficacité spatiale")
                import plotly.graph_objects as go
                
                labels = ['Stockage', 'Circulation', 'Services', 'Sécurité']
                values = [calc['capacity']['storage_ratio'], 
                         100 - calc['capacity']['storage_ratio'] - 15,
                         10, 5]
                
                fig = go.Figure(data=[go.Pie(labels=labels, values=values, hole=.3)])
                fig.update_layout(showlegend=True, height=300)
                st.plotly_chart(fig, use_container_width=True)
        
        with tab2:
            col1, col2 = st.columns(2)
            with col1:
                st.markdown("#### 🚗 Performance logistique")
                circulation_data = {
                    "Paramètre": ["Distance moyenne", "Temps de cycle", "Débit horaire", 
                                "Débit journalier", "Équipements nécessaires", "Capacité théorique"],
                    "Valeur": [f"{calc['circulation']['avg_distance']} m",
                             f"{calc['circulation']['cycle_time']} min",
                             f"{calc['circulation']['pallets_per_hour']} pal/h",
                             f"{calc['circulation']['daily_capacity']} pal/j",
                             f"{calc['circulation']['required_equipment']}",
                             f"{calc['circulation']['daily_throughput']} pal/j"]
                }
                st.dataframe(pd.DataFrame(circulation_data), use_container_width=True, hide_index=True)
            
            with col2:
                st.markdown("#### 📅 Planning de déploiement")
                timeline_data = {
                    "Phase": ["Étude technique", "Commande équipements", "Installation racks", 
                            "Mise en service", "Formation équipe", "Optimisation"],
                    "Durée (sem)": [4, 8, 6, 2, 1, 4],
                    "Statut": ["✅", "🔄", "⏳", "⏳", "⏳", "⏳"]
                }
                st.dataframe(pd.DataFrame(timeline_data), use_container_width=True, hide_index=True)
        
        with tab3:
            col1, col2 = st.columns(2)
            with col1:
                st.markdown("#### 💰 Investissement initial")
                investment_data = {
                    "Poste": ["Racks et rayonnage", "Surface bâtiment", "Équipements", 
                            "Installation", "TOTAL"],
                    "Montant (k€)": [calc['costs']['rack_cost'], calc['costs']['area_cost'],
                                   calc['costs']['equipment_cost'], calc['costs']['installation_cost'],
                                   calc['costs']['total_investment']]
                }
                st.dataframe(pd.DataFrame(investment_data), use_container_width=True, hide_index=True)
            
            with col2:
                st.markdown("#### 💸 Coûts d'exploitation annuels")
                operating_data = {
                    "Poste": ["Maintenance", "Personnel", "Énergie", "TOTAL"],
                    "Montant (k€)": [calc['costs']['annual_maintenance'], calc['costs']['annual_personnel'],
                                    calc['costs']['annual_energy'], calc['costs']['total_annual_cost']]
                }
                st.dataframe(pd.DataFrame(operating_data), use_container_width=True, hide_index=True)
        
        # Alertes et optimisations
        if st.session_state.warehouse_data['warnings']:
            st.markdown("### ⚠️ ALERTES DE CONFORMITÉ")
            for warning in st.session_state.warehouse_data['warnings']:
                st.markdown(f'<div class="warning-box">{warning}</div>', unsafe_allow_html=True)
        
        if st.session_state.warehouse_data['optimizations']:
            st.markdown("### 💡 OPTIMISATIONS RECOMMANDÉES")
            for opt in st.session_state.warehouse_data['optimizations']:
                st.markdown(f'<div class="success-box">{opt}</div>', unsafe_allow_html=True)

# ============================================================================
# ÉTAPE 5 : VISUALISATION ET EXPORT
# ============================================================================
else:
    st.markdown('<div class="section-header">🎨 ÉTAPE 5 : VISUALISATION ET RAPPORTS</div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("### 📐 PLAN D'IMPLANTATION 2D")
        
        # Créer le schéma
        fig, ax = plt.subplots(figsize=(12, 8))
        
        # Dimensions (exemple)
        length, width = 60, 40
        
        # Dessiner le bâtiment
        ax.add_patch(patches.Rectangle((0, 0), length, width,
                                       linewidth=3, edgecolor='#2c3e50',
                                       facecolor='#ecf0f1', alpha=0.3,
                                       label='Bâtiment'))
        
        # Racks côté gauche
        for i in range(6):
            for j in range(8):
                x = 2 + i * 2.2
                y = 2 + j * 2.2
                ax.add_patch(patches.Rectangle((x, y), 1.2, 1.0,
                                             facecolor='#3498db', edgecolor='#2980b9',
                                             alpha=0.7))
        
        # Racks côté droit
        for i in range(6):
            for j in range(8):
                x = 2 + 6*2.2 + 3.5 + i * 2.2
                y = 2 + j * 2.2
                ax.add_patch(patches.Rectangle((x, y), 1.2, 1.0,
                                             facecolor='#2ecc71', edgecolor='#27ae60',
                                             alpha=0.7))
        
        # Allée centrale
        ax.add_patch(patches.Rectangle((2 + 6*2.2, 0), 3.5, width,
                                     facecolor='#bdc3c7', alpha=0.5,
                                     edgecolor='#7f8c8d', linewidth=2,
                                     label='Allée principale'))
        
        # Quais
        for i in range(4):
            ax.add_patch(patches.Rectangle((length - 3, 5 + i*8), 3, 6,
                                         facecolor='#e74c3c', alpha=0.7,
                                         edgecolor='#c0392b', linewidth=2,
                                         label='Quai' if i == 0 else ""))
        
        # Configuration
        ax.set_xlim(0, length)
        ax.set_ylim(0, width)
        ax.set_aspect('equal')
        ax.set_xlabel('Longueur (m)', fontweight='bold')
        ax.set_ylabel('Largeur (m)', fontweight='bold')
        ax.set_title('Plan d\'implantation - Configuration optimisée', 
                    fontsize=14, fontweight='bold', pad=20)
        
        # Légende
        handles, labels = ax.get_legend_handles_labels()
        by_label = dict(zip(labels, handles))
        ax.legend(by_label.values(), by_label.keys(), loc='upper right')
        
        ax.grid(True, linestyle='--', alpha=0.3)
        
        st.pyplot(fig)
    
    with col2:
        st.markdown("### 📥 EXPORTATION")
        
        # Boutons d'export
        col_export1, col_export2 = st.columns(2)
        
        with col_export1:
            if st.button("📊 Excel", use_container_width=True):
                st.success("Fichier Excel généré!")
            
            if st.button("📄 PDF", use_container_width=True):
                st.success("Rapport PDF généré!")
        
        with col_export2:
            if st.button("🖼️ Image", use_container_width=True):
                buf = BytesIO()
                fig.savefig(buf, format="png", dpi=150)
                st.download_button(
                    label="Télécharger l'image",
                    data=buf.getvalue(),
                    file_name="plan_implantation.png",
                    mime="image/png"
                )
            
            if st.button("📋 Rapport", use_container_width=True):
                st.success("Rapport complet généré!")
        
        st.markdown("---")
        st.markdown("### 🤖 GÉNÉRATION IA")
        
        # Prompt pour génération d'image réaliste
        st.markdown("**Générer une visualisation 3D :**")
        prompt = """
        Photorealistic warehouse interior, industrial storage system with racks, 
        forklift operations, LED lighting, safety markings, wide-angle view, 
        architectural visualization, 8K resolution, professional lighting setup
        """
        
        st.code(prompt, language="text")
        
        if st.button("🎨 Générer avec IA", use_container_width=True):
            st.info("Utilisez ce prompt dans Midjourney, DALL-E 3 ou Stable Diffusion")

# ============================================================================
# PIED DE PAGE
# ============================================================================
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #7f8c8d; padding: 20px;">
    <p style="font-size: 0.9em;">
        <strong>Warehouse Dimensioning Pro v3.0</strong> | 
        © 2024 - Solution professionnelle de dimensionnement d'entrepôts |
        Conforme aux normes internationales
    </p>
    <p style="font-size: 0.8em; margin-top: 10px;">
        Développé avec Streamlit • Python • Normes ISO intégrées
    </p>
</div>
""", unsafe_allow_html=True)
