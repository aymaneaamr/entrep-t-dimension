import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import numpy as np
from itertools import product

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
                                      help="Longueur totale de l'entrepôt")
        with col2:
            largeur = st.number_input("Largeur (m)", min_value=10.0, max_value=100.0, value=30.0, step=1.0,
                                     help="Largeur totale de l'entrepôt")
        
        hauteur = st.number_input("Hauteur (m)", min_value=3.0, max_value=30.0, value=12.0, step=0.5,
                                 help="Hauteur sous plafond")
        
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
                                        index=4)
        with col2:
            rack_largeur = st.selectbox("Largeur rack (m)", 
                                       [0.8, 1.0, 1.2, 1.5, 1.8], 
                                       index=1)
        with col3:
            rack_hauteur = st.selectbox("Hauteur rack (m)", 
                                       [2.0, 3.0, 4.0, 5.0, 6.0, 8.0, 10.0, 12.0], 
                                       index=6)
        
        # Configuration verticale dynamique
        st.subheader("📊 Configuration verticale")
        etages = st.slider("Nombre d'étages", 1, 15, 6)
        hauteur_etage = st.number_input("Hauteur utile par étage (m)", 
                                       min_value=0.5, max_value=3.0, value=1.5, step=0.1)
        
        # Calcul automatique de l'espacement vertical
        espacement_vertical = st.slider("Espacement vertical (cm)", 10, 100, 30)
        
        # Capacité par niveau
        st.subheader("🎯 Capacité par niveau")
        palettes_longueur = st.number_input("Palettes en longueur", min_value=1, max_value=10, value=2)
        palettes_largeur = st.number_input("Palettes en largeur", min_value=1, max_value=5, value=1)
        palettes_par_niveau = palettes_longueur * palettes_largeur
        
        # Type de rack
        st.subheader("🔧 Type de rack")
        rack_type = st.selectbox("Sélectionnez le type de rack", 
                                ["Rack palette standard", "Rack palette dynamique", 
                                 "Rack à palettier", "Rack cantilever", "Rack drive-in"])
        
        # Options selon le type de rack
        if rack_type == "Rack drive-in":
            profondeur_double = st.checkbox("Double profondeur")
            espacement_lateral = 0
        else:
            espacement_lateral = st.slider("Espacement latéral (cm)", 10, 100, 20)
            profondeur_double = False
    
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
        
        type_chariot = st.selectbox("Type de chariot", list(chariot_options.keys()))
        
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
                         step=0.1)
        
        # Vérification de compatibilité
        if rack_hauteur > specs['hauteur_max']:
            st.warning(f"⚠️ La hauteur des racks ({rack_hauteur}m) dépasse "
                      f"la capacité du chariot ({specs['hauteur_max']}m)")
        
        # Charge maximale
        charge_max = st.number_input("Charge max (tonnes)", 
                                    min_value=0.5, 
                                    max_value=10.0, 
                                    value=specs['charge_max'], 
                                    step=0.5)
    
    with tab_opt:
        st.header("⚙️ Options avancées")
        
        # Options d'optimisation
        st.subheader("🎯 Optimisation")
        marge_securite = st.slider("Marge de sécurité (%)", 5, 30, 15)
        taux_utilisation_cible = st.slider("Taux d'utilisation cible (%)", 50, 90, 70)
        
        # Configuration des allées
        st.subheader("🛣️ Configuration des allées")
        all_transversale = st.checkbox("Allée transversale centrale", value=True)
        if all_transversale:
            largeur_transversale = st.slider("Largeur allée transversale (m)", 2.0, 5.0, 3.0)
        
        # Options de visualisation
        st.subheader("👁️ Visualisation")
        show_3d = st.checkbox("Afficher vue 3D", value=True)
        show_heatmap = st.checkbox("Afficher heatmap de densité", value=True)

