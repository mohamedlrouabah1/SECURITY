#!/bin/usr/bash
gunicorn app:app --chdir app --reload