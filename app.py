import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.express as px

st.set_page_config(
    page_title="Warehouse Dimension Optimizer",
    page_icon="🏭",
    layout="wide"
)

# Titre principal
st.title("🏭 Warehouse Dimension Optimizer")
st.markdown("### Visualisation complète de la configuration d'entrepôt")

# Sidebar avec les paramètres
with st.sidebar:
    st.header("📐 Dimensions de l'entrepôt")
    
    col1, col2 = st.columns(2)
    with col1:
        warehouse_length = st.number_input("Longueur (m)", min_value=1.0, value=50.0, step=0.5, key="wl")
    with col2:
        warehouse_width = st.number_input("Largeur (m)", min_value=1.0, value=30.0, step=0.5, key="ww")
    warehouse_height = st.number_input("Hauteur (m)", min_value=1.0, value=10.0, step=0.5, key="wh")
    
    st.divider()
    st.header("📦 Paramètres des racks")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        rack_length = st.number_input("L rack (m)", min_value=0.5, value=2.0, step=0.1, key="rl")
    with col2:
        rack_width = st.number_input("l rack (m)", min_value=0.5, value=1.0, step=0.1, key="rw")
    with col3:
        rack_height = st.number_input("H rack (m)", min_value=0.5, value=8.0, step=0.1, key="rh")
    
    rack_levels = st.slider("Étages par rack", 1, 10, 5, key="levels")
    
    st.divider()
    st.header("🚚 Allées et circulation")
    
    main_aisle_width = st.slider("Allée principale (m)", 1.0, 5.0, 3.0, step=0.1, key="main")
    secondary_aisle_width = st.slider("Allée secondaire (m)", 0.5, 3.0, 1.5, step=0.1, key="sec")
    cross_aisle_width = st.slider("Allée transversale (m)", 0.5, 4.0, 2.0, step=0.1, key="cross")
    
    st.divider()
    st.header("⚙️ Options")
    
    double_depth = st.checkbox("Double profondeur", value=False, key="double")
    safety_margin = st.number_input("Marge sécurité (m)", 0.0, 2.0, 0.5, step=0.1, key="margin")
    show_3d = st.checkbox("Afficher vue 3D", value=True, key="show3d")
    rack_color = st.color_picker("Couleur des racks", "#1f77b4", key="color")

