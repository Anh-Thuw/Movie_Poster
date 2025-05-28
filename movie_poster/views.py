from flask import Blueprint, render_template, request, flash, jsonify, redirect, url_for 
from tensorflow.keras.models import load_model
import numpy as np
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
from flask import send_file
from PIL import Image
import io

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

# Load mô hình
model = load_model('movie_poster/training-model/save_model.keras')

# Load danh sách tên thể loại từ file pickle
with open('movie_poster/training-model/label_encoder.pkl', 'rb') as f:
    label_encoder = pickle.load(f)

@views.route('/home/categories', methods=['GET', 'POST'])
@login_required
def categories():
    genre = None  # Mặc định không có kết quả

    if request.method == 'POST':
        if 'image' not in request.files:
            return render_template("categories.html", genre="Không có ảnh được gửi")

        file = request.files['image']
        if file.filename == '':
            return render_template("categories.html", genre="Không có tên file")

        try:
            image_bytes = file.read()
            processed_image = preprocess_image(image_bytes)
            prediction = model.predict(processed_image)
            predicted_index = np.argmax(prediction)
            genre = label_encoder[predicted_index]
        except Exception as e:
            genre = f"Lỗi: {str(e)}"

    return render_template("categories.html", genre=genre)

def preprocess_image(image_bytes):
    image = Image.open(io.BytesIO(image_bytes)).convert('RGB')
    image = image.resize((150, 101))  # resize về kích thước yêu cầu
    image_array = np.array(image) / 255.0  # chuẩn hóa ảnh về [0,1]
    image_array = np.expand_dims(image_array, axis=0)  # thêm batch dimension
    return image_array

@views.route('/account')
@login_required
def account():
    return render_template('account.html', current_user=current_user)
