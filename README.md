# Prototype de client-serveur pour le protocole OTP réalisé en python pour le cours de cryptographie de M2 informatique

Live demo availible on heroku at : https://dsc-securite-otp-c9eac3f8716a.herokuapp.com

![Python](https://img.shields.io/badge/Python-3.8-blue.svg)
![PyOTP](https://img.shields.io/badge/PyOTP-2.6.0-blue.svg)
![Flask](https://img.shields.io/badge/Flask-2.0.1-blue.svg)
![Cryptography](https://img.shields.io/badge/Cryptography-blue.svg)


## Table of contents

- [How to use it ?](#how-to-use-it-)
- [App illustrations](#app-illustrations)

  - [Home page](#home-page)
  - [Client pages](#client-pages)
  - [Server pages](#server-pages)
  - [OTP pop-up](#otp-pop-up)
  - [OTP validation](#otp-validation)

- [Installation](#installation)
- [launch](#launch)
  
  - [localhost with python](#localhost-with-python)
  - [using a gunicorn server](#using-a-gunicorn-server)


## How to use it ?

The root url '/' is used to generate new seed for both HOTP and TOTP methods as well as reinit the HOTP counter.

Then you are redirected to the home page where you can find instructions to navigate among the different pages.

Using an authenticator app is not mandatory but advice for otp thus in the /client/* pages you can find a QRcode compliant with authenticator app as  freeOTP (which as been tested on)

If you interestead about the otp protocol please find attach to this repot a [pdf report](doc/rapport.pdf) about it (in french).

Whithout further ado, please enjoy some screenshots of the app.

## App illustrations

### Home page

![home page](doc/img/C_proto/home.png)

### CLient pages

![client page](doc/img/C_proto/client.png)

### Server pages

![server page](doc/img/C_proto/server.png)


### OTP pop-up

![otp pop-up](doc/img/C_proto/popup_otp.png)

### OTP validation

![otp validation](doc/img/C_proto/otp_result.png)

## Installation

Download project's dependencies with pip:

```bash
pip install -r requirements.txt
```

## launch

### localhost with python

```bash
python3 app/app.py
```

 availible at url : localhost:5000

### using a gunicorn server

```bash
gunicorn app:app --chdir app
```

availible at url : localhost:8000
