from flask import Flask, render_template, request, redirect, url_for, session
import mysql.connector

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'

# Connect to MySQL
def get_db_connection():
    return mysql.connector.connect(
        host='localhost',
        user='root',
        password='Test@123',
        database='shopping_cart_system'
    )

@app.route('/')
def index():
    db = get_db_connection()
    cursor = db.cursor(dictionary=True)

    cursor.execute("SELECT * FROM products")
    products = cursor.fetchall()

    db.close()
    return render_template('index.html', products=products)



@app.route('/add_to_cart/<int:product_id>', methods=['POST'])
def add_to_cart(product_id):
    db = get_db_connection()
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM products WHERE product_id = %s", (product_id,))
    product = cursor.fetchone()
    db.close()

    cart = session.get('cart', [])
    found = False
    for item in cart:
        if item['product_id'] == product_id:
            item['quantity'] += 1
            found = True
            break

    if not found:
        product['quantity'] = 1
        cart.append(product)

    session['cart'] = cart
    return redirect(url_for('index'))

@app.route("/cart")
def cart():
    cart_items = []
    total = 0
    db = get_db_connection()
    cursor = db.cursor(dictionary=True)

    for item in session.get('cart', []):
        product_id = item['product_id']
        cursor.execute("SELECT * FROM products WHERE product_id = %s", (product_id,))
        product = cursor.fetchone()

        if product:
            item_data = {
                'product_id': product_id,
                'name': product['name'],
                'price': product['price'],
                'quantity': item['quantity'],
                'image_url': product.get('image_url')
            }
            cart_items.append(item_data)
            total += product['price'] * item['quantity']

    db.close()
    return render_template("cart.html", cart=cart_items, total=total)


@app.route('/update_quantity', methods=['POST'])
def update_quantity():
    product_id = int(request.form['product_id'])
    action = request.form['action']

    cart = session.get('cart', [])

    for item in cart:
        if item['product_id'] == product_id:
            if action == 'increase':
                item['quantity'] += 1
            elif action == 'decrease' and item['quantity'] > 1:
                item['quantity'] -= 1
            break

    session['cart'] = cart
    return redirect(url_for('cart'))

@app.route('/remove_from_cart', methods=['POST'])
def remove_from_cart():
    product_id = int(request.form['product_id'])
    
    cart = session.get('cart', [])
    cart = [item for item in cart if item['product_id'] != product_id]

    session['cart'] = cart
    return redirect(url_for('cart'))

@app.route('/checkout', methods=['POST'])
def checkout():
    cart = session.get('cart', [])
    if not cart:
        return {'status': 'error', 'message': 'Cart is empty'}, 400

    db = get_db_connection()
    cursor = db.cursor()

    try:
        for item in cart:
            product_id = item['product_id']
            quantity = item['quantity']

            cursor.execute("SELECT quantity FROM inventory WHERE product_id = %s", (product_id,))
            current_stock = cursor.fetchone()[0]

            if current_stock < quantity:
                return {'status': 'error', 'message': f"Not enough stock for {item['name']}"}, 400

            cursor.execute(
                "UPDATE inventory SET quantity = quantity - %s WHERE product_id = %s",
                (quantity, product_id)
            )

        db.commit()
        session['cart'] = []  # Empty the cart after checkout
        return {'status': 'success'}, 200

    except Exception as e:
        db.rollback()
        return {'status': 'error', 'message': str(e)}, 500

    finally:
        db.close()


if __name__ == '__main__':
    app.run(debug=True)
