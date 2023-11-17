import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
import bcrypt

from flask import Flask, request, render_template, redirect, url_for, session
from dotenv import load_dotenv
from blockchain import BlockchainHandler  # Import the blockchain module

import os
import uuid

load_dotenv()

# Initialize Flask app
app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Replace with a real secret key

# Initialize blockchain handler
blockchain_handler = BlockchainHandler()

contract = w3.eth.contract(address=contract_address, abi=contract_abi)

def create_blockchain_record(order_detail_id, order_data):
    """
    Create a record on the blockchain for an order detail.
    """
    # Ensure you have the account unlocked or use private key to sign transaction
    tx_hash = contract.functions.createOrderDetail(
        order_detail_id,
        order_data['product_id'],
        order_data['quantity'],
        order_data['price_each']
    ).transact({'from': w3.eth.accounts[0]})
    receipt = w3.eth.waitForTransactionReceipt(tx_hash)
    return receipt

# Use a service account
cred = credentials.Certificate(os.getenv('FIREBASE_SERVICE_ACCOUNT_JSON'))
firebase_admin.initialize_app(cred)

db = firestore.client()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = bcrypt.hashpw(request.form['password'].encode('utf-8'), bcrypt.gensalt())
        user_id = str(uuid.uuid4())
        db.collection('users').document(user_id).set({
            'username': username,
            'password': password.decode('utf-8')
        })

        # Log the registration activity
        log_activity(user_id, "User registered")

        return redirect(url_for('index'))
    return render_template('register_user.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password'].encode('utf-8')
        user_ref = db.collection('users').where('username', '==', username).get()
        if user_ref:
            user = user_ref[0].to_dict()
            user_id = user_ref[0].id
            if bcrypt.checkpw(password, user['password'].encode('utf-8')):
                session['username'] = username
                session['user_id'] = user_id  # Store user ID in session

                # Log the login activity
                log_activity(user_id, "User logged in")

                return redirect(url_for('index'))
            else:
                return 'Login Failed', 401
        else:
            return 'User does not exist', 404
    return render_template('login_user.html')


@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('index'))

def log_activity(user_id, activity):
    activity_data = {
        'user_id': user_id,
        'activity': activity,
        'activity_date': firestore.SERVER_TIMESTAMP  # Store the current UTC date and time
    }
    db.collection('activities').add(activity_data)

@app.route('/update_inventory', methods=['GET', 'POST'])
def update_inventory():
    if request.method == 'POST':
        product_id = request.form['product_id']
        quantity = int(request.form['quantity'])
        additional_details = request.form['additional_details']

        # Check if the document exists
        inventory_ref = db.collection('inventory').document(product_id)
        doc = inventory_ref.get()

        if not doc.exists:
            # If the document doesn't exist, create a new one
            inventory_ref.set({
                'quantity': quantity,
                'additional_details': additional_details
            })
        else:
            # If the document exists, update it
            inventory_ref.update({
                'quantity': quantity,
                'additional_details': additional_details
            })

        current_user_id = session.get('user_id', 'Unknown user')
        log_activity(current_user_id, f"Updated inventory for product ID: {product_id}")

        return redirect(url_for('index'))
    return render_template('update_inventory.html')


@app.route('/add_product', methods=['GET', 'POST'])
def add_product():
    if request.method == 'POST':
        name = request.form['name']
        details = request.form['details']
        manufacturer_id = request.form['manufacturer_id']
        price = float(request.form['price'])  # Convert the price to a float

        # Generate a unique product ID
        product_id = str(uuid.uuid4())

        # Save product details to Firestore
        db.collection('products').document(product_id).set({
            'name': name,
            'details': details,
            'manufacturer_id': manufacturer_id,
            'price': price  # Add the price to the Firestore document
        })

        # Log the product entry activity
        current_user_id = session.get('user_id', 'Unknown user')
        log_activity(current_user_id, f"Added product: {name}")

        return redirect(url_for('index'))
    return render_template('add_product.html')

