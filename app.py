from email.mime.multipart import MIMEMultipart
from flask import Flask, render_template, request, redirect, url_for, jsonify, session, send_from_directory
from flask_pymongo import PyMongo
from bson.objectid import ObjectId  # Import ObjectId
import bcrypt
from datetime import datetime
import random
import string
from flask import render_template, request, redirect, url_for, session
import pymongo
from datetime import datetime
import os
from werkzeug.utils import secure_filename
from bson import ObjectId
from functools import wraps
import razorpay
import smtplib
from email.mime.text import MIMEText
from werkzeug.security import generate_password_hash
from werkzeug.security import check_password_hash
from pymongo import MongoClient





app = Flask(__name__)

# MongoDB Atlas Connection URI
app.config["MONGO_URI"] = "mongodb+srv://riju:Sudiptadey123@cluster0.kpda0.mongodb.net/ecommerce_db"
mongo = PyMongo(app)

# MongoDB Collections
users = mongo.db.users
products = mongo.db.products
admin = mongo.db.admin
orders=mongo.db.orders

app.secret_key = '56f8c7e3b9e4a8d5f12a6c89db307a4f7b3c91c6745d2198'
app.config['SESSION_COOKIE_SECURE'] = True  # Use HTTPS for session cookies
app.config['SESSION_COOKIE_HTTPONLY'] = True  # Prevent JavaScript access to session cookies





# ✅ Define upload folder and allowed extensions
UPLOAD_FOLDER = 'static/images/'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


# ✅ Check if the uploaded file is valid
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS



# Home page
@app.route('/')
def home():
    all_products = list(products.find())
    return render_template('home.html',products=all_products)

#---------------------------ADMIN ROUTES----------------------------------------------------------------
# ✅ Create a login_required decorator to protect routes
# ✅ Create a login_required decorator for admin
def admin_login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Check if 'admin_phone' is in session (for admin only)
        if 'admin_phone' not in session:
            return redirect(url_for('adminlogin'))  # Redirect to admin login if not authenticated
        return f(*args, **kwargs)
    return decorated_function


# ✅ Admin page (protected route)
# ✅ Admin page (protected route)
@app.route('/admin')
@admin_login_required
def admin_page():
    return render_template('admin.html')




# Adminlogin page
@app.route('/adminlogin')
def adminlogin():
    return render_template('adminlogin.html')



# ✅ adminLogin Endpoint
# ✅ Admin login route
@app.route('/login2', methods=['GET', 'POST'])
def login2():
    if request.method == 'POST':
        phone = request.form['phone']
        password = request.form['password']

        # ✅ Fetch admin from MongoDB
        admin_user = admin.find_one({'phone': phone})

        # ✅ Compare entered password with stored password
        if admin_user and password == admin_user['password']:
            session['admin_phone'] = phone  # Use 'admin_phone' for admin login
            return redirect(url_for('admin_page'))  # Redirect to /admin
        else:
            return 'Invalid credentials!'
    return render_template('adminlogin.html')  # Show admin login page for GET request


# ✅ Admin Logout2 Route
@app.route('/logout2')
def logout2():
    session.pop('admin_phone', None)  # Remove admin sessio
    session.clear()  # Clear session data
    return redirect(url_for('home'))  # Redirect to home page



# ✅ Fetch users from MongoDB
@app.route('/api/users', methods=['GET'])
def get_users():
    # Use mongo.db to access the collection
    users = list(mongo.db.users.find({}, {'_id': 1, 'fullname': 1, 'phone': 1}))

    # Format _id to string for JSON serialization
    for user in users:
        user['_id'] = str(user['_id'])

    return jsonify(users)


# ✅ Single API to get dashboard data
@app.route('/api/dashboard', methods=['GET'])
def get_dashboard_data():
    # Count total users
    total_users = mongo.db.users.count_documents({})
    total_orders = mongo.db.orders.count_documents({})
    total_products = mongo.db.products.count_documents({})



    return jsonify({
        'total_users': total_users,
        'total_orders': total_orders,
        'total_products': total_products
    })


