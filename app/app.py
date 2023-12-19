from flask import Flask, redirect, render_template, request, jsonify, session
import pyotp

from config_server import *
from config_otp import *
from helpers import *
from client.client_routes import client_bp
from server.server_routes import server_bp
from share_seed import generate_otp_qrcode

from myOTP import generate_personnal_totp, generate_personnal_hotp


app = Flask(__name__, template_folder=DIR_TEMPLATES, static_folder=DIR_STATICS)
app.secret_key = 'super_secret_key'  # Clé secrète pour la session

app.register_blueprint(client_bp, url_prefix='/client')
app.register_blueprint(server_bp, url_prefix='/server')

user_secrets['user1'] = {
    'TOTP': pyotp.random_base32(), 
    'HOTP': pyotp.random_base32(), 
    'HOTP_counter': 0
}

@app.route('/')
def home():
    return redirect('/login')

@app.route('/favicon.ico')
def favicon():
    return app.send_static_file('img/favicon.ico')

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

    generate_otp_qrcode('user1')

    return render_template(f'login.html', 
        hotp_code=hotp_code, 
        totp_code=totp_code
        )


@app.route('/validate-otp')
def validate_otp():
    otp_type = request.args.get('otpType')
    otp_code = request.args.get('otpCode').replace(' ', '')
    user = session.get('username', 'user1')

    if otp_type == 'hotp':
        if VERSION_ALGO == 'perso' :
            hotp = generate_personnal_hotp(
                user,
                user_secrets[user]['HOTP'],
                user_secrets[user]['HOTP_counter']
                )
            valid = (hotp == int(otp_code))
        else :
            hotp = pyotp.HOTP(user_secrets[user]['HOTP'])
            valid = hotp.verify(otp_code, user_secrets[user]['HOTP_counter'])
        if valid:
            user_secrets[user]['HOTP_counter'] += 1
    
    elif otp_type == 'totp':
        if VERSION_ALGO == 'perso' :
            print(f"seed = {user_secrets[user]['TOTP']}")
            totp = generate_personnal_totp(user,user_secrets[user]['TOTP'])
            valid = (totp == int(otp_code))
            print(f"totp : {totp} - otp_code : {otp_code} equals : {totp == otp_code}")
        else :
            totp = pyotp.TOTP(user_secrets[user]['TOTP'])
            valid = totp.verify(otp_code)
    else:
        valid = False

    return render_template(f'login.html', 
        hotp_code=1, 
        totp_code=1,
        valid=valid
        )

# give code to generate a htop page for client and server with a button to increment the counter and htop code change(in client page the server side automatiquely increment), also give some style display both client and server in same page
@app.route('/increment-counter')
def increment_counter():
    user = session.get('username', 'user1')
    user_secrets[user]['HOTP_counter'] += 1
    return redirect('/client-side-hotp')


if __name__ == '__main__':
    app.run(debug=True)
    