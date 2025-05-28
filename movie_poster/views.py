from flask import Blueprint, render_template, request, flash, jsonify, redirect, url_for 
from tensorflow.keras.models import load_model
import numpy as np
import movie_poster.forms as forms
import os
from flask_login import login_required, current_user
from .models import Note
from . import db
import json
import pickle
import pandas as pd
import joblib
import smtplib
from email.mime.text import MIMEText

views = Blueprint('views', __name__)

# Trang gốc, không yêu cầu đăng nhập
@views.route('/')
def index():
    return render_template("index.html", current_user=current_user)

# Trang home cho người dùng đã đăng nhập
@views.route('/home')
@login_required
def home():
    return render_template("index.html")

# Trang categories, yêu cầu đăng nhập
@views.route('/home/categories')
@login_required
def categories():
    return render_template("categories.html")

@views.route('/home/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        subject = request.form['subject']
        message = request.form['message']

        # Cấu hình gửi email
        to_email = "thuna.22it@vku.udn.vn"
        content = f"Tên: {name}\nEmail: {email}\nChủ đề: {subject}\n\nNội dung:\n{message}"

        try:
            msg = MIMEText(content)
            msg['Subject'] = f"Liên hệ: {subject}"
            msg['From'] = "quynhpn.22it@vku.udn.vn"
            msg['To'] = to_email
            msg.add_header('Reply-To', email)

            smtp_server = smtplib.SMTP('smtp.gmail.com', 587)
            smtp_server.starttls()
            smtp_server.login('quynhpn.22it@vku.udn.vn', 'nqox tbtc zxel dlue')  # Replace with your app password
            smtp_server.send_message(msg)
            smtp_server.quit()

            flash('Tin nhắn của bạn đã được gửi thành công!', 'success')
        except Exception as e:
            flash(f'Lỗi khi gửi email: {str(e)}', 'danger')

        return redirect(url_for('views.contact'))

    return render_template('contact.html', current_user=current_user)

@views.route('/account')
@login_required
def account():
    return render_template('account.html', current_user=current_user)