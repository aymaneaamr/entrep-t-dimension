import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots

st.set_page_config(
    page_title="Warehouse Dimension Optimizer",
    page_icon="🏭",
    layout="wide"
)

# Titre principal
st.title("🏭 Warehouse Dimension Optimizer")
st.markdown("### Optimisez la configuration de votre entrepôt")

# Sidebar avec les paramètres
with st.sidebar:
    st.header("📐 Dimensions de l'entrepôt")
    
    # Dimensions globales
    warehouse_length = st.number_input("Longueur totale (m)", min_value=1.0, value=50.0, step=0.5)
    warehouse_width = st.number_input("Largeur totale (m)", min_value=1.0, value=30.0, step=0.5)
    warehouse_height = st.number_input("Hauteur totale (m)", min_value=1.0, value=10.0, step=0.5)
    
    st.divider()
    st.header("📦 Paramètres des racks")
    
    # Dimensions des racks
    rack_length = st.number_input("Longueur rack (m)", min_value=0.5, value=2.0, step=0.1)
    rack_width = st.number_input("Largeur rack (m)", min_value=0.5, value=1.0, step=0.1)
    rack_height = st.number_input("Hauteur rack (m)", min_value=0.5, value=8.0, step=0.1)
    rack_levels = st.slider("Nombre d'étages par rack", 1, 10, 5)
    
    st.divider()
    st.header("🚚 Allées et passages")
    
    # Allées
    main_aisle_width = st.number_input("Largeur allée principale (m)", min_value=1.0, value=3.0, step=0.1)
    secondary_aisle_width = st.number_input("Largeur allée secondaire (m)", min_value=0.5, value=1.5, step=0.1)
    cross_aisle_width = st.number_input("Largeur allée transversale (m)", min_value=0.5, value=2.0, step=0.1)
    
    st.divider()
    st.header("⚙️ Options avancées")
    
    # Options
    double_depth = st.checkbox("Racks double profondeur", value=False)
    safety_margin = st.number_input("Marge de sécurité (m)", min_value=0.0, value=0.5, step=0.1)
    fire_aisles = st.checkbox("Allées coupe-feu", value=True)
    optimize_layout = st.selectbox("Mode d'optimisation", ["Max racks", "Max stockage", "Circulation optimale"])