# ✅ Fetch All Products (API)
@app.route('/api/products', methods=['GET'])
def get_products():
    all_products = list(products.find())
    for product in all_products:
        product['_id'] = str(product['_id'])  # Convert ObjectId to string for JSON serialization
    return jsonify(all_products)





# ✅ Add New Product (API) - with multiple images
@app.route('/api/add_product', methods=['POST'])
def add_product():
    category = request.form['category']
    id = request.form['id']
    name = request.form['name']
    price = float(request.form['price'])
    description = request.form['description']

    image_paths = []  # List to store paths of uploaded images

    if 'images' in request.files:
        files = request.files.getlist('images')
        image_paths = []
        for image_file in files:
            if image_file and allowed_file(image_file.filename):
                filename = secure_filename(image_file.filename)
                path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                image_file.save(path)
                image_paths.append(path)
    else:
        image_paths = ['static/images/default.jpg']

    # ✅ Insert product into MongoDB
    product_data = {
        'category': category,
        'id': id,
        'name': name,
        'price': price,
        'description': description,
        'images': image_paths  # store all image paths
    }
    products.insert_one(product_data)
    return jsonify({'success': True})

# ✅ Update Existing Product (API) - Replace Images
@app.route('/api/update_product/<product_id>', methods=['PUT'])
def update_product(product_id):
    category = request.form['category']
    id = request.form['id']
    name = request.form['name']
    price = float(request.form['price'])
    description = request.form['description']

    image_paths = []

    # Replace images if new ones are provided
    if 'images' in request.files:
        uploaded_files = request.files.getlist('images')
        for image_file in uploaded_files:
            if image_file and allowed_file(image_file.filename):
                filename = secure_filename(image_file.filename)
                save_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
                image_file.save(save_path)
                image_paths.append(save_path)
    else:
        # Fallback if no new images uploaded
        image_paths = ['static/images/default.jpg']

    # ✅ Update in MongoDB
    products.update_one(
        {'_id': ObjectId(product_id)},
        {'$set': {
            'category': category,
            'id': id,
            'name': name,
            'price': price,
            'description': description,
            'images': image_paths
        }}
    )

    return jsonify({'success': True})


# ✅ Delete Product (API)
@app.route('/api/delete_product/<product_id>', methods=['DELETE'])
def delete_product(product_id):
    products.delete_one({'_id': ObjectId(product_id)})
    return jsonify({'success': True})






# Get all orders
@app.route('/api/orders', methods=['GET'])
def get_orders():
    orders = list(mongo.db.orders.find({}))
    for order in orders:
        order['_id'] = str(order['_id'])
    return jsonify(orders)


# Update order status
@app.route('/api/update_order/<order_id>', methods=['PUT'])
def update_order(order_id):
    data = request.json
    delhivery_status = data.get('delhivery_status')

    if not delhivery_status:
        return jsonify({"error": "Status is required"}), 400

    mongo.db.orders.update_one({'_id': ObjectId(order_id)}, {'$set': {'delhivery_status': delhivery_status}})
    return jsonify({"message": "Order status updated successfully!"})


# Delete an order
@app.route('/api/delete_order/<order_id>', methods=['DELETE'])
def delete_order(order_id):
    mongo.db.orders.delete_one({'_id': ObjectId(order_id)})
    return jsonify({"message": "Order deleted successfully!"})



#-------------------USER ROUTES----------------------------------------------------------------------

@app.route('/index')
def index():
    return render_template('index.html')

# Email Configuration
EMAIL_ADDRESS = "sudiptadey877@gmail.com"
EMAIL_PASSWORD = "gnyj cfpt eezr ypjz"
# Function to generate a 6-digit OTP
def generate_otp():
    return str(random.randint(100000, 999999))


