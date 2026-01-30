import streamlit as st
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import json
from datetime import datetime

# Configuration de la page
st.set_page_config(
    page_title="Outil de Dimensionnement d'Entrepôts",
    page_icon="🏭",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialisation de session_state
if 'app_mode' not in st.session_state:
    st.session_state.app_mode = "simple"

if 'warehouse_data' not in st.session_state:
    st.session_state.warehouse_data = {
        'simple_params': {
            'longueur': 50.0,
            'largeur': 30.0,
            'hauteur': 10.0,
            'type_entrepot': 'général',
            'temp_controlee': False,
            'nb_niveaux': 1,
            'surface_utile': 0.0,
            'volume_utile': 0.0
        },
        'advanced_params': {},
        'calculations': {},
        'visualization_data': {}
    }

# CSS personnalisé
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1E3A8A;
        text-align: center;
        margin-bottom: 2rem;
        font-weight: bold;
    }
    .step-card {
        background-color: #F3F4F6;
        border-radius: 10px;
        padding: 1.5rem;
        margin-bottom: 1rem;
        border-left: 4px solid #3B82F6;
    }
    .success-box {
        background-color: #D1FAE5;
        border: 1px solid #10B981;
        border-radius: 5px;
        padding: 1rem;
        margin: 1rem 0;
    }
    .warning-box {
        background-color: #FEF3C7;
        border: 1px solid #F59E0B;
        border-radius: 5px;
        padding: 1rem;
        margin: 1rem 0;
    }
    .metric-card {
        background: white;
        border-radius: 10px;
        padding: 1rem;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        margin: 0.5rem 0;
    }
</style>
""", unsafe_allow_html=True)

def show_advanced_mode():
    """Affiche le mode avancé (en construction)"""
    st.title("🚧 MODE AVANCÉ - EN CONSTRUCTION")
    
    st.markdown("---")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("""
        ### Le mode avancé est actuellement en cours de développement
        
        Il offrira des fonctionnalités supplémentaires pour des analyses plus poussées :
        
        📊 **Analyse détaillée des flux logistiques**
        - Simulation des mouvements de stock
        - Analyse des temps de traitement
        - Optimisation des parcours
        
        🧮 **Calculs avancés selon les normes ISO**
        - Conformité ISO 9001:2015
        - Normes de sécurité ISO 45001
        - Standards de qualité ISO 14001
        
        🛣️ **Optimisation automatique des allées**
        - Calcul des largeurs optimales
        - Organisation des zones de circulation
        - Planification des accès
        
        ⏱️ **Simulation des temps de cycle**
        - Analyse des performances
        - Identification des goulots
        - Optimisation des processus
        
        📋 **Rapports techniques complets**
        - Génération automatique de rapports
        - Exports personnalisables
        - Analyse comparative
        """)
    
    with col2:
        st.markdown("### Prochaines fonctionnalités")
        progress_data = {
            "Fonctionnalité": ["Interface avancée", "Simulations 3D", "Rapports ISO", "API d'intégration"],
            "Progression": [30, 15, 45, 10]
        }
        df_progress = pd.DataFrame(progress_data)
        
        for _, row in df_progress.iterrows():
            st.markdown(f"**{row['Fonctionnalité']}**")
            st.progress(row['Progression'] / 100)
            st.markdown("---")
    
    st.markdown("---")
    
    # Bouton pour passer au mode simple
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("🚀 Passer au Mode Simple", use_container_width=True, type="primary"):
            st.session_state.app_mode = "simple"
            st.rerun()

def calculate_warehouse_metrics(params):
    """Calcule les métriques de l'entrepôt"""
    longueur = params.get('longueur', 50.0)
    largeur = params.get('largeur', 30.0)
    hauteur = params.get('hauteur', 10.0)
    nb_niveaux = params.get('nb_niveaux', 1)
    
    # Calculs de base
    surface_totale = longueur * largeur
    surface_utile = surface_totale * 0.85  # 85% de surface utile
    volume_total = surface_totale * hauteur
    volume_utile = volume_total * 0.80  # 80% de volume utile
    
    # Calculs avancés
    perimetre = 2 * (longueur + largeur)
    ratio_forme = longueur / largeur if largeur > 0 else 0
    
    return {
        'surface_totale': surface_totale,
        'surface_utile': surface_utile,
        'volume_total': volume_total,
        'volume_utile': volume_utile,
        'perimetre': perimetre,
        'ratio_forme': ratio_forme,
        'nb_niveaux': nb_niveaux
    }

