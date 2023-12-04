from flask import Flask, jsonify, render_template, request, redirect, url_for, flash
from flask_pymongo import PyMongo
import os

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Replace with your actual secret key

# MongoDB configuration
# app.config["MONGO_URI"] = "mongodb+srv://vrchatAdmin:il4FA64i1Mbeo8Ay@cluster0.r5gre5i.mongodb.net/salesbot"  # Replace with your MongoDB URI
app.config["MONGO_URI"] = "mongodb+srv://admin:admin@mygitdb.v0gnkoy.mongodb.net/transcription"
mongo = PyMongo(app)

# Folder where uploads will be stored
UPLOAD_FOLDER = 'recordings'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route('/upload', methods=['GET', 'POST'])
def file_upload():
    if request.method == 'GET':
        return redirect(url_for('upload_form'))
# @app.route('/upload', methods=['POST'])
# def file_upload():
    if 'file' not in request.files:
        flash('No file part in the request', 'error')  # Flash an error message
        return redirect(url_for('upload_form'))  # Redirect to the upload form

    file = request.files['file']
    
    if file.filename == '':
        flash('No file selected for uploading', 'error')  # Flash an error message
        return redirect(url_for('upload_form'))  # Redirect to the upload form

    if file:
        filename = file.filename
        save_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(save_path)
        mongo.db.transcription_status.insert_one({'file_name': filename, 'status': 'submitted'})
        flash('File uploaded successfully', 'success')  # Flash a success message
        return redirect(url_for('upload_form'))  # Redirect to the upload form
    
@app.route('/upload_form')
def upload_form():
    return render_template('upload_form.html')

if __name__ == '__main__':
    app.run(debug=True)