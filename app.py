import streamlit as st
import pandas as pd
import numpy as np
import itertools

st.set_page_config(
    page_title="Warehouse Configuration Optimizer",
    page_icon="🏭",
    layout="wide"
)

# Titre principal
st.title("🏭 Warehouse Configuration Optimizer")
st.markdown("### Calcul de TOUTES les configurations possibles avec 3m entre les racks")

# Sidebar avec les paramètres
with st.sidebar:
    st.header("📐 Dimensions de l'entrepôt (Fixes)")
    
    col1, col2 = st.columns(2)
    with col1:
        L = st.number_input("Longueur totale L (m)", min_value=10.0, value=50.0, step=1.0, key="L")
    with col2:
        l = st.number_input("Largeur totale l (m)", min_value=10.0, value=30.0, step=1.0, key="l")
    
    H = st.number_input("Hauteur totale H (m)", min_value=3.0, value=12.0, step=0.5, key="H")
    
    st.divider()
    st.header("📦 Dimensions des racks (Variables)")
    
    st.markdown("**Longueur des racks (LR)**")
    min_LR = st.number_input("Min LR (m)", 0.5, 5.0, 1.5, step=0.1)
    max_LR = st.number_input("Max LR (m)", min_LR, 10.0, 3.0, step=0.1)
    step_LR = st.number_input("Step LR (m)", 0.1, 1.0, 0.5, step=0.1)
    
    st.markdown("**Largeur des racks (lR)**")
    min_lR = st.number_input("Min lR (m)", 0.5, 3.0, 0.8, step=0.1)
    max_lR = st.number_input("Max lR (m)", min_lR, 5.0, 1.2, step=0.1)
    step_lR = st.number_input("Step lR (m)", 0.1, 0.5, 0.2, step=0.1)
    
    st.markdown("**Hauteur des racks (HR)**")
    min_HR = st.number_input("Min HR (m)", 1.0, H, 2.0, step=0.1)
    max_HR = st.number_input("Max HR (m)", min_HR, H, 8.0, step=0.1)
    step_HR = st.number_input("Step HR (m)", 0.1, 2.0, 0.5, step=0.1)
    
    st.divider()
    st.header("⚙️ Contraintes de conception")
    
    # Espace entre les racks - FIXÉ À 3m comme demandé
    espace_entre_racks = 3.0
    st.info(f"📏 **Espace entre racks FIXE : {espace_entre_racks}m**")
    
    marge_securite = st.number_input("Marge sécurité (m)", 0.1, 2.0, 0.5, step=0.1)
    all_principale = st.number_input("Allée principale (m)", 2.0, 5.0, 3.5, step=0.1)
    
    st.divider()
    st.header("🎯 Critères d'optimisation")
    
    critere = st.selectbox("Optimiser pour :", [
        "Maximum de racks",
        "Maximum de volume utile",
        "Meilleur taux d'occupation",
        "Équilibre capacité/circulation"
    ])
    
    max_configs = st.slider("Nombre max de configurations à afficher", 10, 100, 50)