def show_visualization(params, metrics):
    """Affiche la visualisation 2D/3D de l'entrepôt"""
    st.header("📊 Visualisation de l'entrepôt")
    
    tab1, tab2, tab3 = st.tabs(["📐 Vue 2D", "🎯 Vue 3D", "📈 Métriques"])
    
    with tab1:
        col1, col2 = st.columns(2)
        
        with col1:
            # Plan 2D
            fig, ax = plt.subplots(figsize=(10, 8))
            
            # Dessiner le bâtiment
            rect = plt.Rectangle((0, 0), 
                                params['longueur'], 
                                params['largeur'],
                                linewidth=3, 
                                edgecolor='#1E3A8A', 
                                facecolor='#60A5FA', 
                                alpha=0.3,
                                label='Bâtiment principal')
            ax.add_patch(rect)
            
            # Zone de stockage (80% de la surface)
            stock_width = params['largeur'] * 0.8
            stock_rect = plt.Rectangle((params['longueur'] * 0.1, params['largeur'] * 0.1),
                                      params['longueur'] * 0.8,
                                      stock_width,
                                      linewidth=2,
                                      edgecolor='#059669',
                                      facecolor='#34D399',
                                      alpha=0.5,
                                      label='Zone de stockage')
            ax.add_patch(stock_rect)
            
            # Allées
            allée_y = params['largeur'] * 0.5
            ax.plot([0, params['longueur']], [allée_y, allée_y], 
                   '--', color='#DC2626', linewidth=2, label='Allée principale')
            
            # Configuration du graphique
            ax.set_xlim(0, params['longueur'] * 1.1)
            ax.set_ylim(0, params['largeur'] * 1.1)
            ax.set_xlabel('Longueur (m)', fontsize=12)
            ax.set_ylabel('Largeur (m)', fontsize=12)
            ax.set_title('Plan de l\'entrepôt', fontsize=16, fontweight='bold')
            ax.grid(True, alpha=0.3)
            ax.legend(loc='upper right')
            ax.set_aspect('equal', adjustable='box')
            
            st.pyplot(fig)
        
        with col2:
            # Légende et informations
            st.markdown("### Légende du plan")
            
            info_data = {
                "Zone": ["Bâtiment principal", "Zone de stockage", "Allées de circulation"],
                "Couleur": ["🔵", "🟢", "🔴"],
                "Surface": [
                    f"{metrics['surface_totale']:,.0f} m²",
                    f"{metrics['surface_utile']:,.0f} m²",
                    f"{metrics['surface_totale'] - metrics['surface_utile']:,.0f} m²"
                ]
            }
            
            df_info = pd.DataFrame(info_data)
            st.dataframe(df_info, use_container_width=True, hide_index=True)
            
            st.markdown("### 📋 Informations techniques")
            st.markdown(f"""
            - **Dimensions extérieures:** {params['longueur']}m × {params['largeur']}m
            - **Surface totale:** {metrics['surface_totale']:,.0f} m²
            - **Surface utile:** {metrics['surface_utile']:,.0f} m²
            - **Volume total:** {metrics['volume_total']:,.0f} m³
            - **Nombre de niveaux:** {params['nb_niveaux']}
            - **Ratio L/l:** {metrics['ratio_forme']:.2f}
            """)
    
    with tab2:
        # Vue 3D simplifiée avec Plotly
        st.markdown("### Vue 3D interactive")
        
        # Créer les coordonnées pour le bâtiment 3D
        x = [0, params['longueur'], params['longueur'], 0, 0, params['longueur'], 
             params['longueur'], 0]
        y = [0, 0, params['largeur'], params['largeur'], 0, 0, 
             params['largeur'], params['largeur']]
        z = [0, 0, 0, 0, params['hauteur'], params['hauteur'], 
             params['hauteur'], params['hauteur']]
        
        # Créer la figure 3D
        fig_3d = go.Figure(data=[
            go.Mesh3d(
                x=x,
                y=y,
                z=z,
                color='lightblue',
                opacity=0.5,
                name='Bâtiment'
            )
        ])
        
        # Configuration de la vue 3D
        fig_3d.update_layout(
            title="Visualisation 3D de l'entrepôt",
            scene=dict(
                xaxis_title='Longueur (m)',
                yaxis_title='Largeur (m)',
                zaxis_title='Hauteur (m)',
                aspectmode='data'
            ),
            height=600,
            showlegend=True
        )
        
        st.plotly_chart(fig_3d, use_container_width=True)
    
    with tab3:
        # Métriques détaillées
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("🏢 Surface totale", f"{metrics['surface_totale']:,.0f} m²")
            st.metric("📦 Surface utile", f"{metrics['surface_utile']:,.0f} m²")
        
        with col2:
            st.metric("📊 Volume total", f"{metrics['volume_total']:,.0f} m³")
            st.metric("🎯 Volume utile", f"{metrics['volume_utile']:,.0f} m³")
        
        with col3:
            st.metric("📐 Périmètre", f"{metrics['perimetre']:,.0f} m")
            st.metric("⚖️ Ratio forme", f"{metrics['ratio_forme']:.2f}")
        
        # Graphique de répartition
        st.markdown("### 📊 Répartition des surfaces")
        
        labels = ['Stockage', 'Circulation', 'Services', 'Sécurité']
        values = [65, 20, 10, 5]
        
        fig_pie, ax_pie = plt.subplots(figsize=(8, 6))
        ax_pie.pie(values, labels=labels, autopct='%1.1f%%', 
                  colors=['#34D399', '#60A5FA', '#FBBF24', '#F87171'])
        ax_pie.set_title('Répartition des surfaces', fontsize=14, fontweight='bold')
        
        st.pyplot(fig_pie)
    
    # Boutons d'export
    st.markdown("---")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("📥 Exporter les données", use_container_width=True):
            export_data = {
                "parametres": params,
                "metriques": metrics,
                "date_export": datetime.now().isoformat(),
                "version_app": "4.0"
            }
            
            st.download_button(
                label="Télécharger JSON",
                data=json.dumps(export_data, indent=2),
                file_name=f"entrepot_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                mime="application/json"
            )
    
    with col2:
        if st.button("🖨️ Générer un rapport", use_container_width=True):
            st.success("Fonctionnalité de génération de rapport en développement")
    
    with col3:
        if st.button("🔄 Réinitialiser", use_container_width=True):
            st.session_state.warehouse_data['simple_params'] = {
                'longueur': 50.0,
                'largeur': 30.0,
                'hauteur': 10.0,
                'type_entrepot': 'général',
                'temp_controlee': False,
                'nb_niveaux': 1
            }
            st.success("Paramètres réinitialisés!")
            st.rerun()

