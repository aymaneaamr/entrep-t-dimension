import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import numpy as np
import json

st.set_page_config(
    page_title="Warehouse Configuration Optimizer Pro",
    page_icon="🏭",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Configuration CSS personnalisée
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1E3A8A;
        text-align: center;
        margin-bottom: 1rem;
    }
    .sub-header {
        font-size: 1.5rem;
        color: #374151;
        margin-bottom: 2rem;
        text-align: center;
    }
    .stButton>button {
        background-color: #1E40AF;
        color: white;
        font-weight: bold;
        padding: 0.75rem 2rem;
        border-radius: 8px;
        border: none;
        width: 100%;
    }
    .stButton>button:hover {
        background-color: #1E3A8A;
    }
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1rem;
        border-radius: 10px;
        margin-bottom: 1rem;
    }
    .warning-card {
        background: linear-gradient(135deg, #f6d365 0%, #fda085 100%);
        padding: 1rem;
        border-radius: 10px;
        margin-bottom: 1rem;
    }
    .success-card {
        background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
        padding: 1rem;
        border-radius: 10px;
        margin-bottom: 1rem;
    }
</style>
""", unsafe_allow_html=True)

st.markdown('<h1 class="main-header">🏭 Warehouse Configuration Optimizer Pro</h1>', unsafe_allow_html=True)
st.markdown('<h2 class="sub-header">Dimensionnement intelligent pour chariots élévateurs</h2>', unsafe_allow_html=True)

# Initialisation de la session state
if 'calcul_done' not in st.session_state:
    st.session_state.calcul_done = False
if 'results' not in st.session_state:
    st.session_state.results = None

# Sidebar avec les paramètres
with st.sidebar:
    st.markdown("### ⚙️ Paramètres de configuration")
    
    # Onglets pour organiser les paramètres
    tab_dim, tab_rack, tab_chariot, tab_opt = st.tabs(["🏢 Dimensions", "📦 Racks", "🚜 Chariots", "⚙️ Options"])
    
    with tab_dim:
        st.header("🏢 Dimensions Entrepôt")
        
        col1, col2 = st.columns(2)
        with col1:
            longueur = st.number_input("Longueur (m)", min_value=10.0, max_value=200.0, value=50.0, step=1.0, 
                                      help="Longueur totale de l'entrepôt", key="longueur")
        with col2:
            largeur = st.number_input("Largeur (m)", min_value=10.0, max_value=100.0, value=30.0, step=1.0,
                                     help="Largeur totale de l'entrepôt", key="largeur")
        
        hauteur = st.number_input("Hauteur (m)", min_value=3.0, max_value=30.0, value=12.0, step=0.5,
                                 help="Hauteur sous plafond", key="hauteur")
        
        # Visualisation rapide des dimensions
        st.metric("Surface totale", f"{longueur * largeur:.0f} m²")
        st.metric("Volume total", f"{longueur * largeur * hauteur:.0f} m³")
    
    with tab_rack:
        st.header("📦 Dimensionnement des Racks")
        
        # Section pour les racks standard
        st.subheader("📏 Dimensions standard")
        col1, col2, col3 = st.columns(3)
        with col1:
            rack_longueur = st.selectbox("Longueur rack (m)", 
                                        [1.2, 1.5, 1.8, 2.0, 2.4, 2.7, 3.0, 3.3], 
                                        index=4, key="rack_longueur")
        with col2:
            rack_largeur = st.selectbox("Largeur rack (m)", 
                                       [0.8, 1.0, 1.2, 1.5, 1.8], 
                                       index=1, key="rack_largeur")
        with col3:
            rack_hauteur = st.selectbox("Hauteur rack (m)", 
                                       [2.0, 3.0, 4.0, 5.0, 6.0, 8.0, 10.0, 12.0], 
                                       index=6, key="rack_hauteur")
        
        # Configuration verticale dynamique
        st.subheader("📊 Configuration verticale")
        etages = st.slider("Nombre d'étages", 1, 15, 6, key="etages")
        hauteur_etage = st.number_input("Hauteur utile par étage (m)", 
                                       min_value=0.5, max_value=3.0, value=1.5, step=0.1,
                                       key="hauteur_etage")
        
        # Calcul automatique de l'espacement vertical
        espacement_vertical = st.slider("Espacement vertical (cm)", 10, 100, 30, key="espacement_vertical")
        
        # Capacité par niveau
        st.subheader("🎯 Capacité par niveau")
        palettes_longueur = st.number_input("Palettes en longueur", min_value=1, max_value=10, value=2, key="pal_long")
        palettes_largeur = st.number_input("Palettes en largeur", min_value=1, max_value=5, value=1, key="pal_larg")
        palettes_par_niveau = palettes_longueur * palettes_largeur
        
        # Type de rack
        st.subheader("🔧 Type de rack")
        rack_type = st.selectbox("Sélectionnez le type de rack", 
                                ["Rack palette standard", "Rack palette dynamique", 
                                 "Rack à palettier", "Rack cantilever", "Rack drive-in"],
                                key="rack_type")
        
        # Options selon le type de rack
        espacement_lateral = 20  # Valeur par défaut
        profondeur_double = False
        
        if rack_type == "Rack drive-in":
            profondeur_double = st.checkbox("Double profondeur", key="double_prof")
            espacement_lateral = 0
        else:
            espacement_lateral = st.slider("Espacement latéral (cm)", 10, 100, 20, key="esp_lat")
    
    with tab_chariot:
        st.header("🚜 Configuration Chariots")
        
        # Types de chariots avec spécifications
        chariot_options = {
            "Contrebalance": {"allee_min": 3.5, "hauteur_max": 12.0, "charge_max": 3.0},
            "Reach Truck": {"allee_min": 2.7, "hauteur_max": 15.0, "charge_max": 2.5},
            "Télescopique": {"allee_min": 3.0, "hauteur_max": 14.0, "charge_max": 4.0},
            "Transpalette": {"allee_min": 1.8, "hauteur_max": 6.0, "charge_max": 1.5},
            "Gerbeur": {"allee_min": 2.0, "hauteur_max": 10.0, "charge_max": 2.0}
        }
        
        type_chariot = st.selectbox("Type de chariot", list(chariot_options.keys()), key="type_chariot")
        
        # Affichage des spécifications du chariot sélectionné
        specs = chariot_options[type_chariot]
        st.info(f"**Spécifications {type_chariot}:**\n"
               f"- Allée minimum: {specs['allee_min']}m\n"
               f"- Hauteur max: {specs['hauteur_max']}m\n"
               f"- Charge max: {specs['charge_max']}t")
        
        # Largeur d'allée avec recommandation
        allee = st.slider("Largeur allée (m)", 
                         float(specs['allee_min']), 
                         float(specs['allee_min'] + 2.0), 
                         float(specs['allee_min'] + 0.5), 
                         step=0.1, key="allee")
        
        # Vérification de compatibilité
        if rack_hauteur > specs['hauteur_max']:
            st.warning(f"⚠️ La hauteur des racks ({rack_hauteur}m) dépasse "
                      f"la capacité du chariot ({specs['hauteur_max']}m)")
        
        # Charge maximale
        charge_max = st.number_input("Charge max (tonnes)", 
                                    min_value=0.5, 
                                    max_value=10.0, 
                                    value=specs['charge_max'], 
                                    step=0.5, key="charge_max")
    
    with tab_opt:
        st.header("⚙️ Options avancées")
        
        # Options d'optimisation
        st.subheader("🎯 Optimisation")
        marge_securite = st.slider("Marge de sécurité (%)", 5, 30, 15, key="marge_sec")
        taux_utilisation_cible = st.slider("Taux d'utilisation cible (%)", 50, 90, 70, key="taux_util")
        
        # Configuration des allées
        st.subheader("🛣️ Configuration des allées")
        all_transversale = st.checkbox("Allée transversale centrale", value=True, key="all_trans")
        if all_transversale:
            largeur_transversale = st.slider("Largeur allée transversale (m)", 2.0, 5.0, 3.0, key="larg_trans")
        
        # Options de visualisation
        st.subheader("👁️ Visualisation")
        show_3d = st.checkbox("Afficher vue 3D", value=True, key="show_3d")

# Fonction d'optimisation intelligente (SIMPLIFIÉE POUR ÉVITER LES ERREURS)
def optimiser_configuration(longueur, largeur, hauteur, rack_longueur, rack_largeur, 
                           rack_hauteur, etages, hauteur_etage, espacement_vertical,
                           palettes_longueur, palettes_largeur, allee, type_chariot,
                           marge_securite, taux_utilisation_cible, rack_type, profondeur_double=False):
    
    try:
        # Calculs de base
        surface_totale = longueur * largeur
        volume_total = surface_totale * hauteur
        
        # Calcul de la hauteur totale des racks
        espacement_vertical_m = espacement_vertical / 100
        hauteur_totale_rack = etages * hauteur_etage + (etages - 1) * espacement_vertical_m
        
        # Vérifications de conformité
        conforme_hauteur = hauteur_totale_rack <= (hauteur - 0.5)
        
        # Calcul intelligent du nombre de racks (version simplifiée)
        coef_utilisation = taux_utilisation_cible / 100
        
        # Si double profondeur, ajuster la largeur
        if profondeur_double:
            rack_largeur_effective = rack_largeur * 2
        else:
            rack_largeur_effective = rack_largeur
        
        # Calcul simplifié du nombre de racks
        espacement_lateral_m = 0.2  # Valeur fixe pour simplifier
        
        max_racks_longueur = max(1, int(longueur * 0.8 / (rack_longueur + espacement_lateral_m)))
        max_racks_largeur = max(1, int(largeur * 0.8 / (rack_largeur_effective + espacement_lateral_m + allee/2)))
        
        racks_longueur = max_racks_longueur
        racks_largeur = max_racks_largeur * 2  # Deux côtés de l'allée
        
        nb_racks = racks_longueur * racks_largeur
        
        # Capacités
        palettes_par_niveau = palettes_longueur * palettes_largeur
        capacite_par_rack = etages * palettes_par_niveau
        capacite_totale = nb_racks * capacite_par_rack
        
        # Calculs de surface
        surface_rack_unitaire = rack_longueur * rack_largeur_effective
        surface_racks_totale = nb_racks * surface_rack_unitaire
        surface_all = surface_totale - surface_racks_totale
        taux_utilisation = (surface_racks_totale / surface_totale) * 100
        
        # Volume utile
        volume_utile = surface_racks_totale * hauteur_totale_rack
        
        # Score d'efficacité simplifié
        score_total = min(100, taux_utilisation * 1.2)
        
        return {
            'surface_totale': surface_totale,
            'volume_total': volume_total,
            'hauteur_totale_rack': hauteur_totale_rack,
            'conforme_hauteur': conforme_hauteur,
            'racks_longueur': racks_longueur,
            'racks_largeur': racks_largeur,
            'nb_racks': nb_racks,
            'palettes_par_niveau': palettes_par_niveau,
            'capacite_par_rack': capacite_par_rack,
            'capacite_totale': capacite_totale,
            'surface_rack_unitaire': surface_rack_unitaire,
            'surface_racks_totale': surface_racks_totale,
            'surface_all': surface_all,
            'taux_utilisation': taux_utilisation,
            'volume_utile': volume_utile,
            'score_total': score_total
        }
    except Exception as e:
        st.error(f"Erreur dans les calculs: {str(e)}")
        return None

# Fonction de visualisation SIMPLIFIÉE (sans subplots complexes)
def creer_visualisation_simple(longueur, largeur, hauteur, results, rack_longueur, 
                              rack_largeur, hauteur_totale_rack, allee, etages):
    
    # Créer des figures séparées au lieu de subplots
    figures = {}
    
    # 1. Vue de dessus
    fig_plan = go.Figure()
    
    # Dessiner le contour de l'entrepôt
    fig_plan.add_shape(
        type="rect",
        x0=0, y0=0, x1=longueur, y1=largeur,
        line=dict(color="darkblue", width=3),
        fillcolor="lightgray",
        opacity=0.3,
        layer="below"
    )
    
    # Ajouter quelques racks (simplifié)
    racks_longueur = min(results['racks_longueur'], 10)
    racks_largeur = min(results['racks_largeur'] // 2, 5)
    
    for i in range(racks_longueur):
        for j in range(racks_largeur):
            for side in [0, 1]:
                x_pos = i * (rack_longueur + 0.5) + 2
                y_pos = side * (largeur/2 + allee/2) + j * (rack_largeur + 0.3) + 2
                
                fig_plan.add_shape(
                    type="rect",
                    x0=x_pos, y0=y_pos,
                    x1=x_pos + rack_longueur, y1=y_pos + rack_largeur,
                    line=dict(color="darkorange", width=2),
                    fillcolor="orange",
                    opacity=0.7
                )
    
    fig_plan.update_layout(
        title="Vue de dessus - Plan de l'entrepôt",
        xaxis_title="Longueur (m)",
        yaxis_title="Largeur (m)",
        height=500,
        showlegend=False,
        plot_bgcolor='white'
    )
    
    figures['plan'] = fig_plan
    
    # 2. Vue 3D simple
    if 'show_3d' in st.session_state and st.session_state.show_3d:
        fig_3d = go.Figure()
        
        # Contour de l'entrepôt
        fig_3d.add_trace(go.Mesh3d(
            x=[0, longueur, longueur, 0, 0, longueur, longueur, 0],
            y=[0, 0, largeur, largeur, 0, 0, largeur, largeur],
            z=[0, 0, 0, 0, hauteur, hauteur, hauteur, hauteur],
            opacity=0.1,
            color='lightblue',
            name='Entrepôt'
        ))
        
        # Ajouter quelques racks en 3D
        for i in range(min(5, racks_longueur)):
            for j in range(min(3, racks_largeur)):
                x_pos = i * (rack_longueur + 1) + 5
                y_pos = j * (rack_largeur + 1) + 5
                
                fig_3d.add_trace(go.Mesh3d(
                    x=[x_pos, x_pos + rack_longueur, x_pos + rack_longueur, x_pos],
                    y=[y_pos, y_pos, y_pos + rack_largeur, y_pos + rack_largeur],
                    z=[0, 0, 0, 0],
                    i=[0, 0],
                    j=[1, 2],
                    k=[2, 3],
                    opacity=0.7,
                    color='orange',
                    name='Rack'
                ))
        
        fig_3d.update_layout(
            title="Vue 3D simplifiée",
            scene=dict(
                xaxis_title='Longueur (m)',
                yaxis_title='Largeur (m)',
                zaxis_title='Hauteur (m)'
            ),
            height=500
        )
        
        figures['3d'] = fig_3d
    
    # 3. Graphique de capacité
    fig_capacite = go.Figure()
    
    niveaux = list(range(1, etages + 1))
    capacite_par_niveau = [results['palettes_par_niveau'] * results['nb_racks']] * etages
    
    fig_capacite.add_trace(go.Bar(
        x=niveaux,
        y=capacite_par_niveau,
        name='Palettes par niveau',
        marker_color='orange'
    ))
    
    fig_capacite.update_layout(
        title='Capacité par niveau',
        xaxis_title='Niveau',
        yaxis_title='Nombre de palettes',
        height=400
    )
    
    figures['capacite'] = fig_capacite
    
    # 4. Graphique de répartition
    fig_repartition = go.Figure()
    
    labels = ['Surface Racks', 'Allées', 'Espace libre']
    values = [
        results['surface_racks_totale'],
        results['surface_all'] * 0.7,
        results['surface_all'] * 0.3
    ]
    
    fig_repartition.add_trace(go.Pie(
        labels=labels,
        values=values,
        hole=0.4,
        marker_colors=['orange', 'lightblue', 'lightgray']
    ))
    
    fig_repartition.update_layout(
        title='Répartition de la surface',
        height=400
    )
    
    figures['repartition'] = fig_repartition
    
    return figures

# Interface principale
st.markdown("## 🚀 Analyse et Optimisation")

col_start, col_reset = st.columns([3, 1])
with col_start:
    if st.button("🚀 Lancer l'analyse complète", type="primary", use_container_width=True):
        with st.spinner("Calcul en cours..."):
            results = optimiser_configuration(
                longueur, largeur, hauteur, rack_longueur, rack_largeur,
                rack_hauteur, etages, hauteur_etage, espacement_vertical,
                palettes_longueur, palettes_largeur, allee, type_chariot,
                marge_securite, taux_utilisation_cible, rack_type, 
                profondeur_double
            )
            
            if results:
                st.session_state.results = results
                st.session_state.calcul_done = True
                st.session_state.show_3d = show_3d
                st.rerun()
            else:
                st.error("Erreur lors du calcul. Vérifiez les paramètres.")

with col_reset:
    if st.button("🔄 Réinitialiser", use_container_width=True):
        st.session_state.calcul_done = False
        st.session_state.results = None
        st.rerun()

if st.session_state.calcul_done and st.session_state.results:
    results = st.session_state.results
    
    # Affichage des métriques principales
    st.markdown("## 📊 Résultats détaillés")
    
    # Cartes de métriques
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.metric("🏢 Surface totale", f"{results['surface_totale']:,.0f} m²".replace(',', ' '))
        st.metric("📦 Surface racks", f"{results['surface_racks_totale']:,.0f} m²".replace(',', ' '))
        st.metric("🚶 Surface allées", f"{results['surface_all']:,.0f} m²".replace(',', ' '))
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.metric("🔢 Nombre de racks", f"{results['nb_racks']:,}".replace(',', ' '))
        st.metric("📐 Disposition", f"{results['racks_longueur']} × {results['racks_largeur']}")
        st.metric("📊 Taux utilisation", f"{results['taux_utilisation']:.1f}%")
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col3:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.metric("🔄 Étages/rack", f"{etages}")
        st.metric("📦 Palettes/niveau", f"{results['palettes_par_niveau']}")
        st.metric("🏗️ Capacité/rack", f"{results['capacite_par_rack']:,} pal".replace(',', ' '))
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col4:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.metric("📈 Capacité totale", f"{results['capacite_totale']:,} pal".replace(',', ' '))
        st.metric("📏 Hauteur rack", f"{results['hauteur_totale_rack']:.2f} m")
        st.metric("⭐ Score global", f"{results['score_total']:.1f}/100")
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Onglets pour différents types d'analyse
    tab_visu, tab_analyse, tab_rapport, tab_export = st.tabs([
        "🎨 Visualisations", "📈 Analyses", "📋 Rapport", "💾 Export"
    ])
    
    with tab_visu:
        # Visualisations simplifiées
        st.subheader("🎨 Visualisations interactives")
        
        figures = creer_visualisation_simple(
            longueur, largeur, hauteur, results, rack_longueur,
            rack_largeur, results['hauteur_totale_rack'], allee, etages
        )
        
        # Afficher les figures
        col_v1, col_v2 = st.columns(2)
        
        with col_v1:
            st.plotly_chart(figures['plan'], use_container_width=True)
            if '3d' in figures:
                st.plotly_chart(figures['3d'], use_container_width=True)
        
        with col_v2:
            st.plotly_chart(figures['capacite'], use_container_width=True)
            st.plotly_chart(figures['repartition'], use_container_width=True)
    
    with tab_analyse:
        # Analyses détaillées
        st.subheader("📈 Analyses approfondies")
        
        # Tableau d'analyse
        analyse_data = {
            'Paramètre': [
                'Efficacité spatiale',
                'Utilisation verticale',
                'Densité de stockage',
                'Accessibilité',
                'Flexibilité',
                'Coût estimé par palette'
            ],
            'Valeur': [
                f"{results['taux_utilisation']:.1f}%",
                f"{(results['hauteur_totale_rack'] / hauteur) * 100:.1f}%",
                f"{results['capacite_totale'] / results['surface_totale']:.1f} pal/m²",
                f"{'Élevée' if allee >= 3.5 else 'Moyenne' if allee >= 3.0 else 'Faible'}",
                f"{'Bonne' if rack_type == 'Rack palette standard' else 'Moyenne'}",
                f"{(results['nb_racks'] * 1500 + results['capacite_totale'] * 50) / results['capacite_totale']:.0f} €"
            ],
            'Évaluation': [
                '✅ Optimal' if results['taux_utilisation'] > 65 else '⚠️ Améliorable',
                '✅ Bonne' if results['hauteur_totale_rack'] / hauteur > 0.7 else '⚠️ Sous-utilisé',
                '✅ Élevée' if results['capacite_totale'] / results['surface_totale'] > 5 else '⚠️ Modérée',
                '✅' if allee >= 3.5 else '⚠️' if allee >= 3.0 else '❌',
                '✅' if rack_type == 'Rack palette standard' else '⚠️',
                '💰'
            ]
        }
        
        st.dataframe(pd.DataFrame(analyse_data), use_container_width=True)
        
        # Analyse de compatibilité
        st.subheader("🔍 Analyse de compatibilité")
        
        specs = chariot_options[type_chariot]
        compatibilite = {
            'Critère': ['Hauteur des racks', 'Largeur des allées', 'Charge maximale'],
            'Valeur actuelle': [
                f"{results['hauteur_totale_rack']:.2f} m",
                f"{allee} m",
                f"{charge_max} t"
            ],
            'Limite chariot': [
                f"{specs['hauteur_max']} m",
                f"{specs['allee_min']} m",
                f"{specs['charge_max']} t"
            ],
            'Statut': [
                '✅ Conforme' if results['hauteur_totale_rack'] <= specs['hauteur_max'] else '❌ Non conforme',
                '✅ Conforme' if allee >= specs['allee_min'] else '❌ Non conforme',
                '✅ Conforme' if charge_max <= specs['charge_max'] else '❌ Non conforme'
            ]
        }
        
        st.dataframe(pd.DataFrame(compatibilite), use_container_width=True)
    
    with tab_rapport:
        # Rapport détaillé
        st.subheader("📋 Rapport technique complet")
        
        rapport = f"""RAPPORT TECHNIQUE - OPTIMISATION D'ENTREPÔT
{'='*70}

I. CARACTÉRISTIQUES DE L'ENTREPÔT
{'-'*40}
• Dimensions : {longueur}m (L) × {largeur}m (l) × {hauteur}m (H)
• Surface totale : {results['surface_totale']:,.0f} m²
• Volume total : {results['volume_total']:,.0f} m³

II. CONFIGURATION DES RACKS
{'-'*40}
• Type de rack : {rack_type}
• Dimensions unitaires : {rack_longueur}m × {rack_largeur}m
• Hauteur totale rack : {results['hauteur_totale_rack']:.2f}m ({etages} étages)
• Nombre total racks : {results['nb_racks']:,}
• Disposition : {results['racks_longueur']} × {results['racks_largeur']}
• Surface racks : {results['surface_racks_totale']:,.0f} m²

III. CAPACITÉ DE STOCKAGE
{'-'*40}
• Palettes par niveau : {results['palettes_par_niveau']}
• Palettes par rack : {results['capacite_par_rack']}
• Capacité totale : {results['capacite_totale']:,} palettes
• Densité : {results['capacite_totale'] / results['surface_totale']:.2f} palettes/m²

IV. CHARIOTS ÉLÉVATEURS
{'-'*40}
• Type : {type_chariot}
• Largeur allée : {allee}m
• Charge maximale : {charge_max} tonnes
• Conformité allée : {'✅ CONFORME' if allee >= specs['allee_min'] else '❌ NON CONFORME'}

V. PERFORMANCES
{'-'*40}
• Taux d'utilisation surface : {results['taux_utilisation']:.1f}%
• Score global d'efficacité : {results['score_total']:.1f}/100
• Conformité hauteur : {'✅ CONFORME' if results['conforme_hauteur'] else '❌ NON CONFORME'}

VI. RECOMMANDATIONS
{'-'*40}
1. Optimisation spatiale :
   - Taux d'utilisation actuel : {results['taux_utilisation']:.1f}%
   - Objectif optimal : 70-80%
   
2. Sécurité et conformité :
   - Allée minimum requise : {specs['allee_min']}m
   - Hauteur libre recommandée : +0.5m minimum

VII. ESTIMATION DES COÛTS
{'-'*40}
• Investissement racks (estimation) : {results['nb_racks'] * 1500:,.0f} €
• Coût par palette : {(results['nb_racks'] * 1500) / results['capacite_totale']:.0f} €

Date d'analyse : {pd.Timestamp.now().strftime('%d/%m/%Y %H:%M')}
{'='*70}
"""
        
        st.code(rapport, language=None)
        
        # Options de téléchargement du rapport
        st.download_button(
            label="📥 Télécharger le rapport complet",
            data=rapport,
            file_name=f"rapport_optimisation_{pd.Timestamp.now().strftime('%Y%m%d_%H%M')}.txt",
            mime="text/plain"
        )
    
    with tab_export:
        # Export des données
        st.subheader("💾 Export des données")
        
        col_e1, col_e2 = st.columns(2)
        
        with col_e1:
            # Export CSV
            export_data = {
                'Paramètre': [
                    'Longueur entrepôt', 'Largeur entrepôt', 'Hauteur entrepôt',
                    'Surface totale', 'Nombre racks', 'Capacité totale',
                    'Taux utilisation', 'Largeur allée', 'Type chariot'
                ],
                'Valeur': [
                    longueur, largeur, hauteur,
                    results['surface_totale'], results['nb_racks'], results['capacite_totale'],
                    results['taux_utilisation'], allee, type_chariot
                ],
                'Unité': [
                    'm', 'm', 'm', 'm²', 'unités', 'palettes',
                    '%', 'm', 'type'
                ]
            }
            
            df_export = pd.DataFrame(export_data)
            csv_export = df_export.to_csv(index=False)
            
            st.download_button(
                label="📊 Données CSV",
                data=csv_export,
                file_name=f"donnees_configuration_{pd.Timestamp.now().strftime('%Y%m%d_%H%M')}.csv",
                mime="text/csv"
            )
        
        with col_e2:
            # Export JSON
            json_data = {
                "entrepot": {
                    "dimensions": {"longueur": longueur, "largeur": largeur, "hauteur": hauteur},
                    "surface": results['surface_totale'],
                    "volume": results['volume_total']
                },
                "racks": {
                    "dimensions": {"longueur": rack_longueur, "largeur": rack_largeur},
                    "nombre": results['nb_racks'],
                    "disposition": f"{results['racks_longueur']}x{results['racks_largeur']}",
                    "etages": etages,
                    "capacite_totale": results['capacite_totale']
                },
                "chariots": {
                    "type": type_chariot,
                    "allee": allee,
                    "conformite": allee >= specs['allee_min']
                }
            }
            
            st.download_button(
                label="📁 Données JSON",
                data=json.dumps(json_data, indent=2),
                file_name=f"configuration_{pd.Timestamp.now().strftime('%Y%m%d_%H%M')}.json",
                mime="application/json"
            )
    
    # Section d'alertes et recommandations
    st.markdown("## ⚠️ Alertes et recommandations")
    
    alert_cols = st.columns(3)
    
    with alert_cols[0]:
        if not results['conforme_hauteur']:
            st.markdown('<div class="warning-card">', unsafe_allow_html=True)
            st.error("**Hauteur non conforme**")
            st.write(f"Racks: {results['hauteur_totale_rack']:.2f}m > Entrepôt: {hauteur}m")
            st.write("**Solution:** Réduire le nombre d'étages")
            st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="success-card">', unsafe_allow_html=True)
            st.success("**✅ Hauteur conforme**")
            st.write(f"Marge: {hauteur - results['hauteur_totale_rack']:.2f}m")
            st.markdown('</div>', unsafe_allow_html=True)
    
    with alert_cols[1]:
        if allee < specs['allee_min']:
            st.markdown('<div class="warning-card">', unsafe_allow_html=True)
            st.error("**Allée trop étroite**")
            st.write(f"Actuelle: {allee}m < Minimum: {specs['allee_min']}m")
            st.write(f"**Recommandation:** Augmenter à {specs['allee_min'] + 0.5}m")
            st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="success-card">', unsafe_allow_html=True)
            st.success("**✅ Allée conforme**")
            st.write(f"Marge: {allee - specs['allee_min']:.1f}m")
            st.markdown('</div>', unsafe_allow_html=True)
    
    with alert_cols[2]:
        if results['taux_utilisation'] < 60:
            st.markdown('<div class="warning-card">', unsafe_allow_html=True)
            st.warning("**Faible utilisation**")
            st.write(f"Taux: {results['taux_utilisation']:.1f}% < Optimal: 70%")
            st.write("**Suggestion:** Ajuster la disposition")
            st.markdown('</div>', unsafe_allow_html=True)
        elif results['taux_utilisation'] > 85:
            st.markdown('<div class="warning-card">', unsafe_allow_html=True)
            st.warning("**Utilisation très élevée**")
            st.write(f"Taux: {results['taux_utilisation']:.1f}% > Maximum conseillé: 85%")
            st.write("**Risque:** Congestion possible")
            st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="success-card">', unsafe_allow_html=True)
            st.success("**✅ Utilisation optimale**")
            st.write(f"Taux: {results['taux_utilisation']:.1f}% (idéal: 70-80%)")
            st.markdown('</div>', unsafe_allow_html=True)

# Section d'aide
with st.expander("📚 Documentation et aide", expanded=False):
    st.markdown("### 🎯 Guide d'utilisation")
    st.markdown("""
    1. **Configurez les paramètres** dans la sidebar
    2. **Lancez l'analyse** avec le bouton principal
    3. **Consultez les résultats** dans les différents onglets
    4. **Exportez** les données et rapports
    
    ### 📏 Normes de sécurité
    - Allée minimum: **3.0m** pour tout chariot
    - Marge hauteur: **+0.5m minimum** au-dessus des racks
    - Charge au sol: vérifier la capacité du plancher
    """)

# Pied de page
st.divider()
st.markdown("""
<div style="text-align: center; color: #666;">
    <p>🏭 <strong>Warehouse Configuration Optimizer Pro</strong> v3.0 | 
    Développé avec Streamlit</p>
</div>
""", unsafe_allow_html=True)
