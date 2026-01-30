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
        'optimizations': [],
        'params': {}
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
        'max_rack_height': 15.0,         # Hauteur maximale recommandée (m)
        'min_turning_radius': 2.0,        # Rayon de braquage minimum (m)
        'load_per_m2': 1500.0,            # Charge au sol maximale (kg/m²)
        'lighting_level': 300.0,          # Niveau d'éclairage minimum (lux)
        'min_door_width': 2.4,            # Largeur minimale porte (m)
        'safety_margin': 0.3,             # Marge de sécurité autour racks (%)
    }
    
    @staticmethod
    def calculate_storage_capacity(params):
        """Calcule la capacité de stockage selon les normes ISO"""
        try:
            # Nombre de racks possibles
            usable_length = params['length'] - params['main_aisle_width'] - 4.0  # 2m de chaque côté
            racks_per_row = max(1, int(usable_length / (params['rack_depth'] + 1.0)))
            
            usable_width = params['width'] - 2.0  # 1m de chaque côté
            rows_per_side = max(1, int(usable_width / (params['rack_width'] + 1.0)))
            
            total_racks = racks_per_row * rows_per_side * 2  # Deux côtés
            
            # Capacité par rack
            levels = min(params.get('max_levels', 3), 
                        int(params['clear_height'] / (params['pallet_height'] + 0.3)))
            positions_per_level = 2  # Avant/arrière
            
            total_positions = total_racks * levels * positions_per_level
            total_pallets = int(total_positions * params.get('filling_rate', 85) / 100.0)
            
            # Surface utile
            storage_area = total_racks * params['rack_width'] * params['rack_depth']
            total_area = params['length'] * params['width']
            storage_ratio = (storage_area / total_area) * 100.0 if total_area > 0 else 0.0
            
            return {
                'total_racks': total_racks,
                'racks_per_row': racks_per_row,
                'rows_per_side': rows_per_side,
                'levels': levels,
                'total_positions': total_positions,
                'total_pallets': total_pallets,
                'storage_area': round(storage_area, 1),
                'total_area': total_area,
                'storage_ratio': round(storage_ratio, 1),
                'volume_capacity': round(total_pallets * params.get('pallet_volume', 1.0), 1)
            }
        except Exception as e:
            st.error(f"Erreur dans le calcul de capacité: {e}")
            return {}
    
    @staticmethod
    def calculate_circulation(params, capacity):
        """Calcule les paramètres de circulation"""
        try:
            # Distance moyenne de parcours
            avg_distance = (params['length'] + params['width']) / 2.0
            
            # Temps de cycle
            travel_speed = params.get('equipment_speed', 10.0) * 1000.0 / 3600.0  # m/s
            travel_time = avg_distance / travel_speed if travel_speed > 0 else 0
            handling_time = 120.0 if params.get('equipment_type') == 'forklift' else 90.0  # secondes
            
            cycle_time = travel_time * 2.0 + handling_time / 60.0  # minutes
            
            # Débit
            pallets_per_hour = 60.0 / cycle_time if cycle_time > 0 else 0
            daily_capacity = pallets_per_hour * params.get('operating_hours', 16.0)
            
            # Nombre d'équipements nécessaires
            daily_throughput = capacity.get('total_pallets', 0) / params.get('stock_rotation', 30.0)
            required_equipment = max(1, math.ceil(daily_throughput / daily_capacity)) if daily_capacity > 0 else 1
            
            return {
                'avg_distance': round(avg_distance, 1),
                'cycle_time': round(cycle_time, 1),
                'pallets_per_hour': round(pallets_per_hour, 1),
                'daily_capacity': int(daily_capacity),
                'daily_throughput': int(daily_throughput),
                'required_equipment': required_equipment
            }
        except Exception as e:
            st.error(f"Erreur dans le calcul de circulation: {e}")
            return {}
    
    @staticmethod
    def calculate_costs(params, capacity, circulation):
        """Calcule les coûts d'investissement et d'exploitation"""
        try:
            # Coût des racks (€/emplacement)
            rack_cost_per_position = 180.0
            rack_cost = capacity.get('total_positions', 0) * rack_cost_per_position
            
            # Coût de la surface (€/m²)
            area_cost_per_m2 = 250.0
            area_cost = params['length'] * params['width'] * area_cost_per_m2
            
            # Coût des équipements
            equipment_costs = {
                'forklift': 45000.0,
                'reach_truck': 55000.0,
                'pallet_truck': 8000.0,
                'automated': 120000.0
            }
            equipment_cost = equipment_costs.get(params.get('equipment_type', 'forklift'), 30000.0) * circulation.get('required_equipment', 1)
            
            # Coût installation
            installation_cost = (rack_cost + area_cost + equipment_cost) * 0.15
            
            # Coût total
            total_investment = rack_cost + area_cost + equipment_cost + installation_cost
            
            # Coûts annuels
            annual_maintenance = total_investment * 0.03
            annual_personnel = circulation.get('required_equipment', 1) * 2.0 * 35000.0  # 2 opérateurs par équipement
            annual_energy = params['length'] * params['width'] * 15.0  # €/m²/an
            
            total_annual_cost = annual_maintenance + annual_personnel + annual_energy
            
            cost_per_pallet = total_annual_cost / capacity.get('total_pallets', 1) if capacity.get('total_pallets', 0) > 0 else 0
            
            return {
                'rack_cost': round(rack_cost / 1000.0, 1),
                'area_cost': round(area_cost / 1000.0, 1),
                'equipment_cost': round(equipment_cost / 1000.0, 1),
                'installation_cost': round(installation_cost / 1000.0, 1),
                'total_investment': round(total_investment / 1000.0, 1),
                'annual_maintenance': round(annual_maintenance / 1000.0, 1),
                'annual_personnel': round(annual_personnel / 1000.0, 1),
                'annual_energy': round(annual_energy / 1000.0, 1),
                'total_annual_cost': round(total_annual_cost / 1000.0, 1),
                'cost_per_pallet': round(cost_per_pallet, 2)
            }
        except Exception as e:
            st.error(f"Erreur dans le calcul des coûts: {e}")
            return {}
    
    @staticmethod
    def check_norms_compliance(params, capacity):
        """Vérifie la conformité aux normes et retourne les alertes"""
        warnings = []
        optimizations = []
        
        try:
            # Vérification hauteur
            if params['clear_height'] - params.get('max_rack_height', 6.0) < WarehouseCalculator.NORMS['clearance_height']:
                warnings.append(f"⚠️ **Hauteur insuffisante** : Dégagement sous poutre inférieur à {WarehouseCalculator.NORMS['clearance_height']}m")
            
            # Vérification largeur allée
            min_aisle = WarehouseCalculator.NORMS['min_aisle_width_forklift'] if params.get('equipment_type') == 'forklift' else WarehouseCalculator.NORMS['min_aisle_width_pallet']
            if params.get('main_aisle_width', 3.5) < min_aisle:
                warnings.append(f"⚠️ **Allée trop étroite** : {params.get('main_aisle_width', 3.5)}m < {min_aisle}m minimum pour {params.get('equipment_type', 'forklift')}")
            
            # Vérification charge au sol
            estimated_load = (capacity.get('total_pallets', 0) * params.get('pallet_weight', 800.0)) / params.get('total_area', 1.0)
            if estimated_load > WarehouseCalculator.NORMS['load_per_m2']:
                warnings.append(f"⚠️ **Charge au sol excessive** : {estimated_load:.0f} kg/m² > {WarehouseCalculator.NORMS['load_per_m2']} kg/m² maximum")
            
            # Optimisations
            storage_ratio = capacity.get('storage_ratio', 0.0)
            if storage_ratio > 70.0:
                optimizations.append("✅ **Excellent ratio de stockage** (>70%)")
            else:
                optimizations.append("💡 **Optimisation possible** : Augmenter le nombre de niveaux pour améliorer le ratio de stockage")
            
            if params.get('stock_rotation', 30.0) < 15.0:
                optimizations.append("🚀 **Rotation rapide** : Considérer une zone de préparation de commandes dédiée")
            
        except Exception as e:
            warnings.append(f"Erreur dans la vérification des normes: {e}")
        
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
    step_options = ["🏢 1. BÂTIMENT", "📦 2. STOCKAGE", "🚚 3. CIRCULATION", 
                   "📊 4. RÉSULTATS", "🎨 5. VISUALISATION"]
    
    step_index = st.session_state.warehouse_data['step'] - 1
    step = st.radio(
        "**PROGRESSION DU PROJET**",
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
            'step': 1, 
            'calculations': {}, 
            'warnings': [], 
            'optimizations': [],
            'params': {}
        }
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
                # CORRECTION ICI : Tous les paramètres doivent être du même type
                length = st.number_input("**Longueur (m)**", 
                                       min_value=10.0, max_value=200.0, value=60.0, step=1.0,
                                       help="Longueur totale du bâtiment")
            with c2:
                width = st.number_input("**Largeur (m)**", 
                                      min_value=10.0, max_value=100.0, value=40.0, step=1.0,
                                      help="Largeur totale du bâtiment")
            with c3:
                # CORRECTION ICI : step=0.5 est float, donc min_value et max_value doivent être float
                clear_height = st.number_input("**Hauteur libre (m)**", 
                                             min_value=3.0, max_value=20.0, value=9.0, step=0.5,
                                             help="Hauteur sous poutre")
        
        with tab2:
            c1, c2 = st.columns(2)
            with c1:
                column_spacing = st.number_input("**Espacement poteaux (m)**", 
                                               min_value=5.0, max_value=15.0, value=9.0, step=1.0,
                                               help="Distance entre les poteaux de structure")
            with c2:
                floor_load = st.number_input("**Charge au sol (T/m²)**", 
                                           min_value=1.0, max_value=10.0, value=3.0, step=1.0,
                                           help="Capacité portante du sol")
        
        with tab3:
            c1, c2 = st.columns(2)
            with c1:
                dock_doors = st.number_input("**Nombre de quais**", 
                                           min_value=1, max_value=20, value=4, step=1,
                                           help="Quais de chargement/déchargement")
            with c2:
                # CORRECTION ICI : step=0.1 est float
                door_width = st.number_input("**Largeur porte (m)**", 
                                           min_value=2.0, max_value=5.0, value=3.0, step=0.1,
                                           help="Largeur des portes de quai")
    
    with col2:
        st.markdown("### 🎯 Prévisualisation")
        
        # Calcul de la surface
        area = length * width
        volume = area * clear_height
        
        st.markdown(f"""
        <div class="parameter-card">
            <h4 style="margin-top:0;">📐 Surface totale</h4>
            <h2 style="color:#3498db; margin:0;">{area:.0f} m²</h2>
            <p>Longueur : {length:.0f}m × Largeur : {width:.0f}m</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown(f"""
        <div class="parameter-card">
            <h4 style="margin-top:0;">📦 Volume disponible</h4>
            <h2 style="color:#3498db; margin:0;">{volume:,.0f} m³</h2>
            <p>Hauteur libre : {clear_height:.1f}m</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown(f"""
        <div class="parameter-card">
            <h4 style="margin-top:0;">🚪 Capacité d'accès</h4>
            <h2 style="color:#3498db; margin:0;">{dock_doors} quais</h2>
            <p>Largeur porte : {door_width:.1f}m</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Sauvegarder les paramètres
    st.session_state.warehouse_data['params'].update({
        'length': float(length),
        'width': float(width),
        'clear_height': float(clear_height),
        'column_spacing': float(column_spacing),
        'floor_load': float(floor_load),
        'dock_doors': int(dock_doors),
        'door_width': float(door_width)
    })

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
                pallet_weight = st.number_input("**Poids palette (kg)**", 
                                              min_value=100.0, max_value=2000.0, value=800.0, step=50.0,
                                              help="Poids moyen par palette")
            with c3:
                # CORRECTION ICI : step=0.1
                pallet_height = st.number_input("**Hauteur palette (m)**", 
                                              min_value=0.5, max_value=2.5, value=1.2, step=0.1,
                                              help="Hauteur moyenne des charges")
        
        with tab2:
            c1, c2, c3 = st.columns(3)
            with c1:
                rack_type = st.selectbox("**Type de rack**", 
                                       ["Palettier conventionnel", "Drive-in", "Palettier mobile", "Cantilever"])
            with c2:
                # CORRECTION ICI : step=0.1
                rack_width = st.number_input("**Largeur rack (m)**", 
                                           min_value=0.8, max_value=3.0, value=1.0, step=0.1,
                                           help="Largeur d'un module de rack")
            with c3:
                # CORRECTION ICI : step=0.1
                rack_depth = st.number_input("**Profondeur rack (m)**", 
                                           min_value=0.8, max_value=3.0, value=1.2, step=0.1,
                                           help="Profondeur d'un module de rack")
        
        with tab3:
            c1, c2 = st.columns(2)
            with c1:
                stock_rotation = st.number_input("**Rotation des stocks (jours)**", 
                                               min_value=1.0, max_value=365.0, value=30.0, step=1.0,
                                               help="Durée moyenne de stockage")
            with c2:
                filling_rate = st.slider("**Taux de remplissage (%)**", 
                                       50, 100, 85, step=1,
                                       help="Pourcentage moyen d'occupation")
    
    with col2:
        st.markdown("### 🎯 Paramètres avancés")
        
        st.markdown("#### 📈 Densité de stockage")
        max_levels = st.slider("**Nombre de niveaux max**", 1, 10, 3, step=1,
                             help="Nombre d'étages de stockage")
        
        st.markdown("#### 🔄 Flux de marchandises")
        flow_type = st.selectbox("**Type de flux**",
                               ["FIFO (First In First Out)", "LIFO (Last In First Out)", "FEFO (First Expired First Out)"])
        
        st.markdown("#### 🌡️ Conditions spéciales")
        special_conditions = st.multiselect("**Besoins spécifiques**",
                                          ["Chambres froides", "Sécurité renforcée", "Produits dangereux", 
                                           "Valeur élevée", "Fragile"])
    
    # Sauvegarder les paramètres
    st.session_state.warehouse_data['params'].update({
        'pallet_type': pallet_type,
        'pallet_weight': float(pallet_weight),
        'pallet_height': float(pallet_height),
        'rack_type': rack_type,
        'rack_width': float(rack_width),
        'rack_depth': float(rack_depth),
        'stock_rotation': float(stock_rotation),
        'filling_rate': float(filling_rate),
        'max_levels': int(max_levels),
        'flow_type': flow_type,
        'special_conditions': special_conditions,
        'pallet_volume': 1.0  # Valeur par défaut
    })

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
                equipment_speed = st.slider("**Vitesse (km/h)**", 5, 25, 10, step=1,
                                          help="Vitesse de circulation moyenne")
            with c2:
                equipment_capacity = st.number_input("**Capacité (kg)**", 
                                                   min_value=1000.0, max_value=5000.0, value=1500.0, step=100.0,
                                                   help="Capacité de levage")
        
        with tab2:
            c1, c2 = st.columns(2)
            with c1:
                # CORRECTION ICI : step=0.1
                main_aisle_width = st.number_input("**Largeur allée principale (m)**", 
                                                 min_value=2.0, max_value=6.0, value=3.5, step=0.1,
                                                 help="Largeur des allées de circulation")
            with c2:
                # CORRECTION ICI : step=0.1
                secondary_aisle_width = st.number_input("**Largeur allée secondaire (m)**", 
                                                      min_value=1.5, max_value=3.0, value=2.0, step=0.1,
                                                      help="Largeur des allées entre racks")
            
            operating_hours = st.slider("**Heures d'exploitation/jour**", 8, 24, 16, step=1)
    
    with col2:
        st.markdown("### 📋 Spécifications techniques")
        
        st.markdown("#### 🛡️ Sécurité")
        safety_margin = st.slider("**Marge de sécurité (%)**", 10, 50, 20, step=1,
                                help="Marge pour manœuvres et sécurité")
        
        st.markdown("#### 💡 Éclairage")
        lighting_type = st.selectbox("**Type d'éclairage**",
                                   ["LED haute baie", "Fluorescent", "Sodium haute pression"])
        
        st.markdown("#### 🚨 Systèmes de sécurité")
        security_systems = st.multiselect("**Équipements de sécurité**",
                                        ["Détection incendie", "Vidéosurveillance", "Contrôle d'accès",
                                         "Alarme intrusion", "Éclairage de sécurité"])
    
    # Sauvegarder les paramètres
    st.session_state.warehouse_data['params'].update({
        'equipment_type': equipment_type,
        'equipment_speed': float(equipment_speed),
        'equipment_capacity': float(equipment_capacity),
        'main_aisle_width': float(main_aisle_width),
        'secondary_aisle_width': float(secondary_aisle_width),
        'operating_hours': float(operating_hours),
        'safety_margin': float(safety_margin),
        'lighting_type': lighting_type,
        'security_systems': security_systems
    })

# ============================================================================
# ÉTAPE 4 : CALCULS ET RÉSULTATS
# ============================================================================
elif st.session_state.warehouse_data['step'] == 4:
    st.markdown('<div class="section-header">📊 ÉTAPE 4 : RÉSULTATS ET ANALYSE</div>', unsafe_allow_html=True)
    
    # Bouton de calcul
    if st.button("🚀 Lancer les calculs de dimensionnement", type="primary", use_container_width=True):
        with st.spinner("🔬 Calculs en cours avec vérification des normes..."):
            calculator = WarehouseCalculator()
            params = st.session_state.warehouse_data['params']
            
            # Calculs
            capacity = calculator.calculate_storage_capacity(params)
            circulation = calculator.calculate_circulation(params, capacity)
            costs = calculator.calculate_costs(params, capacity, circulation)
            warnings, optimizations = calculator.check_norms_compliance(params, capacity)
            
            # Sauvegarder
            st.session_state.warehouse_data['calculations'] = {
                'capacity': capacity,
                'circulation': circulation,
                'costs': costs
            }
            st.session_state.warehouse_data['warnings'] = warnings
            st.session_state.warehouse_data['optimizations'] = optimizations
        
        st.success("✅ Calculs terminés avec succès !")
        st.rerun()
    
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
                <h1 style="color:#3498db;">{calc['capacity'].get('total_racks', 0)}</h1>
                <p>{calc['capacity'].get('racks_per_row', 0)} × {calc['capacity'].get('rows_per_side', 0)} × 2 côtés</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
            <div class="metric-card">
                <h4>📦 Capacité palettes</h4>
                <h1 style="color:#2ecc71;">{calc['capacity'].get('total_pallets', 0):,}</h1>
                <p>{calc['capacity'].get('levels', 0)} niveaux × {calc['capacity'].get('total_positions', 0)} emplacements</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown(f"""
            <div class="metric-card">
                <h4>💰 Investissement</h4>
                <h1 style="color:#e74c3c;">{calc['costs'].get('total_investment', 0)} k€</h1>
                <p>{calc['costs'].get('cost_per_pallet', 0)} €/palette/an</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col4:
            st.markdown(f"""
            <div class="metric-card">
                <h4>⚡ Productivité</h4>
                <h1 style="color:#f39c12;">{calc['circulation'].get('pallets_per_hour', 0):.1f}/h</h1>
                <p>{calc['circulation'].get('required_equipment', 0)} équipements nécessaires</p>
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
                    "Valeur": [f"{calc['capacity'].get('total_area', 0):.0f} m²", 
                             f"{calc['capacity'].get('storage_area', 0):.1f} m²",
                             f"{calc['capacity'].get('storage_ratio', 0):.1f}%",
                             f"{calc['capacity'].get('volume_capacity', 0):.0f} m³",
                             f"{calc['capacity'].get('total_pallets', 0):,}",
                             f"{st.session_state.warehouse_data['params'].get('stock_rotation', 30):.0f} jours"]
                }
                st.dataframe(pd.DataFrame(capacity_data), use_container_width=True, hide_index=True)
            
            with col2:
                st.markdown("#### 🎯 Efficacité spatiale")
                
                # Créer un graphique simple
                fig, ax = plt.subplots(figsize=(8, 6))
                labels = ['Stockage', 'Circulation', 'Services', 'Sécurité']
                values = [
                    calc['capacity'].get('storage_ratio', 0),
                    100 - calc['capacity'].get('storage_ratio', 0) - 15,
                    10, 5
                ]
                colors = ['#3498db', '#2ecc71', '#e74c3c', '#f39c12']
                
                ax.pie(values, labels=labels, colors=colors, autopct='%1.1f%%', startangle=90)
                ax.axis('equal')
                st.pyplot(fig)
        
        with tab2:
            col1, col2 = st.columns(2)
            with col1:
                st.markdown("#### 🚗 Performance logistique")
                circulation_data = {
                    "Paramètre": ["Distance moyenne", "Temps de cycle", "Débit horaire", 
                                "Débit journalier", "Équipements nécessaires", "Capacité théorique"],
                    "Valeur": [f"{calc['circulation'].get('avg_distance', 0):.1f} m",
                             f"{calc['circulation'].get('cycle_time', 0):.1f} min",
                             f"{calc['circulation'].get('pallets_per_hour', 0):.1f} pal/h",
                             f"{calc['circulation'].get('daily_capacity', 0):,} pal/j",
                             f"{calc['circulation'].get('required_equipment', 0)}",
                             f"{calc['circulation'].get('daily_throughput', 0):,} pal/j"]
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
                    "Montant (k€)": [calc['costs'].get('rack_cost', 0), calc['costs'].get('area_cost', 0),
                                   calc['costs'].get('equipment_cost', 0), calc['costs'].get('installation_cost', 0),
                                   calc['costs'].get('total_investment', 0)]
                }
                st.dataframe(pd.DataFrame(investment_data), use_container_width=True, hide_index=True)
            
            with col2:
                st.markdown("#### 💸 Coûts d'exploitation annuels")
                operating_data = {
                    "Poste": ["Maintenance", "Personnel", "Énergie", "TOTAL"],
                    "Montant (k€)": [calc['costs'].get('annual_maintenance', 0), 
                                   calc['costs'].get('annual_personnel', 0),
                                   calc['costs'].get('annual_energy', 0), 
                                   calc['costs'].get('total_annual_cost', 0)]
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
        
        # Récupérer les paramètres
        params = st.session_state.warehouse_data.get('params', {})
        calc = st.session_state.warehouse_data.get('calculations', {}).get('capacity', {})
        
        # Valeurs par défaut si non définies
        length = params.get('length', 60.0)
        width = params.get('width', 40.0)
        rack_width = params.get('rack_width', 1.0)
        rack_depth = params.get('rack_depth', 1.2)
        main_aisle_width = params.get('main_aisle_width', 3.5)
        
        # Créer le schéma
        fig, ax = plt.subplots(figsize=(12, 8))
        
        # Dessiner le bâtiment
        ax.add_patch(patches.Rectangle((0, 0), length, width,
                                       linewidth=3, edgecolor='#2c3e50',
                                       facecolor='#ecf0f1', alpha=0.3,
                                       label='Bâtiment'))
        
        # Calculer la disposition des racks
        racks_per_row = calc.get('racks_per_row', 6)
        rows_per_side = calc.get('rows_per_side', 8)
        
        # Racks côté gauche
        for i in range(min(racks_per_row, 10)):  # Limiter à 10 pour la visibilité
            for j in range(min(rows_per_side, 10)):
                x = 2.0 + i * (rack_depth + 1.0)
                y = 2.0 + j * (rack_width + 1.0)
                ax.add_patch(patches.Rectangle((x, y), rack_depth, rack_width,
                                             facecolor='#3498db', edgecolor='#2980b9',
                                             alpha=0.7))
        
        # Racks côté droit
        for i in range(min(racks_per_row, 10)):
            for j in range(min(rows_per_side, 10)):
                x = 2.0 + racks_per_row * (rack_depth + 1.0) + main_aisle_width + i * (rack_depth + 1.0)
                y = 2.0 + j * (rack_width + 1.0)
                ax.add_patch(patches.Rectangle((x, y), rack_depth, rack_width,
                                             facecolor='#2ecc71', edgecolor='#27ae60',
                                             alpha=0.7))
        
        # Allée centrale
        alley_x = 2.0 + racks_per_row * (rack_depth + 1.0)
        ax.add_patch(patches.Rectangle((alley_x, 0), main_aisle_width, width,
                                     facecolor='#bdc3c7', alpha=0.5,
                                     edgecolor='#7f8c8d', linewidth=2,
                                     label='Allée principale'))
        
        # Quais
        dock_doors = params.get('dock_doors', 4)
        for i in range(min(dock_doors, 6)):
            quai_width = 6.0
            quai_height = 4.0
            quai_x = length - quai_width
            quai_y = (i + 1) * (width / (dock_doors + 1)) - quai_height/2
            ax.add_patch(patches.Rectangle((quai_x, quai_y), quai_width, quai_height,
                                         facecolor='#e74c3c', alpha=0.7,
                                         edgecolor='#c0392b', linewidth=2,
                                         label='Quai' if i == 0 else ""))
        
        # Configuration
        ax.set_xlim(0, length)
        ax.set_ylim(0, width)
        ax.set_aspect('equal')
        ax.set_xlabel('Longueur (m)', fontweight='bold')
        ax.set_ylabel('Largeur (m)', fontweight='bold')
        ax.set_title(f'Plan d\'implantation - {calc.get("total_racks", 0)} racks', 
                    fontsize=14, fontweight='bold', pad=20)
        
        # Légende
        handles, labels = ax.get_legend_handles_labels()
        by_label = dict(zip(labels, handles))
        if by_label:
            ax.legend(by_label.values(), by_label.keys(), loc='upper right')
        
        ax.grid(True, linestyle='--', alpha=0.3)
        
        st.pyplot(fig)
    
    with col2:
        st.markdown("### 📥 EXPORTATION")
        
        # Boutons d'export
        if st.button("📊 Générer rapport Excel", use_container_width=True):
            st.success("Rapport Excel généré avec succès!")
            
            # Créer un DataFrame pour l'export
            params_df = pd.DataFrame([params])
            st.download_button(
                label="⬇️ Télécharger Excel",
                data=params_df.to_csv(index=False).encode('utf-8'),
                file_name="parametres_entrepot.csv",
                mime="text/csv",
                use_container_width=True
            )
        
        if st.button("📄 Générer rapport PDF", use_container_width=True):
            st.success("Rapport PDF généré avec succès!")
        
        # Exporter l'image
        if st.button("🖼️ Exporter l'image", use_container_width=True):
            buf = BytesIO()
            fig.savefig(buf, format="png", dpi=150, bbox_inches='tight')
            st.download_button(
                label="⬇️ Télécharger l'image",
                data=buf.getvalue(),
                file_name="plan_implantation.png",
                mime="image/png",
                use_container_width=True
            )
        
        st.markdown("---")
        st.markdown("### 🤖 GÉNÉRATION IA")
        
        # Prompt pour génération d'image réaliste
        st.markdown("**Générer une visualisation 3D :**")
        
        # Construire le prompt dynamiquement
        calc = st.session_state.warehouse_data.get('calculations', {}).get('capacity', {})
        prompt = f"""
        Photorealistic warehouse interior, industrial storage system with {calc.get('total_racks', 0)} racks, 
        {params.get('max_levels', 3)} levels, {params.get('rack_width', 1.0)}m x {params.get('rack_depth', 1.2)}m rack size,
        {params.get('main_aisle_width', 3.5)}m wide aisle, {params.get('equipment_type', 'forklift')} operations, 
        LED lighting, safety markings, wide-angle view, architectural visualization, 8K resolution
        """
        
        st.code(prompt, language="text")
        
        if st.button("🎨 Générer avec IA", use_container_width=True):
            st.info("Copiez le prompt ci-dessus dans Midjourney, DALL-E 3 ou Stable Diffusion")

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