# Fonction d'optimisation intelligente
def optimiser_configuration(longueur, largeur, hauteur, rack_longueur, rack_largeur, 
                           rack_hauteur, etages, hauteur_etage, espacement_vertical,
                           palettes_longueur, palettes_largeur, allee, type_chariot,
                           marge_securite, taux_utilisation_cible, rack_type, profondeur_double):
    
    # Calculs de base
    surface_totale = longueur * largeur
    volume_total = surface_totale * hauteur
    
    # Calcul de la hauteur totale des racks
    espacement_vertical_m = espacement_vertical / 100
    hauteur_totale_rack = etages * hauteur_etage + (etages - 1) * espacement_vertical_m
    
    # Vérifications de conformité
    conforme_hauteur = hauteur_totale_rack <= (hauteur - 0.5)
    
    # Calcul intelligent du nombre de racks
    coef_utilisation = taux_utilisation_cible / 100
    marge_absolue = marge_securite / 100 * min(rack_longueur, rack_largeur)
    
    # Si double profondeur, ajuster la largeur
    if profondeur_double:
        rack_largeur_effective = rack_largeur * 2
    else:
        rack_largeur_effective = rack_largeur
    
    # Calcul du nombre optimal de racks
    espacement_lateral_m = espacement_lateral / 100 if 'espacement_lateral' in locals() else 0.2
    
    # Méthode d'optimisation améliorée
    max_racks_longueur = int((longueur * coef_utilisation - marge_absolue * 2) / 
                            (rack_longueur + espacement_lateral_m))
    max_racks_largeur = int((largeur * coef_utilisation - marge_absolue * 2 - allee) / 
                           (rack_largeur_effective + espacement_lateral_m))
    
    # Ajuster pour avoir un nombre pair de chaque côté de l'allée
    racks_longueur = max(1, max_racks_longueur)
    racks_largeur = max(1, max_racks_largeur) * 2  # Deux côtés de l'allée
    
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
    
    # Score d'efficacité
    score_hauteur = 1.0 if conforme_hauteur else 0.5
    score_all = 1.0 if allee >= chariot_options[type_chariot]["allee_min"] else 0.7
    score_utilisation = min(taux_utilisation / 80, 1.0)  # Optimal à 80%
    
    score_total = (score_hauteur * 0.3 + score_all * 0.3 + score_utilisation * 0.4) * 100
    
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

# Fonction de visualisation avancée
def creer_visualisation_3d_avancee(longueur, largeur, hauteur, results, rack_longueur, 
                                  rack_largeur, hauteur_totale_rack, allee):
    
    fig = make_subplots(
        rows=2, cols=2,
        specs=[[{'type': 'scene'}, {'type': 'xy'}],
               [{'type': 'surface'}, {'type': 'heatmap'}]],
        subplot_titles=('Vue 3D complète', 'Plan de situation', 
                       'Distribution verticale', 'Densité de stockage'),
        vertical_spacing=0.1,
        horizontal_spacing=0.1
    )
    
    # Vue 3D principale
    # Contour de l'entrepôt
    x_entrepot = [0, longueur, longueur, 0, 0, longueur, longueur, 0]
    y_entrepot = [0, 0, largeur, largeur, 0, 0, largeur, largeur]
    z_entrepot = [0, 0, 0, 0, hauteur, hauteur, hauteur, hauteur]
    
    fig.add_trace(go.Mesh3d(
        x=x_entrepot,
        y=y_entrepot,
        z=z_entrepot,
        opacity=0.1,
        color='lightgray',
        name='Entrepôt'
    ), row=1, col=1)
    
    # Représentation des racks
    racks_longueur = results['racks_longueur']
    racks_largeur = results['racks_largeur'] // 2
    
    for i in range(min(racks_longueur, 10)):  # Limiter pour la performance
        for j in range(min(racks_largeur, 5)):
            for side in [0, 1]:  # Deux côtés de l'allée
                x_pos = i * (rack_longueur + 0.3) + 1
                y_pos = side * (largeur/2 + allee/2) + j * (rack_largeur + 0.2) + 1
                
                # Rack en 3D
                fig.add_trace(go.Mesh3d(
                    x=[x_pos, x_pos + rack_longueur, x_pos + rack_longueur, x_pos],
                    y=[y_pos, y_pos, y_pos + rack_largeur, y_pos + rack_largeur],
                    z=[0, 0, 0, 0],
                    i=[0, 0],
                    j=[1, 2],
                    k=[2, 3],
                    opacity=0.7,
                    color='orange',
                    name=f'Rack' if i == 0 and j == 0 and side == 0 else '',
                    showlegend=i == 0 and j == 0 and side == 0
                ), row=1, col=1)
    
    # Plan de situation
    # Entrepôt
    fig.add_trace(go.Scatter(
        x=[0, longueur, longueur, 0, 0],
        y=[0, 0, largeur, largeur, 0],
        fill="toself",
        fillcolor="rgba(200, 200, 200, 0.2)",
        line=dict(color="black", width=2),
        name="Entrepôt",
        showlegend=False
    ), row=1, col=2)
    
    # Racks en plan
    for i in range(racks_longueur):
        for j in range(racks_largeur):
            for side in [0, 1]:
                x_pos = i * (rack_longueur + 0.3) + 1
                y_pos = side * (largeur/2 + allee/2) + j * (rack_largeur + 0.2) + 1
                
                fig.add_trace(go.Scatter(
                    x=[x_pos, x_pos + rack_longueur, x_pos + rack_longueur, x_pos, x_pos],
                    y=[y_pos, y_pos, y_pos + rack_largeur, y_pos + rack_largeur, y_pos],
                    fill="toself",
                    fillcolor="orange",
                    line=dict(color="darkorange", width=1),
                    mode="lines",
                    showlegend=False
                ), row=1, col=2)
    
    # Distribution verticale
    niveaux = list(range(1, etages + 1))
    capacites = [results['palettes_par_niveau'] * results['nb_racks'] for _ in niveaux]
    
    fig.add_trace(go.Bar(
        x=niveaux,
        y=capacites,
        name='Palettes par niveau',
        marker_color='orange'
    ), row=2, col=1)
    
    # Heatmap de densité
    heatmap_data = np.zeros((10, 10))
    for i in range(10):
        for j in range(10):
            # Simuler une densité de stockage
            heatmap_data[i][j] = np.random.uniform(0.5, 1.0)
    
    fig.add_trace(go.Heatmap(
        z=heatmap_data,
        colorscale='Viridis',
        showscale=True,
        name='Densité'
    ), row=2, col=2)
    
    # Mise en page
    fig.update_layout(
        height=800,
        showlegend=True,
        title_text="Visualisation avancée de la configuration",
        scene=dict(
            xaxis_title='Longueur (m)',
            yaxis_title='Largeur (m)',
            zaxis_title='Hauteur (m)',
            aspectmode='manual',
            aspectratio=dict(x=longueur/10, y=largeur/10, z=hauteur/10)
        ),
        scene2=dict(
            xaxis_title='Longueur (m)',
            yaxis_title='Largeur (m)'
        ),
        scene3=dict(
            xaxis_title='Niveau',
            yaxis_title='Nombre de palettes'
        ),
        scene4=dict(
            xaxis_title='Zone X',
            yaxis_title='Zone Y'
        )
    )
    
    return fig

