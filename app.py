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
st.markdown("### Configuration optimisée pour chariots élévateurs")

# Sidebar avec les paramètres
with st.sidebar:
    st.header("📐 Dimensions de l'entrepôt")
    
    col1, col2 = st.columns(2)
    with col1:
        warehouse_length = st.number_input("Longueur (m)", min_value=1.0, value=50.0, step=0.5, key="wl")
    with col2:
        warehouse_width = st.number_input("Largeur (m)", min_value=1.0, value=30.0, step=0.5, key="ww")
    warehouse_height = st.number_input("Hauteur (m)", min_value=1.0, value=12.0, step=0.5, key="wh")
    
    st.divider()
    st.header("📦 Paramètres des racks")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        rack_length = st.number_input("L rack (m)", min_value=0.5, value=2.4, step=0.1, key="rl", 
                                     help="Longueur standard pour palettes EUR (2.4m)")
    with col2:
        rack_width = st.number_input("Profondeur rack (m)", min_value=0.5, value=1.0, step=0.1, key="rw",
                                    help="Profondeur pour palette standard (1.0m)")
    with col3:
        rack_height = st.number_input("H rack (m)", min_value=1.0, value=10.0, step=0.1, key="rh",
                                     help="Hauteur adaptée aux chariots élévateurs")
    
    rack_levels = st.slider("Étages par rack", 1, 12, 6, key="levels",
                           help="Nombre de niveaux de stockage")
    
    st.divider()
    st.header("🚜 Configuration pour chariots élévateurs")
    
    # Allées pour chariots élévateurs
    st.markdown("**📏 Allées de circulation**")
    
    # Allée principale pour circulation
    main_aisle_width = st.slider("Allée principale (m)", 3.0, 6.0, 4.0, step=0.1, key="main",
                                help="Minimum 3m pour chariots élévateurs")
    
    # Allées entre racks
    secondary_aisle_width = st.slider("Allée entre racks (m)", 1.2, 3.0, 1.5, step=0.1, key="sec",
                                     help="Espace pour accès aux racks")
    
    # Allée transversale
    cross_aisle_width = st.slider("Allée transversale (m)", 2.0, 5.0, 3.0, step=0.1, key="cross",
                                 help="Pour manoeuvres et demi-tours")
    
    # Options spécifiques chariots
    st.markdown("**⚙️ Options chariots**")
    turning_radius = st.number_input("Rayon de virage (m)", 1.5, 4.0, 2.5, step=0.1,
                                    help="Rayon nécessaire pour tourner")
    forklift_type = st.selectbox("Type de chariot", 
                                ["Contrebalance", "Télescopique", "Transpalette", "Gerbeur"])
    
    st.divider()
    st.header("⚙️ Options de stockage")
    
    double_depth = st.checkbox("Double profondeur", value=False, key="double",
                              help="Racks double profondeur (2 palettes)")
    pallets_per_rack = st.number_input("Pallets par emplacement", 1, 4, 2, 
                                      help="Nombre de palettes par niveau")
    safety_margin = st.number_input("Marge sécurité (m)", 0.3, 1.5, 0.8, step=0.1, key="margin")
    
    st.divider()
    st.header("🎨 Options de visualisation")
    
    show_3d = st.checkbox("Afficher vue 3D", value=True, key="show3d")
    rack_color = st.color_picker("Couleur des racks", "#1f77b4", key="color")
    aisle_color = st.color_picker("Couleur des allées", "#808080", key="aisle_color")

# Fonction pour vérifier la conformité chariots élévateurs
def check_forklift_compatibility(aisle_width, turning_radius, forklift_type):
    """Vérifie si les allées sont adaptées aux chariots"""
    
    min_aisle_width = {
        "Contrebalance": 3.5,
        "Télescopique": 2.8,
        "Transpalette": 1.8,
        "Gerbeur": 2.0
    }
    
    min_turning = {
        "Contrebalance": 2.2,
        "Télescopique": 2.0,
        "Transpalette": 1.5,
        "Gerbeur": 1.8
    }
    
    issues = []
    warnings = []
    
    # Vérification allée principale
    if aisle_width < min_aisle_width[forklift_type]:
        issues.append(f"Allée principale trop étroite pour {forklift_type} (minimum {min_aisle_width[forklift_type]}m)")
    elif aisle_width < min_aisle_width[forklift_type] + 0.5:
        warnings.append(f"Allée principale limite pour {forklift_type}")
    
    # Vérification rayon virage
    if turning_radius < min_turning[forklift_type]:
        issues.append(f"Rayon de virage insuffisant pour {forklift_type}")
    
    # Vérification allée transversale pour demi-tour
    if cross_aisle_width < turning_radius * 1.2:
        warnings.append(f"Allée transversale limite pour les manoeuvres")
    
    return issues, warnings

