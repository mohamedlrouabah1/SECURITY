import qrcode
from config_otp import user_secrets, OTP_QRCODE_DIR, OTP_ISSUER

def generate_otp_qrcode(user, debbug=False):
    otp_uri = {}
    
    for type in ['TOTP', 'HOTP']:
        seed = user_secrets[user][type]
        t = type.lower()
        otp_uri[type] = f'otpauth://{t}/{user}?secret={seed}&issuer={OTP_ISSUER}'
        print(otp_uri[type])

    # Générer le QR code
    for type, uri in otp_uri.items():
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )

        qr.add_data(uri)
        qr.make(fit=True)

        img = qr.make_image(fill_color="black", back_color="white")

        # to be sent in the POST response
        img.save(f'{OTP_QRCODE_DIR}/{type}_qrcode.png')

        if debbug:
            img.show()
