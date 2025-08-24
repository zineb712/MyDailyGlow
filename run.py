from flask import Flask, render_template, request, redirect, url_for, send_from_directory, g
import sqlite3
from datetime import date
import random
import io
import base64
import matplotlib
matplotlib.use("Agg")  # Backend non interactif pour Flask
import matplotlib.pyplot as plt

app = Flask(__name__)
DATABASE = 'database/mydailyglow.db'

# --- Connexion SQLite ---
def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
        db.row_factory = sqlite3.Row
    return db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

# --- Fonctions utilitaires ---
def get_routines():
    db = get_db()
    routines = {}
    cursor = db.execute("SELECT * FROM routines")
    for row in cursor.fetchall():
        routines.setdefault(row['periode'], []).append(row['etape'])
    return routines

def add_routine(periode, etape):
    db = get_db()
    db.execute("INSERT INTO routines (periode, etape) VALUES (?, ?)", (periode, etape))
    db.commit()

def get_historique():
    db = get_db()
    historique = {}
    cursor = db.execute("SELECT * FROM historique")
    for row in cursor.fetchall():
        historique.setdefault(row['date'], {}).setdefault(row['periode'], []).append(row['etape'])
    return historique

def add_historique(date_jour, periode, etape):
    db = get_db()
    db.execute("INSERT INTO historique (date, periode, etape) VALUES (?, ?, ?)", (date_jour, periode, etape))
    db.commit()

def get_produits():
    db = get_db()
    cursor = db.execute("SELECT * FROM produits")
    return cursor.fetchall()

def add_produit(nom, type_prod, note):
    db = get_db()
    db.execute("INSERT INTO produits (nom, type, note) VALUES (?, ?, ?)", (nom, type_prod, note))
    db.commit()

def delete_produit(produit_id):
    db = get_db()
    db.execute("DELETE FROM produits WHERE id = ?", (produit_id,))
    db.commit()

# --- Données locales pour affichage ---
conseils = [
    "Hydrate ta peau matin et soir 💧",
    "N'oublie pas le sérum pour un teint lumineux ✨",
    "Fais un masque visage cette semaine 🌸",
    "Bois beaucoup d'eau pour une peau radieuse 💦",
    "Prends 5 minutes pour te relaxer 😌",
    "Applique toujours ta crème du bas vers le haut pour lifter ta peau 💆‍♀️",
    "N’oublie pas tes lèvres : baume hydratant avant de dormir 💋",
    "Masse doucement ton visage 5 minutes par jour ✨",
    "Change ta taie d’oreiller chaque semaine pour une peau nette 🛏️"
]

citations = [
    "Sois toi-même, tout le monde est déjà pris 💕",
    "La beauté commence au moment où tu décides d'être toi-même ✨",
    "Un sourire est le meilleur maquillage 💖",
    "La beauté commence au moment où tu décides d’être toi-même. – Coco Chanel",
    "Souris, et le monde sourira avec toi 🌸",
    "Crois en ta magie ✨",
    "Chaque jour est une nouvelle chance de briller 💖"
]

defis = [
    "Prends 5 min pour méditer 😌",
    "Essaie un nouveau maquillage rose 💖",
    "Fais une pause cocooning 🌸",
    "Bois 2 grands verres d’eau avant 12h 💦",
    "Marche 15 minutes en écoutant ta playlist préférée 🎶",
    "Écris 3 choses positives qui te sont arrivées 🌸",
    "Fais 20 squats devant ton miroir 💪"
]

# --- ROUTES ---
@app.route('/')
@app.route('/home')
def home():
    photos = ["image1.jpg", "image2.jpg"]
    accueil_paragraphe = "Ici, chaque jour est une nouvelle opportunité pour prendre soin de toi 🌸.  Suis tes routines beauté, découvre des conseils personnalisés et observe tes progrès semaine après semaine 💕. Parce que ton bien-être est précieux, prends quelques minutes chaque jour pour te chouchouter.  Ensemble, faisons de ta routine un moment de douceur et de confiance en toi 💖."
    return render_template('index.html', photos=photos, accueil_paragraphe=accueil_paragraphe)