# Function to send OTP via Email
def send_otp(email, otp):


    subject = "Your OTP for Registration"
    body = f"Your OTP for registration is: {otp}. It is valid for 5 minutes."

    msg = MIMEMultipart()
    msg['From'] = EMAIL_ADDRESS
    msg['To'] = email
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))

    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
        server.sendmail(EMAIL_ADDRESS, email, msg.as_string())
        server.quit()
        return True
    except Exception as e:
        print("Failed to send email:", e)
        return False


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        try:
            data = request.get_json()  # 🔄 Instead of request.form

            fullname = data.get('fullname')
            phone = data.get('phone')
            email = data.get('email')
            password = data.get('password')
            re_password = data.get('re_pass')

            # Validate required fields
            if not all([fullname, phone, email, password, re_password]):
                return jsonify({'status': 'error', 'message': 'All fields are required'})
            # Check if user exists
            if mongo.db.users.find_one({'$or': [{'phone': phone}, {'email': email}]}):
                return jsonify({'status': 'error', 'message': 'User already exists!'})

            if password != re_password:
                return jsonify({'status': 'error', 'message': 'Passwords do not match'})

            # Generate and send OTP
            otp = generate_otp()
            session['otp'] = otp
            session['registration_data'] = {
                'fullname': fullname,
                'phone': phone,
                'email': email,
                'password': password  # 🔒 Note: hash before storing in real apps
            }

            if send_otp(email, otp):
                return jsonify({'status': 'success', 'message': 'OTP sent to your email'})
            else:
                return jsonify({'status': 'error', 'message': 'Failed to send OTP'})

        except Exception as e:
            print(f"Registration error: {str(e)}")
            return jsonify({'status': 'error', 'message': 'An error occurred during registration'})

    return render_template('register.html')


@app.route("/otp_verification")
def otp_verification():
    if 'otp' not in session or 'registration_data' not in session:
        # 👇 Redirect back to register if session data is missing
        return redirect("/register")
    return render_template("otp_verification.html")


@app.route('/verify_otp', methods=['POST'])
def verify_otp():
    data = request.get_json()
    user_otp = data.get('otp')

    if user_otp == session.get('otp'):


        registration_data = session.pop('registration_data', None)
        if registration_data:
            # Optional: check if user already exists
            existing_user = mongo.db.users.find_one({'email': registration_data['email']})
            if existing_user:
                return jsonify({'status': 'error', 'redirect_url': '/register', 'message': 'Email already registered'})

            # Hash the password
            hashed_password = generate_password_hash(registration_data['password'])

            # Prepare user document
            user_doc = {
                'fullname': registration_data['fullname'],
                'email': registration_data['email'],
                'phone': registration_data['phone'],
                'password': hashed_password,
                'created_at': datetime.utcnow()
            }

            # ✅ Insert into MongoDB
            mongo.db.users.insert_one(user_doc)


            # Clear session OTP
            session.pop('otp', None)
            session.pop('registration_data', None)

            # ✅ Auto-login: Set session
            session['phone'] = registration_data['phone']

            return jsonify({'status': 'success', 'redirect_url': '/products', 'message': 'OTP verified and user registered'})
        else:
            return jsonify({'status': 'error', 'redirect_url': '/register', 'message': 'Session expired. Please register again.'})
    else:
        return jsonify({'status': 'error', 'redirect_url': '/register', 'message': 'Invalid OTP'})

