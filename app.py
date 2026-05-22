from flask import Flask, render_template, request, redirect, session, jsonify, url_for
import pymysql
from werkzeug.utils import secure_filename
import os
from math import radians, cos, sin, asin, sqrt
from flask import send_from_directory
import uuid
from flask import Flask, render_template, request, redirect, session
import pymysql
from werkzeug.security import generate_password_hash, check_password_hash



app = Flask(__name__)
app.secret_key = "YOUR_SECRET_KEY"

UPLOAD_FOLDER = "uploads"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'avif','webp'}
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# ------------------- DB Connection -------------------
def get_db_connection():
    return pymysql.connect(
        host="localhost",
        user="root",
        password="",
        database="citypulse",
        cursorclass=pymysql.cursors.DictCursor   # 🔥 IMPORTANT
    )

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.',1)[1].lower() in ALLOWED_EXTENSIONS

def haversine(lat1, lon1, lat2, lon2):
    lat1, lon1, lat2, lon2 = map(float,(lat1,lon1,lat2,lon2))
    lat1, lon1, lat2, lon2 = map(radians,[lat1,lon1,lat2,lon2])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = sin(dlat/2)**2 + cos(lat1)*cos(lat2)*sin(dlon/2)**2
    c = 2*asin(sqrt(a))
    km = 6371*c
    return km

def find_nearest(lat, lon, offices):
    nearest = min(offices, key=lambda x: haversine(lat, lon, x['lat'], x['lon']))
    return nearest

# ------------------- Routes -------------------
@app.route('/')
def home():
    return render_template('index.html')

# ------------------- Login/Register -------------------





 

# ------------------- Register -------------------
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name'].strip()
        email = request.form['email'].strip().lower()
        phone = request.form['phone'].strip()
        age = request.form.get('age')
        gender = request.form.get('gender')
        password = request.form['password']
        confirm_password = request.form['confirm_password']

        if password != confirm_password:
            return "Passwords do not match"

        password_hash = generate_password_hash(password)

        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO users (name, email, phone, age, gender, password)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (name, email, phone, age, gender, password_hash))

        conn.commit()
        cursor.close()
        conn.close()

        return redirect('/login')

    return render_template('register.html')


# ------------------- Login -------------------
from flask import Flask, request, render_template, redirect, session
from werkzeug.security import generate_password_hash, check_password_hash

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        phone = request.form.get('phone').strip()
        password = request.form.get('password')
        role = request.form.get('role')   # 🔥 IMPORTANT

        conn = get_db_connection()
        cursor = conn.cursor()

        # ================= USER LOGIN =================
        if role == 'user':
            cursor.execute("SELECT * FROM users WHERE phone=%s", (phone,))
            user = cursor.fetchone()

            if user and check_password_hash(user['password'], password):
                session['user'] = {
                    'id': user['id'],
                    'name': user['name'],
                    'gender': user.get('gender', '')  # ✅ safe
                }

                cursor.close()
                conn.close()
                return redirect('/dashboard')

            cursor.close()
            conn.close()
            return "Invalid user credentials"

        # ================= ADMIN LOGIN =================
        elif role == 'admin':
            cursor.execute("SELECT * FROM admins WHERE phone=%s", (phone,))
            admin = cursor.fetchone()

            if admin and admin['password'] == password:
                session['admin'] = {
                    'id': admin['id'],
                    'name': admin['name'],
                    'role': admin['role']
                }

                cursor.close()
                conn.close()
                return redirect(f"/admin/{admin['role']}")

            cursor.close()
            conn.close()
            return "Invalid admin credentials"

    return render_template('login.html')

    