@app.route('/register_manufacturer', methods=['GET', 'POST'])
def register_manufacturer():
    if request.method == 'POST':
        name = request.form['name']
        details = request.form['details']

        # Generate a unique manufacturer ID
        manufacturer_id = str(uuid.uuid4())

        # Save manufacturer details to Firestore
        db.collection('manufacturers').document(manufacturer_id).set({
            'name': name,
            'details': details
        })

        # Log the manufacturer registration activity
        # Assuming you have a way to identify the current user (e.g., from the session)
        current_user_id = session.get('user_id', 'Unknown user')
        log_activity(current_user_id, f"Registered manufacturer: {name}")

        return redirect(url_for('index'))
    return render_template('register_manufacturer.html')

@app.route('/register_customer', methods=['GET', 'POST'])
def register_customer():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        address = request.form['address']
        phone = request.form['phone']

        # Generate a unique customer ID
        customer_id = str(uuid.uuid4())

        # Save customer details to Firestore
        db.collection('customers').document(customer_id).set({
            'name': name,
            'email': email,
            'address': address,
            'phone': phone
        })

        # Log the customer registration activity
        current_user_id = session.get('user_id', 'Unknown user')
        log_activity(current_user_id, f"Registered customer: {name}")

        return redirect(url_for('index'))
    return render_template('register_customer.html')

@app.route('/place_order', methods=['GET', 'POST'])
def place_order():
    if request.method == 'POST':
        customer_id = request.form['customer_id']
        product_id = request.form['product_id']
        quantity = int(request.form['quantity'])
        total_price = float(request.form['total_price'])
        order_date = firestore.SERVER_TIMESTAMP

        # Generate a unique order ID
        order_id = str(uuid.uuid4())

        # Save order details to Firestore
        db.collection('orders').document(order_id).set({
            'customer_id': customer_id,
            'product_id': product_id,
            'quantity': quantity,
            'total_price': total_price,
            'order_date': order_date
        })

        # Log the order placement activity
        current_user_id = session.get('user_id', 'Unknown user')
        log_activity(current_user_id, f"Placed order: {order_id}")

        return redirect(url_for('index'))
    return render_template('place_order.html')

@app.route('/add_order_detail', methods=['GET', 'POST'])
def add_order_detail():
    if request.method == 'POST':
        order_id = request.form['order_id']
        product_id = request.form['product_id']
        quantity = int(request.form['quantity'])
        price_each = float(request.form['price_each'])

        # Generate a unique order detail ID
        order_detail_id = str(uuid.uuid4())

        # Save order detail to Firestore
        db.collection('orderDetails').document(order_detail_id).set({
            'order_id': order_id,
            'product_id': product_id,
            'quantity': quantity,
            'price_each': price_each
        })


        
        # Create a record on the blockchain
        order_data = {
            'product_id': product_id,
            'quantity': quantity,
            'price_each': price_each
        }
        blockchain_receipt = blockchain_handler.create_order_detail(order_detail_id, order_data)




        # Log the addition of order detail
        current_user_id = session.get('user_id', 'Unknown user')
        log_activity(current_user_id, f"Added order detail for order ID: {order_id}")

        return redirect(url_for('index'))
    return render_template('add_order_detail.html')

@app.route('/process_payment', methods=['GET', 'POST'])
def process_payment():
    if request.method == 'POST':
        order_id = request.form['order_id']
        amount = float(request.form['amount'])
        payment_method = request.form['payment_method']
        payment_date = firestore.SERVER_TIMESTAMP

        # Generate a unique payment ID
        payment_id = str(uuid.uuid4())

        # Save payment details to Firestore
        db.collection('payments').document(payment_id).set({
            'order_id': order_id,
            'amount': amount,
            'payment_method': payment_method,
            'payment_date': payment_date
        })

        # Log the payment processing
        current_user_id = session.get('user_id', 'Unknown user')
        log_activity(current_user_id, f"Processed payment for order ID: {order_id}")

        return redirect(url_for('index'))
    return render_template('process_payment.html')

# Add more routes as necessary...

if __name__ == '__main__':
    app.run(debug=True)