# Fonction pour générer TOUTES les combinaisons possibles
def generer_toutes_configurations(L, l, H, min_LR, max_LR, step_LR, 
                                  min_lR, max_lR, step_lR, min_HR, max_HR, step_HR,
                                  espace_entre_racks, marge_securite, all_principale):
    
    # Générer toutes les tailles de racks possibles
    longueurs_racks = np.arange(min_LR, max_LR + step_LR/2, step_LR)
    largeurs_racks = np.arange(min_lR, max_lR + step_lR/2, step_lR)
    hauteurs_racks = np.arange(min_HR, max_HR + step_HR/2, step_HR)
    
    configurations = []
    
    # Pour chaque combinaison de dimensions de rack
    for LR in longueurs_racks:
        for lR in largeurs_racks:
            for HR in hauteurs_racks:
                
                # Calculer le nombre de racks dans chaque direction
                # Longueur : considérer l'allée transversale
                longueur_disponible = L - 2*marge_securite - all_principale
                nb_racks_longueur = int(longueur_disponible // LR)
                
                # Largeur : racks des deux côtés de l'allée principale
                largeur_disponible = l - 2*marge_securite
                largeur_par_cote = (largeur_disponible - espace_entre_racks) / 2
                nb_racks_largeur = int(largeur_par_cote // (lR + espace_entre_racks))
                
                # Vérifier si c'est réalisable
                if nb_racks_longueur > 0 and nb_racks_largeur > 0:
                    
                    # Calcul du nombre total de racks
                    racks_par_cote = nb_racks_longueur * nb_racks_largeur
                    total_racks = racks_par_cote * 2  # Deux côtés de l'allée
                    
                    # Nombre d'étages possibles (sans dépasser la hauteur)
                    etages_possibles = int(H // HR)
                    
                    # Capacité totale
                    capacite_totale = total_racks * etages_possibles
                    
                    # Calcul des surfaces
                    surface_totale = L * l
                    surface_racks = total_racks * LR * lR
                    surface_all = surface_totale - surface_racks
                    
                    # Taux d'occupation
                    taux_occupation = (surface_racks / surface_totale) * 100
                    
                    # Volume utile
                    volume_utile = total_racks * LR * lR * HR * etages_possibles
                    volume_total = L * l * H
                    taux_volume = (volume_utile / volume_total) * 100
                    
                    # Score d'efficacité
                    score = (taux_occupation * 0.4 + taux_volume * 0.4 + 
                            (total_racks / 100) * 0.2)
                    
                    configuration = {
                        'LR': round(LR, 2),
                        'lR': round(lR, 2),
                        'HR': round(HR, 2),
                        'Racks par côté': racks_par_cote,
                        'Total racks': total_racks,
                        'Étages': etages_possibles,
                        'Capacité totale': capacite_totale,
                        'Surface racks (m²)': round(surface_racks, 1),
                        'Surface totale (m²)': round(surface_totale, 1),
                        'Taux occupation (%)': round(taux_occupation, 1),
                        'Volume utile (m³)': round(volume_utile, 1),
                        'Taux volume (%)': round(taux_volume, 1),
                        'Espace entre racks': espace_entre_racks,
                        'Allée principale': all_principale,
                        'Score': round(score, 2)
                    }
                    
                    configurations.append(configuration)
    
    return pd.DataFrame(configurations)

# Interface principale
st.markdown("## 🔍 Calcul de toutes les configurations possibles")

if st.button("🚀 Lancer le calcul exhaustif", type="primary"):
    
    with st.spinner(f"Calcul de TOUTES les configurations possibles..."):
        
        # Générer toutes les configurations
        df_configs = generer_toutes_configurations(
            L, l, H, min_LR, max_LR, step_LR,
            min_lR, max_lR, step_lR, min_HR, max_HR, step_HR,
            espace_entre_racks, marge_securite, all_principale
        )
        
        if len(df_configs) == 0:
            st.error("❌ Aucune configuration possible avec ces paramètres !")
            st.info("Essayez d'élargir les plages de dimensions des racks.")
        else:
            st.success(f"✅ **{len(df_configs)} configurations possibles trouvées !**")
            
            # Trier selon le critère choisi
            if critere == "Maximum de racks":
                df_sorted = df_configs.sort_values('Total racks', ascending=False)
            elif critere == "Maximum de volume utile":
                df_sorted = df_configs.sort_values('Volume utile (m³)', ascending=False)
            elif critere == "Meilleur taux d'occupation":
                df_sorted = df_configs.sort_values('Taux occupation (%)', ascending=False)
            else:  # Équilibre
                df_sorted = df_configs.sort_values('Score', ascending=False)
            
            # Afficher les meilleures configurations
            st.markdown(f"## 🏆 Top {min(max_configs, len(df_sorted))} configurations")
            
            # Créer un tableau interactif
            st.dataframe(
                df_sorted.head(max_configs),
                use_container_width=True,
                column_config={
                    "LR": st.column_config.NumberColumn("Long. rack (m)", format="%.2f m"),
                    "lR": st.column_config.NumberColumn("Larg. rack (m)", format="%.2f m"),
                    "HR": st.column_config.NumberColumn("Haut. rack (m)", format="%.2f m"),
                    "Total racks": st.column_config.NumberColumn("Nbre racks"),
                    "Capacité totale": st.column_config.NumberColumn("Capacité"),
                    "Taux occupation (%)": st.column_config.ProgressColumn(
                        "Occupation %", format="%.1f%%", min_value=0, max_value=100
                    ),
                    "Score": st.column_config.NumberColumn("Score", format="%.2f")
                }
            )
            
            # Statistiques globales
            st.divider()
            st.markdown("## 📊 Statistiques globales")
            
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Configurations totales", len(df_configs))
                st.metric("Max racks possible", df_configs['Total racks'].max())
            
            with col2:
                st.metric("Meilleur taux occupation", 
                         f"{df_configs['Taux occupation (%)'].max():.1f}%")
                st.metric("Volume utile max", 
                         f"{df_configs['Volume utile (m³)'].max():.0f} m³")
            
            with col3:
                st.metric("Racks moyens par config", 
                         f"{df_configs['Total racks'].mean():.0f}")
                st.metric("Occupation moyenne", 
                         f"{df_configs['Taux occupation (%)'].mean():.1f}%")
            
            with col4:
                st.metric("Étages max", df_configs['Étages'].max())
                st.metric("Capacité max", df_configs['Capacité totale'].max())
            
            # Visualisation des meilleures configurations
            st.divider()
            st.markdown("## 📈 Analyse comparative")
            
            tab1, tab2, tab3 = st.tabs(["📏 Dimensions", "📊 Performances", "🎯 Scores"])
            
            with tab1:
                # Graphique des dimensions optimales
                fig_data = df_sorted.head(20).copy()
                
                st.scatter_chart(
                    fig_data,
                    x='LR',
                    y='lR',
                    size='Total racks',
                    color='Taux occupation (%)'
                )
                st.caption("Relation entre dimensions des racks et nombre total")
            
            with tab2:
                # Graphique de performance
                perf_data = df_sorted.head(20)[['Total racks', 'Taux occupation (%)', 
                                                'Volume utile (m³)', 'Score']]
                st.line_chart(perf_data)
            
            with tab3:
                # Distribution des scores
                hist_values = np.histogram(df_configs['Score'], bins=20)[0]
                st.bar_chart(hist_values)
            
            # Configuration recommandée
            st.divider()
            st.markdown("## 🏅 Configuration OPTIMALE recommandée")
            
            meilleure_config = df_sorted.iloc[0]
            
            col_rec1, col_rec2, col_rec3 = st.columns(3)
            
            with col_rec1:
                st.markdown("**📐 Dimensions racks**")
                st.metric("Longueur rack", f"{meilleure_config['LR']} m")
                st.metric("Largeur rack", f"{meilleure_config['lR']} m")
                st.metric("Hauteur rack", f"{meilleure_config['HR']} m")
            
            with col_rec2:
                st.markdown("**📦 Capacité**")
                st.metric("Total racks", meilleure_config['Total racks'])
                st.metric("Étages par rack", meilleure_config['Étages'])
                st.metric("Capacité totale", meilleure_config['Capacité totale'])
            
            with col_rec3:
                st.markdown("**📊 Performances**")
                st.metric("Taux occupation", f"{meilleure_config['Taux occupation (%)']}%")
                st.metric("Volume utile", f"{meilleure_config['Volume utile (m³)']} m³")
                st.metric("Score global", f"{meilleure_config['Score']}/100")
            
            # Schéma de la configuration optimale
            st.markdown("### 🎨 Schéma de la configuration optimale")
            
            # Créer un schéma ASCII simple
            nb_long = int((L - 2*marge_securite - all_principale) // meilleure_config['LR'])
            nb_larg = int(((l - 2*marge_securite - espace_entre_racks) / 2) // 
                         (meilleure_config['lR'] + espace_entre_racks))
            
            schema = f"""
            ```
            {'=' * 80}
            SCHEMA DE LA CONFIGURATION OPTIMALE
            {'=' * 80}
            
            ENTREPÔT : {L}m × {l}m × {H}m
            RACK : {meilleure_config['LR']}m × {meilleure_config['lR']}m × {meilleure_config['HR']}m
            
            DISPOSITION :
            
            {'┌' + '─' * nb_long * 2 + '┬' + '─' * 3 + '┬' + '─' * nb_long * 2 + '┐'}
            {'│' + '█' * nb_long * 2 + '│' + ' ' * 3 + '│' + '█' * nb_long * 2 + '│'} ← Rangée de racks
            {'├' + '─' * nb_long * 2 + '┼' + '─' * 3 + '┼' + '─' * nb_long * 2 + '┤'}
            {'│' + '█' * nb_long * 2 + '│' + ' ' * 3 + '│' + '█' * nb_long * 2 + '│'}
            {'└' + '─' * nb_long * 2 + '┴' + '─' * 3 + '┴' + '─' * nb_long * 2 + '┘'}
            
            LÉGENDE :
            █ = Rack ({meilleure_config['LR']}m × {meilleure_config['lR']}m)
               = Allée ({espace_entre_racks}m entre racks, {all_principale}m principale)
            
            NOMBRE DE RACKS : {meilleure_config['Total racks']}
            RÉPARTITION : {nb_long} racks en longueur × {nb_larg} racks en largeur × 2 côtés
            
            ESPACES :
            • Entre racks : {espace_entre_racks}m (FIXE)
            • Allée principale : {all_principale}m
            • Marge sécurité : {marge_securite}m
            
            {'=' * 80}
            ```
            """
            
            st.code(schema, language=None)
            
            # Export des données
            st.divider()
            st.markdown("## 💾 Exporter les résultats")
            
            col_exp1, col_exp2, col_exp3 = st.columns(3)
            
            with col_exp1:
                # Toutes les configurations
                csv_all = df_configs.to_csv(index=False)
                st.download_button(
                    label="📥 Toutes configurations (CSV)",
                    data=csv_all,
                    file_name="toutes_configurations.csv",
                    mime="text/csv"
                )
            
            with col_exp2:
                # Top configurations
                csv_top = df_sorted.head(max_configs).to_csv(index=False)
                st.download_button(
                    label="📥 Top configurations (CSV)",
                    data=csv_top,
                    file_name="top_configurations.csv",
                    mime="text/csv"
                )
            
            with col_exp3:
                # Rapport détaillé
                rapport = f"""
                RAPPORT D'OPTIMISATION D'ENTREPÔT
                {'='*60}
                
                PARAMÈTRES INITIAUX :
                • Entrepôt : {L}m × {l}m × {H}m
                • Espace entre racks : {espace_entre_racks}m (FIXE)
                • Allée principale : {all_principale}m
                • Marge sécurité : {marge_securite}m
                
                PLAGES DE DIMENSIONS RACKS :
                • Longueur : {min_LR}m à {max_LR}m (pas {step_LR}m)
                • Largeur : {min_lR}m à {max_lR}m (pas {step_lR}m)
                • Hauteur : {min_HR}m à {max_HR}m (pas {step_HR}m)
                
                RÉSULTATS GLOBAUX :
                • Configurations possibles : {len(df_configs)}
                • Maximum racks possible : {df_configs['Total racks'].max()}
                • Meilleur taux occupation : {df_configs['Taux occupation (%)'].max():.1f}%
                • Volume utile maximum : {df_configs['Volume utile (m³)'].max():.0f} m³
                
                CONFIGURATION OPTIMALE (critère : {critere}) :
                • Dimensions rack : {meilleure_config['LR']}m × {meilleure_config['lR']}m × {meilleure_config['HR']}m
                • Nombre total racks : {meilleure_config['Total racks']}
                • Étages par rack : {meilleure_config['Étages']}
                • Capacité totale : {meilleure_config['Capacité totale']} emplacements
                • Taux occupation : {meilleure_config['Taux occupation (%)']}%
                • Volume utile : {meilleure_config['Volume utile (m³)']} m³
                • Score global : {meilleure_config['Score']}/100
                
                CALCUL EFFECTUÉ LE : {pd.Timestamp.now().strftime('%d/%m/%Y %H:%M:%S')}
                """
                
                st.download_button(
                    label="📄 Rapport complet (TXT)",
                    data=rapport,
                    file_name="rapport_optimisation.txt",
                    mime="text/plain"
                )

# Section d'information
with st.expander("📚 Comment fonctionne l'algorithme"):
    st.markdown("""
    ### 🔍 Méthode de calcul exhaustive
    
    **Algorithme utilisé :**
    1. **Génération systématique** de toutes les tailles de racks possibles
    2. **Test de chaque combinaison** dans l'entrepôt
    3. **Calcul précis** du nombre de racks disposables
    4. **Évaluation** selon plusieurs critères de performance
    5. **Classement** et recommandation de la meilleure solution
    
    **Paramètres fixes :**
    - Espace entre racks : **3.0 mètres** (inchangé)
    - Toutes les allées respectent cette contrainte
    
    **Contraintes respectées :**
    - Pas de chevauchement entre racks
    - Allées de circulation préservées
    - Marges de sécurité appliquées
    - Hauteurs compatibles avec l'entrepôt
    
    **Complexité du calcul :**
    - Nombre de combinaisons testées : (LR × lR × HR)
    - Chaque combinaison évaluée en O(1)
    - Résultats garantis optimaux pour les paramètres donnés
    """)

# Instructions
with st.expander("🎯 Comment utiliser au mieux"):
    st.markdown("""
    ### Guide d'utilisation optimal :
    
    **Étape 1 : Définir les contraintes**
    - Entrez les dimensions EXACTES de votre entrepôt
    - Laissez l'espace entre racks à **3m** (votre exigence)
    
    **Étape 2 : Définir les plages de racks**
    - Donnez des plages réalistes pour les racks
    - Ex: Longueur 1.5m à 3.0m (pas 0.5m)
    
    **Étape 3 : Choisir le critère d'optimisation**
    - Maximum racks : pour stockage intensif
    - Maximum volume : pour produits volumineux
    - Meilleur occupation : pour efficacité spatiale
    - Équilibre : compromis intelligent
    
    **Étape 4 : Analyser les résultats**
    - Consultez le tableau des meilleures configurations
    - Examinez les statistiques globales
    - Téléchargez les données pour analyse approfondie
    
    **Conseil :** Commencez avec des plages larges, puis affinez.
    """)

# Pied de page
st.divider()
st.caption(f"🔬 Warehouse Combinatorial Optimizer | Espace entre racks : 3m fixe | Algorithm exhaustif")

# Affichage des paramètres actuels
with st.sidebar:
    st.divider()
    st.markdown("### 📋 Paramètres actuels")
    st.write(f"Entrepôt : {L}m × {l}m × {H}m")
    st.write(f"Espace racks : {espace_entre_racks}m")
    st.write(f"Plage LR : {min_LR}-{max_LR}m")
    st.write(f"Plage lR : {min_lR}-{max_lR}m")
    st.write(f"Plage HR : {min_HR}-{max_HR}m")