# ------------------- User Dashboard -------------------
@app.route('/dashboard')
def dashboard():
    if 'user' not in session:
        return redirect('/')

    conn = get_db_connection()
    cursor = conn.cursor()

    # Fetch civic issues
    cursor.execute("""
        SELECT id, issue_type, status, 'civic' AS category
        FROM civic_issues
        WHERE user_id=%s
    """, (session['user']['id'],))
    civic = cursor.fetchall()

    # Fetch emergencies
    cursor.execute("""
        SELECT id, emergency_type, status, 'emergency' AS category
        FROM emergencies
        WHERE user_id=%s
    """, (session['user']['id'],))
    emergencies = cursor.fetchall()

    cursor.close()
    conn.close()

    # Combine both
    requests = list(civic) + list(emergencies)

    return render_template('dashboard.html', user=session['user'], requests=requests)


# ------------------- Civic/Category Issue -------------------
@app.route('/civic_issue', methods=['GET','POST'])
def civic_issue():
    if 'user' not in session:
        return redirect('/')

    dept = request.args.get('type','civic')

    categories = {
        'civic': ['Road Damage','Garbage','Streetlight Issue'],
        'electricity': ['Power Cut','Transformer Damage','Fallen Electric Pole','Exposed Electric Wires'],
        'water': ['Water Leakage','No Water Supply','Sewer Overflow','Dirty Drinking Water'],
        'animal': ['Injured Animal','Aggressive Stray Dog','Dead Animal on Road','Illegal Animal Transport'],
        'transport': ['Bus Not Arriving','Overcrowded Bus','Rash Driving','Dirty Public Transport','Driver Misbehavior']
    }

    category_info = {
        'civic': {'title':"🏗 Civic Issues",'handled':"Municipal Department"},
        'electricity': {'title':"⚡ Electricity Issues",'handled':"Municipal Department"},
        'water': {'title':"🚰 Water & Sanitation",'handled':"Municipal Department"},
        'animal': {'title':"🐾 Animal & Stray Issues",'handled':"Municipal Department"},
        'transport': {'title':"🚌 Transport Issues",'handled':"Municipal Department"}
    }

    if request.method=='POST':
        issue_type = request.form.get('description')
        category = request.form.get('issue_type')
        lat = request.form.get('lat')
        lon = request.form.get('lon')
        manual_location = request.form.get('manual_location','')

        file = request.files.get('image')
        filename = None
 
        if file and file.filename != "" and allowed_file(file.filename):

            ext = file.filename.rsplit('.',1)[1].lower()

            import uuid
            filename = str(uuid.uuid4()) + "." + ext

            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id, lat, lon FROM admins WHERE role='Municipal'")
        admins = cursor.fetchall()
        lat = float(lat) if lat else 18.5204
        lon = float(lon) if lon else 73.8567

        nearest = find_nearest(lat, lon, admins)

        cursor.execute("""
            INSERT INTO civic_issues
            (user_id, category, issue_type, description, image, lat, lon, manual_location, assigned_admin, status)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,'SUBMITTED')
        """,(session['user']['id'],category,issue_type,issue_type,filename,lat,lon,manual_location,nearest['id']))
        conn.commit()
        cursor.close()
        conn.close()
        return redirect(url_for('civic_issue', type=issue_type, success=1))


    return render_template('civic_issue.html', dept=dept, categories=categories, info=category_info)
