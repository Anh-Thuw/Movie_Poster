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
        to_email = "your@email.com"
        content = f"Tên: {name}\nEmail: {email}\nChủ đề: {subject}\n\nNội dung:\n{message}"

        try:
            msg = MIMEText(content)
            msg['Subject'] = f"Liên hệ: {subject}"
            msg['From'] = email
            msg['To'] = to_email

            smtp_server = smtplib.SMTP('smtp.gmail.com', 587)
            smtp_server.starttls()
            smtp_server.login('your@gmail.com', 'your_app_password')  # Replace with your app password
            smtp_server.send_message(msg)
            smtp_server.quit()

            flash('Tin nhắn của bạn đã được gửi thành công!', 'success')
        except Exception as e:
            flash(f'Lỗi khi gửi email: {str(e)}', 'danger')

        return redirect(url_for('views.contact'))

    return render_template('contact.html', current_user=current_user)


# Load mô hình
model = load_model('/movie_poster/training-model/save_model.keras')

# Load danh sách tên thể loại từ file pickle
with open('path/to/label_encoder.pkl', 'rb') as f:
    class_names = pickle.load(f)

@views.route('/predict', methods=['POST'])
def predict():
    if 'image' not in request.files:
        return jsonify({'error': 'Không có ảnh được gửi'}), 400

    file = request.files['image']
    if file.filename == '':
        return jsonify({'error': 'Không có tên file'}), 400

    try:
        image_bytes = file.read()
        processed_image = preprocess_image(image_bytes)

        # Dự đoán
        prediction = model.predict(processed_image)
        predicted_index = np.argmax(prediction)
        genre = class_names[predicted_index]  # Ánh xạ chỉ số sang tên thể loại

        return jsonify({'genre': genre})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


def preprocess_image(image_bytes):
    image = Image.open(io.BytesIO(image_bytes)).convert('RGB')
    image = image.resize((224, 224))  # Tùy kích thước input của mô hình
    image_array = np.array(image) / 255.0
    image_array = np.expand_dims(image_array, axis=0)
    return image_array
