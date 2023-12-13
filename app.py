from flask import Flask, redirect, render_template_string, request, jsonify, session
import pyotp
import time
import bootstrap_py

app = Flask(__name__)
app.secret_key = 'super_secret_key'  # Clé secrète pour la session

# Stockage des secrets utilisateur
user_secrets = {
    'user1': {'TOTP': pyotp.random_base32(), 'HOTP': pyotp.random_base32(), 'HOTP_counter': 0}
}

@app.route('/')
def home():
    return redirect('/login')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        session['username'] = 'user1'
        return jsonify({'status': 'success'})

    # Générer les codes HOTP et TOTP pour l'affichage
    user = session.get('username', 'user1')
    hotp = pyotp.HOTP(user_secrets[user]['HOTP'])
    totp = pyotp.TOTP(user_secrets[user]['TOTP'])
    hotp_code = hotp.at(user_secrets[user]['HOTP_counter'])
    totp_code = totp.now()

    return render_template_string('''
        <!DOCTYPE html>
        <html>
        <head>
            <title>OTP Demo</title>
            <style>
                body { font-family: Arial, sans-serif; background-color: #f0f0f0; }
                .container { width: 300px; margin: 100px auto; padding: 20px; background: white; border-radius: 8px; box-shadow: 0 0 10px rgba(0, 0, 0, 0.1); }
                input, button { width: 85%; padding: 10px; margin-top: 10px; border-radius: 5px; border: 1px solid #ddd; }
                button { background-color: #007bff; color: white; }
                button:hover { background-color: #0056b3; }
                .modal { display: none; position: fixed; z-index: 1; left: 0; top: 0; width: 100%; height: 100%; overflow: auto; background-color: rgba(0,0,0,0.4); }
                .modal-content { background-color: #fefefe; margin: 15% auto; padding: 20px; border: 1px solid #888; width: 300px; border-radius: 8px; }
                .close { color: #aaa; float: right; font-size: 28px; font-weight: bold; }
                .close:hover, .close:focus { color: black; text-decoration: none; cursor: pointer; }
                label { display: block; margin-top: 10px; }
            </style>
        </head>
        <body>
            <div class="container">
                <h2>Login</h2>
                <form id="login-form">
                    <input type="text" name="username" placeholder="Username" required>
                    <input type="password" name="password" placeholder="Password" required>
                    <button type="submit">Login</button>
                </form>
            </div>

            <div id="otpModal" class="modal">
                <div class="modal-content">
                    <span class="close">&times;</span>
                    <form id="otp-form">
                        <label><input type="radio" name="otpType" value="totp" checked> TOTP</label>
                        <label><input type="radio" name="otpType" value="hotp"> HOTP</label>
                        <input type="text" name="otpCode" placeholder="OTP Code" required>
                        <button type="submit">Validate OTP</button>
                    </form>
                </div>
            </div>

            <script>
                document.getElementById('login-form').addEventListener('submit', function(event) {
                    event.preventDefault();
                    document.getElementById('otpModal').style.display = 'block';
                });

                document.getElementById('otp-form').addEventListener('submit', function(event) {
                    event.preventDefault();
                    var otpType = document.querySelector('input[name="otpType"]:checked').value;
                    var otpCode = this.otpCode.value;
                    window.location.href = `/validate-otp?otpType=${otpType}&otpCode=${otpCode}`;
                });

                document.getElementsByClassName('close')[0].onclick = function() {
                    document.getElementById('otpModal').style.display = 'none';
                };
            </script>
        </body>
        </html>
    ''')


@app.route('/validate-otp')
def validate_otp():
    otp_type = request.args.get('otpType')
    otp_code = request.args.get('otpCode')
    user = session.get('username', 'user1')

    if otp_type == 'hotp':
        hotp = pyotp.HOTP(user_secrets[user]['HOTP'])
        valid = hotp.verify(otp_code, user_secrets[user]['HOTP_counter'])
        if valid:
            user_secrets[user]['HOTP_counter'] += 1
    elif otp_type == 'totp':
        totp = pyotp.TOTP(user_secrets[user]['TOTP'])
        valid = totp.verify(otp_code)
    else:
        valid = False

    if valid:
        return '<h1>Connexion réussie avec OTP valide!</h1>'
    else:
        return '<h1>Échec de la connexion. OTP invalide.</h1>'

# give code to generate a htop page for client and server with a button to increment the counter and htop code change(in client page the server side automatiquely increment), also give some style display both client and server in same page
@app.route('/increment-counter')
def increment_counter():
    user = session.get('username', 'user1')
    user_secrets[user]['HOTP_counter'] += 1
    return redirect('/client-side-hotp')

def generate_hotp_page(user, page_title,side):
    hotp = pyotp.HOTP(user_secrets[user]['HOTP'])
    otp_code = hotp.at(user_secrets[user]['HOTP_counter'])
    # hide bouton if side is server side
    if side == 'server':
        return render_template_string('''
            <h1>{{ page_title }}</h1>
            <p>Clé secrète: {{ secret }}</p>
            <p>Compteur: {{ counter }}</p>
            <p>Code OTP: {{ otp_code }}</p>
            <a href="/">Retour</a>
        ''', page_title=page_title, secret=user_secrets[user]['HOTP'], counter=user_secrets[user]['HOTP_counter'], otp_code=otp_code)
    else:
        return render_template_string('''
            <h1>{{ page_title }}</h1>
            <p>Clé secrète: {{ secret }}</p>
            <p>Compteur: {{ counter }}</p>
            <p>Code OTP: {{ otp_code }}</p>
            <a href="/">Retour</a>
            <form action="/increment-counter">
                <button type="submit">Incrémenter le compteur</button>
            </form>
        ''', page_title=page_title, secret=user_secrets[user]['HOTP'], counter=user_secrets[user]['HOTP_counter'], otp_code=otp_code)
                               
@app.route('/client-side-hotp')
def client_side_hotp():
    return generate_hotp_page(
        'user1', 'Côté Client - HOTP','client')

@app.route('/server-side-hotp')
def server_side_hotp():
    return generate_hotp_page(
        'user1', 'Côté Serveur - HOTP','server')

# add a minute counter whento the totp page dynamically without refresh
def generate_totp_page(user, page_title):
    totp = pyotp.TOTP(user_secrets[user]['TOTP'])
    otp_code = totp.now()
    return render_template_string('''
        <h1>{{ page_title }}</h1>
        <p>Clé secrète: {{ secret }}</p>
        <p>Code OTP: {{ otp_code }}</p>
        <p>Temps restant: <span id="time">{{ time }}</span></p>
        <a href="/">Retour</a>
        <script>
            var time = {{ time }};
            setInterval(function() {
                time -= 1;
                document.getElementById('time').innerHTML = time;
                if (time == 0) {
                    location.reload();
                }
            }, 1000);
        </script>
    ''', page_title=page_title, secret=user_secrets[user]['TOTP'], otp_code=otp_code, time=30 - int(time.time() % 30))
    
@app.route('/client-side-totp')
def client_side_totp():
    # display in left side the client side and in right side the server side
    return generate_totp_page('user1', 'Côté Client - TOTP')

@app.route('/server-side-totp')
def server_side_totp():
    return generate_totp_page('user1', 'Côté Serveur - TOTP')

if __name__ == '__main__':
    app.run(debug=True)
    