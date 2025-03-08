from models import Offer
from flask_login import current_user

from flask import Flask, render_template, request, redirect, url_for, session, send_file
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import csv
import os

app = Flask(__name__)
app.secret_key = 'tajny_klic'

# Připojení k databázi
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data.db'
db = SQLAlchemy(app)
migrate = Migrate(app, db)

# Model pro partnera
class Partner(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    email = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    bank_account = db.Column(db.String(50), nullable=False)
    address = db.Column(db.String(200), nullable=False)
    password = db.Column(db.String(100), nullable=False)

# Model pro nabídku
class Offer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    model = db.Column(db.String(100), nullable=False)
    size = db.Column(db.String(20), nullable=False)
    price = db.Column(db.Float, nullable=False)
    partner_id = db.Column(db.Integer, db.ForeignKey('partner.id'), nullable=False)
    partner = db.relationship('Partner', backref='offers')
    partner = db.relationship('Partner', backref='offers')
    sold = db.Column(db.Boolean, default=False)
    paid = db.Column(db.Boolean, default=False)

# ✅ Seznam modelů a dostupných velikostí (vygenerováno z dat)
MODELS_SIZES = {'Nike Dunk low Pink Velvet GS': ['35.5', '36', '36.5', '37,5', '38', '38,5', '39', '40'], 'Jordan 1 Mid Obsidian Gold': ['40', '40,5', '41', '42', '42,5', '43', '44', '44,5', '45', '45,5', '46'], 'Jordan 1 High Taxi': ['35,5', '36', '36,5', '37,5', '38', '38,5', '39', '40', '40,5', '41', '42', '42,5', '43', '44', '44,5', '45', '45,5', '46', '47', '47,5', '48'], 'Jordan 4 Red Cement': ['35,5', '36', '36,5', '37,5', '38', '38,5', '39', '40', '40,5', '41', '42', '42,5', '43', '44', '44,5', '45', '45,5', '46', '47', '47,5', '48'], 'Jordan 1 Mid Taxi': ['35,5', '36', '36,5', '37,5', '38', '38,5', '39', '40', '40,5', '41', '42', '42,5', '43', '44', '44,5', '45', '45,5', '46', '47'], 'Nike Dunk low Cacao Wow': ['35,5', '36', '36,5', '37,5', '38', '38,5', '39', '40', '40,5', '41', '42', '42,5', '43', '44', '44,5'], 'Nike Dunk Low Black White "Panda"': ['35,5', '36', '36,5', '37,5', '38', '38,5', '39', '40', '40,5', '41', '42', '42,5', '43', '44', '44,5', '45', '45,5', '46', '47', '47,5', '48'], 'Jordan 1 Mid Barely Grape': ['35,5', '36', '36,5', '37,5', '38', '38,5', '39', '40'], 'Nike Dunk Low Court Purple': ['38,5', '39', '40', '40,5', '41', '42', '42,5', '43', '44', '44,5', '45', '45,5', '46', '47', '47,5', '48'], 'Jordan 1 High Lost and Found': ['36', '36,5', '37,5', '38', '38,5', '39', '40', '40,5', '41', '42', '42,5', '43', '44', '44,5', '45', '45,5', '46', '47'], 'Jordan 1 High UNC Toe': ['40', '40,5', '41', '42', '42,5', '43', '44', '44,5', '45', '45,5', '46', '47', '47,5', '48'], 'Nike Dunk Low Grey Fog': ['35,5', '36', '36,5', '37,5', '38', '38,5', '39', '40', '40,5', '41', '42', '42,5', '43', '44', '44,5', '45', '45,5', '46', '47', '47,5', '48'], 'Jordan 1 Mid Purple Sky': ['35,5', '36', '36,5', '37,5', '38', '38,5', '39', '40', '40,5', '41', '42', '42,5', '43', '44', '44,5', '45', '45,5', '46', '47', '47,5', '48'], 'Jordan 1 Mid True Blue': ['35,5', '36', '36,5', '37,5', '38', '38,5', '39', '40', '40,5', '41', '42', '42,5', '43', '44', '44,5', '45', '45,5', '46', '47'], 'Jordan 1 High True Blue': ['35,5', '36', '36,5', '37,5', '38', '38,5', '39', '40', '40,5', '41', '42', '42,5', '43', '44', '44,5', '45', '45,5', '46', '47', '47,5', '48'], 'Yeezy Slides Azure': ['37', '38', '39', '40,5', '42', '43', '44,5', '46', '47', '48'], 'Jordan 4 Yellow Thunder': ['35,5', '36', '36,5', '37,5', '38', '38,5', '39', '40', '40,5', '41', '42', '42,5', '43', '44', '44,5', '45', '45,5', '46', '47'], 'Jordan 1 High Spider-man': ['35,5', '36', '36,5', '37,5', '38', '38,5', '39', '40', '40,5', '41', '42', '42,5', '43', '44', '44,5', '45', '45,5', '46', '47'], 'Yeezy Slides Slate grey': ['37', '38', '39', '40,5', '42', '43', '44,5', '46', '47', '48'], 'Yeezy Slides Dark Onyx': ['37', '38', '39', '40,5', '42', '43', '44,5', '46', '47', '48'], 'Nike Dunk low Polar Blue': ['35,5', '36', '36,5', '37,5', '38', '38,5', '39', '40', '40,5', '41', '42', '42,5', '43', '44', '44,5', '45', '45,5', '46', '47', '47,5', '48'], 'Yeezy Slides Slate Marine': ['37', '38', '39', '40,5', '42', '43', '44,5', '46', '47', '48'], 'Nike Dunk low Medium Olive': ['35,5', '36', '36,5', '37,5', '38', '38,5', '39', '40', '40,5', '41', '42', '42,5', '43', '44', '44,5'], 'Nike Dunk low Triple Pink': ['35.5', '36', '36.5', '37,5', '38', '38,5', '39', '40'], 'Nike Dunk low Photon Dust': ['35,5', '36', '36,5', '37,5', '38', '38,5', '39', '40', '40,5', '41', '42', '42,5', '43', '44', '44,5'], 'Nike SB Dunk low White Gum': ['35,5', '36', '36,5', '37,5', '38', '38,5', '39', '40', '40,5', '41', '42', '42,5', '43', '44', '44,5', '45', '45,5', '46', '47', '47,5', '48'], 'Nike SB Dunk low Black Gum': ['35,5', '36', '36,5', '37,5', '38', '38,5', '39', '40', '40,5', '41', '42', '42,5', '43', '44', '44,5', '45', '45,5', '46', '47', '47,5', '48'], 'Nike Dunk low Mint': ['35,5', '36', '36,5', '37,5', '38', '38,5', '39', '40', '40,5', '41', '42', '42,5', '43', '44', '44,5'], 'Nike Dunk low Two Toned Grey': ['35.5', '36', '36.5', '37,5', '38', '38,5', '39', '40'], 'Jordan 4 Frozen Moments': ['35,5', '36', '36,5', '37,5', '38', '38,5', '39', '40', '40,5', '41', '42', '42,5', '43', '44', '44,5'], 'Air Force 1 Supreme White': ['40', '40,5', '41', '42', '42,5', '43', '44', '44,5', '45', '45,5', '46'], 'Air Force 1 Supreme Black': ['40', '40,5', '41', '42', '42,5', '43', '44', '44,5', '45', '45,5', '46'], 'Air Force 1 Triple White': ['35,5', '36', '36,5', '37,5', '38', '38,5', '39', '40', '40,5', '41', '42', '42,5', '43', '44', '44,5', '45', '45,5', '46', '47', '47,5', '48'], 'Jordan 1 Mid ice Blue GS': ['35.5', '36', '36.5', '37,5', '38', '38,5', '39', '40'], 'Air Jordan 4 Craft': ['35,5', '36', '36,5', '37,5', '38', '38,5', '39', '40', '40,5', '41', '42', '42,5', '43', '44', '44,5', '45', '45,5', '46', '47', '47,5', '48'], 'Jordan 1 Mid Fierce Pink GS': ['35.5', '36', '36.5', '37,5', '38', '38,5', '39', '40'], 'Nike Dunk low Blue Tint': ['35,5', '36', '36,5', '37,5', '38', '38,5', '39', '40', '40,5', '41', '42', '42,5', '43', '44', '44,5'], 'Jordan 4 Medium Olive': ['35,5', '36', '36,5', '37,5', '38', '38,5', '39', '40', '40,5', '41', '42', '42,5', '43', '44', '44,5', '45', '45,5', '46', '47', '47,5', '48'], 'Adidas Campus 00S Grey': ['35 1/3', '36', '36 2/3', '37 1/3', '38', '38 2/3', '39 1/3', '40', '40 2/3', '41 1/3', '42', '42 2/3', '43 1/3', '44', '44 2/3', '45 1/3', '46', '46 2/3'], 'Adidas Campus 00S Black': ['35 1/3', '36', '36 2/3', '37 1/3', '38', '38 2/3', '39 1/3', '40', '40 2/3', '41 1/3', '42', '42 2/3', '43 1/3', '44', '44 2/3', '45 1/3', '46', '46 2/3'], 'Jordan 4 Retro Bred Reimagined': ['35,5', '36', '36,5', '37,5', '38', '38,5', '39', '40', '40,5', '41', '42', '42,5', '43', '44', '44,5', '45', '45,5', '46', '47'], 'Jordan 4 Retro Messy Room GS': ['35.5', '36', '36.5', '37,5', '38', '38,5', '39', '40'], 'Adidas Campus 00S White Core Black Crystal': ['35 1/3', '36', '36 2/3', '37 1/3', '38', '38 2/3', '39 1/3', '40', '40 2/3', '41 1/3', '42', '42 2/3'], 'Jordan 1 Low Year of the Dragon': ['35,5', '36', '36,5', '37,5', '38', '38,5', '39', '40', '40,5', '41', '42', '42,5', '43', '44', '44,5', '45', '45,5', '46', '47'], 'Adidas Campus 00s Lucid Blue': ['35 1/3', '36', '36 2/3', '37 1/3', '38', '38 2/3', '39 1/3', '40', '40 2/3', '41 1/3', '42', '42 2/3', '43 1/3', '44', '44 2/3', '45 1/3', '46', '46 2/3'], 'Adidas Campus 00s Dark Green Cloud White': ['35 1/3', '36', '36 2/3', '37 1/3', '38', '38 2/3', '39 1/3', '40', '40 2/3', '41 1/3', '42', '42 2/3', '43 1/3', '44', '44 2/3', '45 1/3', '46', '46 2/3'], 'Adidas Campus 00s Better Scarlet Cloud White': ['35 1/3', '36', '36 2/3', '37 1/3', '38', '38 2/3', '39 1/3', '40', '40 2/3', '41 1/3', '42', '42 2/3', '43 1/3', '44', '44 2/3', '45 1/3', '46', '46 2/3'], 'Adidas Campus 00s Pantone Cloud White Yellow': ['35 1/3', '36', '36 2/3', '37 1/3', '38', '38 2/3', '39 1/3', '40', '40 2/3', '41 1/3', '42', '42 2/3', '43 1/3', '44', '44 2/3', '45 1/3', '46', '46 2/3'], 'Adidas Campus 00s Core Black True Pink': ['35 1/3', '36', '36 2/3', '37 1/3', '38', '38 2/3', '39 1/3', '40', '40 2/3', '41 1/3', '42', '42 2/3', '43 1/3'], 'Air Jordan 4 Retro Metallic Gold (W)': ['35,5', '36', '36,5', '37,5', '38', '38,5', '39', '40', '40,5', '41', '42', '42,5', '43', '44', '44,5'], 'Adidas Gazelle Bold Wonder White Clear Sky': ['35 1/3', '36', '36 2/3', '37 1/3', '38', '38 2/3'], 'Adidas Gazelle Bold True Pink Gum': ['35 1/3', '36', '36 2/3', '37 1/3', '38', '38 2/3'], 'Adidas Samba OG Cloud White Core Black': ['36', '36 2/3', '37 1/3', '38', '38 2/3', '39 1/3', '40', '40 2/3', '41 1/3', '42', '42 2/3', '43 1/3', '44', '44 2/3', '45 1/3', '46'], 'Adidas Gazelle Indoor Bliss Pink Purple': ['35 1/3', '36', '36 2/3', '37 1/3', '38', '38 2/3', '39 1/3', '40', '40 2/3', '41 1/3', '42', '42 2/3', '43 1/3', '44', '44 2/3'], 'Jordan 1 Mid Purple Venom': ['35.5', '36', '36.5', '37,5', '38', '38,5', '39', '40'], 'Jordan 4 Military Blue': ['35,5', '36', '36,5', '37,5', '38', '38,5', '39', '40', '40,5', '41', '42', '42,5', '43', '44', '44,5', '45', '45,5', '46', '47', '47,5', '48'], 'Jordan 4 Retro Hyper Violet': ['35.5', '36', '36.5', '37,5', '38', '38,5', '39', '40'], 'Jordan 4 Retro Vivid Sulfur': ['35,5', '36', '36,5', '37,5', '38', '38,5', '39', '40', '40,5', '41', '42', '42,5', '43', '44', '44,5'], 'Adidas Handball Spezial Clear Pink / Arctic Punch': ['35 1/3', '36', '36 2/3', '37 1/3', '38', '38 2/3', '39 1/3', '40', '40 2/3', '41 1/3', '42', '42 2/3', '43 1/3', '44', '44 2/3'], 'Adidas Gazelle Indoor Blue Fusion Gum': ['35 1/3', '36', '36 2/3', '37 1/3', '38', '38 2/3', '39 1/3', '40', '40 2/3', '41 1/3', '42', '42 2/3', '43 1/3', '44', '44 2/3'], 'Adidas Campus 00s Core Black White': ['35 1/3', '36', '36 2/3', '37 1/3', '38', '38 2/3', '39 1/3', '40', '40 2/3', '41 1/3', '42', '42 2/3', '43 1/3', '44', '44 2/3', '45 1/3', '46', '46 2/3'], 'Adidas Handball Spezial Navy Gum': ['36', '36 2/3', '37 1/3', '38', '38 2/3', '39 1/3', '40', '40 2/3', '41 1/3', '42', '42 2/3', '43 1/3', '44', '44 2/3', '45 1/3', '46'], 'Nike SB Dunk Low J-Pack Chicago': ['37,5', '38', '38,5', '39', '40', '40,5', '41', '42', '42,5', '43', '44', '44,5', '45', '45,5', '46', '47'], 'Yeezy Slide Bone': ['37', '38', '39', '40,5', '42', '43', '44,5', '46', '47'], 'Yeezy Slide Onyx': ['37', '38', '39', '40,5', '42', '43', '44,5', '46', '47'], 'Jordan 4 Retro Oxidized Green': ['35,5', '36', '36,5', '37,5', '38', '38,5', '39', '40', '40,5', '41', '42', '42,5', '43', '44', '44,5', '45', '45,5', '46', '47'], 'Jordan 4 Retro White Thunder': ['35,5', '36', '36,5', '37,5', '38', '38,5', '39', '40', '40,5', '41', '42', '42,5', '43', '44', '44,5', '45', '45,5', '46', '47', '47,5'], 'Air Jordan 4 Retro SE Paris Olympics Wet Cement': ['40,5', '41', '42', '42,5', '43', '44', '44,5', '45', '45,5', '46', '47', '47,5'], 'UGG Tazz Slipper Black': [36.0, 37.0, 38.0, 39.0, 40.0, 41.0, 42.0, 43.0], 'UGG Tazz Slipper Chestnut': [36.0, 37.0, 38.0, 39.0, 40.0, 41.0, 42.0, 43.0], 'UGG Lowmel Black': [36.0, 37.0, 38.0, 39.0, 40.0, 41.0, 42.0], 'UGG Lowmel Chestnut': [36.0, 37.0, 38.0, 39.0, 40.0, 41.0, 42.0], 'UGG Tasman Slipper Black': [36.0, 37.0, 38.0, 39.0, 40.0, 41.0, 42.0, 43.0, 44.0, 45.0], 'UGG Tasman Slipper Chestnut': [36.0, 37.0, 38.0, 39.0, 40.0, 41.0, 42.0, 43.0], 'Adidas Handball Spezial Earth Strata Gum': ['36', '36 2/3', '37 1/3', '38', '38 2/3', '39 1/3', '40', '40 2/3', '41 1/3', '42', '42 2/3', '43 1/3', '44', '44 2/3', '45 1/3', '46'], "UGG Tazz Slipper Sand (Women's)": [36.0, 37.0, 38.0, 39.0, 40.0, 41.0, 42.0, 43.0], 'Adidas Handball Spezial Shadow Red (W)': ['35 1/3', '36', '36 2/3', '37 1/3', '38', '38 2/3', '39 1/3', '40', '40 2/3', '41 1/3', '42', '42 2/3', '43 1/3', '44'], 'Adidas Campus 00s Black Leopard': ['35 1/3', '36', '36 2/3', '37 1/3', '38', '38 2/3', '39 1/3', '40', '40 2/3', '41 1/3', '42', '42 2/3'], 'Jordan 4 Retro OG SP A Ma Maniére While You Were Sleeping': ['35,5', '36', '36,5', '37,5', '38', '38,5', '39', '40', '40,5', '41', '42', '42,5', '43', '44', '44,5', '45', '45,5', '46'], 'Jordan 4 Retro Orchid (W)': ['35,5', '36', '36,5', '37,5', '38', '38,5', '39', '40', '40,5', '41', '42', '42,5', '43', '44', '44,5'], 'UGG Tazz Slipper Hickory (W)': [36.0, 37.0, 38.0, 39.0, 40.0, 41.0, 42.0], 'Air Jordan 4 Retro Fear': ['35,5', '36', '36,5', '37,5', '38', '38,5', '39', '40', '40,5', '41', '42', '42,5', '43', '44', '44,5', '45', '45,5', '46', '47', '47,5', '48'], 'Represent Owners Club T-Shirt Fog': ['L'], 'Supreme x Jordan Biggie S/S Top "Black"': ['L'], 'Supreme Jordan Biggie S/S Top "White"': ['L']}

# ✅ Vytvoření databázových tabulek
with app.app_context():
    with app.app_context():
        db.create_all()

# Přihlašovací údaje pro admina
USERS = {'admin': 'heslo123'}

# ✅ Hlavní stránka (admin dashboard)
@app.route('/')
def index():
    if 'user' not in session:
        return redirect(url_for('login'))
    
    offers = Offer.query.all()
    partners = Partner.query.all()
    
    return render_template('index.html', offers=offers, partners=partners)

# ✅ Přidání nabídky

@app.route('/add_offer', methods=['GET', 'POST'])
def add_offer():
    if 'user' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        model = request.form.get('model')
        size = request.form.get('size')
        price = request.form.get('price')
        partner_name = session['user']

        partner = Partner.query.filter_by(name=partner_name).first()
        if partner:
            offer = Offer(
                model=model,
                size=size,
                price=float(price),
                partner_id=partner.id
            )
            db.session.add(offer)
            db.session.commit()

        return redirect(url_for('index'))

    partners = Partner.query.all()
    return render_template('add_offer.html', partners=partners, models_sizes=MODELS_SIZES)

    if 'user' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        model = request.form.get('model')
        size = request.form.get('size')
        price = request.form.get('price')
        partner_name = request.form.get('partner')

        if model not in MODELS_SIZES or size not in MODELS_SIZES[model]:
            return "Neplatný model nebo velikost!"

        partner = Partner.query.filter_by(name=partner_name).first()

        if partner:
            offer = Offer(
                model=model,
                size=size,
                price=float(price),
                partner_id=partner.id
            )
            db.session.add(offer)
            db.session.commit()

        return redirect(url_for('index'))

    partners = Partner.query.all()
    return render_template('add_offer.html', partners=partners, models_sizes=MODELS_SIZES)


# ✅ Upravení nabídky
@app.route('/edit_offer/<int:id>', methods=['GET', 'POST'])
def edit_offer(id):
    if 'user' not in session:
        return redirect(url_for('login'))

    offer = Offer.query.get_or_404(id)

    if session['user'] != 'admin' and offer.partner.name != session['user']:
        return redirect(url_for('index'))

    if request.method == 'POST':
        offer.model = request.form.get('model')
        offer.size = request.form.get('size')
        offer.price = float(request.form.get('price'))
        db.session.commit()
        return redirect(url_for('index'))

    return render_template('edit_offer.html', offer=offer)

# ✅ Smazání nabídky
@app.route('/delete_offer/<int:id>', methods=['POST'])
def delete_offer(id):
    if 'user' not in session:
        return redirect(url_for('login'))

    offer = Offer.query.get_or_404(id)

    if session['user'] != 'admin' and offer.partner.name != session['user']:
        return redirect(url_for('index'))

    db.session.delete(offer)
    db.session.commit()
    return redirect(url_for('index'))


@app.route('/partner/<int:id>')
def partner_detail(id):
    if 'user' not in session:
        return redirect(url_for('login'))

    if session['user'] != 'admin':
        return redirect(url_for('index'))

    partner = Partner.query.get_or_404(id)
    offers = Offer.query.filter_by(partner_id=partner.id).all()

    return render_template('partner_detail.html', partner=partner, offers=offers)

    if 'user' not in session:
        return redirect(url_for('login'))
    
    partner = Partner.query.get_or_404(id)
    offers = Offer.query.filter_by(partner_id=partner.id).all()
    
    return render_template('partner_detail.html', partner=partner, offers=offers)

# ✅ Odhlášení
@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('login'))