#----------------------Emergency------------------------------
@app.route('/emergency', methods=['GET', 'POST'])
def emergency():
    if 'user' not in session:
        return redirect('/')

    if request.method == 'POST':
        emergency_type = request.form.get('emergency_type')
        lat_str = request.form.get('lat')
        lon_str = request.form.get('lon')
        manual_location = request.form.get('manual_location', '')

        # Validate lat/lon
        try:
            lat = float(lat_str)
            lon = float(lon_str)
        except (TypeError, ValueError):
            return jsonify({'status': 'error', 'message': 'Invalid location coordinates'})

        # Handle image
        image = request.files.get('image')
        filename = None
        if image and image.filename != "" and allowed_file(image.filename):
            ext = image.filename.rsplit('.', 1)[1].lower()
            filename = str(uuid.uuid4()) + "." + ext
            image.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

        # Determine role
        if emergency_type.lower() == "medical":
            role = "Ambulance"
        elif emergency_type.lower() == "fire":
            role = "Fire"
        else:
            return jsonify({'status': 'error', 'message': 'Invalid emergency type'})

        # Fetch admins
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id, lat, lon FROM admins WHERE role=%s", (role,))
        admins = cursor.fetchall()
        if not admins:
            cursor.close()
            conn.close()
            return jsonify({'status': 'error', 'message': f'No {role} admin available'})

        # Find nearest admin
        nearest = find_nearest(lat, lon, admins)

        # Insert emergency
        cursor.execute("""
            INSERT INTO emergencies
            (user_id, emergency_type, lat, lon, manual_location, image, status, assigned_admin)
            VALUES (%s,%s,%s,%s,%s,%s,'SUBMITTED',%s)
        """, (session['user']['id'], emergency_type, lat, lon, manual_location, filename, nearest['id']))
        conn.commit()
        cursor.close()
        conn.close()

        

    return render_template('emergency.html')
# ------------------- Women SOS -------------------
@app.route('/women_safety', methods=['GET', 'POST'])
def women_safety():
    if 'user' not in session or session['user']['gender'].lower() != 'female':
        return "Access denied"

    conn = get_db_connection()
    cursor = conn.cursor()

    if request.method == 'POST':
        # Data sent from JS (geolocation)
        data = request.get_json()
        lat = data['lat']
        lon = data['lon']

        # Get nearest police (static nearest admin)
        cursor.execute("SELECT id, lat, lon FROM admins WHERE role='Police'")
        police = cursor.fetchall()
        nearest = find_nearest(float(lat), float(lon), police)

        # Insert new alert if not exists, else update location dynamically
        cursor.execute("""
            INSERT INTO women_alerts (user_id, lat, lon, assigned_police, status)
            VALUES (%s, %s, %s, %s, 'SUBMITTED')
            ON DUPLICATE KEY UPDATE lat=%s, lon=%s
        """, (session['user']['id'], lat, lon, nearest['id'], lat, lon))

        conn.commit()
        cursor.close()
        conn.close()
        return jsonify({'status':'sent'})

    # GET request → render page
    cursor.close()
    conn.close()
    return render_template('women_safety.html')

# ------------------- Admin Dashboard -------------------
@app.route('/admin/<role>')
def admin_dashboard(role):
    if 'admin' not in session:
        return redirect('/')

    conn = get_db_connection()
    cursor = conn.cursor(pymysql.cursors.DictCursor)

    role = role.lower()   # ✅ normalize once

    # ---------------- MUNICIPAL ----------------
    if role == 'municipal':
        cursor.execute("""
            SELECT ci.id,
                   ci.category,
                   ci.issue_type,
                   ci.image,
                   ci.manual_location,
                   ci.lat,
                   ci.lon,
                   u.name,
                   u.phone,
                   ci.status
            FROM civic_issues ci
            JOIN users u ON ci.user_id = u.id
            WHERE ci.assigned_admin=%s
            ORDER BY ci.id DESC
        """, (session['admin']['id'],))

    # ---------------- POLICE ----------------
    elif role == 'police':
        cursor.execute("""
            SELECT w.id,
                   'Women SOS' AS issue_type,
                   NULL AS image,
                   w.lat,
                   w.lon,
                   u.name,
                   u.phone,
                   w.status
            FROM women_alerts w
            JOIN users u ON w.user_id = u.id
            WHERE w.assigned_police=%s
            ORDER BY w.id DESC
        """, (session['admin']['id'],))

    # ---------------- OTHER (AMBULANCE / FIRE) ----------------
    else:
        cursor.execute("""
            SELECT e.id,
                   e.emergency_type AS issue_type,
                   e.image,
                   e.lat,
                   e.lon,
                   u.name,
                   u.phone,
                   e.status
            FROM emergencies e
            JOIN users u ON e.user_id = u.id
            WHERE e.assigned_admin=%s
            ORDER BY e.id DESC
        """, (session['admin']['id'],))

    assigned = cursor.fetchall()

    # ✅ DEBUG (remove later)
    print("ADMIN ID:", session['admin']['id'])
    print("TOTAL ASSIGNED:", len(assigned))

    cursor.close()
    conn.close()

    return render_template(
        'admin_dashboard.html',
        role=role.capitalize(),   # keeps UI same
        admin=session['admin'],
        assigned=assigned
    )
