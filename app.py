import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import numpy as np

st.set_page_config(
    page_title="Warehouse Optimizer",
    page_icon="🏭",
    layout="wide"
)

st.title("🏭 Entrepôt Dimension Optimizer")
st.markdown("### Configuration pour chariots élévateurs")

with st.sidebar:
    st.header("📐 Dimensions Entrepôt")
    
    col1, col2 = st.columns(2)
    with col1:
        longueur = st.number_input("Longueur (m)", 50.0)
    with col2:
        largeur = st.number_input("Largeur (m)", 30.0)
    
    hauteur = st.number_input("Hauteur (m)", 12.0)
    
    st.divider()
    st.header("📦 Dimensionnement des Racks")
    
    # Section améliorée pour les racks
    st.subheader("🔧 Dimensions unitaires")
    rack_longueur = st.number_input("Longueur rack (m)", min_value=0.5, max_value=10.0, value=2.4, step=0.1)
    rack_largeur = st.number_input("Largeur rack (m)", min_value=0.5, max_value=5.0, value=1.0, step=0.1)
    rack_hauteur = st.number_input("Hauteur rack (m)", min_value=1.0, max_value=15.0, value=10.0, step=0.5)
    
    st.subheader("📊 Configuration verticale")
    etages = st.slider("Étages par rack", 1, 10, 6)
    hauteur_etage = st.number_input("Hauteur par étage (m)", min_value=0.5, max_value=3.0, value=1.5, step=0.1)
    
    st.subheader("📦 Capacité par niveau")
    palettes_longueur = st.number_input("Palettes en longueur", min_value=1, max_value=10, value=2)
    palettes_largeur = st.number_input("Palettes en largeur", min_value=1, max_value=5, value=1)
    palettes_par_niveau = palettes_longueur * palettes_largeur
    
    st.subheader("🎯 Espacement")
    espacement_vertical = st.number_input("Espacement vertical (cm)", min_value=10, max_value=100, value=30)
    espacement_lateral = st.number_input("Espacement latéral (cm)", min_value=10, max_value=100, value=20)
    
    st.divider()
    st.header("🚜 Chariots élévateurs")
    
    allee = st.slider("Allée chariots (m)", 3.0, 6.0, 4.0, step=0.1)
    type_chariot = st.selectbox("Type chariot", ["Contrebalance", "Télescopique", "Transpalette", "Reach Truck"])
    charge_max = st.number_input("Charge max (tonnes)", min_value=1.0, max_value=10.0, value=2.5, step=0.5)
    
    st.divider()
    st.header("⚙️ Options avancées")
    
    marge_securite = st.slider("Marge sécurité (%)", 5, 25, 15)
    utilisation_surface = st.slider("Utilisation surface (%)", 50, 90, 70)

