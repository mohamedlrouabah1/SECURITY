from flask import Blueprint
from helpers import *

server_bp = Blueprint('server', __name__)


@server_bp.route('/totp')
def server_side_totp():
    return generate_totp_page('user1', __name__)


@server_bp.route('/hotp')
def server_side_hotp():
    return generate_hotp_page('user1', __name__)
