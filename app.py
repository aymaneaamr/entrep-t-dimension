import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import Rectangle, FancyBboxPatch
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
    
    # Créer deux vues : plan et vue 3D simplifiée
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### 📐 Vue de dessus (Plan)")
        
        # Créer la figure pour la vue de dessus
        fig_plan, ax_plan = plt.subplots(figsize=(10, 8))
        
        # Dessiner le contour de l'entrepôt
        warehouse_rect = Rectangle((0, 0), longueur, largeur, 
                                   linewidth=3, edgecolor='darkblue', 
                                   facecolor='lightgray', alpha=0.3, 
                                   label='Entrepôt')
        ax_plan.add_patch(warehouse_rect)
        
        # Calculer l'espacement entre les racks
        espace_lat = espacement_lateral / 100
        
        # Dessiner les racks avec allées
        rack_color = 'orange'
        allee_color = 'white'
        
        x_offset = (longueur - (racks_longueur * rack_longueur + (racks_longueur - 1) * espace_lat)) / 2
        y_offset = allee / 2
        
        for i in range(racks_longueur):
            for j in range(racks_largeur):
                x = x_offset + i * (rack_longueur + espace_lat)
                y = y_offset + j * (rack_largeur + allee)
                
                rack = FancyBboxPatch((x, y), rack_longueur, rack_largeur,
                                     boxstyle="round,pad=0.05", 
                                     linewidth=1.5, 
                                     edgecolor='darkred', 
                                     facecolor=rack_color, 
                                     alpha=0.7)
                ax_plan.add_patch(rack)
                
                # Ajouter le nombre de palettes sur le rack
                if nb_racks <= 50:  # Afficher seulement si pas trop de racks
                    ax_plan.text(x + rack_longueur/2, y + rack_largeur/2, 
                               f'{capacite_par_rack}p',
                               ha='center', va='center', 
                               fontsize=8, fontweight='bold',
                               color='white')
        
        # Dessiner les allées principales
        for j in range(racks_largeur + 1):
            y_allee = y_offset + j * (rack_largeur + allee) - allee/2
            if j == 0:
                y_allee = 0
            if j == racks_largeur:
                y_allee = y_offset + j * (rack_largeur + allee) - allee
            
            allee_rect = Rectangle((0, y_allee), longueur, 
                                   allee if j != 0 and j != racks_largeur else allee/2,
                                   linewidth=0, 
                                   facecolor='lightblue', 
                                   alpha=0.3)
            if j > 0 and j < racks_largeur:
                ax_plan.add_patch(allee_rect)
        
        # Annotations
        ax_plan.text(longueur/2, -1.5, f'Longueur: {longueur}m', 
                    ha='center', fontsize=10, fontweight='bold')
        ax_plan.text(-1.5, largeur/2, f'Largeur: {largeur}m', 
                    ha='center', va='center', rotation=90, 
                    fontsize=10, fontweight='bold')
        
        # Légende
        legend_elements = [
            patches.Patch(facecolor='lightgray', edgecolor='darkblue', 
                         label=f'Entrepôt ({surface:.0f}m²)', alpha=0.3),
            patches.Patch(facecolor=rack_color, edgecolor='darkred', 
                         label=f'Racks ({nb_racks} unités)', alpha=0.7),
            patches.Patch(facecolor='lightblue', 
                         label=f'Allées ({allee}m)', alpha=0.3)
        ]
        ax_plan.legend(handles=legend_elements, loc='upper right', fontsize=9)
        
        ax_plan.set_xlim(-2, longueur + 2)
        ax_plan.set_ylim(-2, largeur + 2)
        ax_plan.set_aspect('equal')
        ax_plan.grid(True, alpha=0.3, linestyle='--')
        ax_plan.set_xlabel('Longueur (m)', fontsize=10)
        ax_plan.set_ylabel('Largeur (m)', fontsize=10)
        ax_plan.set_title(f'Configuration: {racks_longueur}×{racks_largeur} racks | Utilisation: {taux_utilisation:.1f}%', 
                         fontsize=11, fontweight='bold')
        
        st.pyplot(fig_plan)
    
    with col2:
        st.markdown("#### 📊 Vue latérale (Élévation)")
        
        # Créer la figure pour la vue latérale
        fig_elevation, ax_elev = plt.subplots(figsize=(10, 8))
        
        # Dessiner le bâtiment
        building = Rectangle((0, 0), longueur, hauteur,
                            linewidth=3, edgecolor='darkblue',
                            facecolor='lightgray', alpha=0.2,
                            label='Bâtiment')
        ax_elev.add_patch(building)
        
        # Dessiner quelques racks en vue latérale (max 5 pour la lisibilité)
        racks_to_show = min(5, racks_longueur)
        rack_spacing = longueur / (racks_to_show + 1)
        
        for i in range(racks_to_show):
            x_rack = rack_spacing * (i + 1) - rack_longueur/2
            
            # Dessiner le rack complet
            rack_elevation = Rectangle((x_rack, 0), rack_longueur, hauteur_totale_rack,
                                      linewidth=2, edgecolor='darkred',
                                      facecolor='orange', alpha=0.6)
            ax_elev.add_patch(rack_elevation)
            
            # Dessiner les niveaux
            for niveau in range(etages):
                y_niveau = niveau * (hauteur_etage + espacement_vertical/100)
                
                # Ligne de niveau
                ax_elev.plot([x_rack, x_rack + rack_longueur], 
                           [y_niveau, y_niveau], 
                           'r-', linewidth=1, alpha=0.8)
                
                # Dessiner les palettes sur ce niveau
                palette_width = rack_longueur / (palettes_longueur * 1.2)
                palette_height = hauteur_etage * 0.7
                
                for p in range(palettes_longueur):
                    x_palette = x_rack + (rack_longueur / (palettes_longueur + 1)) * (p + 1) - palette_width/2
                    y_palette = y_niveau + 0.1
                    
                    palette = Rectangle((x_palette, y_palette), 
                                      palette_width, palette_height,
                                      linewidth=1, edgecolor='brown',
                                      facecolor='wheat', alpha=0.9)
                    ax_elev.add_patch(palette)
        
        # Ligne du sol
        ax_elev.plot([0, longueur], [0, 0], 'k-', linewidth=3, label='Sol')
        
        # Ligne de hauteur maximale rack
        ax_elev.plot([0, longueur], [hauteur_totale_rack, hauteur_totale_rack], 
                    'r--', linewidth=2, label=f'Hauteur rack: {hauteur_totale_rack:.2f}m')
        
        # Ligne de hauteur entrepôt
        ax_elev.plot([0, longueur], [hauteur, hauteur], 
                    'b--', linewidth=2, label=f'Hauteur entrepôt: {hauteur}m')
        
        # Annotations pour les dimensions
        # Hauteur rack
        ax_elev.annotate('', xy=(longueur + 1, 0), xytext=(longueur + 1, hauteur_totale_rack),
                        arrowprops=dict(arrowstyle='<->', color='red', lw=2))
        ax_elev.text(longueur + 1.5, hauteur_totale_rack/2, 
                    f'{hauteur_totale_rack:.2f}m\n({etages} étages)',
                    va='center', fontsize=9, fontweight='bold', color='red')
        
        # Marge de sécurité
        if conforme_hauteur:
            marge = hauteur - hauteur_totale_rack
            ax_elev.annotate('', xy=(longueur + 1, hauteur_totale_rack), 
                           xytext=(longueur + 1, hauteur),
                           arrowprops=dict(arrowstyle='<->', color='green', lw=1.5))
            ax_elev.text(longueur + 1.5, hauteur_totale_rack + marge/2, 
                        f'Marge\n{marge:.2f}m',
                        va='center', fontsize=8, color='green')
        
        # Hauteur d'un étage
        if etages > 0:
            ax_elev.annotate('', xy=(x_rack - 0.5, 0), 
                           xytext=(x_rack - 0.5, hauteur_etage),
                           arrowprops=dict(arrowstyle='<->', color='orange', lw=1.5))
            ax_elev.text(x_rack - 1.2, hauteur_etage/2, 
                        f'{hauteur_etage}m',
                        va='center', ha='right', fontsize=8, color='orange')
        
        ax_elev.set_xlim(-2, longueur + 4)
        ax_elev.set_ylim(-0.5, hauteur + 1)
        ax_elev.grid(True, alpha=0.3, linestyle='--')
        ax_elev.set_xlabel('Longueur (m)', fontsize=10)
        ax_elev.set_ylabel('Hauteur (m)', fontsize=10)
        ax_elev.set_title(f'Élévation: {etages} étages × {hauteur_etage}m = {hauteur_totale_rack:.2f}m', 
                         fontsize=11, fontweight='bold')
        ax_elev.legend(loc='upper left', fontsize=9)
        
        st.pyplot(fig_elevation)
    
    # Vue 3D simplifiée (isométrique)
    st.markdown("#### 🏗️ Vue isométrique")
    
    fig_iso, ax_iso = plt.subplots(figsize=(12, 8))
    
    # Fonction pour dessiner un cube en perspective isométrique
    def draw_isometric_box(ax, x, y, z, width, depth, height, color, alpha=0.7, edge_color='black'):
        # Facteurs de projection isométrique
        iso_x = lambda x, y: x - y * 0.5
        iso_y = lambda x, y, z: x * 0.25 + y * 0.25 + z
        
        # Points du cube
        vertices = [
            [x, y, z],
            [x + width, y, z],
            [x + width, y + depth, z],
            [x, y + depth, z],
            [x, y, z + height],
            [x + width, y, z + height],
            [x + width, y + depth, z + height],
            [x, y + depth, z + height]
        ]
        
        # Convertir en coordonnées isométriques
        iso_vertices = [[iso_x(v[0], v[1]), iso_y(v[0], v[1], v[2])] for v in vertices]
        
        # Faces visibles (top, front, right)
        faces = [
            [iso_vertices[4], iso_vertices[5], iso_vertices[6], iso_vertices[7]],  # Top
            [iso_vertices[0], iso_vertices[1], iso_vertices[5], iso_vertices[4]],  # Front
            [iso_vertices[1], iso_vertices[2], iso_vertices[6], iso_vertices[5]]   # Right
        ]
        
        colors_shade = [color, color, color]
        alphas = [alpha, alpha * 0.8, alpha * 0.6]
        
        for face, fc, a in zip(faces, colors_shade, alphas):
            poly = plt.Polygon(face, facecolor=fc, edgecolor=edge_color, 
                             linewidth=0.5, alpha=a)
            ax.add_patch(poly)
    
    # Dessiner l'entrepôt
    draw_isometric_box(ax_iso, 0, 0, 0, longueur, largeur, hauteur, 
                      'lightblue', alpha=0.15, edge_color='darkblue')
    
    # Dessiner un échantillon de racks (limité pour la lisibilité)
    sample_racks_x = min(4, racks_longueur)
    sample_racks_y = min(3, racks_largeur)
    
    for i in range(sample_racks_x):
        for j in range(sample_racks_y):
            x_pos = x_offset + i * (rack_longueur + espace_lat)
            y_pos = y_offset + j * (rack_largeur + allee)
            
            draw_isometric_box(ax_iso, x_pos, y_pos, 0, 
                             rack_longueur, rack_largeur, hauteur_totale_rack,
                             'orange', alpha=0.8, edge_color='darkred')
    
    # Ajouter des annotations
    iso_x = lambda x, y: x - y * 0.5
    iso_y = lambda x, y, z: x * 0.25 + y * 0.25 + z
    
    # Texte informatif
    ax_iso.text(iso_x(longueur/2, 0), iso_y(longueur/2, 0, hauteur + 2),
               f'{nb_racks} racks | {capacite_totale:,} palettes'.replace(',', ' '),
               ha='center', fontsize=12, fontweight='bold',
               bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8))
    
    ax_iso.set_xlim(-5, longueur + 5)
    ax_iso.set_ylim(-5, hauteur + largeur * 0.5 + 5)
    ax_iso.set_aspect('equal')
    ax_iso.axis('off')
    ax_iso.set_title('Vue 3D isométrique de l\'entrepôt', 
                    fontsize=13, fontweight='bold', pad=20)
    
    # Légende
    legend_text = f"""Configuration:
• {racks_longueur} × {racks_largeur} = {nb_racks} racks
• {etages} étages par rack
• Hauteur totale: {hauteur_totale_rack:.2f}m
• Capacité: {capacite_totale:,} palettes""".replace(',', ' ')
    
    ax_iso.text(0.02, 0.98, legend_text,
               transform=ax_iso.transAxes,
               fontsize=10,
               verticalalignment='top',
               bbox=dict(boxstyle='round', facecolor='lightgray', alpha=0.8))
    
    st.pyplot(fig_iso)
    
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