# Calculs détaillés
if st.button("🚀 Calculer la configuration", type="primary"):
    
    # Calculs de base
    surface = longueur * largeur
    surface_rack = rack_longueur * rack_largeur
    volume_entrepot = longueur * largeur * hauteur
    
    # Calculs racks
    hauteur_totale_rack = etages * hauteur_etage + (etages - 1) * (espacement_vertical / 100)
    
    # Vérification conformité hauteur
    conforme_hauteur = hauteur_totale_rack <= (hauteur - 0.5)
    
    # Estimation nombre de racks (avec marge de sécurité)
    coef_utilisation = utilisation_surface / 100
    racks_longueur = int((longueur * coef_utilisation) / (rack_longueur + espacement_lateral / 100))
    racks_largeur = int((largeur * coef_utilisation) / (rack_largeur + allee))
    nb_racks = racks_longueur * racks_largeur
    
    # Capacités
    capacite_par_rack = etages * palettes_par_niveau
    capacite_totale = nb_racks * capacite_par_rack
    
    # Surface utilisée
    surface_racks_reelle = nb_racks * surface_rack
    surface_allees = surface - surface_racks_reelle
    taux_utilisation = (surface_racks_reelle / surface) * 100
    
    # Résultats
    st.success(f"### 📊 Résultats de la configuration")
    
    # Métriques principales
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("🏢 Surface totale", f"{surface:.0f} m²")
        st.metric("📦 Surface racks", f"{surface_racks_reelle:.0f} m²")
        st.metric("🚶 Surface allées", f"{surface_allees:.0f} m²")
    
    with col2:
        st.metric("🔢 Nombre de racks", f"{nb_racks}")
        st.metric("📐 Disposition", f"{racks_longueur} × {racks_largeur}")
        st.metric("📊 Taux utilisation", f"{taux_utilisation:.1f}%")
    
    with col3:
        st.metric("🔄 Étages/rack", f"{etages}")
        st.metric("📦 Palettes/niveau", f"{palettes_par_niveau}")
        st.metric("🏗️ Capacité/rack", f"{capacite_par_rack} pal.")
    
    with col4:
        st.metric("📈 Capacité totale", f"{capacite_totale:,} pal.".replace(',', ' '))
        st.metric("📏 Hauteur rack", f"{hauteur_totale_rack:.2f} m")
        st.metric("✅ Conformité", "✅" if (conforme_hauteur and allee >= 3.0) else "⚠️")
    
    # Analyse détaillée des racks
    st.divider()
    st.subheader("🔍 Analyse détaillée des Racks")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### 📐 Dimensions")
        rack_data = {
            'Paramètre': [
                'Longueur unitaire',
                'Largeur unitaire', 
                'Hauteur totale',
                'Surface au sol',
                'Volume par rack',
                'Hauteur par étage',
                'Espacement vertical',
                'Espacement latéral'
            ],
            'Valeur': [
                f"{rack_longueur} m",
                f"{rack_largeur} m",
                f"{hauteur_totale_rack:.2f} m",
                f"{surface_rack:.2f} m²",
                f"{surface_rack * hauteur_totale_rack:.2f} m³",
                f"{hauteur_etage} m",
                f"{espacement_vertical} cm",
                f"{espacement_lateral} cm"
            ]
        }
        st.dataframe(pd.DataFrame(rack_data), hide_index=True, use_container_width=True)
    
    with col2:
        st.markdown("#### 📊 Capacité")
        capacite_data = {
            'Paramètre': [
                'Palettes/longueur',
                'Palettes/largeur',
                'Palettes/niveau',
                'Nombre d\'étages',
                'Palettes/rack',
                'Nombre de racks',
                'Capacité totale',
                'Charge totale estimée'
            ],
            'Valeur': [
                f"{palettes_longueur}",
                f"{palettes_largeur}",
                f"{palettes_par_niveau}",
                f"{etages}",
                f"{capacite_par_rack}",
                f"{nb_racks}",
                f"{capacite_totale:,}".replace(',', ' '),
                f"{capacite_totale * charge_max / 1000:.1f} tonnes"
            ]
        }
        st.dataframe(pd.DataFrame(capacite_data), hide_index=True, use_container_width=True)
    
    # Visualisation de la configuration
    st.divider()
    st.subheader("🎨 Visualisation de la configuration")
    
    # Créer deux vues : plan et vue de côté
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### 📐 Vue de dessus (Plan)")
        
        # Créer la figure Plotly pour la vue de dessus
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
        
        # Calculer l'espacement entre les racks
        espace_lat = espacement_lateral / 100
        
        x_offset = (longueur - (racks_longueur * rack_longueur + (racks_longueur - 1) * espace_lat)) / 2
        y_offset = allee / 2
        
        # Dessiner les racks
        for i in range(racks_longueur):
            for j in range(racks_largeur):
                x = x_offset + i * (rack_longueur + espace_lat)
                y = y_offset + j * (rack_largeur + allee)
                
                fig_plan.add_shape(
                    type="rect",
                    x0=x, y0=y, x1=x + rack_longueur, y1=y + rack_largeur,
                    line=dict(color="darkred", width=2),
                    fillcolor="orange",
                    opacity=0.7
                )
                
                # Ajouter le nombre de palettes sur le rack (si pas trop de racks)
                if nb_racks <= 50:
                    fig_plan.add_annotation(
                        x=x + rack_longueur/2,
                        y=y + rack_largeur/2,
                        text=f"{capacite_par_rack}p",
                        showarrow=False,
                        font=dict(size=10, color="white", family="Arial Black"),
                        bgcolor="rgba(0,0,0,0.3)",
                        borderpad=2
                    )
        
        # Dessiner les allées principales
        for j in range(1, racks_largeur):
            y_allee = y_offset + j * (rack_largeur + allee) - allee/2
            fig_plan.add_shape(
                type="rect",
                x0=0, y0=y_allee, x1=longueur, y1=y_allee + allee,
                fillcolor="lightblue",
                opacity=0.3,
                layer="below",
                line_width=0
            )
        
        # Mise en forme
        fig_plan.update_layout(
            title=dict(
                text=f'Configuration: {racks_longueur}×{racks_largeur} racks | Utilisation: {taux_utilisation:.1f}%',
                font=dict(size=14, family="Arial Black")
            ),
            xaxis=dict(title="Longueur (m)", range=[-2, longueur + 2], showgrid=True, gridwidth=1, gridcolor='lightgray'),
            yaxis=dict(title="Largeur (m)", range=[-2, largeur + 2], showgrid=True, gridwidth=1, gridcolor='lightgray'),
            height=500,
            showlegend=False,
            plot_bgcolor='white',
            hovermode='closest'
        )
        
        # Ajouter annotations des dimensions
        fig_plan.add_annotation(
            x=longueur/2, y=-1,
            text=f"Longueur: {longueur}m",
            showarrow=False,
            font=dict(size=12, family="Arial Black")
        )
        fig_plan.add_annotation(
            x=-1, y=largeur/2,
            text=f"Largeur: {largeur}m",
            showarrow=False,
            textangle=-90,
            font=dict(size=12, family="Arial Black")
        )
        
        st.plotly_chart(fig_plan, use_container_width=True)
    
    with col2:
        st.markdown("#### 📊 Vue latérale (Élévation)")
        
        # Créer la figure pour la vue latérale
        fig_elevation = go.Figure()
        
        # Dessiner le bâtiment
        fig_elevation.add_shape(
            type="rect",
            x0=0, y0=0, x1=longueur, y1=hauteur,
            line=dict(color="darkblue", width=3),
            fillcolor="lightgray",
            opacity=0.2,
            layer="below"
        )
        
        # Dessiner quelques racks en vue latérale (max 5 pour la lisibilité)
        racks_to_show = min(5, racks_longueur)
        rack_spacing = longueur / (racks_to_show + 1)
        
        for i in range(racks_to_show):
            x_rack = rack_spacing * (i + 1) - rack_longueur/2
            
            # Dessiner le rack complet
            fig_elevation.add_shape(
                type="rect",
                x0=x_rack, y0=0, x1=x_rack + rack_longueur, y1=hauteur_totale_rack,
                line=dict(color="darkred", width=2),
                fillcolor="orange",
                opacity=0.6
            )
            
            # Dessiner les niveaux
            for niveau in range(etages):
                y_niveau = niveau * (hauteur_etage + espacement_vertical/100)
                
                # Ligne de niveau
                fig_elevation.add_shape(
                    type="line",
                    x0=x_rack, y0=y_niveau, x1=x_rack + rack_longueur, y1=y_niveau,
                    line=dict(color="red", width=1)
                )
                
                # Dessiner les palettes sur ce niveau
                palette_width = rack_longueur / (palettes_longueur * 1.2)
                palette_height = hauteur_etage * 0.7
                
                for p in range(palettes_longueur):
                    x_palette = x_rack + (rack_longueur / (palettes_longueur + 1)) * (p + 1) - palette_width/2
                    y_palette = y_niveau + 0.1
                    
                    fig_elevation.add_shape(
                        type="rect",
                        x0=x_palette, y0=y_palette,
                        x1=x_palette + palette_width, y1=y_palette + palette_height,
                        line=dict(color="brown", width=1),
                        fillcolor="wheat",
                        opacity=0.9
                    )
        
        # Ligne du sol
        fig_elevation.add_shape(
            type="line",
            x0=0, y0=0, x1=longueur, y1=0,
            line=dict(color="black", width=3)
        )
        
        # Ligne de hauteur maximale rack
        fig_elevation.add_shape(
            type="line",
            x0=0, y0=hauteur_totale_rack, x1=longueur, y1=hauteur_totale_rack,
            line=dict(color="red", width=2, dash="dash")
        )
        
        # Annotations
        fig_elevation.add_annotation(
            x=longueur + 1, y=hauteur_totale_rack/2,
            text=f'{hauteur_totale_rack:.2f}m<br>({etages} étages)',
            showarrow=True,
            arrowhead=2,
            arrowsize=1,
            arrowwidth=2,
            arrowcolor="red",
            ax=40,
            ay=0,
            font=dict(size=10, color="red", family="Arial Black"),
            bgcolor="white",
            borderpad=4
        )
        
        # Marge de sécurité
        if conforme_hauteur:
            marge = hauteur - hauteur_totale_rack
            fig_elevation.add_annotation(
                x=longueur + 1, y=hauteur_totale_rack + marge/2,
                text=f'Marge<br>{marge:.2f}m',
                showarrow=False,
                font=dict(size=9, color="green", family="Arial Black"),
                bgcolor="lightgreen",
                borderpad=3
            )
        
        # Mise en forme
        fig_elevation.update_layout(
            title=dict(
                text=f'Élévation: {etages} étages × {hauteur_etage}m = {hauteur_totale_rack:.2f}m',
                font=dict(size=14, family="Arial Black")
            ),
            xaxis=dict(title="Longueur (m)", range=[-2, longueur + 4], showgrid=True),
            yaxis=dict(title="Hauteur (m)", range=[-0.5, hauteur + 1], showgrid=True),
            height=500,
            showlegend=False,
            plot_bgcolor='white',
            hovermode='closest'
        )
        
        st.plotly_chart(fig_elevation, use_container_width=True)
    
    # Vue 3D interactive
    st.markdown("#### 🏗️ Vue 3D interactive")
    
    fig_3d = go.Figure()
    
    # Fonction pour créer les points d'un cube
    def create_cube(x, y, z, width, depth, height, color, name):
        # Les 8 sommets du cube
        vertices = np.array([
            [x, y, z],
            [x + width, y, z],
            [x + width, y + depth, z],
            [x, y + depth, z],
            [x, y, z + height],
            [x + width, y, z + height],
            [x + width, y + depth, z + height],
            [x, y + depth, z + height]
        ])
        
        # Les 6 faces du cube (indices des sommets)
        faces = [
            [0, 1, 2, 3],  # Bottom
            [4, 5, 6, 7],  # Top
            [0, 1, 5, 4],  # Front
            [2, 3, 7, 6],  # Back
            [0, 3, 7, 4],  # Left
            [1, 2, 6, 5]   # Right
        ]
        
        return vertices, faces
    
    # Dessiner l'entrepôt (contour)
    vertices_warehouse, _ = create_cube(0, 0, 0, longueur, largeur, hauteur, 'lightblue', 'Entrepôt')
    
    # Arêtes de l'entrepôt
    edges = [
        [0, 1], [1, 2], [2, 3], [3, 0],  # Bottom
        [4, 5], [5, 6], [6, 7], [7, 4],  # Top
        [0, 4], [1, 5], [2, 6], [3, 7]   # Vertical
    ]
    
    for edge in edges:
        fig_3d.add_trace(go.Scatter3d(
            x=[vertices_warehouse[edge[0]][0], vertices_warehouse[edge[1]][0]],
            y=[vertices_warehouse[edge[0]][1], vertices_warehouse[edge[1]][1]],
            z=[vertices_warehouse[edge[0]][2], vertices_warehouse[edge[1]][2]],
            mode='lines',
            line=dict(color='darkblue', width=3),
            showlegend=False,
            hoverinfo='skip'
        ))
    
    # Dessiner un échantillon de racks en 3D
    sample_racks_x = min(racks_longueur, 6)
    sample_racks_y = min(racks_largeur, 4)
    
    step_x = racks_longueur // sample_racks_x if sample_racks_x > 0 else 1
    step_y = racks_largeur // sample_racks_y if sample_racks_y > 0 else 1
    
    for i in range(0, racks_longueur, step_x):
        for j in range(0, racks_largeur, step_y):
            x_pos = x_offset + i * (rack_longueur + espace_lat)
            y_pos = y_offset + j * (rack_largeur + allee)
            
            vertices_rack, faces_rack = create_cube(
                x_pos, y_pos, 0,
                rack_longueur, rack_largeur, hauteur_totale_rack,
                'orange', f'Rack {i},{j}'
            )
            
            # Dessiner les faces du rack
            for face_idx, face in enumerate(faces_rack):
                xs = [vertices_rack[i][0] for i in face] + [vertices_rack[face[0]][0]]
                ys = [vertices_rack[i][1] for i in face] + [vertices_rack[face[0]][1]]
                zs = [vertices_rack[i][2] for i in face] + [vertices_rack[face[0]][2]]
                
                fig_3d.add_trace(go.Mesh3d(
                    x=xs, y=ys, z=zs,
                    color='orange',
                    opacity=0.7,
                    showlegend=False,
                    hovertext=f'Rack: {capacite_par_rack} palettes',
                    hoverinfo='text'
                ))
    
    # Mise en forme 3D
    fig_3d.update_layout(
        title=dict(
            text=f'Vue 3D: {nb_racks} racks | {capacite_totale:,} palettes'.replace(',', ' '),
            font=dict(size=16, family="Arial Black")
        ),
        scene=dict(
            xaxis=dict(title='Longueur (m)', backgroundcolor="white", gridcolor="lightgray"),
            yaxis=dict(title='Largeur (m)', backgroundcolor="white", gridcolor="lightgray"),
            zaxis=dict(title='Hauteur (m)', backgroundcolor="white", gridcolor="lightgray"),
            camera=dict(
                eye=dict(x=1.5, y=1.5, z=1.2)
            ),
            aspectmode='data'
        ),
        height=600,
        showlegend=False,
        hovermode='closest'
    )
    
    st.plotly_chart(fig_3d, use_container_width=True)
    
    # Graphique de répartition de la surface
    st.divider()
    st.subheader("📊 Répartition de l'espace")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Pie chart de la répartition
        fig_pie = go.Figure(data=[go.Pie(
            labels=['Surface Racks', 'Surface Allées', 'Espace libre'],
            values=[surface_racks_reelle, surface_allees * 0.6, surface_allees * 0.4],
            hole=0.4,
            marker=dict(colors=['orange', 'lightblue', 'lightgray']),
            textinfo='label+percent',
            textfont=dict(size=12)
        )])
        
        fig_pie.update_layout(
            title='Répartition de la surface au sol',
            height=400,
            showlegend=True
        )
        
        st.plotly_chart(fig_pie, use_container_width=True)
    
    with col2:
        # Bar chart de capacité par niveau
        niveaux = list(range(1, etages + 1))
        capacite_par_niveau = [palettes_par_niveau] * etages
        capacite_cumulee = [sum(capacite_par_niveau[:i+1]) for i in range(etages)]
        
        fig_bar = go.Figure()
        
        fig_bar.add_trace(go.Bar(
            x=niveaux,
            y=capacite_par_niveau,
            name='Palettes par niveau',
            marker=dict(color='orange'),
            text=capacite_par_niveau,
            textposition='outside'
        ))
        
        fig_bar.update_layout(
            title='Capacité par niveau (par rack)',
            xaxis_title='Niveau',
            yaxis_title='Nombre de palettes',
            height=400,
            showlegend=True,
            hovermode='x'
        )
        
        st.plotly_chart(fig_bar, use_container_width=True)
    
    # Tableau récapitulatif général
    st.divider()
    st.subheader("📋 Configuration complète")
    
    data = {
        'Catégorie': ['Entrepôt', 'Racks', 'Disposition', 'Chariots', 'Capacité', 'Utilisation'],
        'Spécifications': [
            f"{longueur}m × {largeur}m × {hauteur}m",
            f"{rack_longueur}m × {rack_largeur}m × {hauteur_totale_rack:.1f}m",
            f"{racks_longueur} × {racks_largeur} = {nb_racks} racks",
            f"{type_chariot} - {charge_max}t - Allée {allee}m",
            f"{etages} étages × {palettes_par_niveau} pal/niveau",
            f"{taux_utilisation:.1f}% de la surface"
        ],
        'Résultats': [
            f"{surface:.0f} m² | {volume_entrepot:.0f} m³",
            f"{capacite_par_rack} palettes par rack",
            f"{surface_racks_reelle:.0f} m² occupés",
            "Conforme" if allee >= 3.0 else "⚠️ À vérifier",
            f"{capacite_totale:,} palettes totales".replace(',', ' '),
            f"{surface_allees:.0f} m² d'allées"
        ]
    }
    
    df = pd.DataFrame(data)
    st.table(df)
    
    # Alertes et recommandations
    st.divider()
    st.subheader("⚠️ Vérifications et recommandations")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### ✅ Conformité")
        if conforme_hauteur:
            st.success(f"✅ Hauteur rack ({hauteur_totale_rack:.2f}m) conforme (marge: {hauteur - hauteur_totale_rack:.2f}m)")
        else:
            st.error(f"❌ Hauteur rack ({hauteur_totale_rack:.2f}m) > hauteur entrepôt ({hauteur}m)")
        
        if allee >= 3.0:
            st.success(f"✅ Largeur allée ({allee}m) conforme")
        else:
            st.error(f"❌ Largeur allée ({allee}m) < minimum requis (3.0m)")
        
        if taux_utilisation >= 50 and taux_utilisation <= 80:
            st.success(f"✅ Taux d'utilisation optimal ({taux_utilisation:.1f}%)")
        elif taux_utilisation < 50:
            st.warning(f"⚠️ Faible utilisation de l'espace ({taux_utilisation:.1f}%)")
        else:
            st.warning(f"⚠️ Utilisation très dense ({taux_utilisation:.1f}%)")
    
    with col2:
        st.markdown("#### 💡 Recommandations")
        if type_chariot == "Contrebalance" and allee < 3.5:
            st.info("💡 Allée recommandée pour contrebalance: 3.5m minimum")
        if type_chariot == "Reach Truck" and allee > 3.5:
            st.info("💡 Un Reach Truck peut fonctionner dans des allées plus étroites (2.7-3.0m)")
        if hauteur - hauteur_totale_rack < 1.0:
            st.warning("💡 Prévoir au moins 1m de marge au-dessus des racks")
        if palettes_par_niveau == 1:
            st.info("💡 Envisager 2 palettes/niveau pour optimiser l'espace")
    
    # Export détaillé
    st.divider()
    st.subheader("💾 Exporter la configuration")
    
    rapport = f"""CONFIGURATION ENTREPÔT - RAPPORT DÉTAILLÉ
{'='*60}

ENTREPÔT:
---------
  Dimensions: {longueur}m × {largeur}m × {hauteur}m
  Surface: {surface:.0f} m²
  Volume: {volume_entrepot:.0f} m³

DIMENSIONNEMENT DES RACKS:
--------------------------
  Dimensions unitaires:
    - Longueur: {rack_longueur} m
    - Largeur: {rack_largeur} m
    - Hauteur totale: {hauteur_totale_rack:.2f} m
    - Surface au sol: {surface_rack:.2f} m²
  
  Configuration verticale:
    - Nombre d'étages: {etages}
    - Hauteur par étage: {hauteur_etage} m
    - Espacement vertical: {espacement_vertical} cm
    - Espacement latéral: {espacement_lateral} cm
  
  Capacité par rack:
    - Palettes en longueur: {palettes_longueur}
    - Palettes en largeur: {palettes_largeur}
    - Palettes par niveau: {palettes_par_niveau}
    - Palettes par rack: {capacite_par_rack}

DISPOSITION:
-----------
  Nombre total de racks: {nb_racks}
  Disposition: {racks_longueur} racks × {racks_largeur} racks
  Surface racks: {surface_racks_reelle:.0f} m²
  Surface allées: {surface_allees:.0f} m²
  Taux d'utilisation: {taux_utilisation:.1f}%

CHARIOTS ÉLÉVATEURS:
-------------------
  Type: {type_chariot}
  Charge maximale: {charge_max} tonnes
  Largeur allée: {allee} m
  Conformité allée: {'CONFORME' if allee >= 3.0 else 'NON CONFORME - Minimum 3.0m requis'}

CAPACITÉ TOTALE:
---------------
  Palettes totales: {capacite_totale:,}
  Emplacements de stockage: {nb_racks * etages}
  Charge totale estimée: {capacite_totale * charge_max / 1000:.1f} tonnes

CONFORMITÉ:
----------
  Hauteur: {'✅ CONFORME' if conforme_hauteur else '❌ NON CONFORME'} 
    (Rack {hauteur_totale_rack:.2f}m vs Entrepôt {hauteur}m - Marge {hauteur - hauteur_totale_rack:.2f}m)
  Allées: {'✅ CONFORME' if allee >= 3.0 else '❌ NON CONFORME'}
    (Largeur {allee}m vs Minimum 3.0m)
  Utilisation surface: {taux_utilisation:.1f}%

PARAMÈTRES DE CONFIGURATION:
---------------------------
  Marge de sécurité: {marge_securite}%
  Utilisation surface ciblée: {utilisation_surface}%

GÉNÉRÉ LE: {pd.Timestamp.now().strftime('%d/%m/%Y à %H:%M:%S')}
{'='*60}
"""
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.download_button(
            label="📄 Télécharger le rapport TXT",
            data=rapport,
            file_name=f"config_entrepot_{pd.Timestamp.now().strftime('%Y%m%d_%H%M')}.txt",
            mime="text/plain",
            use_container_width=True
        )
    
    with col2:
        # Export CSV
        csv_data = pd.DataFrame({
            'Paramètre': [
                'Surface totale', 'Nombre de racks', 'Capacité totale', 
                'Hauteur rack', 'Palettes/rack', 'Taux utilisation',
                'Largeur allée', 'Type chariot'
            ],
            'Valeur': [
                surface, nb_racks, capacite_totale,
                hauteur_totale_rack, capacite_par_rack, taux_utilisation,
                allee, type_chariot
            ]
        })
        
        st.download_button(
            label="📊 Télécharger les données CSV",
            data=csv_data.to_csv(index=False).encode('utf-8'),
            file_name=f"donnees_entrepot_{pd.Timestamp.now().strftime('%Y%m%d_%H%M')}.csv",
            mime="text/csv",
            use_container_width=True
        )