@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    routines = get_routines()
    historique = get_historique()
    today = str(date.today())
    historique.setdefault(today, {"matin": [], "soir": []})

    if request.method == 'POST':
        checked = request.form.getlist('routine')
        for periode, etapes in routines.items():
            historique[today][periode] = [etape for etape in etapes if etape in checked]

        nouvelle_activite = request.form.get('nouvelle_activite')
        periode_activite = request.form.get('periode_activite')
        if nouvelle_activite and periode_activite in ["matin", "soir"]:
            add_routine(periode_activite, nouvelle_activite)
            add_historique(today, periode_activite, nouvelle_activite)
        return redirect(url_for('dashboard'))

    done_today = []
    for periode_etapes in historique.get(today, {}).values():
        done_today.extend(periode_etapes)

    total = sum(len(etapes) for etapes in routines.values())
    done_count = sum(len(v) for v in historique.get(today, {}).values())
    pourcentage = int((done_count / total) * 100) if total > 0 else 0

    fig, ax = plt.subplots()
    ax.bar(["Routines faites"], [pourcentage], color="#ff66b2")
    ax.set_ylim(0, 100)
    ax.set_ylabel("%")
    ax.set_title("🌸 Progression du jour 🌸")

    buf = io.BytesIO()
    plt.savefig(buf, format="png")
    plt.close(fig)
    buf.seek(0)
    image_base64 = base64.b64encode(buf.getvalue()).decode("utf-8")
    buf.close()

    return render_template(
        'dashboard.html',
        routines=routines,
        done_today=done_today,
        conseil_du_jour=random.choice(conseils),
        citation_du_jour=random.choice(citations),
        defi_du_jour=random.choice(defis),
        image_base64=image_base64
    )

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/manage', methods=['GET', 'POST'])
def manage_routines():
    routines = get_routines()
    if request.method == 'POST':
        action = request.form.get('action')
        periode = request.form.get('periode')
        etape = request.form.get('etape')
        if action == 'Ajouter' and etape:
            add_routine(periode, etape)
        elif action == 'Supprimer' and etape:
            db = get_db()
            db.execute("DELETE FROM routines WHERE periode = ? AND etape = ?", (periode, etape))
            db.commit()
        return redirect(url_for('manage_routines'))
    return render_template('manage.html', routines=routines)

@app.route('/history')
def history():
    historique = get_historique()
    return render_template('history.html', historique=historique)

@app.route('/products', methods=['GET', 'POST'])
def products_page():
    produits = get_produits()
    if request.method == 'POST':
        action = request.form.get("action")
        if action == "delete":
            produit_id = request.form.get("produit_id")
            if produit_id:
                delete_produit(produit_id)
        else:
            nom = request.form.get('nom')
            type_prod = request.form.get('type')
            note = request.form.get('note')
            if nom and type_prod and note:
                add_produit(nom, type_prod, note)
        return redirect(url_for('products_page'))
    return render_template('products.html', produits=produits)

@app.route('/images/<filename>')
def custom_images(filename):
    return send_from_directory('images', filename)

@app.route('/stats')
def stats():
    routines = get_routines()
    historique = get_historique()
    jours = list(historique.keys())
    total_routines_semaine = routines_faites_semaine = masques_visage = 0

    for jour in jours:
        for periode, etapes in routines.items():
            total_routines_semaine += len(etapes)
            routines_faites_semaine += len(historique.get(jour, {}).get(periode, []))
        for periode, etapes_faites in historique.get(jour, {}).items():
            for etape in etapes_faites:
                if "masque" in etape.lower():
                    masques_visage += 1

    pourcentage = int((routines_faites_semaine / total_routines_semaine) * 100) if total_routines_semaine else 0

    fig, ax = plt.subplots(figsize=(6,4))
    ax.bar(["Routines faites"], [pourcentage], color="#ff66b2")
    ax.set_ylim(0, 100)
    ax.set_ylabel("%")
    ax.set_title("🌸 Progression de la semaine 🌸")

    buf = io.BytesIO()
    plt.savefig(buf, format="png", bbox_inches="tight")
    plt.close(fig)
    buf.seek(0)
    image_base64 = base64.b64encode(buf.getvalue()).decode("utf-8")
    buf.close()

    return render_template("stats.html",
                           pourcentage=pourcentage,
                           masques_visage=masques_visage,
                           image_base64=image_base64)

if __name__ == "__main__":
    app.run(debug=True)

