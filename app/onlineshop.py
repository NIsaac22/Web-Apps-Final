import flask
from collections import Counter
from flask import render_template, session, request, redirect
from flask_sqlalchemy import SQLAlchemy
from flask_bootstrap import Bootstrap

app = flask.Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
db = SQLAlchemy(app)
Bootstrap(app)
app.secret_key = 'key'

@app.route('/', methods=['GET', 'POST'])
def index():
    sort = request.args.get('sort', 'default')
    if sort == "name":
        products = product.query.order_by(product.name).all()
    elif sort == "price":
        products = product.query.order_by(product.price).all()
    elif sort == "environmental_impact":
        products = product.query.order_by(product.environmental_impact).all()
    else:
        products = product.query.order_by(product.id).all()
    return render_template('index.html', products = products)

@app.route('/basket', methods=['GET', 'POST'])
def basket():
    basket_items = session.get("basket", [])
    quantities = Counter(basket_items)
    products = product.query.filter(product.id.in_(basket_items)).all()
    basket_items = []
    total = 0

    for p in products:
        quantity = quantities[p.id]
        subtotal = p.price * quantity
        total += subtotal
        basket_items.append({
            "product": p,
            "quantity": quantity,
            "subtotal": subtotal
        })
    

    return render_template('basket.html', products = basket_items, total = total)

@app.route('/checkout', methods=['GET', 'POST'])
def checkout():
    basket_ids = session.get("basket", [])
    products = product.query.filter(product.id.in_(basket_ids)).all()
    total = sum(p.price for p in products)

    if request.method == 'POST':
        name = request.form.get('name')
        card = request.form.get('card')
        card = card.replace(" ", ""). replace("-", "")
        if not card or not name:
            return render_template('checkout.html', error= "All fields are required", total = total)
        
        if not card.isdigit() or len(card) != 16:
            return render_template('checkout.html', error= "Invalid card number", total = total)

        session.basket = []
        session.modified = True

        return redirect('/payment_comfirmation')

    return render_template('checkout.html', total = total)

@app.route('/payment_comfirmation', methods=['GET', 'POST'])
def payment_comfirmation():
    if request.method == 'GET':
        basket_ids = session.get("basket", [])
        items = product.query.filter(product.id.in_(basket_ids)).all()
        basket_summary = ", ".join(p.name for p in items)
        session["basket"] = []
        session.modified = True
    return render_template('payment_comfirmation.html', summary = basket_summary)

@app.route('/product_page/<int:id>', methods=['GET', 'POST'])
def product_page(id):
    products = product.query.get(id)
    return render_template('product_page.html', product = products)

@app.route('/product_data/<int:id>', methods=['GET', 'POST'])
def product_data_api(id):
    p = product.query.get(id)
    if not p:
        return flask.jsonify({"error": "Product not found"}), 404
    return flask.jsonify({
        "id": p.id,
        "name": p.name,
        "description": p.description,
        "image": p.image,
        "price": p.price,
        "environmental_impact": p.environmental_impact
    })