def show_simple_mode():
    """Affiche le mode simple avec les 5 étapes"""
    
    # Header principal
    st.markdown('<h1 class="main-header">🏭 OUTIL INTELLIGENT DE DIMENSIONNEMENT D\'ENTREPÔTS</h1>', 
                unsafe_allow_html=True)
    
    # Barre latérale - ÉTAPES DU PROJET
    with st.sidebar:
        st.markdown("## 📋 PROGRESSION")
        st.markdown("### ÉTAPES DU PROJET")
        
        etapes = ["BÂTIMENT", "STOCKAGE", "CIRCULATION", "RÉSULTATS", "VISUALISATION"]
        etape_actuelle = st.radio(
            "Sélectionnez une étape:",
            etapes,
            index=0,
            label_visibility="collapsed"
        )
        
        st.markdown("---")
        st.markdown("### Mode de calcul")
        mode = st.radio(
            "CHOISISSEZ LE MODE:",
            ["CALCUL SIMPLE", "CALCUL AVANCÉ"],
            index=0,
            key="mode_selector"
        )
        
        if mode == "CALCUL AVANCÉ":
            if st.button("🔧 Passer au Mode Avancé", use_container_width=True):
                st.session_state.app_mode = "advanced"
                st.rerun()
        
        st.markdown("---")
        st.caption("v4.0 | Mode Simple & Mode Avancé • Normes ISO intégrées")
    
    # Récupération des paramètres actuels
    params = st.session_state.warehouse_data['simple_params']
    
    # ÉTAPE 1: BÂTIMENT
    if etape_actuelle == "BÂTIMENT":
        st.header("🏢 ÉTAPE 1: BÂTIMENT")
        st.markdown("Définissez les caractéristiques principales de votre entrepôt")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            params['longueur'] = st.number_input(
                "Longueur (m)",
                min_value=10.0,
                max_value=200.0,
                value=params['longueur'],
                step=5.0,
                help="Longueur totale du bâtiment"
            )
        
        with col2:
            params['largeur'] = st.number_input(
                "Largeur (m)",
                min_value=10.0,
                max_value=100.0,
                value=params['largeur'],
                step=5.0,
                help="Largeur totale du bâtiment"
            )
        
        with col3:
            params['hauteur'] = st.number_input(
                "Hauteur sous plafond (m)",
                min_value=3.0,
                max_value=30.0,
                value=params['hauteur'],
                step=1.0,
                help="Hauteur libre sous plafond"
            )
        
        st.markdown("---")
        
        col1, col2 = st.columns(2)
        
        with col1:
            params['type_entrepot'] = st.selectbox(
                "Type d'entrepôt",
                ["général", "frigorifique", "dangereux", "à température contrôlée", "automatisé"],
                index=["général", "frigorifique", "dangereux", "à température contrôlée", "automatisé"].index(params.get('type_entrepot', 'général'))
            )
        
        with col2:
            params['nb_niveaux'] = st.selectbox(
                "Nombre de niveaux",
                [1, 2, 3, 4, 5],
                index=params.get('nb_niveaux', 1) - 1
            )
        
        params['temp_controlee'] = st.checkbox(
            "Température contrôlée",
            value=params.get('temp_controlee', False)
        )
        
        # Prévisualisation rapide
        st.markdown("---")
        st.subheader("📊 Aperçu des dimensions")
        
        metrics_preview = calculate_warehouse_metrics(params)
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Surface", f"{metrics_preview['surface_totale']:,.0f} m²")
        with col2:
            st.metric("Volume", f"{metrics_preview['volume_total']:,.0f} m³")
        with col3:
            st.metric("Périmètre", f"{metrics_preview['perimetre']:,.0f} m")
        with col4:
            st.metric("Niveaux", params['nb_niveaux'])
    
    # ÉTAPE 2: STOCKAGE
    elif etape_actuelle == "STOCKAGE":
        st.header("📦 ÉTAPE 2: STOCKAGE")
        st.markdown("Configurez les paramètres de stockage")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Système de stockage")
            
            systeme_stockage = st.selectbox(
                "Type de système",
                ["Palettes rack", "Étagères fixes", "Cantilever", "Drive-in", "Automatisé"]
            )
            
            hauteur_rack = st.slider(
                "Hauteur des racks (m)",
                min_value=3.0,
                max_value=float(params['hauteur']),
                value=min(8.0, float(params['hauteur'])),
                step=0.5
            )
            
            profondeur_palette = st.selectbox(
                "Profondeur palette",
                ["0.8m", "1.0m", "1.2m", "1.5m"]
            )
        
        with col2:
            st.subheader("Capacité de stockage")
            
            nb_allees = st.number_input(
                "Nombre d'allées de stockage",
                min_value=2,
                max_value=20,
                value=4,
                step=1
            )
            
            nb_niveaux_rack = st.number_input(
                "Niveaux par rack",
                min_value=1,
                max_value=10,
                value=4,
                step=1
            )
            
            # Estimation de capacité
            if st.button("Estimer la capacité"):
                capacité_estimée = nb_allees * nb_niveaux_rack * 100  # Estimation simplifiée
                st.success(f"Capacité estimée: {capacité_estimée} palettes")
        
        st.markdown("---")
        st.markdown("### 📈 Configuration des zones")
        
        zones = st.multiselect(
            "Zones à inclure",
            ["Réception", "Stockage principal", "Préparation de commande", "Expédition", "Quarantaine", "Retours"],
            default=["Réception", "Stockage principal", "Préparation de commande", "Expédition"]
        )
    
    # ÉTAPE 3: CIRCULATION
    elif etape_actuelle == "CIRCULATION":
        st.header("🚚 ÉTAPE 3: CIRCULATION")
        st.markdown("Définissez les voies de circulation et accès")
        
        tab1, tab2, tab3 = st.tabs(["Allées intérieures", "Accès extérieurs", "Sécurité"])
        
        with tab1:
            col1, col2 = st.columns(2)
            
            with col1:
                largeur_allee_princ = st.number_input(
                    "Largeur allée principale (m)",
                    min_value=3.0,
                    max_value=10.0,
                    value=4.0,
                    step=0.5
                )
                
                largeur_allee_second = st.number_input(
                    "Largeur allées secondaires (m)",
                    min_value=2.0,
                    max_value=6.0,
                    value=3.0,
                    step=0.5
                )
            
            with col2:
                sens_circulation = st.selectbox(
                    "Sens de circulation",
                    ["Sens unique", "Double sens", "Mixte"]
                )
                
                type_manutention = st.multiselect(
                    "Équipements de manutention",
                    ["Chariot élévateur", "Transpalette", "Gerbeur", "Convoyeur", "Robot"]
                )
        
        with tab2:
            col1, col2 = st.columns(2)
            
            with col1:
                nb_quais = st.number_input(
                    "Nombre de quais",
                    min_value=1,
                    max_value=20,
                    value=4,
                    step=1
                )
                
                largeur_porte = st.selectbox(
                    "Largeur des portes",
                    ["3.0m", "4.0m", "4.5m", "5.0m", "6.0m"]
                )
            
            with col2:
                hauteur_porte = st.selectbox(
                    "Hauteur des portes",
                    ["3.0m", "3.5m", "4.0m", "4.5m", "5.0m"]
                )
                
                zone_retournement = st.checkbox(
                    "Zone de retournement camions",
                    value=True
                )
        
        with tab3:
            col1, col2 = st.columns(2)
            
            with col1:
                st.checkbox("Voies d'évacuation", value=True)
                st.checkbox("Signalisations au sol", value=True)
                st.checkbox("Rétroviseurs", value=False)
            
            with col2:
                st.checkbox("Barrières de protection", value=True)
                st.checkbox("Zones piétonnes", value=True)
                st.checkbox("Feux de circulation", value=False)
    
    # ÉTAPE 4: RÉSULTATS
    elif etape_actuelle == "RÉSULTATS":
        st.header("📊 ÉTAPE 4: RÉSULTATS")
        st.markdown("Synthèse des calculs et recommandations")
        
        # Calcul des métriques
        metrics = calculate_warehouse_metrics(params)
        
        # Section des indicateurs clés
        st.markdown("### 📈 Indicateurs clés")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.markdown('<div class="metric-card">', unsafe_allow_html=True)
            st.markdown("**🏢 Surface totale**")
            st.markdown(f"# {metrics['surface_totale']:,.0f} m²")
            st.markdown("</div>", unsafe_allow_html=True)
        
        with col2:
            st.markdown('<div class="metric-card">', unsafe_allow_html=True)
            st.markdown("**📦 Surface utile**")
            st.markdown(f"# {metrics['surface_utile']:,.0f} m²")
            st.markdown(f"*({metrics['surface_utile']/metrics['surface_totale']*100:.1f}% de la surface)*")
            st.markdown("</div>", unsafe_allow_html=True)
        
        with col3:
            st.markdown('<div class="metric-card">', unsafe_allow_html=True)
            st.markdown("**📊 Volume utile**")
            st.markdown(f"# {metrics['volume_utile']:,.0f} m³")
            st.markdown(f"*({metrics['nb_niveaux']} niveau{'s' if metrics['nb_niveaux'] > 1 else ''})*")
            st.markdown("</div>", unsafe_allow_html=True)
        
        with col4:
            st.markdown('<div class="metric-card">', unsafe_allow_html=True)
            st.markdown("**⚖️ Efficacité spatiale**")
            efficacite = (metrics['surface_utile'] / metrics['surface_totale']) * 100
            st.markdown(f"# {efficacite:.1f}%")
            st.progress(efficacite / 100)
            st.markdown("</div>", unsafe_allow_html=True)
        
        st.markdown("---")
        
        # Recommandations
        st.markdown("### 💡 Recommandations")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### ✅ Points forts")
            st.markdown("""
            - **Dimensions bien proportionnées** (ratio L/l: {:.2f})
            - **Hauteur sous plafond adaptée** pour {} niveaux
            - **Type d'entrepôt**: {}""".format(
                metrics['ratio_forme'],
                params['nb_niveaux'],
                params['type_entrepot']
            ))
            
            if params['temp_controlee']:
                st.success("✓ Température contrôlée active")
        
        with col2:
            st.markdown("#### 📝 Suggestions d'amélioration")
            
            suggestions = []
            
            if metrics['ratio_forme'] > 3:
                suggestions.append("Ratio longueur/largeur élevé - vérifier l'organisation interne")
            
            if params['hauteur'] > 12 and params['nb_niveaux'] == 1:
                suggestions.append("Hauteur importante avec un seul niveau - envisager des racks plus hauts")
            
            if not suggestions:
                suggestions.append("Configuration satisfaisante")
            
            for i, suggestion in enumerate(suggestions, 1):
                st.markdown(f"{i}. {suggestion}")
        
        # Tableau récapitulatif
        st.markdown("---")
        st.markdown("### 📋 Récapitulatif des paramètres")
        
        recap_data = {
            "Paramètre": [
                "Longueur", "Largeur", "Hauteur", 
                "Type d'entrepôt", "Température contrôlée", "Nombre de niveaux",
                "Surface totale", "Surface utile", "Volume total", "Volume utile"
            ],
            "Valeur": [
                f"{params['longueur']} m",
                f"{params['largeur']} m",
                f"{params['hauteur']} m",
                params['type_entrepot'].capitalize(),
                "Oui" if params['temp_controlee'] else "Non",
                str(params['nb_niveaux']),
                f"{metrics['surface_totale']:,.0f} m²",
                f"{metrics['surface_utile']:,.0f} m²",
                f"{metrics['volume_total']:,.0f} m³",
                f"{metrics['volume_utile']:,.0f} m³"
            ]
        }
        
        df_recap = pd.DataFrame(recap_data)
        st.dataframe(df_recap, use_container_width=True, hide_index=True)
    
    # ÉTAPE 5: VISUALISATION
    elif etape_actuelle == "VISUALISATION":
        # Calcul des métriques
        metrics = calculate_warehouse_metrics(params)
        
        # Afficher la visualisation
        show_visualization(params, metrics)

def main():
    """Fonction principale de l'application"""
    
    # Vérification du mode actuel
    if st.session_state.app_mode == "advanced":
        show_advanced_mode()
    else:
        show_simple_mode()
    
    # Footer
    st.markdown("---")
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.caption("© 2024 - Outil de Dimensionnement d'Entrepôts v4.0")
        st.caption("Développé avec Streamlit • Normes ISO intégrées")

if __name__ == "__main__":
    main()