# Interface principale
st.markdown("## 🚀 Analyse et Optimisation")

col_start, col_reset = st.columns([3, 1])
with col_start:
    if st.button("🚀 Lancer l'analyse complète", type="primary", use_container_width=True):
        st.session_state.calcul_done = True
with col_reset:
    if st.button("🔄 Réinitialiser", use_container_width=True):
        st.session_state.calcul_done = False
        st.rerun()

if st.session_state.calcul_done:
    # Calcul des résultats
    results = optimiser_configuration(
        longueur, largeur, hauteur, rack_longueur, rack_largeur,
        rack_hauteur, etages, hauteur_etage, espacement_vertical,
        palettes_longueur, palettes_largeur, allee, type_chariot,
        marge_securite, taux_utilisation_cible, rack_type, 
        profondeur_double if 'profondeur_double' in locals() else False
    )
    
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
        # Visualisations avancées
        st.subheader("🎨 Visualisations interactives")
        
        if show_3d:
            fig_3d = creer_visualisation_3d_avancee(
                longueur, largeur, hauteur, results, rack_longueur,
                rack_largeur, results['hauteur_totale_rack'], allee
            )
            st.plotly_chart(fig_3d, use_container_width=True)
        
        # Graphiques supplémentaires
        col_v1, col_v2 = st.columns(2)
        
        with col_v1:
            # Graphique de répartition
            labels = ['Racks', 'Allées', 'Espace libre']
            values = [
                results['surface_racks_totale'],
                results['surface_all'] * 0.7,
                results['surface_all'] * 0.3
            ]
            
            fig_pie = px.pie(
                values=values,
                names=labels,
                title='Répartition de la surface',
                color_discrete_sequence=px.colors.qualitative.Set3
            )
            fig_pie.update_traces(textposition='inside', textinfo='percent+label')
            st.plotly_chart(fig_pie, use_container_width=True)
        
        with col_v2:
            # Graphique de capacité cumulée
            niveaux = list(range(1, etages + 1))
            capacite_niveaux = [results['palettes_par_niveau'] * results['nb_racks'] for _ in niveaux]
            capacite_cumulee = np.cumsum(capacite_niveaux)
            
            fig_area = go.Figure()
            fig_area.add_trace(go.Scatter(
                x=niveaux,
                y=capacite_cumulee,
                fill='tozeroy',
                fillcolor='rgba(255, 165, 0, 0.3)',
                line=dict(color='orange', width=3),
                name='Capacité cumulée'
            ))
            fig_area.update_layout(
                title='Capacité cumulée par niveau',
                xaxis_title='Niveau',
                yaxis_title='Palettes cumulées',
                hovermode='x'
            )
            st.plotly_chart(fig_area, use_container_width=True)
        
        if show_heatmap:
            st.subheader("🗺️ Heatmap de densité")
            # Créer une heatmap simulée
            heatmap_data = np.random.rand(20, 20)
            fig_heat = px.imshow(
                heatmap_data,
                title='Densité de stockage simulée',
                color_continuous_scale='Viridis'
            )
            st.plotly_chart(fig_heat, use_container_width=True)
    
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
        
        # Analyse de scénarios
        st.subheader("🔮 Analyse de scénarios")
        
        scenario_cols = st.columns(3)
        with scenario_cols[0]:
            if st.button("📈 Optimiser pour la capacité"):
                # Simulation d'optimisation pour la capacité
                st.info(f"Capacité maximale estimée: {int(results['capacite_totale'] * 1.2):,} palettes")
        
        with scenario_cols[1]:
            if st.button("💰 Optimiser pour les coûts"):
                # Simulation d'optimisation pour les coûts
                st.info(f"Réduction estimée: {int(results['nb_racks'] * 0.8)} racks (-20%)")
        
        with scenario_cols[2]:
            if st.button("🚚 Optimiser pour la productivité"):
                # Simulation d'optimisation pour la productivité
                st.info(f"Gain productivité estimé: +15% avec allée {allee + 0.5}m")
    
    with tab_rapport:
        # Rapport détaillé
        st.subheader("📋 Rapport technique complet")
        
        rapport = f"""
        RAPPORT TECHNIQUE - OPTIMISATION D'ENTREPÔT
        {'='*70}
        
        I. CONTEXTE ET OBJECTIFS
        {'-'*40}
        • Type de rack : {rack_type}
        • Type de chariot : {type_chariot}
        • Objectif d'utilisation : {taux_utilisation_cible}%
        • Date d'analyse : {pd.Timestamp.now().strftime('%d/%m/%Y %H:%M')}
        
        II. CARACTÉRISTIQUES DE L'ENTREPÔT
        {'-'*40}
        • Dimensions : {longueur}m (L) × {largeur}m (l) × {hauteur}m (H)
        • Surface totale : {results['surface_totale']:,.0f} m²
        • Volume total : {results['volume_total']:,.0f} m³
        • Hauteur sous plafond : {hauteur}m
        
        III. CONFIGURATION DES RACKS
        {'-'*40}
        • Dimensions unitaires : {rack_longueur}m × {rack_largeur}m × {rack_hauteur}m
        • Hauteur totale rack : {results['hauteur_totale_rack']:.2f}m ({etages} étages)
        • Hauteur par étage : {hauteur_etage}m
        • Espacement vertical : {espacement_vertical}cm
        • Configuration : {results['racks_longueur']} × {results['racks_largeur']}
        • Nombre total racks : {results['nb_racks']:,}
        • Surface au sol racks : {results['surface_racks_totale']:,.0f} m²
        
        IV. CAPACITÉ DE STOCKAGE
        {'-'*40}
        • Palettes par niveau : {results['palettes_par_niveau']}
        • Palettes par rack : {results['capacite_par_rack']}
        • Capacité totale : {results['capacite_totale']:,} palettes
        • Densité : {results['capacite_totale'] / results['surface_totale']:.2f} palettes/m²
        • Volume utile : {results['volume_utile']:,.0f} m³
        
        V. CIRCULATION ET ACCESSIBILITÉ
        {'-'*40}
        • Type chariot : {type_chariot}
        • Largeur allée : {allee}m (minimum recommandé : {chariot_options[type_chariot]['allee_min']}m)
        • Surface allées : {results['surface_all']:,.0f} m²
        • Pourcentage circulation : {(results['surface_all'] / results['surface_totale']) * 100:.1f}%
        
        VI. PERFORMANCES ET INDICATEURS
        {'-'*40}
        • Taux d'utilisation surface : {results['taux_utilisation']:.1f}%
        • Utilisation verticale : {(results['hauteur_totale_rack'] / hauteur) * 100:.1f}%
        • Score global d'efficacité : {results['score_total']:.1f}/100
        • Conformité hauteur : {'✅ CONFORME' if results['conforme_hauteur'] else '❌ NON CONFORME'}
        • Conformité allées : {'✅ CONFORME' if allee >= chariot_options[type_chariot]['allee_min'] else '❌ NON CONFORME'}
        
        VII. RECOMMANDATIONS
        {'-'*40}
        1. Optimisation spatiale :
           - Taux d'utilisation actuel : {results['taux_utilisation']:.1f}%
           - Objectif optimal : 70-80%
           - Marge d'amélioration : {max(0, 75 - results['taux_utilisation']):.1f}%
        
        2. Sécurité et conformité :
           - Allée minimum requise : {chariot_options[type_chariot]['allee_min']}m
           - Hauteur libre recommandée : +0.5m minimum
           - Vérifier charge au sol : {results['capacite_totale'] * charge_max / 1000:.1f} tonnes
        
        3. Productivité :
           - Temps d'accès estimé : {max(1, results['racks_longueur'] * 0.5):.1f} minutes
           - Débit théorique : {results['capacite_totale'] / 8:.0f} palettes/heure
           - Rotation optimale : Tous les {365 / (results['capacite_totale'] / 1000):.0f} jours
        
        VIII. ESTIMATION DES COÛTS
        {'-'*40}
        • Investissement racks (estimation) : {results['nb_racks'] * 1500:,.0f} €
        • Coût par palette : {(results['nb_racks'] * 1500) / results['capacite_totale']:.0f} €
        • Coût par m² : {(results['nb_racks'] * 1500) / results['surface_totale']:.0f} €/m²
        • ROI estimé : 3-5 ans
        
        IX. RISQUES IDENTIFIÉS
        {'-'*40}
        • {'Aucun risque majeur' if results['score_total'] > 80 else 'Risques modérés détectés'}
        • {'Conformité validée' if allee >= chariot_options[type_chariot]['allee_min'] and results['conforme_hauteur'] else 'Points de non-conformité'}
        • {'Capacité adaptée' if results['taux_utilisation'] > 60 else 'Sous-utilisation détectée'}
        
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
        
        # Options d'export multiples
        col_e1, col_e2, col_e3 = st.columns(3)
        
        with col_e1:
            # Export CSV des données principales
            export_data = {
                'Paramètre': [
                    'Longueur entrepôt', 'Largeur entrepôt', 'Hauteur entrepôt',
                    'Surface totale', 'Volume total', 'Nombre racks',
                    'Capacité totale', 'Taux utilisation', 'Largeur allée',
                    'Type chariot', 'Hauteur rack', 'Étages par rack'
                ],
                'Valeur': [
                    longueur, largeur, hauteur,
                    results['surface_totale'], results['volume_total'], results['nb_racks'],
                    results['capacite_totale'], results['taux_utilisation'], allee,
                    type_chariot, results['hauteur_totale_rack'], etages
                ],
                'Unité': [
                    'm', 'm', 'm', 'm²', 'm³', 'unités',
                    'palettes', '%', 'm', 'type', 'm', 'niveaux'
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
            # Export JSON pour intégration
            import json
            json_data = {
                "entrepot": {
                    "dimensions": {"longueur": longueur, "largeur": largeur, "hauteur": hauteur},
                    "surface": results['surface_totale'],
                    "volume": results['volume_total']
                },
                "racks": {
                    "dimensions": {"longueur": rack_longueur, "largeur": rack_largeur, "hauteur": rack_hauteur},
                    "nombre": results['nb_racks'],
                    "disposition": f"{results['racks_longueur']}x{results['racks_largeur']}",
                    "etages": etages,
                    "capacite_totale": results['capacite_totale']
                },
                "chariots": {
                    "type": type_chariot,
                    "allee": allee,
                    "conformite": allee >= chariot_options[type_chariot]['allee_min']
                },
                "performances": {
                    "taux_utilisation": results['taux_utilisation'],
                    "score": results['score_total'],
                    "date_analyse": pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')
                }
            }
            
            st.download_button(
                label="📁 Données JSON",
                data=json.dumps(json_data, indent=2),
                file_name=f"configuration_{pd.Timestamp.now().strftime('%Y%m%d_%H%M')}.json",
                mime="application/json"
            )
        
        with col_e3:
            # Export image des visualisations
            st.info("💡 Pour exporter les graphiques :")
            st.markdown("""
            1. Cliquez sur l'icône appareil photo 📷 dans le graphique
            2. Choisissez le format (PNG, JPEG, SVG)
            3. Téléchargez l'image
            """)
    
    # Section d'alertes et recommandations
    st.markdown("## ⚠️ Alertes et recommandations")
    
    alert_cols = st.columns(3)
    
    with alert_cols[0]:
        if not results['conforme_hauteur']:
            st.markdown('<div class="warning-card">', unsafe_allow_html=True)
            st.error("**Hauteur non conforme**")
            st.write(f"Racks: {results['hauteur_totale_rack']:.2f}m > Entrepôt: {hauteur}m")
            st.write("**Solution:** Réduire le nombre d'étages ou la hauteur par étage")
            st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="success-card">', unsafe_allow_html=True)
            st.success("**✅ Hauteur conforme**")
            st.write(f"Marge: {hauteur - results['hauteur_totale_rack']:.2f}m")
            st.markdown('</div>', unsafe_allow_html=True)
    
    with alert_cols[1]:
        if allee < chariot_options[type_chariot]['allee_min']:
            st.markdown('<div class="warning-card">', unsafe_allow_html=True)
            st.error("**Allée trop étroite**")
            st.write(f"Actuelle: {allee}m < Minimum: {chariot_options[type_chariot]['allee_min']}m")
            st.write(f"**Recommandation:** Augmenter à {chariot_options[type_chariot]['allee_min'] + 0.5}m")
            st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="success-card">', unsafe_allow_html=True)
            st.success("**✅ Allée conforme**")
            st.write(f"Marge: {allee - chariot_options[type_chariot]['allee_min']:.1f}m")
            st.markdown('</div>', unsafe_allow_html=True)
    
    with alert_cols[2]:
        if results['taux_utilisation'] < 60:
            st.markdown('<div class="warning-card">', unsafe_allow_html=True)
            st.warning("**Faible utilisation**")
            st.write(f"Taux: {results['taux_utilisation']:.1f}% < Optimal: 70%")
            st.write("**Suggestion:** Ajuster la disposition des racks")
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

# Section d'aide et documentation
with st.expander("📚 Documentation et aide", expanded=False):
    col_doc1, col_doc2 = st.columns(2)
    
    with col_doc1:
        st.markdown("### 🎯 Guide d'utilisation")
        st.markdown("""
        1. **Configurez les paramètres** dans la sidebar
        2. **Lancez l'analyse** avec le bouton principal
        3. **Consultez les résultats** dans les différents onglets
        4. **Exportez** les données et rapports
        5. **Ajustez** selon les recommandations
        
        ### 📏 Normes de sécurité
        - Allée minimum: **3.0m** pour tout chariot
        - Marge hauteur: **+0.5m minimum** au-dessus des racks
        - Charge au sol: vérifier la capacité du plancher
        - Éclairage: minimum **200 lux** dans les allées
        """)
    
    with col_doc2:
        st.markdown("### 🔍 Bonnes pratiques")
        st.markdown("""
        **Optimisation spatiale:**
        - Taux d'utilisation idéal: 70-80%
        - Hauteur d'étage adaptée aux produits
        - Considérer la rotation des stocks
        
        **Productivité:**
        - Allées plus larges = productivité +15%
        - Organisation en zones (réception, stockage, expédition)
        - Chemins de circulation optimisés
        
        **Maintenance:**
        - Espace pour maintenance des chariots
        - Accès aux systèmes de sécurité
        - Passage pour inspections
        """)

# Pied de page
st.divider()
st.markdown("""
<div style="text-align: center; color: #666;">
    <p>🏭 <strong>Warehouse Configuration Optimizer Pro</strong> v3.0 | 
    Développé avec Streamlit | 
    <a href="#" style="color: #1E40AF;">Documentation complète</a></p>
    <p style="font-size: 0.9em;">© 2024 - Outil d'optimisation d'entrepôt professionnel</p>
</div>
""", unsafe_allow_html=True)

# Option pour générer un rapport automatique
if st.session_state.calcul_done:
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 📈 Statistiques rapides")
    st.sidebar.metric("📦 Capacité totale", f"{results['capacite_totale']:,}".replace(',', ' '))
    st.sidebar.metric("💰 Coût estimé/rack", f"{1500:,} €".replace(',', ' '))
    st.sidebar.metric("⭐ Score global", f"{results['score_total']:.1f}/100")