# Fonction pour générer la visualisation 2D
def create_2d_visualization(warehouse_length, warehouse_width, rack_length, rack_width, 
                           main_aisle_width, secondary_aisle_width, cross_aisle_width,
                           double_depth, safety_margin, rack_color):
    
    fig = go.Figure()
    
    # Dessiner l'entrepôt
    fig.add_trace(go.Scatter(
        x=[0, warehouse_length, warehouse_length, 0, 0],
        y=[0, 0, warehouse_width, warehouse_width, 0],
        fill="toself",
        fillcolor="rgba(240, 240, 240, 0.3)",
        line=dict(color="black", width=3),
        name="Entrepôt"
    ))
    
    # Calculer la configuration
    available_width = warehouse_width - main_aisle_width - (2 * safety_margin)
    available_length = warehouse_length - cross_aisle_width - (2 * safety_margin)
    
    if double_depth:
        effective_rack_width = rack_width * 2
    else:
        effective_rack_width = rack_width
    
    # Calcul des rangées
    rows_per_side = int(available_width // (effective_rack_width + secondary_aisle_width))
    total_rows = rows_per_side * 2
    
    # Calcul des racks par rangée
    racks_per_row = int(available_length // rack_length)
    
    # Dessiner les racks
    rack_counter = 0
    for row in range(total_rows):
        for rack in range(racks_per_row):
            x_start = safety_margin + rack * rack_length
            y_start = safety_margin + row * (effective_rack_width + secondary_aisle_width)
            
            # Allée principale au milieu
            if y_start + effective_rack_width > warehouse_width/2 - main_aisle_width/2 and y_start < warehouse_width/2 + main_aisle_width/2:
                continue
            
            # Dessiner le rack
            fig.add_trace(go.Scatter(
                x=[x_start, x_start + rack_length, x_start + rack_length, x_start, x_start],
                y=[y_start, y_start, y_start + effective_rack_width, y_start + effective_rack_width, y_start],
                fill="toself",
                fillcolor=rack_color,
                line=dict(color="black", width=1),
                name=f"Rack {rack_counter+1}" if rack_counter == 0 else "",
                showlegend=rack_counter == 0,
                hovertemplate=f"Rack {rack_counter+1}<br>Position: ({x_start:.1f}, {y_start:.1f})<br>Taille: {rack_length}m x {effective_rack_width}m"
            ))
            rack_counter += 1
    
    # Dessiner les allées
    # Allée principale (verticale au centre)
    fig.add_trace(go.Scatter(
        x=[safety_margin, warehouse_length - safety_margin, warehouse_length - safety_margin, safety_margin, safety_margin],
        y=[warehouse_width/2 - main_aisle_width/2, warehouse_width/2 - main_aisle_width/2, 
           warehouse_width/2 + main_aisle_width/2, warehouse_width/2 + main_aisle_width/2, 
           warehouse_width/2 - main_aisle_width/2],
        fill="toself",
        fillcolor="rgba(200, 200, 200, 0.5)",
        line=dict(color="gray", width=1, dash="dash"),
        name="Allée principale"
    ))
    
    # Allée transversale (horizontale)
    fig.add_trace(go.Scatter(
        x=[warehouse_length - safety_margin - cross_aisle_width, warehouse_length - safety_margin, 
           warehouse_length - safety_margin, warehouse_length - safety_margin - cross_aisle_width,
           warehouse_length - safety_margin - cross_aisle_width],
        y=[safety_margin, safety_margin, warehouse_width - safety_margin, warehouse_width - safety_margin,
           safety_margin],
        fill="toself",
        fillcolor="rgba(150, 150, 150, 0.4)",
        line=dict(color="gray", width=1, dash="dot"),
        name="Allée transversale"
    ))
    
    # Mise en page
    fig.update_layout(
        title="Vue de dessus - Configuration des racks et allées",
        xaxis_title="Longueur (m)",
        yaxis_title="Largeur (m)",
        showlegend=True,
        height=600,
        plot_bgcolor="white",
        legend=dict(
            yanchor="top",
            y=0.99,
            xanchor="left",
            x=0.01
        )
    )
    
    fig.update_xaxes(range=[0, warehouse_length], gridcolor="lightgray")
    fig.update_yaxes(range=[0, warehouse_width], gridcolor="lightgray")
    
    return fig, rack_counter

# Fonction pour générer la visualisation 3D
def create_3d_visualization(warehouse_length, warehouse_width, warehouse_height, 
                           rack_length, rack_width, rack_height, rack_levels,
                           main_aisle_width, rack_color):
    
    fig = go.Figure()
    
    # Entrepôt en 3D (transparent)
    fig.add_trace(go.Mesh3d(
        # Points du cube
        x=[0, warehouse_length, warehouse_length, 0, 0, warehouse_length, warehouse_length, 0],
        y=[0, 0, warehouse_width, warehouse_width, 0, 0, warehouse_width, warehouse_width],
        z=[0, 0, 0, 0, warehouse_height, warehouse_height, warehouse_height, warehouse_height],
        # Triangles
        i=[0, 0, 0, 2, 4, 4, 6, 6],
        j=[1, 2, 3, 3, 5, 6, 7, 5],
        k=[2, 3, 7, 6, 6, 7, 4, 4],
        opacity=0.1,
        color="lightgray",
        name="Entrepôt",
        showlegend=True
    ))
    
    # Ajouter quelques racks en 3D (pour la démonstration)
    num_racks_to_show = 8  # Limiter pour la lisibilité
    
    for i in range(num_racks_to_show):
        row = i // 2
        side = i % 2
        
        # Positionner les racks de chaque côté de l'allée
        x_pos = 5 + (i % 4) * (rack_length + 2)
        y_pos = 5 if side == 0 else warehouse_width - 5 - rack_width
        z_pos = 0
        
        # Créer un rack 3D avec plusieurs niveaux
        for level in range(rack_levels):
            level_height = level * (rack_height / rack_levels)
            
            # Points du rack (cube)
            x = [x_pos, x_pos + rack_length, x_pos + rack_length, x_pos]
            y = [y_pos, y_pos, y_pos + rack_width, y_pos + rack_width]
            z = [level_height, level_height, level_height, level_height]
            
            # Ajouter le rack
            fig.add_trace(go.Mesh3d(
                x=x + x,
                y=y + y,
                z=z + [z[0] + rack_height/rack_levels] * 4,
                i=[0, 0, 4, 4],
                j=[1, 2, 5, 6],
                k=[2, 3, 6, 7],
                opacity=0.7,
                color=rack_color,
                name=f"Rack {i+1}" if level == 0 else "",
                showlegend=level == 0 and i == 0,
                hovertemplate=f"Rack {i+1}-Niveau {level+1}<br>Position: ({x_pos:.1f}, {y_pos:.1f})"
            ))
    
    # Allée principale en 3D
    fig.add_trace(go.Mesh3d(
        x=[warehouse_length/4, 3*warehouse_length/4, 3*warehouse_length/4, warehouse_length/4],
        y=[warehouse_width/2 - main_aisle_width/2, warehouse_width/2 - main_aisle_width/2,
           warehouse_width/2 + main_aisle_width/2, warehouse_width/2 + main_aisle_width/2],
        z=[0, 0, 0, 0],
        i=[0, 0],
        j=[1, 2],
        k=[2, 3],
        opacity=0.3,
        color="gray",
        name="Allée"
    ))
    
    # Mise en page 3D
    fig.update_layout(
        title="Vue 3D - Perspective de l'entrepôt",
        scene=dict(
            xaxis_title="Longueur (m)",
            yaxis_title="Largeur (m)",
            zaxis_title="Hauteur (m)",
            aspectmode="manual",
            aspectratio=dict(x=warehouse_length/10, y=warehouse_width/10, z=warehouse_height/10),
            camera=dict(
                eye=dict(x=2, y=2, z=1.5)
            )
        ),
        height=600,
        showlegend=True
    )
    
    return fig

# Interface principale
if st.button("🎨 Générer la visualisation", type="primary"):
    
    with st.spinner("Création des visualisations..."):
        
        # Calculer la configuration
        available_width = warehouse_width - main_aisle_width - (2 * safety_margin)
        available_length = warehouse_length - cross_aisle_width - (2 * safety_margin)
        
        if double_depth:
            effective_rack_width = rack_width * 2
        else:
            effective_rack_width = rack_width
        
        rows_per_side = int(available_width // (effective_rack_width + secondary_aisle_width))
        total_rows = rows_per_side * 2
        racks_per_row = int(available_length // rack_length)
        total_racks = total_rows * racks_per_row
        storage_capacity = total_racks * rack_levels
        
        # Afficher les statistiques
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("🏢 Racks totaux", f"{total_racks}")
        with col2:
            st.metric("📏 Rangées", f"{total_rows}")
        with col3:
            st.metric("📦 Capacité", f"{storage_capacity}")
        with col4:
            st.metric("🔄 Étages", f"{rack_levels}")
        
        st.divider()
        
        # Créer et afficher la visualisation 2D
        st.subheader("📐 Vue de dessus - Plan de l'entrepôt")
        fig_2d, actual_racks = create_2d_visualization(
            warehouse_length, warehouse_width, rack_length, rack_width,
            main_aisle_width, secondary_aisle_width, cross_aisle_width,
            double_depth, safety_margin, rack_color
        )
        
        st.plotly_chart(fig_2d, use_container_width=True)
        
        # Légende explicative
        with st.expander("📖 Légende de la visualisation"):
            st.markdown("""
            **Symboles et couleurs :**
            - 🏢 **Rectangle bleu** : Racks de stockage
            - 🚶 **Zone grise pointillée** : Allée principale
            - 🛒 **Zone grise en pointillés** : Allée transversale
            - ▫️ **Grand rectangle** : Périmètre de l'entrepôt
            
            **Conseils :**
            - Passez la souris sur un rack pour voir ses dimensions
            - Utilisez les outils de zoom en haut à droite
            - Cliquez sur les éléments de la légende pour les masquer/afficher
            """)
        
        # Vue 3D si activée
        if show_3d:
            st.divider()
            st.subheader("🔭 Vue 3D - Perspective")
            
            fig_3d = create_3d_visualization(
                warehouse_length, warehouse_width, warehouse_height,
                rack_length, rack_width, rack_height, rack_levels,
                main_aisle_width, rack_color
            )
            
            st.plotly_chart(fig_3d, use_container_width=True)
            
            st.info("💡 **Astuce 3D** : Utilisez la souris pour tourner, zoomer et déplacer la vue 3D.")
        
        # Tableau de configuration
        st.divider()
        st.subheader("⚙️ Configuration générée")
        
        config_data = {
            "Paramètre": [
                "Dimensions entrepôt", "Surface totale", "Nombre total de racks",
                "Rangées de racks", "Racks par rangée", "Capacité totale",
                "Largeur allée principale", "Largeur allées secondaires",
                "Type configuration", "Marge de sécurité"
            ],
            "Valeur": [
                f"{warehouse_length}m × {warehouse_width}m × {warehouse_height}m",
                f"{warehouse_length * warehouse_width:.0f} m²",
                f"{total_racks} racks",
                f"{total_rows} rangées",
                f"{racks_per_row} racks/rangée",
                f"{storage_capacity} emplacements",
                f"{main_aisle_width}m",
                f"{secondary_aisle_width}m",
                "Double profondeur" if double_depth else "Simple profondeur",
                f"{safety_margin}m"
            ]
        }
        
        st.dataframe(pd.DataFrame(config_data), use_container_width=True, hide_index=True)
        
        # Export de l'image
        st.divider()
        st.subheader("💾 Exporter la configuration")
        
        col_exp1, col_exp2 = st.columns(2)
        
        with col_exp1:
            # Exporter les données
            export_data = f"""CONFIGURATION D'ENTREPÔT - RAPPORT DE VISUALISATION

DIMENSIONS ENTREPÔT:
• Longueur: {warehouse_length} m
• Largeur: {warehouse_width} m
• Hauteur: {warehouse_height} m
• Surface: {warehouse_length * warehouse_width:.0f} m²

CONFIGURATION RACKS:
• Dimensions rack: {rack_length}m × {rack_width}m × {rack_height}m
• Nombre total: {total_racks} racks
• Rangées: {total_rows}
• Racks par rangée: {racks_per_row}
• Étages par rack: {rack_levels}
• Capacité totale: {storage_capacity} emplacements

ALLÉES:
• Principale: {main_aisle_width} m
• Secondaires: {secondary_aisle_width} m
• Transversale: {cross_aisle_width} m

OPTIONS:
• Profondeur: {"Double" if double_depth else "Simple"}
• Marge sécurité: {safety_margin} m

VISUALISATION:
• Racks affichés: {actual_racks}
• Couleur racks: {rack_color}
• Vue 3D: {"Activée" if show_3d else "Désactivée"}

Date de génération: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
            
            st.download_button(
                label="📄 Télécharger le rapport (TXT)",
                data=export_data,
                file_name="rapport_visualisation_entrepot.txt",
                mime="text/plain"
            )
        
        with col_exp2:
            st.download_button(
                label="📊 Télécharger configuration (CSV)",
                data=pd.DataFrame(config_data).to_csv(index=False),
                file_name="configuration_entrepot.csv",
                mime="text/csv"
            )

# Section d'aide
with st.expander("🎯 Comment utiliser les visualisations"):
    st.markdown("""
    ### Guide des visualisations
    
    **1. Vue de dessus (2D)**
    - Montre la disposition exacte des racks
    - Visualise les allées de circulation
    - Indique les marges de sécurité
    - Interactive : survolez les éléments pour plus d'infos
    
    **2. Vue 3D (optionnelle)**
    - Perspective réaliste de l'entrepôt
    - Montre la hauteur des racks
    - Affiche les différents niveaux
    - Navigation libre avec la souris
    
    **3. Paramètres importants**
    - **Double profondeur** : Double la capacité mais réduit l'accessibilité
    - **Allée principale** : Doit permettre le passage des chariots
    - **Marge de sécurité** : Espace autour des racks pour la sécurité
    
    **4. Conseils d'optimisation**
    - Augmentez la hauteur pour plus de capacité verticale
    - Réduisez les allées secondaires si pas de circulation fréquente
    - Utilisez la double profondeur pour le stockage à long terme
    """)

# Pied de page
st.divider()
st.caption("🏭 Warehouse Visualizer v3.0 | Visualisation avancée d'entrepôt | Déployé avec Streamlit Cloud")