# ------------------- Admin Track -------------------
@app.route('/admin/track/<role>/<int:item_id>')
def admin_track_item(role, item_id):
    if 'admin' not in session:
        return redirect('/')

    conn = get_db_connection()
    cursor = conn.cursor()

    if role == 'Municipal':
        cursor.execute("""
            SELECT ci.*, u.name, u.phone, u.id as user_id
            FROM civic_issues ci
            JOIN users u ON ci.user_id=u.id
            WHERE ci.id=%s
        """, (item_id,))
        request_type = "civic"

    else:
        cursor.execute("""
            SELECT e.*, u.name, u.phone, u.id as user_id
            FROM emergencies e
            JOIN users u ON e.user_id=u.id
            WHERE e.id=%s
        """, (item_id,))
        request_type = "emergency"

    item = cursor.fetchone()
    cursor.close()
    conn.close()

    return render_template(
        'tracking.html',
        item=item,
        role=role,
        admin=session['admin'],
        request_type=request_type,
        request_id=item_id
    )

# ------------------- Update Status -------------------
@app.route('/admin/update_status', methods=['POST'])
def update_status():
    if 'admin' not in session:
        return redirect('/')
    role = request.form['role']
    item_id = request.form['item_id']
    status = request.form['status']

    conn = get_db_connection()
    cursor = conn.cursor()
    if role=='Municipal':
        cursor.execute("UPDATE civic_issues SET status=%s WHERE id=%s", (status,item_id))
    elif role=='Police':
        cursor.execute("UPDATE women_alerts SET status=%s WHERE id=%s", (status,item_id))
    else:
        cursor.execute("UPDATE emergencies SET status=%s WHERE id=%s", (status,item_id))
    conn.commit()
    cursor.close()
    conn.close()
    return redirect(f"/admin/{role}")

# 

#----------------------------------------------------------------------------------------------     
@app.route('/city_info')
def city_info():
    return render_template("city_info.html") 

# ---------------- User Requests ----------------
# ---------------- User Requests ----------------
@app.route('/user/requests')
def user_requests():

    if 'user' not in session:
        return redirect('/')

    user_id = session['user']['id']

    conn = get_db_connection()
    cursor = conn.cursor()

    # Civic Issues
    cursor.execute("""
        SELECT id, issue_type, status, 'civic' AS category
        FROM civic_issues
        WHERE user_id=%s
    """, (user_id,))
    civic_rows = cursor.fetchall()

    civic = []
    for r in civic_rows:
        civic.append({
            "id": r['id'],
            "issue_type": r['issue_type'],
            "status": r['status'],
            "category": r['category']
        })

    # Emergencies
    cursor.execute("""
        SELECT id, emergency_type, status, 'emergency' AS category
        FROM emergencies
        WHERE user_id=%s
    """, (user_id,))
    emergency_rows = cursor.fetchall()

    emergencies = []
    for r in emergency_rows:
        emergencies.append({
            "id": r['id'],
            "emergency_type": r['emergency_type'],
            "status": r['status'],
            "category": r['category']
        })

    cursor.close()
    conn.close()

    requests = civic + emergencies

    return render_template(
        'user_requests.html',
        user=session['user'],
        requests=requests
    )

    if 'user' not in session:
        return redirect('/')

    user_id = session['user']['id']

    conn = get_db_connection()
    cursor = conn.cursor()

    # Civic issues
    cursor.execute("""
        SELECT id, issue_type, status, 'civic' AS category
        FROM civic_issues
        WHERE user_id=%s
    """, (user_id,))
    civic_rows = cursor.fetchall()

    civic = []
    for r in civic_rows:
        civic.append({
            'id': r[0],
            'issue_type': r[1],
            'status': r[2],
            'category': r[3]
        })

    # Emergencies
    cursor.execute("""
        SELECT id, emergency_type, status, 'emergency' AS category
        FROM emergencies
        WHERE user_id=%s
    """, (user_id,))
    emergency_rows = cursor.fetchall()

    emergencies = []
    for r in emergency_rows:
        emergencies.append({
            'id': r[0],
            'emergency_type': r[1],
            'status': r[2],
            'category': r[3]
        })

    cursor.close()
    conn.close()

    requests = civic + emergencies

    return render_template('user_requests.html',
                           user=session['user'],
                           requests=requests)