@app.route('/resend_otp', methods=['POST'])
def resend_otp():
    try:
        registration_data = session.get('registration_data')
        if not registration_data:
            return jsonify({'status': 'error', 'message': 'Session expired. Please register again.'})

        new_otp = generate_otp()
        session['otp'] = new_otp

        if send_otp(registration_data['email'], new_otp):
            return jsonify({'status': 'success', 'message': 'OTP resent successfully.'})
        else:
            return jsonify({'status': 'error', 'message': 'Failed to send OTP.'})
    except Exception as e:
        print(f"Resend OTP error: {str(e)}")
        return jsonify({'status': 'error', 'message': 'Server error'})

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        phone = request.form['phone']
        password = request.form['password']

        # Fetch user from MongoDB
        user = users.find_one({'phone': phone})

        # Compare entered password with stored hashed password
        if user and check_password_hash(user['password'], password):
            session['phone'] = phone  # Store phone number in session
            return redirect(url_for('allproducts_page'))
        else:
            return 'Invalid credentials! *PLEASE SIGN UP*'

    return render_template('index.html')  # Render the login page for GET request

# --------------------------------
# ✅ Logout Route
@app.route('/logout')
def logout():
    session.clear()  # Clear session data
    return redirect(url_for('index'))  # Redirect to homepage after logout


# --------------------------------PRODUCTS PAGE------------------------------------------------

@app.route('/products')
def allproducts_page():
    phone = session.get('phone')  # ✅ Get phone securely from session
    if not phone:
        return redirect(url_for('login'))  # Redirect if no session


    # Fetch user's cart from MongoDB
    user = users.find_one({'phone': phone})
    cart = user.get('cart', []) if user else []  # Get cart if user exists

    return render_template('products.html',   cart=cart)



@app.route('/products/<product_category>')
def product_page(product_category):
    phone = session.get('phone')
    if not phone:
        return redirect(url_for('login'))

    # ✅ Filter products by category
    filtered_products = list(products.find({'category': product_category}))

    # Get user's cart
    user = users.find_one({'phone': phone})
    cart = user.get('cart', []) if user else []

    return render_template('product.html', products=filtered_products, cart=cart)


# Route to display product details
@app.route('/product/<product_id>')
def product_details(product_id):
    # Search only in products collection
    product = mongo.db.products.find_one({'_id': ObjectId(product_id)})

    # If product is not found, return error
    if not product:
        return "Product not found", 404

    # Load related products (you can filter these later by category if needed)
    all_products = list(mongo.db.products.find({
        'category': product.get('category'),
        '_id': {'$ne': product['_id']}  # Exclude the current product
    }))

    return render_template('product_details.html', product=product, products=all_products)


@app.route('/get_cart', methods=['GET'])
def get_cart():
    phone = session.get('phone')
    if not phone:
        return jsonify({'success': False, 'message': 'Unauthorized access please login!'})
    # Fetch the user's cart from the database
    user = users.find_one({'phone': phone})
    cart = user.get('cart', []) if user else []

    return jsonify({'cart': cart})


@app.route('/reduce_from_cart', methods=['POST'])
def reduce_from_cart():
    data = request.json
    phone = session.get('phone')

    if not phone:
        return jsonify({'success': False, 'message': 'Unauthorized access!'})

    product_id = data.get('productId')

    # Convert to ObjectId safely
    try:
        product_id = ObjectId(product_id)
    except Exception as e:
        return jsonify({'success': False, 'message': f'Invalid product ID: {str(e)}'})

    # Find user
    user = users.find_one({'phone': phone})
    if not user:
        return jsonify({'success': False, 'message': 'User not found!'})

    # Check if the product exists in products collection
    product = products.find_one({'_id': product_id})
    if not product:
        return jsonify({'success': False, 'message': 'Product not found!'})

    # Update cart
    cart = user.get('cart', [])
    product_found = False

    for item in cart:
        if item['productId'] == str(product['_id']):
            if item['quantity'] > 1:
                item['quantity'] -= 1
            else:
                cart.remove(item)
            product_found = True
            break

    if not product_found:
        return jsonify({'success': False, 'message': 'Product not found in cart!'})

    # Save the updated cart
    result = users.update_one({'phone': phone}, {'$set': {'cart': cart}})

    if result.modified_count > 0:
        return jsonify({'success': True, 'message': 'Product quantity reduced!'})
    else:
        return jsonify({'success': False, 'message': 'Error updating cart.'})