def product_data():
    db.create_all()
    if product.query.count() == 0:
        p1 = product(name = "Gosling's Black Seal Rum", description = "Goslings Black Seal Rum is a renowned 40% ABV, dark bermuda rum known for its rich, complex flavor profile featuring notes of butterscotch, vanilla, and caramel. It is crafted from a blend of pot and continuous still distillates, famously serving as the essential ingredient in the trademarked Dark 'n Stormy cocktail.", image = "/static/GRum.png", price = 24.50, environmental_impact = 1.2)
        p2 = product(name = "Smirnoff Vodka", description = "Smirnoff is the world's best-selling vodka brand, originally founded in Moscow in 1864. It is known for its triple distillation and 10-stage charcoal filtration process, which creates an exceptionally smooth and neutral spirit.", image = "/static/SVodka.png", price = 27.50, environmental_impact = 7.8)
        p3 = product(name = "Bacardi Superior Rum", description = "Bacardi Superior (also known as Carta Blanca) is the world's most famous white rum, celebrated for its versatility in cocktails like the Mojito and Daiquiri. Developed by Don Facundo Bacardí Massó in 1862, it was the first 'refined' white rum, designed to be smoother and more mixable than the harsh spirits of that era.", image = "/static/BRum.png", price = 23.40, environmental_impact = 8.9)
        p4 = product(name = "Don Julio Blanco Tequila", description = "A crisp and clear tequila with a fresh agave flavor", image = "/static/DTequila.png", price = 29.49, environmental_impact = 6.5)
        p5 = product(name = "Grey Goose Vodka", description = "A premium vodka with a smooth and clean taste", image = "/static/GVodka.png", price = 34.60, environmental_impact = 4.3)
        p6 = product(name = "El Gobernador Pisco", description = "A Peruvian brandy with a fruity and floral aroma", image = "/static/EPisco.png", price = 39.95, environmental_impact = 2.8)
        p7 = product(name="Don Zavier Mamajuana", description="A traditional Caribbean herbal liqueur made by infusing rum with a blend of natural roots, herbs, and spices. Don Zavier Mamajuana offers a rich, earthy flavour with subtle hints of sweetness and warmth, delivering a smooth and unique drinking experience rooted in Dominican heritage.", image="/static/DZM.png", price=63.40, environmental_impact=1.2)
        p8 = product(name="Aguardiente Amarillo de Manzanares", description="Aguardiente Amarillo de Manzanares is a premium Colombian spirit crafted from sugarcane alcohol and infused with distinctive anise flavours. Recognised for its signature golden-yellow hue, this traditional aguardiente delivers a smooth, crisp taste with subtle herbal notes and a warming finish. Originating from Manzanares, Colombia, it is celebrated for its balanced profile, making it ideal served chilled, neat, or enjoyed during social occasions and celebrations. A true expression of Colombian heritage in every pour. ", image="/static/AADM.png", price=31.50, environmental_impact=2.4)
        p9 = product(name="Russkaya Vodka", description="Russkaya Vodka is a legendary, historically popular Soviet-era brand created in 1967, known for its traditional 40% ABV, high-quality grain alcohol (wheat and rye), and charcoal/quartz filtration. It offers a creamy, slightly spiced, and smooth flavor profile, often paired with Russian cuisine and recognized for its ""Russian Vodka"" appellation of origin.", image="/static/RVodka.png", price=26.30, environmental_impact=3.5)
        p10 = product(name="Uvachado", description="Uvachado is a traditional, sweet Peruvian liqueur from the Amazonian region (mainly San Martín) made by macerating black grapes (often Borgogna) in sugarcane aguardiente (cañazo) with honey. Originating around the 1930s in Tarapoto, it is considered an aphrodisiac, a ""trago regional,"" and a celebratory drink", image="/static/Uvachado.png", price=78.40, environmental_impact=1.7)
        p11 = product(name="Liberte", description="Liberté Black Spiced Rum is a budget-friendly, 40% ABV spiced rum sold at Lidl, often considered a cost-effective alternative to Kraken, costing roughly £15-£16 per 70cl bottle. It is a blend of Trinidadian and Dominican rum, typically featuring strong notes of vanilla, burnt toffee, coffee, and spices.", image="/static/LRum.jpg", price=18.40, environmental_impact=8.9)
        p12 = product(name="Metaxa 7 Star", description="METAXA is a renowned Greek amber spirit founded in 1888 by Spyros Metaxa, often categorized as a brandy but unique due to its blend of wine distillates, Muscat wines from Samos, and a secret botanical mix. It is characterized by a smooth, sweet, and complex profile, with stars indicating aging (5, 7, 12, and Private Reserve)", image="/static/Metaxa.png", price=37.00, environmental_impact=6.5)
        db.session.add(p1)
        db.session.add(p2)
        db.session.add(p3)
        db.session.add(p4)
        db.session.add(p5)
        db.session.add(p6)
        db.session.add(p7)
        db.session.add(p8)
        db.session.add(p9)
        db.session.add(p10)
        db.session.add(p11)
        db.session.add(p12)
        db.session.commit()

def init_db():
    db.create_all()
    product_data()
        

class product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    description = db.Column(db.String(400), unique=True, nullable=True)
    image = db.Column(db.String(100), unique=True,nullable=True)
    price = db.Column(db.Float, nullable=False)
    environmental_impact = db.Column(db.Float, nullable=False)

@app.route('/add_to_basket/<int:id>', methods=['POST', 'GET'])
def add_to_basket(id):
    if "basket" not in session:
        session["basket"] = []

    session["basket"].append(id)
    session.modified = True
    
    sort = request.args.get('sort', 'default')
    return flask.redirect(f'/?sort={sort}')

@app.route('/delete_from_basket/<int:id>', methods=['POST','GET'])
def delete_from_basket(id):
    if "basket" in session and id in session["basket"]:
        session["basket"].remove(id)
        session.modified = True
    return flask.redirect('/basket')










if __name__ == '__main__':
    with app.app_context():
        init_db()
    app.run(host="0.0.0.0", port = 80)
