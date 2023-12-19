user_secrets = {}
# otp params
OTP_HASH_FUNCTION = 'sha1' # to be compliant with freeOTP app
OTP_CODE_SIZE = 6
# NB: this is public folder to ease the access to the QR code
# don't do that in prod, send the QRcode in the POST response
OTP_QRCODE_DIR = 'static/QRcodes' 
OTP_ISSUER = "Projet-Securite-OTP"

throttling_parameter = 8
scheme_delais = 5000 # ms
latency = 10 # ms
look_ahead_window = 3