from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'canteen-secret-key-2024')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///canteen.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)


class MenuItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(200))
    price = db.Column(db.Float, nullable=False)
    category = db.Column(db.String(50), nullable=False)
    available = db.Column(db.Boolean, default=True)


class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    customer_name = db.Column(db.String(100), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(20), default='pending')
    total = db.Column(db.Float, default=0.0)
    items = db.relationship('OrderItem', backref='order', lazy=True)


class OrderItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('order.id'), nullable=False)
    menu_item_id = db.Column(db.Integer, db.ForeignKey('menu_item.id'), nullable=False)
    quantity = db.Column(db.Integer, default=1)
    menu_item = db.relationship('MenuItem')


def init_db():
    db.create_all()
    if MenuItem.query.count() == 0:
        sample_items = [
            MenuItem(name='Veg Thali', description='Full vegetarian meal with dal, sabzi, roti, rice', price=80, category='Meals'),
            MenuItem(name='Chicken Biryani', description='Fragrant basmati rice with spiced chicken', price=120, category='Meals'),
            MenuItem(name='Paneer Butter Masala', description='Cottage cheese in rich tomato-butter gravy', price=100, category='Meals'),
            MenuItem(name='Masala Dosa', description='Crispy crepe filled with spiced potato', price=60, category='Breakfast'),
            MenuItem(name='Poha', description='Flattened rice with vegetables and spices', price=40, category='Breakfast'),
            MenuItem(name='Idli Sambar', description='Steamed rice cakes with lentil soup', price=50, category='Breakfast'),
            MenuItem(name='Samosa', description='Crispy fried pastry with spiced potato filling', price=20, category='Snacks'),
            MenuItem(name='Vada Pav', description='Spiced potato fritter in a bun', price=25, category='Snacks'),
            MenuItem(name='Bread Pakora', description='Bread slices battered and fried', price=30, category='Snacks'),
            MenuItem(name='Masala Chai', description='Spiced Indian tea with milk', price=15, category='Beverages'),
            MenuItem(name='Cold Coffee', description='Chilled coffee with milk and ice cream', price=50, category='Beverages'),
            MenuItem(name='Fresh Lime Soda', description='Refreshing lime with soda water', price=30, category='Beverages'),
        ]
        db.session.bulk_save_objects(sample_items)
        db.session.commit()


@app.route('/')
def index():
    categories = db.session.query(MenuItem.category).distinct().all()
    categories = [c[0] for c in categories]
    menu_items = MenuItem.query.filter_by(available=True).all()
    cart = session.get('cart', {})
    cart_count = sum(cart.values()) if cart else 0
    return render_template('index.html', menu_items=menu_items, categories=categories, cart_count=cart_count)


@app.route('/add_to_cart/<int:item_id>', methods=['POST'])
def add_to_cart(item_id):
    cart = session.get('cart', {})
    cart[str(item_id)] = cart.get(str(item_id), 0) + 1
    session['cart'] = cart
    flash('Item added to cart!', 'success')
    return redirect(url_for('index'))


@app.route('/cart')
def cart():
    cart = session.get('cart', {})
    items = []
    total = 0
    for item_id, qty in cart.items():
        item = MenuItem.query.get(int(item_id))
        if item:
            subtotal = item.price * qty
            total += subtotal
            items.append({'item': item, 'quantity': qty, 'subtotal': subtotal})
    return render_template('cart.html', items=items, total=total)


@app.route('/remove_from_cart/<int:item_id>', methods=['POST'])
def remove_from_cart(item_id):
    cart = session.get('cart', {})
    if str(item_id) in cart:
        del cart[str(item_id)]
        session['cart'] = cart
    flash('Item removed from cart.', 'info')
    return redirect(url_for('cart'))


@app.route('/checkout', methods=['GET', 'POST'])
def checkout():
    cart = session.get('cart', {})
    if not cart:
        flash('Your cart is empty.', 'warning')
        return redirect(url_for('index'))

    if request.method == 'POST':
        customer_name = request.form.get('customer_name', '').strip()
        if not customer_name:
            flash('Please enter your name.', 'danger')
            return redirect(url_for('checkout'))

        total = 0
        order = Order(customer_name=customer_name)
        db.session.add(order)
        db.session.flush()

        for item_id, qty in cart.items():
            item = MenuItem.query.get(int(item_id))
            if item:
                subtotal = item.price * qty
                total += subtotal
                order_item = OrderItem(order_id=order.id, menu_item_id=item.id, quantity=qty)
                db.session.add(order_item)

        order.total = total
        db.session.commit()
        session.pop('cart', None)
        flash(f'Order #{order.id} placed successfully! Total: ₹{total:.0f}', 'success')
        return redirect(url_for('order_confirmation', order_id=order.id))

    items = []
    total = 0
    for item_id, qty in cart.items():
        item = MenuItem.query.get(int(item_id))
        if item:
            subtotal = item.price * qty
            total += subtotal
            items.append({'item': item, 'quantity': qty, 'subtotal': subtotal})
    return render_template('checkout.html', items=items, total=total)


@app.route('/order/<int:order_id>')
def order_confirmation(order_id):
    order = Order.query.get_or_404(order_id)
    return render_template('order_confirmation.html', order=order)


@app.route('/orders')
def orders():
    all_orders = Order.query.order_by(Order.created_at.desc()).all()
    return render_template('orders.html', orders=all_orders)


if __name__ == '__main__':
    with app.app_context():
        init_db()
    app.run(host='0.0.0.0', port=5000, debug=True)
