#!/bin/usr/bash
gunicorn --reload app:app --chdir app 