@app.route('/add_to_cart', methods=['POST'])
def add_to_cart():
    data = request.json
    phone = session.get('phone')

    if not phone:
        return jsonify({'success': False, 'message': 'Unauthorized access!'})

    product_id = data.get('productId')

    # Convert to ObjectId safely
    try:
        product_id = ObjectId(product_id)
    except Exception as e:
        return jsonify({'success': False, 'message': f'Invalid product ID: {str(e)}'})

    # Fetch user
    user = users.find_one({'phone': phone})
    if not user:
        return jsonify({'success': False, 'message': 'User not found!'})

    # Fetch product from `products` only
    product = products.find_one({'_id': product_id})
    if not product:
        return jsonify({'success': False, 'message': 'Product not found!'})

    # Update cart
    cart = user.get('cart', [])
    product_found = False

    for item in cart:
        if item['productId'] == str(product['_id']):
            item['quantity'] += 1
            product_found = True
            break

    if not product_found:
        cart.append({
            'productId': str(product['_id']),
            'name': product['name'],
            'id': product.get('id', ''),  # safely get ID
            'price': product['price'],
            'quantity': 1,
            'image': product['images'][0] if product.get('images') else ''
        })

    print(f"Cart after adding product: {cart}")

    # Save updated cart
    result = users.update_one({'phone': phone}, {'$set': {'cart': cart}})

    if result.modified_count > 0:
        return jsonify({'success': True})
    else:
        return jsonify({'success': False, 'message': 'Error updating cart.'})


@app.route('/remove_from_cart', methods=['POST'])
def remove_from_cart():
    data = request.json
    phone = session.get('phone')

    if not phone:
        return jsonify({'success': False, 'message': 'Unauthorized access!'})

    product_id = data.get('productId')

    # Ensure productId is a valid ObjectId string
    try:
        str_product_id = str(ObjectId(product_id))
    except Exception as e:
        return jsonify({'success': False, 'message': f'Invalid product ID: {str(e)}'})

    # Fetch user
    user = users.find_one({'phone': phone})
    if not user:
        return jsonify({'success': False, 'message': 'User not found!'})

    # Remove the product from the user's cart
    cart = user.get('cart', [])
    updated_cart = [item for item in cart if item['productId'] != str_product_id]

    # Update the user's cart in the database
    result = users.update_one({'phone': phone}, {'$set': {'cart': updated_cart}})

    if result.modified_count > 0:
        return jsonify({'success': True, 'message': 'Product removed from cart!'})
    else:
        return jsonify({'success': False, 'message': 'Error updating cart or product not found in cart.'})



def get_cart_by_phone(phone):
    user = users.find_one({'phone': phone})
    if user:
        cart = user.get('cart', [])
        print(f"User {phone} cart: {cart}")  # Log the cart contents for debugging
        return cart
    else:
        print(f"User {phone} not found")  # Log if user is not found
        return []


@app.route('/cart_count')
def cart_count():
    phone = session.get('phone')

    if not phone:
        return jsonify({'success': False, 'cartItemCount': 0})

    user = users.find_one({'phone': phone})
    if not user:
        return jsonify({'success': False, 'cartItemCount': 0})

    cart = user.get('cart', [])
    total_items = sum(item['quantity'] for item in cart)
    return jsonify({'success': True, 'cartItemCount': total_items})



# Fetch user details by phone
@app.route('/get_user_details')
def get_user_details():
    phone = session.get('phone')
    if not phone:
        return jsonify({'success': False, 'message': 'Unauthorized access!'})

    user = users.find_one({'phone': phone})
    if user:
        return jsonify({'success': True, 'user': {'fullname': user['fullname'], 'phone': user['phone']}})
    else:
        return jsonify({'success': False, 'message': 'User not found'})
# Route to serve static images correctly

