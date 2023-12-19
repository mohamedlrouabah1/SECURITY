from flask import Flask, redirect, render_template, request, jsonify, session
import pyotp
import time
import bootstrap_py
from config_server import *
from config_otp import *

app = Flask(__name__)
app.secret_key = 'super_secret_key'  # Clé secrète pour la session
app = Flask(__name__, template_folder=DIR_TEMPLATES, static_folder=DIR_STATICS)

user_secrets['user1'] = {
    'TOTP': pyotp.random_base32(), 
    'HOTP': pyotp.random_base32(), 
    'HOTP_counter': 0
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

    return render_template(f'login.html', hotp_code=hotp_code, totp_code=totp_code)


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

def generate_hotp_page(user, side):
    """
    Parameters:
        user : str
            Name of the user which information we want to display.
        page_title : str
            Title of the page depending on which side we are.
        side : 'client' or 'server'
            To adjust the display of information depending on which side we are.

    """
    hotp = pyotp.HOTP(user_secrets[user]['HOTP'])
    otp_code = hotp.at(user_secrets[user]['HOTP_counter'])
    return render_template('hotp.html', 
        page_title=f'Côté {side} - HOTP', 
        secret=user_secrets[user]['HOTP'], 
        counter=user_secrets[user]['HOTP_counter'], 
        otp_code=otp_code, 
        side=side
        )
   
@app.route('/client-side-hotp')
def client_side_hotp():
    return generate_hotp_page(
        'user1', 'client')

@app.route('/server-side-hotp')
def server_side_hotp():
    return generate_hotp_page(
        'user1', 'Côté Serveur - HOTP','server')


def generate_totp_page(user, page_title):
    totp = pyotp.TOTP(user_secrets[user]['TOTP'])
    otp_code = totp.now()
    return render_template('totp.html', 
        page_title=page_title, 
        secret=user_secrets[user]['TOTP'], 
        otp_code=otp_code, 
        time=30 - int(time.time() % 30)
        )
    
@app.route('/client-side-totp')
def client_side_totp():
    # display in left side the client side and in right side the server side
    return generate_totp_page('user1', 'Côté Client - TOTP')

@app.route('/server-side-totp')
def server_side_totp():
    return generate_totp_page('user1', 'Côté Serveur - TOTP')

if __name__ == '__main__':
    app.run(debug=True)
    