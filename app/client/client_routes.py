from flask import Blueprint
from helpers import *

client_bp = Blueprint('client', __name__)


@client_bp.route('/totp')
def client_side_totp():
    return generate_totp_page('user1', 'client')

@client_bp.route('/hotp')
def client_side_hotp():
    return generate_hotp_page(
        'user1', 'client')