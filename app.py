import matplotlib
matplotlib.use('Agg')  # Pour éviter les problèmes avec Flask
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np
from io import BytesIO
import base64
from flask import Flask, render_template_string, request, send_file

app = Flask(__name__)

HTML_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>Générateur de Configuration d'Entrepôt</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 30px; background: #f5f5f5; }
        .container { max-width: 1200px; margin: auto; background: white; padding: 20px; border-radius: 10px; }
        h1 { color: #333; text-align: center; }
        .config-form { display: grid; grid-template-columns: 1fr 1fr; gap: 15px; margin: 20px 0; }
        .form-group { display: flex; flex-direction: column; }
        label { font-weight: bold; margin-bottom: 5px; }
        input, select { padding: 8px; border: 1px solid #ddd; border-radius: 4px; }
        button { grid-column: span 2; padding: 12px; background: #4CAF50; color: white; 
                 border: none; border-radius: 5px; font-size: 16px; cursor: pointer; }
        button:hover { background: #45a049; }
        .image-container { text-align: center; margin-top: 30px; }
        img { max-width: 100%; border: 1px solid #ddd; border-radius: 5px; }
        .download-btn { display: inline-block; margin-top: 10px; padding: 10px 20px; 
                        background: #2196F3; color: white; text-decoration: none; border-radius: 5px; }
        .download-btn:hover { background: #0b7dda; }
        .info-box { background: #e8f4fd; padding: 15px; border-radius: 5px; margin: 15px 0; }
    </style>
</head>
<body>
    <div class="container">
        <h1>📦 Générateur de Configuration d'Entrepôt</h1>
        
        <div class="info-box">
            <strong>Instructions :</strong> Ajustez les paramètres ci-dessous, puis cliquez sur "Générer le schéma".
        </div>
        
        <form method="POST" class="config-form">
            <div class="form-group">
                <label>Largeur totale de l'entrepôt (m) :</label>
                <input type="number" name="largeur_entrepot" value="{{ largeur_entrepot }}" step="1" min="10" max="200" required>
            </div>
            
            <div class="form-group">
                <label>Longueur totale de l'entrepôt (m) :</label>
                <input type="number" name="longueur_entrepot" value="{{ longueur_entrepot }}" step="1" min="10" max="200" required>
            </div>
            
            <div class="form-group">
                <label>Largeur d'un rack (m) :</label>
                <input type="number" name="largeur_rack" value="{{ largeur_rack }}" step="0.5" min="0.5" max="5" required>
            </div>
            
            <div class="form-group">
                <label>Longueur d'un rack (m) :</label>
                <input type="number" name="longueur_rack" value="{{ longueur_rack }}" step="0.5" min="1" max="15" required>
            </div>
            
            <div class="form-group">
                <label>Hauteur des racks (m) :</label>
                <input type="number" name="hauteur_rack" value="{{ hauteur_rack }}" step="0.5" min="2" max="20" required>
            </div>
            
            <div class="form-group">
                <label>Nombre de rangées :</label>
                <input type="number" name="nb_rangees" value="{{ nb_rangees }}" step="1" min="1" max="20" required>
            </div>
            
            <div class="form-group">
                <label>Largeur des allées (m) :</label>
                <input type="number" name="largeur_allee" value="{{ largeur_allee }}" step="0.5" min="2" max="15" required>
            </div>
            
            <div class="form-group">
                <label>Type de configuration :</label>
                <select name="config_type">
                    <option value="simple" {{ 'selected' if config_type=='simple' else '' }}>Simple (2 rangées)</option>
                    <option value="double" {{ 'selected' if config_type=='double' else '' }}>Double (4 rangées)</option>
                    <option value="compact" {{ 'selected' if config_type=='compact' else '' }}>Compact (maximiser espace)</option>
                </select>
            </div>
            
            <button type="submit">🏭 Générer le schéma</button>
        </form>
        
        {% if image_data %}
        <div class="image-container">
            <h2>📐 Schéma généré</h2>
            <img src="data:image/png;base64,{{ image_data }}" alt="Schéma d'entrepôt">
            <br>
            <a href="/download" class="download-btn">📥 Télécharger l'image (PNG)</a>
            <a href="/download_svg" class="download-btn">📐 Télécharger en SVG (modifiable)</a>
        </div>
        
        <div class="info-box">
            <h3>📋 Spécifications générées :</h3>
            <p>• Surface totale : {{ largeur_entrepot }}m x {{ longueur_entrepot }}m</p>
            <p>• Nombre total de racks : {{ nb_racks_total }}</p>
            <p>• Surface de stockage estimée : {{ surface_stockage }} m²</p>
            <p>• Largeur allée : {{ largeur_allee }}m ({{ "✓ Conforme chariot élévateur" if largeur_allee >= 3 else "⚠ Allée étroite" }})</p>
            <p>• Hauteur maximale : {{ hauteur_rack }}m ({{ "✓ Standard" if hauteur_rack <= 12 else "⚠ Nécessite équipement spécial" }})</p>
        </div>
        {% endif %}
        
        <div style="margin-top: 30px; padding-top: 20px; border-top: 1px solid #ddd; color: #666;">
            <p><strong>Conseil pour une image réaliste :</strong> Copiez ce prompt dans un générateur d'images IA (DALL·E, Midjourney) :</p>
            <code style="background: #eee; padding: 10px; display: block; border-radius: 5px; margin-top: 10px;">
            "Photorealistic warehouse storage layout with {{ nb_racks_total }} metal racks, {{ hauteur_rack }}m height, 
            {{ largeur_rack }}m x {{ longueur_rack }}m rack size, {{ largeur_allee }}m wide aisles, 
            pallet storage system, forklift in operation, dimension markers visible on floor, 
            professional lighting, wide-angle view, technical drawing overlay"
            </code>
        </div>
    </div>
</body>
</html>
'''

def generate_warehouse_schema(largeur_entrepot=50, longueur_entrepot=30, 
                             largeur_rack=2, longueur_rack=5, 
                             hauteur_rack=4, nb_rangees=4, 
                             largeur_allee=4, config_type='simple'):
    """Génère un schéma d'entrepôt 2D avec mesures"""
    fig, ax = plt.subplots(figsize=(14, 10))
    
    # Fond de l'entrepôt
    ax.add_patch(patches.Rectangle((0, 0), largeur_entrepot, longueur_entrepot,
                                   linewidth=3, edgecolor='#2c3e50', facecolor='#ecf0f1', 
                                   alpha=0.3, label='Limites entrepôt'))
    
    # Calcul de la configuration
    nb_racks_total = 0
    
    if config_type == 'simple':
        # Configuration simple : 2 rangées de chaque côté de l'allée
        rack_positions = []
        for r in range(nb_rangees):
            # Racks gauche
            for c in range(2):
                x = 2 + c * (largeur_rack + 1)
                y = 2 + r * (longueur_rack + 2)
                rack_positions.append((x, y))
                nb_racks_total += 1
            
            # Racks droite
            for c in range(2):
                x = 2 + 2*(largeur_rack + 1) + largeur_allee + c * (largeur_rack + 1)
                y = 2 + r * (longueur_rack + 2)
                rack_positions.append((x, y))
                nb_racks_total += 1
                
    elif config_type == 'double':
        # Configuration double : 4 rangées de chaque côté
        rack_positions = []
        for r in range(nb_rangees):
            for side in [0, 1]:  # Gauche et droite
                base_x = 2 if side == 0 else 2 + 4*(largeur_rack + 1) + largeur_allee
                for c in range(4):
                    x = base_x + c * (largeur_rack + 1)
                    y = 2 + r * (longueur_rack + 2)
                    rack_positions.append((x, y))
                    nb_racks_total += 1
                    
    else:  # compact
        # Configuration compacte : maximiser l'espace
        rack_positions = []
        max_racks_x = int((largeur_entrepot - largeur_allee - 4) / (largeur_rack + 1))
        racks_per_side = max_racks_x // 2
        
        for r in range(nb_rangees):
            for side in [0, 1]:
                base_x = 2 if side == 0 else 2 + racks_per_side*(largeur_rack + 1) + largeur_allee
                for c in range(racks_per_side):
                    x = base_x + c * (largeur_rack + 1)
                    y = 2 + r * (longueur_rack + 2)
                    rack_positions.append((x, y))
                    nb_racks_total += 1
    
    # Dessiner les racks
    for idx, (x, y) in enumerate(rack_positions):
        color = '#3498db' if idx % 2 == 0 else '#2980b9'
        ax.add_patch(patches.Rectangle((x, y), largeur_rack, longueur_rack,
                                       facecolor=color, edgecolor='#1a5276', 
                                       linewidth=1.5, alpha=0.8,
                                       label='Rack' if idx == 0 else ""))
        
        # Texte avec dimensions
        ax.text(x + largeur_rack/2, y + longueur_rack/2, 
                f'{largeur_rack}m\n×\n{longueur_rack}m',
                ha='center', va='center', fontsize=7, color='white', fontweight='bold')
        
        # Numéro du rack
        ax.text(x + largeur_rack/2, y - 0.5, f'R{idx+1:02d}',
                ha='center', va='center', fontsize=6, color='#2c3e50')
    
    # Allées
    ax.add_patch(patches.Rectangle((2 + nb_racks_total//(nb_rangees*2)*(largeur_rack+1), 0),
                                   largeur_allee, longueur_entrepot,
                                   facecolor='#bdc3c7', alpha=0.5, 
                                   edgecolor='#7f8c8d', linewidth=2,
                                   label='Allée de circulation'))
    
    # Portes
    door_width = 6
    ax.add_patch(patches.Rectangle((largeur_entrepot/2 - door_width/2, -0.5),
                                   door_width, 1,
                                   facecolor='#e74c3c', alpha=0.7,
                                   label='Entrée principale'))
    
    # Ajouter les mesures
    # Mesure de l'allée
    ax.annotate(f'{largeur_allee}m', 
                xy=(2 + nb_racks_total//(nb_rangees*2)*(largeur_rack+1) + largeur_allee/2, longueur_entrepot-2),
                xytext=(0, 0), textcoords='offset points',
                ha='center', va='center', fontsize=10, fontweight='bold',
                color='#c0392b',
                arrowprops=dict(arrowstyle='<->', color='#c0392b', lw=2))
    
    # Mesure totale
    ax.annotate(f'{largeur_entrepot}m', 
                xy=(largeur_entrepot/2, -3),
                xytext=(0, 0), textcoords='offset points',
                ha='center', va='center', fontsize=12, fontweight='bold',
                color='#2c3e50',
                arrowprops=dict(arrowstyle='<->', color='#2c3e50', lw=3))
    
    ax.annotate(f'{longueur_entrepot}m', 
                xy=(-3, longueur_entrepot/2),
                xytext=(0, 0), textcoords='offset points',
                ha='center', va='center', fontsize=12, fontweight='bold',
                color='#2c3e50', rotation=90,
                arrowprops=dict(arrowstyle='<->', color='#2c3e50', lw=3))
    
    # Configuration du graphique
    ax.set_xlim(-5, largeur_entrepot + 5)
    ax.set_ylim(-5, longueur_entrepot + 5)
    ax.set_aspect('equal')
    ax.set_xlabel('Largeur (mètres)', fontsize=12, fontweight='bold')
    ax.set_ylabel('Longueur (mètres)', fontsize=12, fontweight='bold')
    ax.set_title(f'Configuration d\'entrepôt - {nb_racks_total} racks', 
                fontsize=16, fontweight='bold', pad=20)
    
    # Légende
    handles, labels = ax.get_legend_handles_labels()
    unique_labels = []
    unique_handles = []
    for handle, label in zip(handles, labels):
        if label not in unique_labels:
            unique_labels.append(label)
            unique_handles.append(handle)
    ax.legend(unique_handles, unique_labels, loc='upper right', fontsize=10)
    
    ax.grid(True, linestyle='--', alpha=0.3, color='#7f8c8d')
    
    plt.tight_layout()
    
    # Convertir en base64 pour affichage HTML
    buffer = BytesIO()
    plt.savefig(buffer, format='png', dpi=150, bbox_inches='tight')
    buffer.seek(0)
    image_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
    plt.close()
    
    return image_base64, nb_racks_total

@app.route('/', methods=['GET', 'POST'])
def index():
    # Valeurs par défaut
    params = {
        'largeur_entrepot': 50,
        'longueur_entrepot': 30,
        'largeur_rack': 2,
        'longueur_rack': 5,
        'hauteur_rack': 4,
        'nb_rangees': 4,
        'largeur_allee': 4,
        'config_type': 'simple',
        'image_data': None,
        'nb_racks_total': 0,
        'surface_stockage': 0
    }
    
    if request.method == 'POST':
        # Récupérer les paramètres du formulaire
        for key in params:
            if key != 'image_data' and key != 'nb_racks_total' and key != 'surface_stockage':
                if key in ['largeur_entrepot', 'longueur_entrepot', 'nb_rangees']:
                    params[key] = int(request.form.get(key, params[key]))
                elif key == 'config_type':
                    params[key] = request.form.get(key, params[key])
                else:
                    params[key] = float(request.form.get(key, params[key]))
        
        # Générer l'image
        image_data, nb_racks_total = generate_warehouse_schema(
            largeur_entrepot=params['largeur_entrepot'],
            longueur_entrepot=params['longueur_entrepot'],
            largeur_rack=params['largeur_rack'],
            longueur_rack=params['longueur_rack'],
            hauteur_rack=params['hauteur_rack'],
            nb_rangees=params['nb_rangees'],
            largeur_allee=params['largeur_allee'],
            config_type=params['config_type']
        )
        
        params['image_data'] = image_data
        params['nb_racks_total'] = nb_racks_total
        params['surface_stockage'] = nb_racks_total * params['largeur_rack'] * params['longueur_rack']
    
    return render_template_string(HTML_TEMPLATE, **params)

@app.route('/download')
def download():
    # Régénérer l'image pour le téléchargement (simplifié)
    buffer = BytesIO()
    fig, ax = plt.subplots(figsize=(12, 8))
    ax.text(0.5, 0.5, "Schéma d'entrepôt - Export PNG\n(La même image que vue sur la page)",
            ha='center', va='center', transform=ax.transAxes, fontsize=14)
    ax.axis('off')
    plt.savefig(buffer, format='png', dpi=300)
    buffer.seek(0)
    plt.close()
    
    return send_file(buffer, mimetype='image/png', 
                     as_attachment=True, 
                     download_name='schema_entrepot.png')

@app.route('/download_svg')
def download_svg():
    # Créer un SVG simple
    buffer = BytesIO()
    fig, ax = plt.subplots(figsize=(12, 8))
    ax.text(0.5, 0.5, "Schéma d'entrepôt - Export SVG\n(Ouvrir avec Inkscape/AutoCAD)",
            ha='center', va='center', transform=ax.transAxes, fontsize=14)
    ax.axis('off')
    plt.savefig(buffer, format='svg')
    buffer.seek(0)
    plt.close()
    
    return send_file(buffer, mimetype='image/svg+xml', 
                     as_attachment=True, 
                     download_name='schema_entrepot.svg')

if __name__ == '__main__':
    print("🚀 Application démarrée !")
    print("🌐 Ouvrez votre navigateur et allez sur : http://localhost:5000")
    print("📦 Configurez votre entrepôt et générez le schéma !")
    app.run(debug=True, host='0.0.0.0', port=5000)
