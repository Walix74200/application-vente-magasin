from flask import Flask, render_template, request, redirect, url_for
import mysql.connector
from flask import session
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'super_secret_key'  # Clé pour la gestion des sessions

# Configuration de la connexion à la base de données
config = {
    'user': '379021',  # Remplace par ton utilisateur MySQL
    'password': '8bNiRRdY23HC*3E',  # Remplace par ton mot de passe MySQL
    'host': 'mysql-bonsergent.alwaysdata.net',  # Hôte de ta base de données
    'database': 'bonsergent_projet_pomm-d-api',  # Remplace par le nom de ta base de données
    'port': '3306'  # Port par défaut de MySQL
}

# Route principale avec les 4 boutons de catégories
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/continuer-achats')
def continuer_achats():
    return redirect('/')

# Route pour ajouter un produit au panier
@app.route('/ajouter-au-panier/<int:variete_id>', methods=['POST'])
def ajouter_au_panier(variete_id):
    quantite = int(request.form['quantite'])
    prix_unitaire = float(request.form['prix_unitaire'])

    # Connexion à la base de données pour récupérer le nom de la variété
    try:
        connection = mysql.connector.connect(**config)
        cursor = connection.cursor()
        cursor.execute("SELECT nom FROM Varietes WHERE id = %s", (variete_id,))
        variete_nom = cursor.fetchone()[0]  # Récupère le nom de la variété
        cursor.close()
        connection.close()
    except mysql.connector.Error as err:
        return f"Erreur : {err}"

    # Vérifie si le panier existe déjà, sinon crée-le
    if 'panier' not in session:
        session['panier'] = []

    # Cherche si le produit existe déjà dans le panier
    produit_existe = False
    for item in session['panier']:
        if item['variete_id'] == variete_id:
            # Si le produit existe déjà, mets à jour la quantité
            item['quantite'] += quantite
            produit_existe = True
            break

    # Si le produit n'existe pas encore, l'ajoute avec son nom
    if not produit_existe:
        session['panier'].append({
            'variete_id': variete_id,
            'variete_nom': variete_nom,  # On ajoute aussi le nom du produit ici
            'quantite': quantite,
            'prix_unitaire': prix_unitaire
        })

    session.modified = True  # Assure que la session est mise à jour

    return redirect(url_for('afficher_panier'))

# Route pour afficher le panier
@app.route('/panier')
def afficher_panier():
    # Récupère le panier de la session, ou un panier vide s'il n'existe pas encore
    panier = session.get('panier', [])
    total = sum(item['quantite'] * item['prix_unitaire'] for item in panier)
    return render_template('panier.html', panier=panier, total=total)

# Route pour finaliser la commande
@app.route('/finaliser-commande')
def finaliser_commande():
    # Traite la commande et enregistre-la dans la base de données
    session.pop('panier', None)  # Vide le panier après la commande
    return redirect('/')

# Route pour la catégorie Pommes
@app.route('/pommes')
def pommes():
    try:
        connection = mysql.connector.connect(**config)
        cursor = connection.cursor()
        cursor.execute("SELECT id, nom FROM Varietes WHERE produit_id = (SELECT id FROM Produits WHERE nom = 'Pommes')")
        varietes = cursor.fetchall()
        cursor.close()
        connection.close()
    except mysql.connector.Error as err:
        return f"Erreur : {err}"
    
    return render_template('categories.html', titre="Pommes", varietes=varietes)

# Route pour la catégorie Poires
@app.route('/poires')
def poires():
    try:
        connection = mysql.connector.connect(**config)
        cursor = connection.cursor()
        cursor.execute("SELECT id, nom FROM Varietes WHERE produit_id = (SELECT id FROM Produits WHERE nom = 'Poires')")
        varietes = cursor.fetchall()
        cursor.close()
        connection.close()
    except mysql.connector.Error as err:
        return f"Erreur : {err}"
    
    return render_template('categories.html', titre="Poires", varietes=varietes)

# Route pour la catégorie Jus
@app.route('/jus')
def jus():
    try:
        connection = mysql.connector.connect(**config)
        cursor = connection.cursor()
        cursor.execute("SELECT id, nom FROM Varietes WHERE produit_id = (SELECT id FROM Produits WHERE nom = 'Jus de pommes')")
        varietes = cursor.fetchall()
        cursor.close()
        connection.close()
    except mysql.connector.Error as err:
        return f"Erreur : {err}"
    
    return render_template('categories.html', titre="Jus", varietes=varietes)

# Route pour la catégorie Autres produits
@app.route('/autres')
def autres():
    try:
        connection = mysql.connector.connect(**config)
        cursor = connection.cursor()
        cursor.execute("SELECT id, nom FROM Varietes WHERE produit_id = (SELECT id FROM Produits WHERE nom = 'Autres produits')")
        varietes = cursor.fetchall()
        cursor.close()
        connection.close()
    except mysql.connector.Error as err:
        return f"Erreur : {err}"
    
    return render_template('categories.html', titre="Autres produits", varietes=varietes)

# Route pour la création d'une nouvelle commande
@app.route('/nouvelle-commande')
def nouvelle_commande():
    return redirect('/')

@app.route('/historique-commandes')
def historique_commandes():
    try:
        # Connexion à la base de données
        connection = mysql.connector.connect(**config)
        cursor = connection.cursor()

        # Requête pour récupérer les commandes de la journée
        cursor.execute("""
            SELECT c.id, c.date, GROUP_CONCAT(v.nom, ' (', cp.quantite, 'kg)') AS produits, SUM(cp.quantite * cp.prix_unitaire) AS total
            FROM Commandes c
            JOIN Commande_Produits cp ON c.id = cp.commande_id
            JOIN Varietes v ON cp.variete_id = v.id
            WHERE DATE(c.date) = CURDATE()
            GROUP BY c.id, c.date
            ORDER BY c.date DESC
        """)

        commandes = cursor.fetchall()
        cursor.close()
        connection.close()

    except mysql.connector.Error as err:
        return f"Erreur : {err}"

    if not commandes:
        return "<h2>Aucune commande pour aujourd'hui.</h2>"

    return render_template('historique.html', commandes=commandes)

@app.route('/ajouter_commande', methods=['POST'])
def ajouter_commande():
    try:
        # Connexion à la base de données
        connection = mysql.connector.connect(**config)
        cursor = connection.cursor()

        # Insérer une nouvelle commande avec la date actuelle
        insert_commande_query = """
        INSERT INTO Commandes (date, prix_total)
        VALUES (NOW(), %s)
        """
        total_prix = sum(item['quantite'] * item['prix_unitaire'] for item in session['panier'])
        cursor.execute(insert_commande_query, (total_prix,))

        # Récupérer l'ID de la commande nouvellement créée
        commande_id = cursor.lastrowid

        # Insérer les produits dans Commande_Produits
        insert_produits_query = """
        INSERT INTO Commande_Produits (commande_id, variete_id, quantite, prix_unitaire)
        VALUES (%s, %s, %s, %s)
        """
        for item in session['panier']:
            cursor.execute(insert_produits_query, (commande_id, item['variete_id'], item['quantite'], item['prix_unitaire']))

        # Commit pour sauvegarder les changements
        connection.commit()

        # Vider le panier après l'ajout de la commande
        session.pop('panier', None)

        cursor.close()
        connection.close()

        return redirect(url_for('historique_commandes'))

    except mysql.connector.Error as err:
        return f"Erreur : {err}"

if __name__ == '__main__':
    app.run(debug=True)