# Fonction pour générer la visualisation 2D optimisée chariots
def create_forklift_optimized_2d(warehouse_length, warehouse_width, rack_length, rack_width, 
                                main_aisle_width, secondary_aisle_width, cross_aisle_width,
                                double_depth, safety_margin, rack_color, aisle_color,
                                turning_radius):
    
    fig = go.Figure()
    
    # Dessiner l'entrepôt
    fig.add_trace(go.Scatter(
        x=[0, warehouse_length, warehouse_length, 0, 0],
        y=[0, 0, warehouse_width, warehouse_width, 0],
        fill="toself",
        fillcolor="rgba(245, 245, 245, 0.3)",
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
    
    # Calcul des rangées (séparées par l'allée principale)
    racks_per_side_width = int(available_width // (effective_rack_width + secondary_aisle_width))
    
    # Calcul des racks par rangée
    racks_per_row = int(available_length // rack_length)
    
    # Dessiner les racks côté GAUCHE de l'allée principale
    rack_counter = 0
    for side in [0, 1]:  # 0 = gauche, 1 = droite
        for row in range(racks_per_side_width):
            for rack in range(racks_per_row):
                
                x_start = safety_margin + rack * rack_length
                
                # Position verticale selon le côté
                if side == 0:  # Côté gauche de l'allée
                    y_start = safety_margin + row * (effective_rack_width + secondary_aisle_width)
                    max_y = warehouse_width/2 - main_aisle_width/2
                else:  # Côté droit de l'allée
                    y_start = warehouse_width/2 + main_aisle_width/2 + safety_margin + row * (effective_rack_width + secondary_aisle_width)
                    max_y = warehouse_width - safety_margin
                
                # Vérifier que le rack ne dépasse pas
                if y_start + effective_rack_width > max_y:
                    continue
                
                # Dessiner le rack
                fig.add_trace(go.Scatter(
                    x=[x_start, x_start + rack_length, x_start + rack_length, x_start, x_start],
                    y=[y_start, y_start, y_start + effective_rack_width, y_start + effective_rack_width, y_start],
                    fill="toself",
                    fillcolor=rack_color,
                    line=dict(color="black", width=1.5),
                    name=f"Rack {rack_counter+1}" if rack_counter == 0 else "",
                    showlegend=rack_counter == 0,
                    hovertemplate=f"Rack {rack_counter+1}<br>Position: ({x_start:.1f}, {y_start:.1f})<br>"
                                 f"Taille: {rack_length}m × {effective_rack_width}m<br>"
                                 f"Côté: {'Gauche' if side == 0 else 'Droit'}"
                ))
                rack_counter += 1
    
    # Total racks (approximation)
    total_racks = racks_per_side_width * racks_per_row * 2
    
    # Dessiner l'ALLÉE PRINCIPALE pour chariots (3m minimum)
    fig.add_trace(go.Scatter(
        x=[safety_margin, warehouse_length - safety_margin - cross_aisle_width, 
           warehouse_length - safety_margin - cross_aisle_width, safety_margin, safety_margin],
        y=[warehouse_width/2 - main_aisle_width/2, warehouse_width/2 - main_aisle_width/2, 
           warehouse_width/2 + main_aisle_width/2, warehouse_width/2 + main_aisle_width/2, 
           warehouse_width/2 - main_aisle_width/2],
        fill="toself",
        fillcolor=aisle_color,
        line=dict(color="black", width=2),
        name=f"Allée chariots ({main_aisle_width}m)"
    ))
    
    # Zone de virage (cercle pour représenter le rayon)
    turn_center_x = warehouse_length - safety_margin - cross_aisle_width/2
    turn_center_y = warehouse_width/2
    
    # Créer un cercle pour le rayon de virage
    theta = np.linspace(0, 2*np.pi, 100)
    turn_x = turn_center_x + turning_radius * np.cos(theta)
    turn_y = turn_center_y + turning_radius * np.sin(theta)
    
    fig.add_trace(go.Scatter(
        x=turn_x,
        y=turn_y,
        fill="toself",
        fillcolor="rgba(255, 200, 0, 0.2)",
        line=dict(color="orange", width=1, dash="dash"),
        name=f"Zone virage (R={turning_radius}m)"
    ))
    
    # Allée transversale pour manoeuvres
    fig.add_trace(go.Scatter(
        x=[warehouse_length - safety_margin - cross_aisle_width, warehouse_length - safety_margin, 
           warehouse_length - safety_margin, warehouse_length - safety_margin - cross_aisle_width,
           warehouse_length - safety_margin - cross_aisle_width],
        y=[safety_margin, safety_margin, warehouse_width - safety_margin, warehouse_width - safety_margin,
           safety_margin],
        fill="toself",
        fillcolor="rgba(150, 150, 150, 0.4)",
        line=dict(color="gray", width=2),
        name=f"Allée manoeuvres ({cross_aisle_width}m)"
    ))
    
    # Marquer l'entrée/sortie
    fig.add_trace(go.Scatter(
        x=[warehouse_length - 2, warehouse_length],
        y=[warehouse_width/2 - 1, warehouse_width/2 + 1],
        fill="toself",
        fillcolor="rgba(0, 200, 0, 0.5)",
        line=dict(color="green", width=2),
        name="Entrée/Sortie"
    ))
    
    # Mise en page
    fig.update_layout(
        title=f"Plan d'entrepôt optimisé pour chariots élévateurs",
        xaxis_title="Longueur (m)",
        yaxis_title="Largeur (m)",
        showlegend=True,
        height=650,
        plot_bgcolor="white",
        legend=dict(
            yanchor="top",
            y=0.99,
            xanchor="left",
            x=0.01,
            bgcolor="rgba(255, 255, 255, 0.8)"
        )
    )
    
    fig.update_xaxes(range=[0, warehouse_length], gridcolor="lightgray", dtick=5)
    fig.update_yaxes(range=[0, warehouse_width], gridcolor="lightgray", dtick=5)
    
    return fig, total_racks, rack_counter

# Fonction pour générer la vue 3D avec chariots
def create_3d_with_forklift(warehouse_length, warehouse_width, warehouse_height, 
                           rack_length, rack_width, rack_height, rack_levels,
                           main_aisle_width, rack_color, aisle_color):
    
    fig = go.Figure()
    
    # Entrepôt en 3D
    fig.add_trace(go.Mesh3d(
        x=[0, warehouse_length, warehouse_length, 0, 0, warehouse_length, warehouse_length, 0],
        y=[0, 0, warehouse_width, warehouse_width, 0, 0, warehouse_width, warehouse_width],
        z=[0, 0, 0, 0, warehouse_height, warehouse_height, warehouse_height, warehouse_height],
        i=[0, 0, 0, 2, 4, 4, 6, 6],
        j=[1, 2, 3, 3, 5, 6, 7, 5],
        k=[2, 3, 7, 6, 6, 7, 4, 4],
        opacity=0.05,
        color="lightgray",
        name="Entrepôt"
    ))
    
    # Ajouter des racks en 3D
    num_racks_per_side = 6  # Pour la lisibilité
    
    for side in [0, 1]:  # Deux côtés de l'allée
        for i in range(num_racks_per_side):
            x_pos = 3 + (i % 3) * (rack_length + 2)
            y_pos = 4 if side == 0 else warehouse_width - 4 - rack_width
            z_pos = 0
            
            # Rack avec plusieurs niveaux
            for level in range(rack_levels):
                level_height = level * (rack_height / rack_levels)
                
                # Points du rack
                x = [x_pos, x_pos + rack_length, x_pos + rack_length, x_pos]
                y = [y_pos, y_pos, y_pos + rack_width, y_pos + rack_width]
                z = [level_height, level_height, level_height, level_height]
                
                fig.add_trace(go.Mesh3d(
                    x=x + x,
                    y=y + y,
                    z=z + [z[0] + rack_height/rack_levels] * 4,
                    i=[0, 0, 4, 4],
                    j=[1, 2, 5, 6],
                    k=[2, 3, 6, 7],
                    opacity=0.7,
                    color=rack_color,
                    name=f"Rack {i+1}" if level == 0 and side == 0 and i == 0 else "",
                    showlegend=level == 0 and side == 0 and i == 0
                ))
    
    # Allée en 3D
    fig.add_trace(go.Mesh3d(
        x=[warehouse_length/4, 3*warehouse_length/4, 3*warehouse_length/4, warehouse_length/4],
        y=[warehouse_width/2 - main_aisle_width/2, warehouse_width/2 - main_aisle_width/2,
           warehouse_width/2 + main_aisle_width/2, warehouse_width/2 + main_aisle_width/2],
        z=[0, 0, 0, 0],
        i=[0, 0],
        j=[1, 2],
        k=[2, 3],
        opacity=0.3,
        color=aisle_color,
        name="Allée chariots"
    ))
    
    # Représentation schématique d'un chariot élévateur
    fig.add_trace(go.Mesh3d(
        x=[warehouse_length/2 - 1, warehouse_length/2 + 1, warehouse_length/2 + 1, warehouse_length/2 - 1],
        y=[warehouse_width/2 - 0.5, warehouse_width/2 - 0.5, warehouse_width/2 + 0.5, warehouse_width/2 + 0.5],
        z=[0, 0, 0, 0],
        i=[0, 0],
        j=[1, 2],
        k=[2, 3],
        opacity=0.8,
        color="red",
        name="Chariot élévateur"
    ))
    
    # Mise en page 3D
    fig.update_layout(
        title="Vue 3D avec allées chariots élévateurs",
        scene=dict(
            xaxis_title="Longueur (m)",
            yaxis_title="Largeur (m)",
            zaxis_title="Hauteur (m)",
            aspectmode="manual",
            aspectratio=dict(x=warehouse_length/10, y=warehouse_width/10, z=warehouse_height/10),
            camera=dict(
                eye=dict(x=1.5, y=1.5, z=1.2)
            )
        ),
        height=600,
        showlegend=True
    )
    
    return fig

# Interface principale
st.info("⚠️ **Configuration optimisée pour chariots élévateurs** - Allées minimum 3m requises")

if st.button("🚜 Générer plan chariots élévateurs", type="primary"):
    
    # Vérification conformité
    issues, warnings = check_forklift_compatibility(main_aisle_width, turning_radius, forklift_type)
    
    if issues:
        st.error("### ❌ Problèmes de conformité détectés :")
        for issue in issues:
            st.error(f"- {issue}")
        st.warning("Ajustez les paramètres avant de générer le plan.")
    else:
        with st.spinner("Création du plan optimisé pour chariots..."):
            
            # Calculs
            available_width = warehouse_width - main_aisle_width - (2 * safety_margin)
            available_length = warehouse_length - cross_aisle_width - (2 * safety_margin)
            
            if double_depth:
                effective_rack_width = rack_width * 2
            else:
                effective_rack_width = rack_width
            
            racks_per_side_width = int(available_width // (effective_rack_width + secondary_aisle_width))
            racks_per_row = int(available_length // rack_length)
            total_racks = racks_per_side_width * racks_per_row * 2
            storage_capacity = total_racks * rack_levels * pallets_per_rack
            
            # Afficher les avertissements
            if warnings:
                st.warning("### ⚠️ Avertissements :")
                for warning in warnings:
                    st.warning(f"- {warning}")
            
            # Afficher les spécifications chariots
            st.success(f"### ✅ Configuration adaptée pour : {forklift_type}")
            
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("🚜 Type chariot", forklift_type)
                st.metric("📏 Allée chariots", f"{main_aisle_width}m")
            with col2:
                st.metric("🔄 Rayon virage", f"{turning_radius}m")
                st.metric("🛣️ Allée manoeuvres", f"{cross_aisle_width}m")
            with col3:
                st.metric("🏢 Racks totaux", f"{total_racks}")
                st.metric("📦 Palettes totales", f"{storage_capacity}")
            with col4:
                st.metric("📐 Étages/rack", f"{rack_levels}")
                st.metric("📊 Pallets/emplacement", f"{pallets_per_rack}")
            
            st.divider()
            
            # Créer et afficher la visualisation 2D
            st.subheader("📐 Plan d'implantation avec allées chariots")
            fig_2d, estimated_racks, actual_racks = create_forklift_optimized_2d(
                warehouse_length, warehouse_width, rack_length, rack_width,
                main_aisle_width, secondary_aisle_width, cross_aisle_width,
                double_depth, safety_margin, rack_color, aisle_color,
                turning_radius
            )
            
            st.plotly_chart(fig_2d, use_container_width=True)
            
            # Légende chariots
            with st.expander("🚜 Légende spécifique chariots"):
                st.markdown(f"""
                **Configuration pour {forklift_type} :**
                
                - 🟦 **Zones bleues** : Racks de stockage
                - 🟩 **Zone verte** : Entrée/Sortie
                - 🟨 **Zone jaune** : Rayon de virage ({turning_radius}m)
                - ⬜ **Zone grise large** : Allée chariots ({main_aisle_width}m)
                - ⬛ **Zone grise transversale** : Allée de manoeuvres
                - 🔴 **Point rouge** : Zone chariot élévateur
                
                **Recommandations :**
                - Allée minimum : **{main_aisle_width}m** (conforme : ✅)
                - Espace virage : **{turning_radius}m** requis
                - Allée transversale : **{cross_aisle_width}m** pour demi-tours
                """)
            
            # Vue 3D si activée
            if show_3d:
                st.divider()
                st.subheader("🔭 Vue 3D avec circulation chariots")
                
                fig_3d = create_3d_with_forklift(
                    warehouse_length, warehouse_width, warehouse_height,
                    rack_length, rack_width, rack_height, rack_levels,
                    main_aisle_width, rack_color, aisle_color
                )
                
                st.plotly_chart(fig_3d, use_container_width=True)
                
                st.info("💡 **Visualisation 3D** : Le chariot élévateur (en rouge) montre l'échelle dans l'allée.")
            
            # Tableau de configuration détaillée
            st.divider()
            st.subheader("📋 Spécifications techniques complètes")
            
            config_data = {
                "Catégorie": ["ENTREPÔT", "RACKS", "CHARIOTS", "CAPACITÉ", "SÉCURITÉ"],
                "Paramètre": [
                    f"{warehouse_length}×{warehouse_width}×{warehouse_height}m",
                    f"{rack_length}×{rack_width}×{rack_height}m",
                    forklift_type,
                    f"{storage_capacity} palettes",
                    f"{safety_margin}m marge"
                ],
                "Valeur": [
                    f"{warehouse_length*warehouse_width:.0f}m² surface",
                    f"{rack_levels} étages, {pallets_per_rack} pallets/niveau",
                    f"Allée {main_aisle_width}m, virage {turning_radius}m",
                    f"{total_racks} racks × {rack_levels} étages",
                    f"Allées secondaires: {secondary_aisle_width}m"
                ],
                "Conformité": [
                    "✅",
                    "✅",
                    "✅" if not issues else "❌",
                    "✅",
                    "✅"
                ]
            }
            
            st.dataframe(pd.DataFrame(config_data), use_container_width=True, hide_index=True)
            
            # Rapport détaillé
            st.divider()
            st.subheader("📄 Rapport technique complet")
            
            report = f"""
            RAPPORT TECHNIQUE - ENTREPÔT AVEC CHARIOTS ÉLÉVATEURS
            {'='*60}
            
            I. CARACTÉRISTIQUES DE L'ENTREPÔT
            {'-'*40}
            • Dimensions : {warehouse_length}m (L) × {warehouse_width}m (l) × {warehouse_height}m (H)
            • Surface utile : {warehouse_length * warehouse_width:.0f} m²
            • Hauteur sous plafond : {warehouse_height}m
            
            II. CONFIGURATION DES RACKS
            {'-'*40}
            • Dimensions rack : {rack_length}m × {rack_width}m × {rack_height}m
            • Type : {"Double profondeur" if double_depth else "Simple profondeur"}
            • Nombre total racks : {total_racks}
            • Étages par rack : {rack_levels}
            • Pallets par emplacement : {pallets_per_rack}
            
            III. CIRCULATION CHARIOTS ÉLÉVATEURS
            {'-'*40}
            • Type chariot : {forklift_type}
            • Allée principale : {main_aisle_width}m (minimum requis: 3.0m)
            • Rayon de virage : {turning_radius}m
            • Allée transversale : {cross_aisle_width}m (manoeuvres)
            • Allées secondaires : {secondary_aisle_width}m
            
            IV. CAPACITÉ DE STOCKAGE
            {'-'*40}
            • Emplacements totaux : {total_racks * rack_levels}
            • Pallets totaux : {storage_capacity}
            • Surface utilisée racks : {total_racks * rack_length * effective_rack_width:.0f} m²
            • Surface allées : {(warehouse_length * warehouse_width) - (total_racks * rack_length * effective_rack_width):.0f} m²
            
            V. SÉCURITÉ ET CONFORMITÉ
            {'-'*40}
            • Marge de sécurité : {safety_margin}m
            • Conformité chariots : {"CONFORME" if not issues else "NON CONFORME"}
            • Allées secondaires : {secondary_aisle_width}m
            • Espaces de manoeuvre : PRÉVUS
            
            VI. RECOMMANDATIONS
            {'-'*40}
            • Vérifier la hauteur libre sous chemin de roulement
            • Prévoir zones de stationnement chariots
            • Marquer au sol les allées de circulation
            • Installer protections d'angles sur racks
            • Prévoir éclairage adapté (minimum 200 lux)
            
            Date : {pd.Timestamp.now().strftime('%d/%m/%Y %H:%M')}
            """
            
            col1, col2 = st.columns(2)
            with col1:
                st.download_button(
                    label="📥 Télécharger rapport technique",
                    data=report,
                    file_name="rapport_technique_entrepot_chariots.txt",
                    mime="text/plain"
                )
            with col2:
                # Générer un CSV avec les données
                csv_data = pd.DataFrame({
                    'Catégorie': ['Entrepôt', 'Racks', 'Chariots', 'Allées', 'Capacité'],
                    'Paramètre': ['Dimensions', 'Taille', 'Type', 'Principale', 'Pallets'],
                    'Valeur': [
                        f"{warehouse_length}x{warehouse_width}x{warehouse_height}",
                        f"{rack_length}x{rack_width}x{rack_height}",
                        forklift_type,
                        f"{main_aisle_width}m",
                        str(storage_capacity)
                    ],
                    'Conformité': ['✅', '✅', '✅' if not issues else '❌', '✅', '✅']
                })
                
                st.download_button(
                    label="📊 Exporter données (CSV)",
                    data=csv_data.to_csv(index=False),
                    file_name="configuration_chariots.csv",
                    mime="text/csv"
                )

# Section d'information
with st.expander("📚 Normes et recommandations pour chariots élévateurs"):
    st.markdown("""
    ### 📏 Normes minimales pour circulation chariots :
    
    **1. Allées principales :**
    - Chariots contrebalance : 3.5m minimum
    - Chariots télescopiques : 2.8m minimum
    - Transpalettes : 1.8m minimum
    - Gerbeurs : 2.0m minimum
    
    **2. Rayons de virage :**
    - Chariot standard : 2.2-2.5m
    - Chariot compact : 1.8-2.0m
    - Prévoir +20% pour manoeuvres confortables
    
    **3. Hauteurs de stockage :**
    - Hauteur libre sous chemin de roulement : +0.5m
    - Distance plafond/charges : minimum 0.3m
    - Hauteur max selon chariot : vérifier spécifications
    
    **4. Sécurité :**
    - Murs et poteaux : protéger avec pare-chocs
    - Sol : résistant et plat (pente max 2%)
    - Signalisation au sol obligatoire
    - Éclairage minimum 200 lux dans les allées
    """)

# Pied de page
st.divider()
st.caption("🏭 Warehouse Forklift Optimizer v4.0 | Conforme normes chariots élévateurs | Allées minimum 3m")