# Instructions améliorées
with st.expander("ℹ️ Guide d'utilisation"):
    st.markdown("""
    ### Comment utiliser l'optimiseur :
    
    #### 1️⃣ Dimensions de l'entrepôt
    - Saisissez les dimensions totales de votre entrepôt (L × l × H)
    
    #### 2️⃣ Dimensionnement des racks
    - **Dimensions unitaires** : Taille d'un rack individuel
    - **Configuration verticale** : Nombre d'étages et hauteur de chaque niveau
    - **Capacité par niveau** : Combien de palettes peuvent être stockées par niveau
    - **Espacement** : Marges de sécurité verticale et latérale
    
    #### 3️⃣ Chariots élévateurs
    - Choisissez le type de chariot adapté à vos besoins
    - Définissez la largeur d'allée nécessaire
    - Spécifiez la charge maximale
    
    #### 4️⃣ Options avancées
    - Ajustez les marges de sécurité
    - Définissez le taux d'utilisation souhaité
    
    #### 5️⃣ Calcul et export
    - Cliquez sur **Calculer** pour voir les résultats
    - Exportez le rapport au format TXT ou CSV
    
    ### 📏 Normes et recommandations :
    
    **Chariots élévateurs :**
    - Allée minimum : **3.0 mètres**
    - Contrebalance : **3.5m recommandé**
    - Reach Truck : **2.7-3.0m possible**
    - Télescopique : **3.0-3.5m**
    
    **Hauteur :**
    - Prévoir **+0.5m minimum** au-dessus des racks
    - **+1.0m recommandé** pour l'éclairage et la sécurité
    
    **Espacement :**
    - Vertical : **30cm minimum** entre niveaux
    - Latéral : **20cm minimum** entre racks
    
    **Utilisation de surface :**
    - Optimal : **60-80%** (balance stockage/circulation)
    - Minimum : **50%** (trop d'espace perdu)
    - Maximum : **85%** (risque de congestion)
    """)

st.caption("🏭 Warehouse Optimizer v2.0 | Dimensionnement avancé des racks | Streamlit Cloud Compatible")