@app.route('/get_order_history')
def get_order_history():
    phone = session.get('phone')
    if not phone:
        return jsonify({'success': False, 'message': 'Unauthorized access!'})

    order_history = list(orders.find({'user_phone': phone}))

    if order_history:
        for order in order_history:
            order['_id'] = str(order['_id'])  # Convert order _id to string

            for item in order['items']:
                item['item_id'] = str(item['item_id'])  # Convert item_id to string

                # Fetch product from 'products' collection
                product = products.find_one({'_id': ObjectId(item['item_id'])})

                # Assign first image from images array if exists
                if product and 'images' in product and product['images']:
                    # Use only the first image from the 'images' list
                    item['image'] = f"/static/images/{os.path.basename(product['images'][0])}"
                else:
                    item['image'] = "/static/images/default.jpg"

                print(f"Image for item {item['name']}: {item['image']}")

        return jsonify({'success': True, 'orders': order_history})
    else:
        return jsonify({'success': False, 'message': 'No orders found'})



# --------------------------------CHECKOUT PAGE------------------------------------------------

@app.route('/checkout')
def checkout():
    phone = session.get('phone')
    if not phone:
        return redirect(url_for('login'))

    cart = get_cart_by_phone(phone)
    if not cart:
        print(f"Cart is empty for user {phone}")
        return "Error: Cart is empty"

    session['visited_checkout'] = True  # ✅ Set flag for security user cant directly enter shipping page
    total_price = sum(item['price'] * item['quantity'] for item in cart)
    return render_template('checkout.html', cart=cart, total_price=total_price)



# --------------------------------SHIPPING PAGE------------------------------------------------
@app.route('/shipping', methods=['GET', 'POST'])
def shipping():
    phone = session.get('phone')  # Get phone number from session, this is the user's actual phone number

    if not phone:
        return redirect(url_for('login'))  # If no phone in session, redirect to login

    # ✅ Only allow access if checkout was visited
    if not session.get('visited_checkout'):
        return redirect(url_for('checkout'))

    # ✅ Fetch the user details using the phone from session
    user = users.find_one({'phone': phone})

    # Fetch the cart data for the user using the actual phone number
    cart = get_cart_by_phone(phone)



    if not cart:
        return redirect(url_for('products_page', phone=phone))  # If the cart is empty, go back to the products page

    # Calculate total price for the cart
    subtotal = sum(item['price'] * item['quantity'] for item in cart)
    delivery_charge = 50.00  # ₹50 fixed delivery fee
    discount = subtotal * 0.1  # 10% discount on subtotal
    total_price= subtotal + delivery_charge - discount

    if request.method == 'POST':
        # Get the shipping details from the form

        user_name = user['fullname'] if user else 'Unknown'  # Default to 'Unknown' if not found
        user_phone = request.form['phone']

        name = request.form['name']
        phno = request.form['phno']       # This is the phone number for delivery
        address = request.form['address']
        payment_method = request.form['payment_method']

        # Store the user's details in the session
        session['shipping_details'] = {
            'user_name':user_name,
            'user_phone':user_phone,

            'name': name,
            'phno':phno,
            'address': address,
            'payment_method': payment_method,
            'total_price': total_price
        }

        if payment_method == 'cod':
            # Generate a random 4-digit code
            confirmation_code = ''.join(random.choices(string.digits, k=4))
            session['confirmation_code'] = confirmation_code  # Store the code in the session

            # Redirect to the confirmation page with the generated code
            return redirect(url_for('cod_confirmation'))

        if payment_method == 'Razorpay':
            # Redirect to the online payment page
            return redirect(url_for('pay'))


    return render_template('shipping.html', cart=cart, total_price=total_price)



#-------------------RAZORPAY ROUTES----------------------------------------------------------------------