# Fonction de calcul d'optimisation
def calculate_warehouse_layout(warehouse_length, warehouse_width, rack_length, rack_width, 
                               main_aisle_width, secondary_aisle_width, cross_aisle_width,
                               double_depth=False, safety_margin=0.5):
    
    # Calcul du nombre de racks possibles
    # Zone disponible après déduction des allées
    available_width = warehouse_width - main_aisle_width - (2 * safety_margin)
    available_length = warehouse_length - cross_aisle_width - (2 * safety_margin)
    
    # Pour double profondeur
    if double_depth:
        effective_rack_width = rack_width * 2
    else:
        effective_rack_width = rack_width
    
    # Calcul des rangées
    rows_per_side = int(available_width // (effective_rack_width + secondary_aisle_width))
    total_rows = rows_per_side * 2
    
    # Calcul des racks par rangée
    racks_per_row = int(available_length // rack_length)
    
    # Total racks
    total_racks = total_rows * racks_per_row
    
    # Calcul des allées
    num_main_aisles = 1
    num_cross_aisles = 1
    num_secondary_aisles = total_rows - 1
    
    # Calcul de la surface utilisée
    total_area = warehouse_length * warehouse_width
    rack_area = total_racks * rack_length * effective_rack_width
    aisle_area = (main_aisle_width * warehouse_length + 
                  cross_aisle_width * warehouse_width + 
                  secondary_aisle_width * available_length * (total_rows - 1))
    
    utilization_percentage = (rack_area / total_area) * 100
    
    return {
        'total_racks': total_racks,
        'total_rows': total_rows,
        'racks_per_row': racks_per_row,
        'rows_per_side': rows_per_side,
        'total_area_m2': total_area,
        'rack_area_m2': rack_area,
        'aisle_area_m2': aisle_area,
        'utilization_percentage': utilization_percentage,
        'available_length': available_length,
        'available_width': available_width
    }

# Fonction pour générer la visualisation
def create_warehouse_visualization(warehouse_length, warehouse_width, results, 
                                   rack_length, rack_width, double_depth):
    
    fig = make_subplots(
        rows=1, cols=2,
        subplot_titles=('Vue de dessus', 'Vue 3D'),
        specs=[[{'type': 'xy'}, {'type': 'scene'}]]
    )
    
    # Vue de dessus (2D)
    # Dessiner l'entrepôt
    fig.add_trace(go.Scatter(
        x=[0, warehouse_length, warehouse_length, 0, 0],
        y=[0, 0, warehouse_width, warehouse_width, 0],
        fill="toself",
        fillcolor="rgba(200, 200, 200, 0.2)",
        line=dict(color="black", width=2),
        name="Entrepôt"
    ), row=1, col=1)
    
    # Dessiner les racks
    total_rows = results['total_rows']
    racks_per_row = results['racks_per_row']
    
    # Couleurs pour les racks
    colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd']
    
    for row in range(total_rows):
        for rack in range(racks_per_row):
            x_start = rack * rack_length
            y_start = row * (rack_width * (2 if double_depth else 1) + 0.5)
            
            fig.add_trace(go.Scatter(
                x=[x_start, x_start + rack_length, x_start + rack_length, x_start, x_start],
                y=[y_start, y_start, y_start + rack_width, y_start + rack_width, y_start],
                fill="toself",
                fillcolor=colors[row % len(colors)],
                line=dict(color="black", width=1),
                name=f"Rack R{row+1}C{rack+1}",
                showlegend=False
            ), row=1, col=1)
    
    # Vue 3D
    # Entrepôt en 3D
    fig.add_trace(go.Mesh3d(
        x=[0, warehouse_length, warehouse_length, 0, 0, warehouse_length, warehouse_length, 0],
        y=[0, 0, warehouse_width, warehouse_width, 0, 0, warehouse_width, warehouse_width],
        z=[0, 0, 0, 0, warehouse_height, warehouse_height, warehouse_height, warehouse_height],
        i=[0, 0, 0, 2, 4, 4, 6, 6],
        j=[1, 2, 3, 3, 5, 6, 7, 5],
        k=[2, 3, 7, 6, 6, 7, 4, 4],
        opacity=0.1,
        color='lightgray',
        name='Entrepôt'
    ), row=1, col=2)
    
    # Racks en 3D
    for i in range(min(10, results['total_racks'])):  # Limiter à 10 racks pour la lisibilité
        row = i // racks_per_row
        rack = i % racks_per_row
        
        x_start = rack * rack_length
        y_start = row * (rack_width * (2 if double_depth else 1) + 1.5)
        
        fig.add_trace(go.Mesh3d(
            x=[x_start, x_start + rack_length, x_start + rack_length, x_start],
            y=[y_start, y_start, y_start + rack_width, y_start + rack_width],
            z=[0, 0, 0, 0],
            i=[0, 0],
            j=[1, 2],
            k=[2, 3],
            opacity=0.7,
            color=colors[row % len(colors)],
            name=f'Rack {i+1}',
            showlegend=False
        ), row=1, col=2)
    
    # Mise en page
    fig.update_layout(
        height=600,
        showlegend=True,
        title_text="Visualisation de la configuration de l'entrepôt"
    )
    
    fig.update_xaxes(title_text="Longueur (m)", row=1, col=1)
    fig.update_yaxes(title_text="Largeur (m)", row=1, col=1)
    
    fig.update_scenes(
        xaxis_title='Longueur (m)',
        yaxis_title='Largeur (m)',
        zaxis_title='Hauteur (m)',
        row=1, col=2
    )
    
    return fig

# Interface principale
st.markdown("## 📊 Résultats de l'optimisation")

if st.button("🚀 Calculer la configuration optimale", type="primary"):
    
    # Calcul des résultats
    results = calculate_warehouse_layout(
        warehouse_length, warehouse_width, rack_length, rack_width,
        main_aisle_width, secondary_aisle_width, cross_aisle_width,
        double_depth, safety_margin
    )
    
    # Calcul du stockage total
    storage_capacity = results['total_racks'] * rack_levels
    pallets_per_rack = int(rack_height // 1.6) * 2  # Estimation palettes
    
    # Affichage des résultats
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("🏢 Nombre total de racks", f"{results['total_racks']}")
        st.metric("📏 Nombre de rangées", f"{results['total_rows']}")
        st.metric("🔢 Racks par rangée", f"{results['racks_per_row']}")
    
    with col2:
        st.metric("📦 Capacité de stockage", f"{storage_capacity} emplacements")
        st.metric("🔄 Niveaux par rack", f"{rack_levels}")
        st.metric("📊 Taux d'occupation", f"{results['utilization_percentage']:.1f}%")
    
    with col3:
        st.metric("📐 Surface totale", f"{results['total_area_m2']:.0f} m²")
        st.metric("📦 Surface racks", f"{results['rack_area_m2']:.0f} m²")
        st.metric("🚶 Surface allées", f"{results['aisle_area_m2']:.0f} m²")
    
    st.divider()
    
    # Visualisation
    st.markdown("## 🎨 Visualisation de la configuration")
    
    fig = create_warehouse_visualization(
        warehouse_length, warehouse_width, results,
        rack_length, rack_width, double_depth
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Tableau détaillé
    st.markdown("## 📋 Détails de la configuration")
    
    details_df = pd.DataFrame({
        'Paramètre': [
            'Dimensions entrepôt', 'Dimensions rack', 'Allée principale',
            'Allée secondaire', 'Allée transversale', 'Marge sécurité',
            'Double profondeur', 'Mode optimisation'
        ],
        'Valeur': [
            f"{warehouse_length}m x {warehouse_width}m x {warehouse_height}m",
            f"{rack_length}m x {rack_width}m x {rack_height}m",
            f"{main_aisle_width}m",
            f"{secondary_aisle_width}m",
            f"{cross_aisle_width}m",
            f"{safety_margin}m",
            "Oui" if double_depth else "Non",
            optimize_layout
        ]
    })
    
    st.table(details_df)
    
    # Export des résultats
    st.divider()
    st.markdown("## 📥 Exporter les résultats")
    
    export_data = f"""
    RAPPORT DE CONFIGURATION D'ENTREPÔT
    ====================================
    
    DIMENSIONS ENTREPÔT:
    - Longueur: {warehouse_length} m
    - Largeur: {warehouse_width} m
    - Hauteur: {warehouse_height} m
    
    CONFIGURATION RACKS:
    - Nombre total de racks: {results['total_racks']}
    - Rangées: {results['total_rows']}
    - Racks par rangée: {results['racks_per_row']}
    - Étages par rack: {rack_levels}
    - Double profondeur: {'Oui' if double_depth else 'Non'}
    
    CAPACITÉ:
    - Emplacements totaux: {storage_capacity}
    - Surface utilisée: {results['utilization_percentage']:.1f}%
    - Surface totale: {results['total_area_m2']:.0f} m²
    - Surface racks: {results['rack_area_m2']:.0f} m²
    - Surface allées: {results['aisle_area_m2']:.0f} m²
    
    ALLÉES:
    - Principale: {main_aisle_width} m
    - Secondaire: {secondary_aisle_width} m
    - Transversale: {cross_aisle_width} m
    
    OPTIONS:
    - Marge de sécurité: {safety_margin} m
    - Allées coupe-feu: {'Oui' if fire_aisles else 'Non'}
    - Mode optimisation: {optimize_layout}
    
    Date de génération: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}
    """
    
    col_export1, col_export2 = st.columns(2)
    
    with col_export1:
        st.download_button(
            label="📄 Télécharger le rapport (TXT)",
            data=export_data,
            file_name="rapport_configuration_entrepot.txt",
            mime="text/plain"
        )
    
    with col_export2:
        # Générer un CSV
        csv_data = pd.DataFrame({
            'Paramètre': [
                'Longueur_entrepot', 'Largeur_entrepot', 'Hauteur_entrepot',
                'Total_racks', 'Total_rangées', 'Racks_par_rangée',
                'Surface_totale', 'Surface_racks', 'Surface_allées',
                'Taux_occupation', 'Capacité_totale'
            ],
            'Valeur': [
                warehouse_length, warehouse_width, warehouse_height,
                results['total_racks'], results['total_rows'], results['racks_per_row'],
                results['total_area_m2'], results['rack_area_m2'], results['aisle_area_m2'],
                results['utilization_percentage'], storage_capacity
            ]
        })
        
        st.download_button(
            label="📊 Télécharger les données (CSV)",
            data=csv_data.to_csv(index=False),
            file_name="donnees_configuration_entrepot.csv",
            mime="text/csv"
        )

# Section d'aide
with st.expander("❓ Comment utiliser cette application"):
    st.markdown("""
    ### Guide d'utilisation
    
    1. **Définir les dimensions de l'entrepôt** dans la barre latérale
    2. **Configurer les paramètres des racks** (longueur, largeur, hauteur)
    3. **Ajuster les allées** selon vos besoins de circulation
    4. **Choisir les options avancées** selon votre configuration
    5. **Cliquer sur 'Calculer la configuration optimale'**
    
    ### Conseils :
    - Pour un entrepôt standard, prévoyez 3m pour l'allée principale
    - La double profondeur augmente la capacité mais réduit l'accessibilité
    - Prévoir une marge de sécurité de 0.5m minimum
    """)

# Pied de page
st.divider()
st.caption("🏭 Warehouse Dimension Optimizer v2.0 | Optimisation de configuration d'entrepôt")
