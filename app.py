import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import numpy as np
import json

st.set_page_config(
    page_title="Warehouse Configuration Optimizer",
    page_icon="🏭",
    layout="wide"
)

# Configuration CSS
st.markdown("""
<style>
    .main-title {
        text-align: center;
        color: #1E3A8A;
        font-size: 2.5rem;
        margin-bottom: 1rem;
    }
    .sub-title {
        text-align: center;
        color: #4B5563;
        font-size: 1.2rem;
        margin-bottom: 2rem;
    }
    .stButton>button {
        background-color: #2563EB;
        color: white;
        font-weight: bold;
        border-radius: 8px;
        border: none;
        width: 100%;
        padding: 0.75rem;
    }
    .metric-box {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        margin-bottom: 1rem;
    }
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="main-title">🏭 Warehouse Configuration Optimizer</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-title">Dimensionnement intelligent pour chariots élévateurs</div>', unsafe_allow_html=True)

# Initialisation session state
if 'results' not in st.session_state:
    st.session_state.results = None
if 'calculated' not in st.session_state:
    st.session_state.calculated = False

# SIDEBAR - Paramètres
with st.sidebar:
    st.header("⚙️ Paramètres de configuration")
    
    # Dimensions entrepôt
    st.subheader("🏢 Dimensions Entrepôt")
    col1, col2 = st.columns(2)
    with col1:
        longueur = st.number_input("Longueur (m)", 10.0, 200.0, 50.0, 1.0)
    with col2:
        largeur = st.number_input("Largeur (m)", 10.0, 100.0, 30.0, 1.0)
    
    hauteur = st.number_input("Hauteur (m)", 3.0, 30.0, 12.0, 0.5)
    
    st.divider()
    
    # Paramètres racks
    st.subheader("📦 Paramètres Racks")
    
    rack_longueur = st.selectbox("Longueur rack (m)", [1.2, 1.5, 1.8, 2.0, 2.4, 2.7, 3.0], index=4)
    rack_largeur = st.selectbox("Largeur rack (m)", [0.8, 1.0, 1.2, 1.5, 1.8], index=1)
    
    etages = st.slider("Nombre d'étages", 1, 15, 6)
    hauteur_etage = st.number_input("Hauteur par étage (m)", 0.5, 3.0, 1.5, 0.1)
    
    st.divider()
    
    # Chariots élévateurs
    st.subheader("🚜 Chariots Élévateurs")
    
    type_chariot = st.selectbox("Type de chariot", 
                               ["Contrebalance", "Reach Truck", "Télescopique", "Transpalette", "Gerbeur"])
    
    # Spécifications par type
    specs = {
        "Contrebalance": {"allee_min": 3.5, "hauteur_max": 12.0},
        "Reach Truck": {"allee_min": 2.7, "hauteur_max": 15.0},
        "Télescopique": {"allee_min": 3.0, "hauteur_max": 14.0},
        "Transpalette": {"allee_min": 1.8, "hauteur_max": 6.0},
        "Gerbeur": {"allee_min": 2.0, "hauteur_max": 10.0}
    }
    
    allee = st.slider(f"Largeur allée (m)", 
                     float(specs[type_chariot]["allee_min"]), 
                     float(specs[type_chariot]["allee_min"] + 2.0), 
                     float(specs[type_chariot]["allee_min"] + 0.5), 
                     step=0.1)
    
    st.divider()
    
    # Options
    st.subheader("⚙️ Options")
    espacement_vertical = st.slider("Espacement vertical (cm)", 10, 100, 30)
    marge_securite = st.slider("Marge sécurité (%)", 5, 30, 15)
    taux_utilisation = st.slider("Taux utilisation cible (%)", 50, 90, 70)

# Fonction de calcul SIMPLIFIÉE
def calculer_configuration(longueur, largeur, hauteur, rack_longueur, rack_largeur, 
                          etages, hauteur_etage, espacement_vertical, 
                          marge_securite, taux_utilisation, allee, type_chariot):
    
    try:
        # Calculs de base
        surface_totale = longueur * largeur
        volume_total = surface_totale * hauteur
        
        # Hauteur totale rack
        hauteur_totale_rack = etages * hauteur_etage + (etages - 1) * (espacement_vertical / 100)
        conforme_hauteur = hauteur_totale_rack <= (hauteur - 0.5)
        
        # Calcul nombre de racks (simplifié)
        coef_utilisation = taux_utilisation / 100
        espace_lat = 0.2  # 20cm entre racks
        
        # Racks en longueur
        racks_longueur = int((longueur * coef_utilisation) / (rack_longueur + espace_lat))
        racks_longueur = max(1, racks_longueur)
        
        # Racks en largeur (des deux côtés de l'allée)
        largeur_dispo = largeur * coef_utilisation - allee
        racks_largeur_par_cote = int(largeur_dispo / (2 * (rack_largeur + espace_lat)))
        racks_largeur = max(1, racks_largeur_par_cote) * 2
        
        nb_racks = racks_longueur * racks_largeur
        
        # Capacité (simplifiée)
        palettes_par_niveau = 2  # Valeur par défaut
        capacite_par_rack = etages * palettes_par_niveau
        capacite_totale = nb_racks * capacite_par_rack
        
        # Surfaces
        surface_rack_unitaire = rack_longueur * rack_largeur
        surface_racks_totale = nb_racks * surface_rack_unitaire
        surface_all = surface_totale - surface_racks_totale
        taux_utilisation_reel = (surface_racks_totale / surface_totale) * 100
        
        # Score
        score = min(100, taux_utilisation_reel * 1.2)
        
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
            'surface_racks_totale': surface_racks_totale,
            'surface_all': surface_all,
            'taux_utilisation': taux_utilisation_reel,
            'score': score,
            'specs_chariot': specs[type_chariot]
        }
    except Exception as e:
        return None

# Interface principale
st.markdown("## 🚀 Analyse et Configuration")

col1, col2 = st.columns([3, 1])
with col1:
    if st.button("🚀 Calculer la configuration", type="primary", use_container_width=True):
        with st.spinner("Calcul en cours..."):
            results = calculer_configuration(
                longueur, largeur, hauteur, rack_longueur, rack_largeur,
                etages, hauteur_etage, espacement_vertical,
                marge_securite, taux_utilisation, allee, type_chariot
            )
            
            if results:
                st.session_state.results = results
                st.session_state.calculated = True
                st.success("✅ Configuration calculée avec succès!")
            else:
                st.error("❌ Erreur lors du calcul")

with col2:
    if st.button("🔄 Réinitialiser", use_container_width=True):
        st.session_state.results = None
        st.session_state.calculated = False
        st.rerun()

# Affichage des résultats
if st.session_state.calculated and st.session_state.results:
    results = st.session_state.results
    
    # Métriques principales
    st.markdown("## 📊 Résultats de la configuration")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown('<div class="metric-box">', unsafe_allow_html=True)
        st.metric("🏢 Surface totale", f"{results['surface_totale']:,.0f} m²")
        st.metric("📦 Surface racks", f"{results['surface_racks_totale']:,.0f} m²")
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="metric-box">', unsafe_allow_html=True)
        st.metric("🔢 Nombre de racks", f"{results['nb_racks']:,}")
        st.metric("📐 Disposition", f"{results['racks_longueur']} × {results['racks_largeur']}")
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col3:
        st.markdown('<div class="metric-box">', unsafe_allow_html=True)
        st.metric("📈 Capacité totale", f"{results['capacite_totale']:,} palettes")
        st.metric("🔄 Étages/rack", f"{etages}")
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col4:
        st.markdown('<div class="metric-box">', unsafe_allow_html=True)
        st.metric("📊 Taux utilisation", f"{results['taux_utilisation']:.1f}%")
        st.metric("⭐ Score", f"{results['score']:.1f}/100")
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Onglets
    tab1, tab2, tab3 = st.tabs(["📐 Visualisation", "📋 Détails", "💾 Export"])
    
    with tab1:
        # Vue de dessus
        st.subheader("📐 Vue de dessus")
        
        fig_plan = go.Figure()
        
        # Entrepôt
        fig_plan.add_shape(
            type="rect",
            x0=0, y0=0, x1=longueur, y1=largeur,
            line=dict(color="black", width=3),
            fillcolor="lightgray",
            opacity=0.2
        )
        
        # Racks
        for i in range(min(results['racks_longueur'], 10)):
            for j in range(min(results['racks_largeur'], 6)):
                x_pos = i * (rack_longueur + 0.5) + 2
                y_pos = j * (rack_largeur + 0.5) + 2
                
                fig_plan.add_shape(
                    type="rect",
                    x0=x_pos, y0=y_pos,
                    x1=x_pos + rack_longueur, y1=y_pos + rack_largeur,
                    line=dict(color="orange", width=2),
                    fillcolor="orange",
                    opacity=0.6
                )
        
        fig_plan.update_layout(
            xaxis_range=[0, longueur + 5],
            yaxis_range=[0, largeur + 5],
            height=500,
            showlegend=False,
            plot_bgcolor='white'
        )
        
        st.plotly_chart(fig_plan, use_container_width=True)
        
        # Graphique de répartition
        st.subheader("📊 Répartition de l'espace")
        
        fig_pie = go.Figure(data=[go.Pie(
            labels=['Racks', 'Allées', 'Espace libre'],
            values=[results['surface_racks_totale'], 
                   results['surface_all'] * 0.7,
                   results['surface_all'] * 0.3],
            hole=0.4,
            marker_colors=['orange', 'lightblue', 'lightgray']
        )])
        
        st.plotly_chart(fig_pie, use_container_width=True)
    
    with tab2:
        # Tableau détaillé
        st.subheader("📋 Détails techniques")
        
        details = pd.DataFrame({
            'Paramètre': [
                'Dimensions entrepôt',
                'Surface totale',
                'Volume total',
                'Dimensions rack',
                'Hauteur totale rack',
                'Conformité hauteur',
                'Nombre total racks',
                'Disposition racks',
                'Étages par rack',
                'Capacité par rack',
                'Capacité totale',
                'Type chariot',
                'Largeur allée',
                'Conformité allée',
                'Taux d\'utilisation',
                'Surface racks',
                'Surface allées'
            ],
            'Valeur': [
                f"{longueur}m × {largeur}m × {hauteur}m",
                f"{results['surface_totale']:,.0f} m²",
                f"{results['volume_total']:,.0f} m³",
                f"{rack_longueur}m × {rack_largeur}m",
                f"{results['hauteur_totale_rack']:.2f} m",
                '✅ Conforme' if results['conforme_hauteur'] else '❌ Non conforme',
                f"{results['nb_racks']:,}",
                f"{results['racks_longueur']} × {results['racks_largeur']}",
                f"{etages}",
                f"{results['capacite_par_rack']} palettes",
                f"{results['capacite_totale']:,} palettes",
                type_chariot,
                f"{allee} m",
                '✅ Conforme' if allee >= results['specs_chariot']['allee_min'] else '❌ Non conforme',
                f"{results['taux_utilisation']:.1f}%",
                f"{results['surface_racks_totale']:,.0f} m²",
                f"{results['surface_all']:,.0f} m²"
            ]
        })
        
        st.dataframe(details, use_container_width=True, hide_index=True)
        
        # Alertes
        st.subheader("⚠️ Vérifications")
        
        if not results['conforme_hauteur']:
            st.error(f"**Hauteur non conforme:** Les racks ({results['hauteur_totale_rack']:.2f}m) "
                    f"dépassent la hauteur disponible ({hauteur}m)")
        
        if allee < results['specs_chariot']['allee_min']:
            st.error(f"**Allée trop étroite:** {allee}m < minimum {results['specs_chariot']['allee_min']}m "
                    f"pour {type_chariot}")
        
        if results['taux_utilisation'] < 60:
            st.warning(f"**Faible utilisation:** {results['taux_utilisation']:.1f}% < optimal 70%")
        elif results['taux_utilisation'] > 85:
            st.warning(f"**Utilisation très élevée:** {results['taux_utilisation']:.1f}% > maximum conseillé 85%")
    
    with tab3:
        # Export
        st.subheader("💾 Exporter les données")
        
        # Rapport TXT
        rapport = f"""CONFIGURATION D'ENTREPÔT
{'='*50}

ENTREPÔT:
  Dimensions: {longueur}m × {largeur}m × {hauteur}m
  Surface: {results['surface_totale']:,.0f} m²
  Volume: {results['volume_total']:,.0f} m³

RACKS:
  Dimensions: {rack_longueur}m × {rack_largeur}m
  Hauteur: {results['hauteur_totale_rack']:.2f}m ({etages} étages)
  Nombre: {results['nb_racks']:,}
  Disposition: {results['racks_longueur']} × {results['racks_largeur']}
  Capacité: {results['capacite_totale']:,} palettes

CHARIOTS:
  Type: {type_chariot}
  Allée: {allee}m
  Conformité: {'CONFORME' if allee >= results['specs_chariot']['allee_min'] else 'NON CONFORME'}

PERFORMANCES:
  Taux utilisation: {results['taux_utilisation']:.1f}%
  Score: {results['score']:.1f}/100
  Conformité hauteur: {'CONFORME' if results['conforme_hauteur'] else 'NON CONFORME'}

Date: {pd.Timestamp.now().strftime('%d/%m/%Y %H:%M')}
{'='*50}
"""
        
        st.download_button(
            label="📄 Télécharger le rapport (TXT)",
            data=rapport,
            file_name=f"config_entrepot_{pd.Timestamp.now().strftime('%Y%m%d_%H%M')}.txt",
            mime="text/plain"
        )
        
        # Données CSV
        df_export = pd.DataFrame({
            'Paramètre': ['Longueur', 'Largeur', 'Hauteur', 'Surface', 'Nombre_racks', 
                         'Capacite_totale', 'Taux_utilisation', 'Type_chariot', 'Largeur_allee'],
            'Valeur': [longueur, largeur, hauteur, results['surface_totale'], 
                      results['nb_racks'], results['capacite_totale'], 
                      results['taux_utilisation'], type_chariot, allee],
            'Unité': ['m', 'm', 'm', 'm²', 'unités', 'palettes', '%', 'type', 'm']
        })
        
        st.download_button(
            label="📊 Télécharger les données (CSV)",
            data=df_export.to_csv(index=False),
            file_name=f"donnees_entrepot_{pd.Timestamp.now().strftime('%Y%m%d_%H%M')}.csv",
            mime="text/csv"
        )

# Instructions
with st.expander("ℹ️ Comment utiliser"):
    st.markdown("""
    ### Guide d'utilisation :
    
    1. **Configurez les paramètres** dans la sidebar
    2. **Cliquez sur 'Calculer la configuration'**
    3. **Consultez les résultats** dans les onglets
    4. **Exportez** le rapport si nécessaire
    
    ### Normes recommandées :
    - Allée minimum : **3.0m** pour tout chariot
    - Marge hauteur : **+0.5m** au-dessus des racks
    - Taux utilisation optimal : **70-80%**
    - Espacement entre racks : **20cm minimum**
    """)

# Pied de page
st.divider()
st.caption("🏭 Warehouse Configuration Optimizer | Version stable | Streamlit Cloud Compatible")

# Affichage des paramètres actuels dans la sidebar
with st.sidebar:
    st.divider()
    st.markdown("**📋 Paramètres actuels :**")
    st.write(f"Entrepôt : {longueur}m × {largeur}m × {hauteur}m")
    st.write(f"Racks : {rack_longueur}m × {rack_largeur}m")
    st.write(f"Allée : {allee}m ({type_chariot})")
