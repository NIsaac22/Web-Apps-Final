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
        products = product.query.all()
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
        basket_summary = ", ".join(str(id) for id in basket_ids)
        session["basket"] = []
        session.modified = True
    return render_template('payment_comfirmation.html', summary = basket_summary)

@app.route('/product_page/<int:id>', methods=['GET', 'POST'])
def product_page(id):
    products = product.query.get(id)
    return render_template('product_page.html', product = products)



def product_data():
    db.create_all()
    if product.query.count() == 0:
        p1 = product(name = "Gosling's Black Seal Rum", description = "World Class Bermuda Rum", image = "/static/GRum.png", price = 1.99, environmental_impact = 3.5)
        p2 = product(name = "SmirnoffVodka", description = "Decent Vodka", image = "/static/SVodka.png", price = 0.99, environmental_impact = 2.5)
        p3 = product(name = "Bacardi Superior Rum", description = "A light-bodied white rum with a subtle aroma of vanilla and almond", image = "/static/BRum.png", price = 1.49, environmental_impact = 3.0)
        p4 = product(name = "Don Julio Blanco Tequila", description = "A crisp and clear tequila with a fresh agave flavor", image = "/static/DTequila.png", price = 2.49, environmental_impact = 4.0)
        p5 = product(name = "Grey Goose Vodka", description = "A premium vodka with a smooth and clean taste", image = "/static/GVodka.png", price = 2.99, environmental_impact = 3.8)
        p6 = product(name = "El Gobernador Pisco", description = "A Peruvian brandy with a fruity and floral aroma", image = "/static/EPisco.png", price = 1.79, environmental_impact = 2.8)
        db.session.add(p1)
        db.session.add(p2)
        db.session.add(p3)
        db.session.add(p4)
        db.session.add(p5)
        db.session.add(p6)
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
    return flask.redirect('/')

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