#---------------------------------------------------------

# -------------------------------
# SEND MESSAGE

# ✅ SEND MESSAGE
@app.route('/send_message', methods=['POST'])
def send_message():
    data = request.json

    # ✅ Normalize sender (VERY IMPORTANT)
    sender = str(data.get('sender')).strip().lower()

    if sender not in ['user', 'admin']:
        sender = 'user'  # default safety

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO chat_messages 
        (request_type, request_id, sender, sender_id, message)
        VALUES (%s, %s, %s, %s, %s)
    """, (
        data['request_type'],
        data['request_id'],
        sender,                # ✅ fixed
        data['sender_id'],
        data['message']
    ))

    conn.commit()
    cursor.close()
    conn.close()

    return jsonify({"status": "success"})
#--------------------------------------------------------------------------------------

# ✅ GET MESSAGES
from datetime import timedelta

@app.route('/get_messages/<request_type>/<int:request_id>')
def get_messages(request_type, request_id):

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT sender, message, created_at
        FROM chat_messages
        WHERE request_type=%s AND request_id=%s
        ORDER BY created_at ASC
    """, (request_type, request_id))

    messages = cursor.fetchall()

    result = []

    for m in messages:
        # ✅ FIX sender
        sender = str(m['sender']).strip().lower()

        if sender not in ['user', 'admin']:
            sender = 'admin'

        # ✅ FIX datetime
        created_at = ""
        if m['created_at']:
            created_at = m['created_at'].strftime('%Y-%m-%d %H:%M:%S')

        result.append({
            "sender": sender,
            "message": m['message'],
            "created_at": created_at
        })

    cursor.close()
    conn.close()

    return jsonify(result)
#--------------------------------------------------------------------------------------




import requests
from flask import request, jsonify
import requests

@app.route('/get_user_location/<int:user_id>')
def get_user_location(user_id):
    conn = get_db_connection()
    cursor = conn.cursor(pymysql.cursors.DictCursor)

    cursor.execute("SELECT lat, lon, manual_location FROM civic_issues WHERE user_id=%s ORDER BY id DESC LIMIT 1", (user_id,))
    loc = cursor.fetchone()
    cursor.close()
    conn.close()

    lat = loc['lat']
    lon = loc['lon']

    # If lat/lon missing, but manual_location exists → geocode using OpenStreetMap Nominatim
    if (not lat or not lon) and loc.get('manual_location'):
        try:
            url = "https://nominatim.openstreetmap.org/search"
            params = {
                "q": loc['manual_location'],
                "format": "json",
                "limit": 1
            }
            headers = {"User-Agent": "CityPulse-App"}
            resp = requests.get(url, params=params, headers=headers, timeout=5)
            data = resp.json()
            if data:
                lat = float(data[0]['lat'])
                lon = float(data[0]['lon'])
        except Exception as e:
            print("Geocoding error:", e)
            lat = 18.5204  # fallback Pune lat
            lon = 73.8567  # fallback Pune lon

    return jsonify({"lat": lat, "lon": lon})
#----------------------------------------


#----------------------------------------

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)


    

# ------------------- Logout -------------------

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')

if __name__=='__main__':
    app.run(host="0.0.0.0",debug=True)
