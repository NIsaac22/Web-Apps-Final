import flask
from flask import render_template, session
from flask_sqlalchemy import SQLAlchemy

app = flask.Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
db = SQLAlchemy(app)
app.secret_key = 'key'

@app.route('/', methods=['GET', 'POST'])
def index():
    products = product.query.all()
    return render_template('index.html', products = products)

@app.route('/basket', methods=['GET', 'POST'])
def basket():
    basket_ids = session.get("basket", [])
    products = product.query.filter(product.id.in_(basket_ids)).all()
    total = sum(p.price for p in products)
    return render_template('basket.html', products = products, total = total)

@app.route('/checkout', methods=['GET', 'POST'])
def checkout():
    return render_template('checkout.html')

@app.route('/payment_comfirmation', methods=['GET', 'POST'])
def payment_comfirmation():
    return render_template('payment_comfirmation.html')

@app.route('/product_page/<int:id>', methods=['GET', 'POST'])
def product_page(id):
    products = product.query.get(id)
    return render_template('product_page.html', product = products)



def product_data():
    db.create_all()
    if product.query.count() == 0:
        p1 = product(name = "Gosling's Black Seal Rum", description = "World Class Bermuda Rum", image = "/static/GRum.png", price = 1.99, environmental_impact = 3.5)
        p2 = product(name = "SmirnoffVodka", description = "Decent Vodka", image = "/static/SVodka.png", price = 0.99, environmental_impact = 2.5)
        db.session.add(p1)
        db.session.add(p2)
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
