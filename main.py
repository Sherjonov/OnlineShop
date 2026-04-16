#!/usr/bin/env python3
"""
QUVVAT.MARKET — Flask Backend
Run: python app.py
"""

from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import json, os, time, random, string, hashlib
from datetime import datetime, timedelta
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

app = Flask(__name__, static_folder='../frontend/dist', static_url_path='/')
CORS(app, origins=['http://localhost:3000', 'http://localhost:5000'])

# ─── Config ────────────────────────────────────────────────────────────────
SECRET_KEY = 'quvvat_market_secret_2025'
DATA_FILE   = 'data.json'

SMTP_HOST   = 'smtp.gmail.com'
SMTP_PORT   = 587
SMTP_USER   = 'abduazizsherjonov7@gmail.com'
SMTP_PASS   = ''           # Gmail App Password ni shu yerga yozing
ADMIN_EMAIL = 'abduazizsherjonov7@gmail.com'

# ─── Data layer ─────────────────────────────────────────────────────────────
def load_data():
    if not os.path.exists(DATA_FILE):
        return default_data()
    with open(DATA_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_data(d):
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(d, f, ensure_ascii=False, indent=2)

def default_data():
    data = {
        'users': [
            {
                'id': 1,
                'username': 'Sherjonov',
                'name': 'Abduaziz',
                'surname': 'Sherjonov',
                'email': 'abduazizsherjonov357@gmail.com',
                'password': hash_pass('abushka2011'),
                'role': 'admin',
                'created_at': time.time()
            }
        ],
        'products': build_default_products(),
        'orders': [],
        'activity': [],
        'messages': [],
        'likes': {},
        'views': {},
        'otp_store': {}   # {email: {code, expires}}
    }
    save_data(data)
    return data

def build_default_products():
    return [
        # ── FastFood ──────────────────────────────────────────────────────
        {'id':1,'cat':'fastfood','emoji':'🍔','name':'Classic Burger','desc':"Mol go'shti, kesmik, sabzavotlar",'price':35000,'badge':'hot','image':'https://images.unsplash.com/photo-1568901346375-23c9450c58cd?w=400&q=80','variants':['Kichik (25cm)','O\'rta (30cm)','Katta (35cm)']},
        {'id':2,'cat':'fastfood','emoji':'🍟','name':'Katta Kartoshka','desc':"Tuz va sous bilan",'price':18000,'badge':'','image':'https://images.unsplash.com/photo-1573080496219-bb080dd4f877?w=400&q=80','variants':['Kichik (100g)','O\'rta (200g)','Katta (350g)']},
        {'id':3,'cat':'fastfood','emoji':'🌮','name':'Taco Supreme','desc':"Go'sht, avokado, salsa",'price':28000,'badge':'new','image':'https://images.unsplash.com/photo-1565299585323-38d6b0865b47?w=400&q=80','variants':['1 dona','2 dona','3 dona']},
        {'id':4,'cat':'fastfood','emoji':'🌯','name':'Shawarma Grand','desc':"Tovuq, sabzavotlar",'price':32000,'badge':'hot','image':'https://images.unsplash.com/photo-1600850056064-a8b380df8395?w=400&q=80','variants':["Tovuq go'shti","Mol go'shti","Qo'zichoq"]},
        {'id':5,'cat':'fastfood','emoji':'🍕','name':'Pizza Margarita','desc':"Mozzarella, tomat",'price':55000,'badge':'','image':'https://images.unsplash.com/photo-1574071318508-1cdbab80d002?w=400&q=80','variants':['26 sm','32 sm','40 sm']},
        {'id':6,'cat':'fastfood','emoji':'🌭','name':'Hot Dog','desc':"Kolbasa, gorchitsa, ketchup",'price':22000,'badge':'','image':'https://images.unsplash.com/photo-1612392062631-94b8ae13b04e?w=400&q=80','variants':['Classic','Cheese','BBQ']},
        {'id':7,'cat':'fastfood','emoji':'🍗','name':'Tovuq Qanotlari','desc':"10 dona, achchiq sous",'price':48000,'badge':'hot','image':'https://images.unsplash.com/photo-1527477396000-e27163b481c2?w=400&q=80','variants':['6 dona','10 dona','15 dona']},
        {'id':8,'cat':'fastfood','emoji':'🥪','name':'Club Sandwich','desc':"Tovuq, tuxum, pomidor",'price':38000,'badge':'','image':'https://images.unsplash.com/photo-1528736235302-52922df5c122?w=400&q=80','variants':['Classic','Double','Triple']},
        {'id':9,'cat':'fastfood','emoji':'🍖','name':"BBQ Qovurg'a",'desc':"Mol qovurg'asi BBQ",'price':72000,'badge':'hot','image':'https://images.unsplash.com/photo-1544025162-d76694265947?w=400&q=80','variants':['500g','750g','1kg']},
        {'id':10,'cat':'fastfood','emoji':'🥙','name':'Donner Kebab','desc':"Mol go'shti, lavash",'price':35000,'badge':'new','image':'https://images.unsplash.com/photo-1561651823-34feb02250e4?w=400&q=80','variants':["Kichik","O'rta","Katta"]},
        {'id':11,'cat':'fastfood','emoji':'🧆','name':'Falafel Wrap','desc':"Nohot, sabzavot, sous",'price':28000,'badge':'','image':'https://images.unsplash.com/photo-1593001874117-c99c800e3eb8?w=400&q=80','variants':['1 dona','2 dona','3 dona']},
        {'id':12,'cat':'fastfood','emoji':'🍱','name':'Combo Box','desc':"Burger + kartoshka + ichimlik",'price':55000,'badge':'sale','image':'https://images.unsplash.com/photo-1576107232684-1279f814f08d?w=400&q=80','variants':['Kichik combo','O\'rta combo','Katta combo']},
        {'id':13,'cat':'fastfood','emoji':'🥚','name':'Tuxumli Burger','desc':"Ikkita tuxum, bacon",'price':42000,'badge':'','image':'https://images.unsplash.com/photo-1551782450-17144efb9c50?w=400&q=80','variants':['Single egg','Double egg','Triple egg']},
        {'id':14,'cat':'fastfood','emoji':'🍣','name':'Sushi Roll','desc':"Losos, avokado, nori",'price':65000,'badge':'new','image':'https://images.unsplash.com/photo-1617196034183-421b4040ed20?w=400&q=80','variants':['6 dona','8 dona','12 dona']},

        # ── Drinks ────────────────────────────────────────────────────────
        {'id':15,'cat':'drinks','emoji':'🥤','name':'Coca-Cola','desc':"0.5L sovuq",'price':12000,'badge':'cold','image':'https://images.unsplash.com/photo-1622483767028-3f66f32aef97?w=400&q=80','variants':['0.25L','0.5L','1L']},
        {'id':16,'cat':'drinks','emoji':'☕','name':'Cappuccino','desc':"Double espresso",'price':22000,'badge':'hot','image':'https://images.unsplash.com/photo-1572442388796-11668a67e53d?w=400&q=80','variants':['Small 200ml','Medium 300ml','Large 400ml']},
        {'id':17,'cat':'drinks','emoji':'🧋','name':'Bubble Tea','desc':"Taro, mango",'price':28000,'badge':'new','image':'https://images.unsplash.com/photo-1558857563-b371033873b8?w=400&q=80','variants':['Taro','Mango','Strawberry','Classic Black']},
        {'id':18,'cat':'drinks','emoji':'🍵','name':"Ko'k Choy",'desc':"Premium Xitoy choyi",'price':15000,'badge':'','image':'https://images.unsplash.com/photo-1556679343-c7306c1976bc?w=400&q=80','variants':["Issiq",'Sovuq (iced)','Zanjabil bilan']},
        {'id':19,'cat':'drinks','emoji':'🥛','name':'Milk Shake','desc':"Shokolad, vanilya",'price':24000,'badge':'hot','image':'https://images.unsplash.com/photo-1568901346375-23c9450c58cd?w=400&q=80','variants':['Shokolad','Vanilya','Qulupnay','Karamel']},
        {'id':20,'cat':'drinks','emoji':'🍊','name':'Apelsin Sharbati','desc':"Yangi siqilgan, 0.4L",'price':18000,'badge':'new','image':'https://images.unsplash.com/photo-1622597467836-f3285f2131b8?w=400&q=80','variants':['0.3L','0.4L','0.6L']},
        {'id':21,'cat':'drinks','emoji':'🍋','name':'Limonata','desc':"Limon, nanaa, sovuq",'price':16000,'badge':'cold','image':'https://images.unsplash.com/photo-1621263764928-df1444c5e859?w=400&q=80','variants':['Klassik','Nanali','Zanjabillik','Qulupnayli']},
        {'id':22,'cat':'drinks','emoji':'🧃','name':'Meva Sharbati','desc':"Olma, anor, uzum",'price':14000,'badge':'','image':'https://images.unsplash.com/photo-1600271886742-f049cd451bba?w=400&q=80','variants':['Olma','Anor','Uzum','Terescha']},
        {'id':23,'cat':'drinks','emoji':'☕','name':'Americano','desc':"Double shot, issiq",'price':18000,'badge':'','image':'https://images.unsplash.com/photo-1509042239860-f550ce710b93?w=400&q=80','variants':['Single','Double','Triple']},
        {'id':24,'cat':'drinks','emoji':'🍫','name':'Issiq Kakao','desc':"Sut bilan, kremli",'price':20000,'badge':'hot','image':'https://images.unsplash.com/photo-1542990253-0d0f5be5f0ed?w=400&q=80','variants':['Kichik','O\'rta','Katta']},
        {'id':25,'cat':'drinks','emoji':'🥤','name':'Pepsi Max','desc':"0.5L, shakar yo'q",'price':12000,'badge':'cold','image':'https://images.unsplash.com/photo-1629203851122-3726555cf89c?w=400&q=80','variants':['0.25L','0.5L','1L']},
        {'id':26,'cat':'drinks','emoji':'🍵','name':'Qora Choy','desc':"Hind choyi, limon",'price':12000,'badge':'','image':'https://images.unsplash.com/photo-1564890369478-c89ca6d9cde9?w=400&q=80','variants':['Limon bilan','Sut bilan','Asal bilan']},
        {'id':27,'cat':'drinks','emoji':'🧉','name':'Energetik Ichimlik','desc':"Red Bull 0.25L",'price':22000,'badge':'hot','image':'https://images.unsplash.com/photo-1613919113640-25732ec5e61f?w=400&q=80','variants':['0.25L','0.35L','0.5L']},
        {'id':28,'cat':'drinks','emoji':'🍹','name':'Mango Smoothie','desc':"Mango, banan, sut",'price':26000,'badge':'new','image':'https://images.unsplash.com/photo-1623065422902-30a2d299bbe4?w=400&q=80','variants':['Mango','Banan','Qulupnay','Aralash']},

        # ── Milliy ────────────────────────────────────────────────────────
        {'id':29,'cat':'milliy','emoji':'🍚','name':'Palov','desc':"Mol go'shti, sabzi",'price':48000,'badge':'hot','image':'https://images.unsplash.com/photo-1588166524941-3bf61a9c41db?w=400&q=80','variants':['Kichik (300g)','O\'rta (500g)','Katta (700g)']},
        {'id':30,'cat':'milliy','emoji':'🥟','name':'Manti','desc':"Qo'zichoq, piyoz",'price':42000,'badge':'hot','image':'https://images.unsplash.com/photo-1496116218417-1a781b1c416c?w=400&q=80','variants':['6 dona','10 dona','16 dona']},
        {'id':31,'cat':'milliy','emoji':'🍲','name':'Shurpa','desc':"Qo'zichoq, sabzavotlar",'price':38000,'badge':'new','image':'https://images.unsplash.com/photo-1547592180-85f173990554?w=400&q=80','variants':['Kichik (400ml)','O\'rta (600ml)','Katta (1L)']},
        {'id':32,'cat':'milliy','emoji':'🥩','name':'Dimlama','desc':"Mol go'shti, sabzavotlar",'price':52000,'badge':'','image':'https://images.unsplash.com/photo-1504674900247-0877df9cc836?w=400&q=80','variants':['1 porsiya','2 porsiya','Oila (4 porsiya)']},
        {'id':33,'cat':'milliy','emoji':'🍢','name':'Kabob','desc':"Qo'zichoq kabob",'price':55000,'badge':'hot','image':'https://images.unsplash.com/photo-1544025162-d76694265947?w=400&q=80','variants':['3 shampurli','5 shampurli','8 shampurli']},
        {'id':34,'cat':'milliy','emoji':'🥣','name':'Mastava','desc':"Guruch, go'sht, sabzavot",'price':35000,'badge':'','image':'https://images.unsplash.com/photo-1547592180-85f173990554?w=400&q=80','variants':['Kichik','O\'rta','Katta']},
        {'id':35,'cat':'milliy','emoji':'🥟','name':'Chuchvara','desc':"Go'sht to'ldirilgan",'price':38000,'badge':'new','image':'https://images.unsplash.com/photo-1496116218417-1a781b1c416c?w=400&q=80','variants':['10 dona','20 dona','30 dona']},
        {'id':36,'cat':'milliy','emoji':'🍞','name':'Non (Toshkent)','desc':"Yangi yopilgan",'price':8000,'badge':'','image':'https://images.unsplash.com/photo-1509440159596-0249088772ff?w=400&q=80','variants':['Kichik','O\'rta','Katta']},
        {'id':37,'cat':'milliy','emoji':'🥣','name':'Norin','desc':"Ot go'shti, qiyma",'price':45000,'badge':'hot','image':'https://images.unsplash.com/photo-1557499305-0af888c3d8ec?w=400&q=80','variants':['1 porsiya','2 porsiya','3 porsiya']},
        {'id':38,'cat':'milliy','emoji':'🍜','name':"Lag'mon",'desc':"Qo'lda yoylgan",'price':42000,'badge':'hot','image':'https://images.unsplash.com/photo-1569718212165-3a8278d5f624?w=400&q=80','variants':["Qo'lda yoylgan","Uy uslubida","Qovurma lag'mon"]},
        {'id':39,'cat':'milliy','emoji':'🥘','name':'Qovurma','desc':"Mol go'shti qovurma",'price':48000,'badge':'','image':'https://images.unsplash.com/photo-1504674900247-0877df9cc836?w=400&q=80','variants':['300g','500g','700g']},
        {'id':40,'cat':'milliy','emoji':'🫕','name':"Osh ko'za",'desc':"Katta ko'zada palov",'price':65000,'badge':'new','image':'https://images.unsplash.com/photo-1585325701956-60dd9c8553bc?w=400&q=80','variants':['Kichik ko\'za','O\'rta ko\'za','Katta ko\'za']},
        {'id':41,'cat':'milliy','emoji':'🥩','name':'Tandir Kabob','desc':"Tandirda pishirilgan",'price':68000,'badge':'hot','image':'https://images.unsplash.com/photo-1544025162-d76694265947?w=400&q=80','variants':['3 dona','5 dona','7 dona']},
    ]

def hash_pass(p):
    return hashlib.sha256(p.encode()).hexdigest()

def gen_token(uid):
    payload = f'{uid}:{time.time()}:{SECRET_KEY}'
    return hashlib.sha256(payload.encode()).hexdigest()[:32] + str(uid)

def get_user_from_token(token):
    if not token or len(token) < 33:
        return None
    try:
        uid = int(token[32:])
        d = load_data()
        return next((u for u in d['users'] if u['id'] == uid), None)
    except:
        return None

def send_email(to_email, subject, html_body):
    """Send email via SMTP. Returns True/False"""
    try:
        msg = MIMEMultipart('alternative')
        msg['Subject'] = subject
        msg['From']    = SMTP_USER
        msg['To']      = to_email
        msg.attach(MIMEText(html_body, 'html'))
        with smtplib.SMTP(SMTP_HOST, SMTP_PORT, timeout=10) as s:
            s.starttls()
            s.login(SMTP_USER, SMTP_PASS)
            s.sendmail(SMTP_USER, to_email, msg.as_string())
        return True
    except Exception as e:
        print(f'[EMAIL ERROR] {e}')
        return False

def otp_email_html(code, purpose='tasdiqlash'):
    return f"""
    <div style="font-family:Arial;max-width:480px;margin:auto;background:#0d0d1a;color:#f0f0fa;padding:40px;border-radius:16px">
      <h2 style="color:#ff2d55;font-size:28px;margin-bottom:4px">⚡ QUVVAT.MARKET</h2>
      <p style="color:#606080;font-size:12px;letter-spacing:2px;text-transform:uppercase">Premium Food & Drinks</p>
      <hr style="border-color:#222;margin:24px 0">
      <h3 style="font-size:18px;margin-bottom:16px">📬 {purpose.title()} kodi</h3>
      <div style="background:#1c1c2e;border:2px solid #ff2d55;border-radius:12px;padding:24px;text-align:center;margin:20px 0">
        <div style="font-size:42px;font-weight:900;letter-spacing:12px;color:#ff8c00;font-family:monospace">{code}</div>
        <div style="color:#606080;font-size:12px;margin-top:8px">Kod 10 daqiqa amal qiladi</div>
      </div>
      <p style="color:#606080;font-size:13px">Agar siz bu amalni bajarmagan bo'lsangiz, ushbu xabarni e'tiborsiz qoldiring.</p>
      <hr style="border-color:#222;margin:24px 0">
      <p style="color:#303050;font-size:11px;text-align:center">© 2025 QUVVAT.MARKET · Toshkent, Chilonzor</p>
    </div>"""

# ═══════════════════════════════════════════════════════════════════════
# AUTH ROUTES
# ═══════════════════════════════════════════════════════════════════════

@app.route('/api/auth/register', methods=['POST'])
def register():
    body = request.json or {}
    required = ['name','surname','username','email','password']
    if not all(body.get(k,'').strip() for k in required):
        return jsonify({'error': "Barcha maydonlarni to'ldiring"}), 400

    d = load_data()
    if any(u['username'] == body['username'] for u in d['users']):
        return jsonify({'error': 'Username band'}), 409
    if any(u['email'] == body['email'] for u in d['users']):
        return jsonify({'error': "Email allaqachon ro'yxatdan o'tgan"}), 409

    # Generate OTP
    otp = ''.join(random.choices(string.digits, k=6))
    d['otp_store'][body['email']] = {
        'code': otp,
        'expires': time.time() + 600,  # 10 min
        'user_data': {
            'id': int(time.time()),
            'username': body['username'].strip(),
            'name': body['name'].strip(),
            'surname': body['surname'].strip(),
            'email': body['email'].strip().lower(),
            'password': hash_pass(body['password']),
            'role': 'user',
            'created_at': time.time()
        }
    }
    save_data(d)

    sent = send_email(body['email'], '⚡ QUVVAT.MARKET — Ro\'yxatdan o\'tish kodi', otp_email_html(otp, "ro'yxatdan o'tish"))
    return jsonify({'message': f'OTP yuborildi (email: {body["email"]})', 'sent': sent, 'dev_otp': otp}), 200

@app.route('/api/auth/verify-otp', methods=['POST'])
def verify_otp():
    body = request.json or {}
    email = (body.get('email','') or '').lower()
    code  = str(body.get('code',''))
    d = load_data()
    entry = d['otp_store'].get(email)
    if not entry:
        return jsonify({'error': 'OTP topilmadi, qaytadan urinib ko\'ring'}), 400
    if time.time() > entry['expires']:
        del d['otp_store'][email]; save_data(d)
        return jsonify({'error': 'OTP muddati tugagan'}), 400
    if entry['code'] != code:
        return jsonify({'error': "Noto'g'ri kod"}), 400

    user = entry['user_data']
    d['users'].append(user)
    del d['otp_store'][email]
    d['activity'].insert(0, {'type':'register','username':user['username'],'name':user['name'],'surname':user['surname'],'email':user['email'],'time':time.time()})
    save_data(d)
    token = gen_token(user['id'])
    return jsonify({'token': token, 'user': safe_user(user)}), 200

@app.route('/api/auth/login', methods=['POST'])
def login():
    body = request.json or {}
    uname = (body.get('username','') or '').strip()
    pw    = body.get('password','')
    d = load_data()
    user = next((u for u in d['users'] if u['username'] == uname and u['password'] == hash_pass(pw)), None)
    if not user:
        return jsonify({'error': "Username yoki parol noto'g'ri"}), 401
    d['activity'].insert(0, {'type':'login','username':user['username'],'name':user['name'],'surname':user['surname'],'email':user['email'],'pass_hint':'***','time':time.time()})
    save_data(d)
    token = gen_token(user['id'])
    return jsonify({'token': token, 'user': safe_user(user)}), 200

@app.route('/api/auth/logout', methods=['POST'])
def logout():
    token = request.headers.get('Authorization','').replace('Bearer ','')
    user  = get_user_from_token(token)
    if user:
        d = load_data()
        d['activity'].insert(0, {'type':'logout','username':user['username'],'name':user['name'],'surname':user['surname'],'email':user['email'],'time':time.time()})
        save_data(d)
    return jsonify({'message': 'Chiqdingiz'}), 200

def safe_user(u):
    return {k:v for k,v in u.items() if k not in ('password',)}

# ═══════════════════════════════════════════════════════════════════════
# PRODUCTS
# ═══════════════════════════════════════════════════════════════════════

@app.route('/api/products', methods=['GET'])
def get_products():
    d = load_data()
    cat = request.args.get('cat','')
    prods = d['products'] if not cat or cat == 'all' else [p for p in d['products'] if p['cat']==cat]
    return jsonify(prods), 200

@app.route('/api/products', methods=['POST'])
def add_product():
    token = request.headers.get('Authorization','').replace('Bearer ','')
    user  = get_user_from_token(token)
    if not user or user.get('role') != 'admin':
        return jsonify({'error': 'Ruxsat yo\'q'}), 403
    body = request.json or {}
    if not body.get('name') or not body.get('price'):
        return jsonify({'error': "Maydonlarni to'ldiring"}), 400
    d = load_data()
    new_id = max((p['id'] for p in d['products']), default=0) + 1
    prod = {
        'id':   new_id,
        'cat':  body.get('cat','fastfood'),
        'emoji':body.get('emoji','🍔'),
        'name': body['name'],
        'desc': body.get('desc',''),
        'price':int(body['price']),
        'badge':body.get('badge',''),
        'image':body.get('image',''),
        'variants': body.get('variants',[])
    }
    d['products'].append(prod); save_data(d)
    return jsonify(prod), 201

@app.route('/api/products/<int:pid>', methods=['PUT'])
def update_product(pid):
    token = request.headers.get('Authorization','').replace('Bearer ','')
    user  = get_user_from_token(token)
    if not user or user.get('role') != 'admin':
        return jsonify({'error': 'Ruxsat yo\'q'}), 403
    d = load_data()
    prod = next((p for p in d['products'] if p['id']==pid), None)
    if not prod: return jsonify({'error': 'Topilmadi'}), 404
    body = request.json or {}
    for k in ['name','desc','price','badge','image','variants','cat','emoji']:
        if k in body: prod[k] = body[k]
    save_data(d)
    return jsonify(prod), 200

@app.route('/api/products/<int:pid>', methods=['DELETE'])
def delete_product(pid):
    token = request.headers.get('Authorization','').replace('Bearer ','')
    user  = get_user_from_token(token)
    if not user or user.get('role') != 'admin':
        return jsonify({'error': 'Ruxsat yo\'q'}), 403
    d = load_data()
    d['products'] = [p for p in d['products'] if p['id'] != pid]
    save_data(d)
    return jsonify({'ok': True}), 200

@app.route('/api/products/<int:pid>/like', methods=['POST'])
def toggle_like(pid):
    token = request.headers.get('Authorization','').replace('Bearer ','')
    user  = get_user_from_token(token)
    if not user: return jsonify({'error': 'Login qiling'}), 401
    d = load_data()
    key = f'{pid}_{user["id"]}'
    liked_set = d.setdefault('liked_by_user', [])
    if key in liked_set:
        liked_set.remove(key)
        d['likes'][str(pid)] = max(0, d['likes'].get(str(pid), 0) - 1)
        liked = False
    else:
        liked_set.append(key)
        d['likes'][str(pid)] = d['likes'].get(str(pid), 0) + 1
        liked = True
    save_data(d)
    return jsonify({'liked': liked, 'count': d['likes'].get(str(pid), 0)}), 200

@app.route('/api/products/<int:pid>/view', methods=['POST'])
def add_view(pid):
    d = load_data()
    d['views'][str(pid)] = d['views'].get(str(pid), 0) + 1
    save_data(d)
    return jsonify({'views': d['views'][str(pid)]}), 200

# ═══════════════════════════════════════════════════════════════════════
# ORDERS
# ═══════════════════════════════════════════════════════════════════════

@app.route('/api/orders', methods=['GET'])
def get_orders():
    token = request.headers.get('Authorization','').replace('Bearer ','')
    user  = get_user_from_token(token)
    if not user: return jsonify({'error': 'Login qiling'}), 401
    d = load_data()
    if user.get('role') == 'admin':
        return jsonify(d['orders']), 200
    return jsonify([o for o in d['orders'] if o.get('user_id') == user['id']]), 200

@app.route('/api/orders', methods=['POST'])
def place_order():
    token = request.headers.get('Authorization','').replace('Bearer ','')
    user  = get_user_from_token(token)
    if not user: return jsonify({'error': 'Login qiling'}), 401
    body = request.json or {}
    required = ['name','surname','phone','region','items']
    if not all(body.get(k) for k in required):
        return jsonify({'error': "Barcha maydonlarni to'ldiring"}), 400
    d = load_data()
    order_id = 'QM-' + str(int(time.time()))[-5:]
    total = sum(i['price']*i['qty'] for i in body['items'])
    order = {
        'id': order_id,
        'user_id': user['id'],
        'username': user['username'],
        'name': body['name'],
        'surname': body['surname'],
        'phone': body['phone'],
        'email': body.get('email',''),
        'region': body['region'],
        'delivery_time': body.get('delivery_time','30'),
        'payment': body.get('payment','cash'),
        'items': body['items'],
        'total': total,
        'status': 'new',
        'time': time.time()
    }
    d['orders'].insert(0, order); save_data(d)
    return jsonify({'order_id': order_id, 'total': total}), 201

# ═══════════════════════════════════════════════════════════════════════
# CHAT / MESSAGES
# ═══════════════════════════════════════════════════════════════════════

@app.route('/api/messages', methods=['GET'])
def get_messages():
    d = load_data()
    return jsonify(d['messages'][-100:]), 200

@app.route('/api/messages', methods=['POST'])
def send_message():
    token = request.headers.get('Authorization','').replace('Bearer ','')
    user  = get_user_from_token(token)
    if not user: return jsonify({'error': 'Login qiling'}), 401
    body = request.json or {}
    text = (body.get('text','') or '').strip()
    if not text: return jsonify({'error': 'Xabar bo\'sh'}), 400
    d = load_data()
    msg = {
        'id': int(time.time()*1000),
        'user_id': user['id'],
        'username': user['username'],
        'name': user['name'],
        'text': text,
        'time': time.time()
    }
    d['messages'].append(msg)
    if len(d['messages']) > 500: d['messages'] = d['messages'][-500:]
    save_data(d)
    return jsonify(msg), 201

@app.route('/api/messages/<int:msg_id>', methods=['DELETE'])
def delete_message(msg_id):
    token = request.headers.get('Authorization','').replace('Bearer ','')
    user  = get_user_from_token(token)
    if not user or user.get('role') != 'admin':
        return jsonify({'error': 'Ruxsat yo\'q'}), 403
    d = load_data()
    d['messages'] = [m for m in d['messages'] if m.get('id') != msg_id]
    save_data(d)
    return jsonify({'ok': True}), 200

# ═══════════════════════════════════════════════════════════════════════
# ACTIVITY / USERS (admin only)
# ═══════════════════════════════════════════════════════════════════════

@app.route('/api/activity', methods=['GET'])
def get_activity():
    token = request.headers.get('Authorization','').replace('Bearer ','')
    user  = get_user_from_token(token)
    if not user or user.get('role') != 'admin':
        return jsonify({'error': 'Ruxsat yo\'q'}), 403
    d = load_data()
    return jsonify(d['activity'][:200]), 200

@app.route('/api/users', methods=['GET'])
def get_users():
    token = request.headers.get('Authorization','').replace('Bearer ','')
    user  = get_user_from_token(token)
    if not user or user.get('role') != 'admin':
        return jsonify({'error': 'Ruxsat yo\'q'}), 403
    d = load_data()
    return jsonify([safe_user(u) for u in d['users']]), 200

# ═══════════════════════════════════════════════════════════════════════
# SETTINGS (change username / password — admin gets OTP on email)
# ═══════════════════════════════════════════════════════════════════════

@app.route('/api/settings/request', methods=['POST'])
def settings_request():
    token = request.headers.get('Authorization','').replace('Bearer ','')
    user  = get_user_from_token(token)
    if not user: return jsonify({'error': 'Login qiling'}), 401
    body = request.json or {}
    if user.get('role') == 'admin':
        otp = ''.join(random.choices(string.digits, k=6))
        d = load_data()
        d['otp_store'][user['email']] = {
            'code': otp,
            'expires': time.time() + 600,
            'pending_change': {
                'username': body.get('username'),
                'password': body.get('password')
            }
        }
        save_data(d)
        sent = send_email(ADMIN_EMAIL, '⚡ QUVVAT.MARKET — Sozlamalar OTP', otp_email_html(otp, 'sozlamalar'))
        return jsonify({'needs_otp': True, 'sent': sent, 'dev_otp': otp}), 200
    else:
        # Non-admin: apply directly
        d = load_data()
        idx = next((i for i,u in enumerate(d['users']) if u['id']==user['id']), None)
        if idx is None: return jsonify({'error': 'Topilmadi'}), 404
        if body.get('username'): d['users'][idx]['username'] = body['username']
        if body.get('password'): d['users'][idx]['password'] = hash_pass(body['password'])
        save_data(d)
        return jsonify({'needs_otp': False, 'ok': True}), 200

@app.route('/api/settings/confirm', methods=['POST'])
def settings_confirm():
    token = request.headers.get('Authorization','').replace('Bearer ','')
    user  = get_user_from_token(token)
    if not user: return jsonify({'error': 'Login qiling'}), 401
    body = request.json or {}
    code = str(body.get('code',''))
    d = load_data()
    entry = d['otp_store'].get(user['email'])
    if not entry: return jsonify({'error': 'OTP topilmadi'}), 400
    if time.time() > entry['expires']:
        del d['otp_store'][user['email']]; save_data(d)
        return jsonify({'error': 'OTP muddati tugagan'}), 400
    if entry['code'] != code:
        return jsonify({'error': "Noto'g'ri kod"}), 400
    change = entry.get('pending_change', {})
    idx = next((i for i,u in enumerate(d['users']) if u['id']==user['id']), None)
    if idx is not None:
        if change.get('username'): d['users'][idx]['username'] = change['username']
        if change.get('password'): d['users'][idx]['password'] = hash_pass(change['password'])
    del d['otp_store'][user['email']]; save_data(d)
    return jsonify({'ok': True}), 200

# ═══════════════════════════════════════════════════════════════════════
# CONTACT
# ═══════════════════════════════════════════════════════════════════════

@app.route('/api/contact', methods=['POST'])
def contact():
    body = request.json or {}
    html = f"""
    <div style='font-family:Arial;background:#0d0d1a;color:#f0f0fa;padding:30px;border-radius:12px'>
      <h2 style='color:#ff2d55'>📬 Yangi xabar — QUVVAT.MARKET</h2>
      <p><b>Ism:</b> {body.get('name','')}</p>
      <p><b>Telefon:</b> {body.get('phone','')}</p>
      <p><b>Email:</b> {body.get('email','')}</p>
      <p><b>Xabar:</b> {body.get('message','')}</p>
    </div>"""
    send_email(ADMIN_EMAIL, '📬 Yangi murojaat — QUVVAT.MARKET', html)
    return jsonify({'ok': True}), 200

# ═══════════════════════════════════════════════════════════════════════
# SERVE REACT BUILD
# ═══════════════════════════════════════════════════════════════════════

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve_react(path):
    dist = os.path.join(app.static_folder or '../frontend/dist')
    target = os.path.join(dist, path)
    if path and os.path.exists(target):
        return send_from_directory(dist, path)
    return send_from_directory(dist, 'index.html')

if __name__ == '__main__':
    load_data()   # initialise data.json if needed
    print('🚀 QUVVAT.MARKET Backend  →  http://localhost:5000')
    app.run(host='0.0.0.0', port=5000, debug=True)