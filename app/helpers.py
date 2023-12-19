import pyotp
import time
from flask import render_template
from config_otp import user_secrets
from config_server import VERSION_ALGO
from myOTP import generate_personnal_totp


def generate_totp_page(user,side):
    """
    Parameters:
        user : str
            Name of the user which information we want to display.
        side : 'client' or 'server'
            To adjust the display of information depending on which side we are.
    """
    if VERSION_ALGO == 'perso' :
        totp = generate_personnal_totp(user,user_secrets[user]['TOTP'])
    else :
        totp = pyotp.TOTP(
            user_secrets[user]['TOTP'], interval=60
            ).now()

    return render_template('totp.html', 
        page_title=f'Côté {side} - TOTP', 
        secret=user_secrets[user]['TOTP'], 
        otp_code=totp, 
        time=30 - int(time.time() % 30),
        side=side
        )

def generate_hotp_page(user, side):
    """
    Parameters:
        user : str
            Name of the user which information we want to display.
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
