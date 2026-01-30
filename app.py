import streamlit as st
import pandas as pd

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