# Razorpay API keys (replace with your actual keys)
RAZORPAY_KEY_ID = "rzp_test_PFBcx5VoQQl9cf"
RAZORPAY_KEY_SECRET = "b3Z4fl1aMET6dT1SZII8J7Rn"

# Initialize Razorpay client
razorpay_client = razorpay.Client(auth=(RAZORPAY_KEY_ID, RAZORPAY_KEY_SECRET))


@app.route('/pay', methods=['GET', 'POST'])
def pay():
    if 'shipping_details' not in session:
        return redirect(url_for('shipping'))  # Redirect if no shipping details

    shipping_details = session['shipping_details']
    total_price = shipping_details['total_price'] * 100  # Convert to paise

    # Create a Razorpay order
    order_data = {
        'amount': int(total_price),  # Amount in paise
        'currency': 'INR',
        'receipt': f"order_rcpt_{shipping_details['user_phone']}",
        'payment_capture': 1  # Auto-capture payment
    }

    razorpay_order = razorpay_client.order.create(data=order_data)

    # Store order ID in session
    session['razorpay_order_id'] = razorpay_order['id']

    return render_template(
        'pay.html',
        key=RAZORPAY_KEY_ID,
        amount=total_price,
        order_id=razorpay_order['id'],
        user_name=shipping_details['user_name'],
        user_phone=shipping_details['user_phone']
    )


@app.route('/payment_success')
def payment_success():
    payment_id = request.args.get('payment_id')
    order_id = request.args.get('order_id')

    if not payment_id or not order_id:
        return "Error: Payment verification failed."

    # Retrieve order details from session
    shipping_details = session.get('shipping_details')

    if not shipping_details:
        return "Error: Shipping details not found."

    # Get user phone
    phone = session.get('phone')

    if not phone:
        return "Error: User phone not found."

    # Fetch user's email
    user = users.find_one({'phone': phone})
    if not user or 'email' not in user:
        return "Error: User email not found."

    user_email = user['email']

    # Get cart data
    cart = get_cart_by_phone(phone)

    if not cart:
        return "Error: Cart is empty."

    # Create order data for MongoDB
    order_data = {
        'user_phone': phone,
        'user_name': shipping_details['user_name'],
        'name': shipping_details['name'],
        'phno': shipping_details['phno'],
        'address': shipping_details['address'],
        'payment_method': 'Razorpay',
        'total_price': shipping_details['total_price'],
        'items': [
            {
                'item_id': item['productId'],  # Ensure correct field names
                'name': item['name'],
                'id': item['id'],
                'price': item['price'],
                'quantity': item['quantity']
            }
            for item in cart
        ],
        'order_date': datetime.now(),
        'delhivery_status': 'Pending',
        'payment_status': 'Paid',
        'payment_id': payment_id
    }

    # Save order in MongoDB
    orders.insert_one(order_data)

    # ✅ Send email confirmation
    send_order_email(user_email, order_data)

    # Clear user cart after successful payment
    users.update_one({'phone': phone}, {'$set': {'cart': []}})

    session.pop('visited_checkout', None)
    # Clear session
    session.pop('shipping_details', None)
    session.pop('razorpay_order_id', None)

    return render_template('order_success.html', order_data=order_data)





@app.route('/payment_failed')
def payment_failed():
    return render_template('payment_failed.html')




#-------------------CASH ON DELHIVERY ROUTES----------------------------------------------------------------------






@app.route('/cod_confirmation')
def cod_confirmation():

    # Retrieve the confirmation code from the session
    confirmation_code = session.get('confirmation_code')

    # Render the confirmation page with the confirmation code
    return render_template('cod_confirmation.html', confirmation_code=confirmation_code)


# MongoDB Collections
users = mongo.db.users
products = mongo.db.products
orders = mongo.db.orders  # Make sure this line is present



