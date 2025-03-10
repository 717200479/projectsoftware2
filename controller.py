# controller.py
import re
from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from model import *

app = Flask(__name__)
app.secret_key = 'your_secret_key'

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/tools_boxes')
def tools_boxes():
    return render_template('tools_boxes.html')

@app.route('/imei_services')
def imei_services():
    return render_template('imei_services.html')

@app.route('/remote')
def remote():
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute('SELECT DISTINCT brand FROM services')
    brands = cursor.fetchall()
    conn.close()
    
    return render_template('remote.html', brands=brands)

@app.route('/services/<brand>', methods=['GET'])
def get_services(brand):
    services = get_services_by_brand(brand)
    services_list = [{'name': service[0], 'description': service[1], 'price': service[2], 'requirements': service[3]} for service in services]
    return jsonify(services_list)

@app.route('/user_details')
def user_details():
    if 'user_id' not in session:
        flash('يجب تسجيل الدخول لعرض التفاصيل.', 'danger')
        return redirect(url_for('login'))

    user_id = session['user_id']
    user = get_user_by_id(user_id)
    
    if user:
        logger.info(f"Fetched user details for user ID {user_id}")
        return render_template('user_details.html', user=user)
    else:
        flash('لم يتم العثور على المستخدم.', 'danger')
        return redirect(url_for('home'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
        phone = request.form['phone']
        smartphone_services = request.form['smartphone_services']
        
        if len(password) < 8 or not re.search(r'[A-Za-z]', password) or not re.search(r'\d', password) or not re.search(r'[\W_]', password):
            flash('خطأ: يجب أن تتكون كلمة المرور من 8 أحرف على الأقل، وتحتوي على أحرف وأرقام ورموز خاصة.', 'danger')
            return render_template('register.html')

        password_hashed = hash_password(password)
        
        try:
            add_user(username, password_hashed, email, phone, smartphone_services == 'yes')
            flash('تم التسجيل بنجاح! يمكنك الآن تسجيل الدخول.', 'success')
            logger.info(f"User registered: {username}")
            return redirect(url_for('login'))
        except sqlite3.IntegrityError:
            flash('اسم المستخدم أو البريد الإلكتروني موجود بالفعل!', 'danger')
            logger.warning(f"Registration failed for {username}: User already exists.")
    
    return render_template('register.html')

@app.route('/users', methods=['GET'])
def list_users():
    users = get_all_users()
    return jsonify(users)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = hash_password(request.form['password'])
        
        user = get_user_by_username(username)
        
        if user and user[2] == password:
            session['user_id'] = user[0]
            session['is_admin'] = user[6]
            flash('Logged in successfully!', 'success')
            logger.info(f"User logged in: {username}")
            return redirect(url_for('balance'))
        else:
            flash('Invalid username or password!', 'danger')
            logger.warning(f"Login failed for {username}: Invalid credentials.")
    
    return render_template('login.html')

@app.route('/increase_credit', methods=['POST'])
def increase_credit():
    username = request.form['username']
    password = request.form['password']
    credit_to_add = request.form['credit']

    user = get_user_by_username(username)
    if user and user[2] == hash_password(password):
        update_user_credit(user[0], credit_to_add)
        flash('تم زيادة الرصيد بنجاح!', 'success')
        logger.info(f"Credit increased for user: {username}")
    else:
        flash('اسم المستخدم أو كلمة المرور غير صحيحة!', 'danger')
        logger.warning(f"Credit increase failed for {username}: Invalid credentials.")

    return redirect(url_for('manage_services'))

@app.route('/admin/services', methods=['GET', 'POST'])
def manage_services():
    if request.method == 'POST':
        if 'add' in request.form:
            brand = request.form['brand']
            name = request.form['name']
            price = request.form['price']
            description = request.form['description']
            requirements = request.form['requirements']
            add_service(brand, name, price, description, requirements)
            flash('تم إضافة الخدمة بنجاح!', 'success')
            logger.info(f"Service added: {name}")

        elif 'delete' in request.form:
            service_id = request.form['service_id']
            delete_service(service_id)
            flash('تم حذف الخدمة بنجاح!', 'success')
            logger.info(f"Service deleted: {service_id}")

        elif 'edit' in request.form:
            service_id = request.form['service_id']
            brand = request.form['brand']
            name = request.form['name']
            price = request.form['price']
            description = request.form['description']
            requirements = request.form['requirements']
            update_service(service_id, brand, name, price, description, requirements)
            flash('تم تعديل الخدمة بنجاح!', 'success')
            logger.info(f"Service updated: {service_id}")

    users = get_all_users()
    services = get_all_services()
    
    return render_template('manage_services.html', services=services, users=users)

@app.route('/balance')
def balance():
    if 'user_id' in session:
        user = get_user_by_id(session['user_id'])
        if user:
            return render_template('index.html', balance=user[3])
    return redirect(url_for('login'))

@app.route('/logout')
def logout():
    session.clear()
    flash('Logged out successfully!', 'success')
    logger.info("User logged out.")
    return redirect(url_for('home'))