# ✅ Export dat do CSV
@app.route('/export_csv')
def export_csv():
    if 'user' not in session:
        return redirect(url_for('login'))
    
    offers = Offer.query.all()
    filename = 'offers.csv'

    with open(filename, 'w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(['Model', 'Velikost', 'Cena', 'Partner', 'Prodáno', 'Vyplaceno'])
        for offer in offers:
            partner = Partner.query.get(offer.partner_id)
            writer.writerow([
                offer.model,
                offer.size,
                offer.price,
                partner.name if partner else '',
                'Ano' if offer.sold else 'Ne',
                'Ano' if offer.paid else 'Ne'
            ])
    
    return send_file(filename, as_attachment=True)

# ✅ Přihlášení
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        name = request.form.get('name')
        password = request.form.get('password')

        if USERS.get(name) == password:
            session['user'] = name
            return redirect(url_for('index'))

        partner = Partner.query.filter_by(name=name, password=password).first()
        if partner:
            session['user'] = name
            return redirect(url_for('index'))

    return render_template('login.html')

# ✅ Registrace partnera
@app.route('/register_partner', methods=['GET', 'POST'])
def register_partner():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        phone = request.form.get('phone')
        bank_account = request.form.get('bank_account')
        address = request.form.get('address')
        password = request.form.get('password')

        if Partner.query.filter_by(name=name).first():
            return "Partner už existuje!"

        new_partner = Partner(
            name=name,
            email=email,
            phone=phone,
            bank_account=bank_account,
            address=address,
            password=password
        )

        db.session.add(new_partner)
        db.session.commit()
        return redirect(url_for('login'))

    return render_template('register_partner.html')

if __name__ == '__main__':
    app.run(debug=True)

    
@app.route('/my_offers')
def my_offers():
    offers = Offer.query.filter_by(partner_id=current_user.id).all()
    return render_template('my_offers.html', offers=offers)