def send_order_email(user_email, order_data):
    """Send an email with the order details."""
    subject = "Order Confirmation - Your Order Has Been Placed!"
    body = f"""
    Hi {order_data['user_name']},

    Your order has been successfully placed! Here are the details:

    📍 **Shipping Address:**  
    {order_data['name']}  
    {order_data['address']}  
    📞 {order_data['phno']}  

    💰 **Total Price:** ₹{order_data['total_price']}  
    💳 **Payment Method:** {order_data['payment_method']}  
    🛒 **Items Ordered:**

    """
    for item in order_data['items']:
        body += f"- {item['id']} {item['name']} (Qty: {item['quantity']}) - ₹{item['price']}\n"

    body += f"\n📅 **Order Date:** {order_data['order_date'].strftime('%Y-%m-%d %H:%M:%S')}\n"
    body += "\n\nThank you for shopping with us! 🚀"

    msg = MIMEText(body)
    msg["From"] = EMAIL_ADDRESS
    msg["To"] = user_email
    msg["Subject"] = subject

    try:
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
            server.sendmail(EMAIL_ADDRESS, user_email, msg.as_string())
        print("✅ Order confirmation email sent successfully!")
    except Exception as e:
        print("❌ Error sending email:", e)




@app.route('/verify_cod', methods=['POST'])
def verify_cod():
    entered_code = (
            request.form.get('code1', '') +
            request.form.get('code2', '') +
            request.form.get('code3', '') +
            request.form.get('code4', '')
    )
    confirmation_code = session.get('confirmation_code')

    if entered_code == confirmation_code:
        # If the entered code is correct, proceed to create the order
        shipping_details = session.get('shipping_details')

        if not shipping_details:
            return "Error: Shipping details not found. Please provide shipping information."

        # Use the phone number from the session
        phone = session.get('phone')  # Get the phone number from session (entered during login)

        if not phone:
            return "Error: Phone number not found. Please log in first."

        # Fetch user's email
        user = users.find_one({'phone': phone})
        if not user or 'email' not in user:
            return "Error: User email not found."

        user_email = user['email']

        # Get the cart data using the phone number from login
        cart = get_cart_by_phone(phone)

        if not cart:
            return "Error: Cart is empty or not found for this phone number."

        # Log cart data to ensure correct values
        print(f"Order data cart: {cart}")

        # Construct order data
        order_data = {
            'user_phone': phone,
            'user_name':shipping_details['user_name'],

            'name': shipping_details['name'],
            'phno': shipping_details['phno'],
            'address': shipping_details['address'],
            'payment_method': shipping_details['payment_method'],
            'total_price': shipping_details['total_price'],
            'items': [
                {
                    'item_id': item['productId'],  # Ensure correct field names
                    'name': item['name'],
                    'id':item['id'],

                    'price': item['price'],
                    'quantity': item['quantity']
                }
                for item in cart  # Ensure this loop is correctly mapping cart items
            ],
            'order_date': datetime.now(),
            'delhivery_status': 'Pending', # Set the order status to "Pending"
            'payment_status': 'COD'  # Set the order status to "Pending"
        }

        # Log the final order_data for debugging
        print(f"Final order data: {order_data}")

        # Insert the order into the MongoDB collection
        orders.insert_one(order_data)

        # ✅ Send email confirmation
        send_order_email(user_email, order_data)

        # ✅ Clear the user's cart after placing the order
        users.update_one({'phone': phone}, {'$set': {'cart': []}})

        session.pop('visited_checkout', None)

        # Clear the session after saving the order
        session.pop('shipping_details', None)
        session.pop('confirmation_code', None)

        return render_template('order_success.html', order_data=order_data)
    else:
        # If the code does not match, show an error message
        return render_template('cod_confirmation.html', error="The entered code is incorrect. Please try again.", confirmation_code=confirmation_code)












@app.after_request
def add_header(response):
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0, post-check=0, pre-check=0'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '-1'
    return response









@app.before_request
def make_session_permanent():
    session.permanent = True


if __name__ == '__main__':
    app.run(debug=True)
