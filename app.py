import os
from flask import Flask, request, jsonify
from flask_pymongo import PyMongo
from flask_cors import CORS
from werkzeug.utils import secure_filename

app = Flask(__name__)
CORS(app)

# Folder Setup
UPLOAD_FOLDER = 'uploaded_docs'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

app.config["MONGO_URI"] = "mongodb://localhost:27017/university_db"
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
mongo = PyMongo(app)

ADMIN_USER = "admin123"
ADMIN_PASS = "admin@uni"

@app.route('/submit_application', methods=['POST'])
def submit():
    try:
        # Form data receive karna
        name = request.form.get('name')
        email = request.form.get('email')
        ssc = float(request.form.get('ssc', 0))
        hssc = float(request.form.get('hssc', 0))
        dob = request.form.get('dob')
        program = request.form.get('program')
        
        # Files handling
        uploaded_files = request.files.getlist("files")
        saved_paths = []
        for file in uploaded_files:
            filename = secure_filename(f"{name}_{file.filename}")
            path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(path)
            saved_paths.append(path)

        # ID Generation
        count = mongo.db.applications.count_documents({})
        adm_id = f"ADM-{100 + count + 1}"
        
        doc = {
            "admission_id": adm_id,
            "name": name,
            "email": email,
            "dob": dob,
            "program": program,
            "merit": round((ssc + hssc) / 2, 2),
            "documents": saved_paths,
            "payment": "Unpaid"
        }
        mongo.db.applications.insert_one(doc)
        return jsonify({"id": adm_id}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/admin/login', methods=['POST'])
def admin_login():
    data = request.json
    if data.get('user') == ADMIN_USER and data.get('pass') == ADMIN_PASS:
        return jsonify({"status": "Success"}), 200
    return jsonify({"status": "Failed"}), 401

@app.route('/admin/list', methods=['GET'])
def list_apps():
    apps = list(mongo.db.applications.find().sort("merit", -1))
    for a in apps: a['_id'] = str(a['_id'])
    return jsonify(apps)

@app.route('/pay', methods=['POST'])
def pay():
    data = request.json
    res = mongo.db.applications.update_one({"admission_id": data.get('id')}, {"$set": {"payment": "Paid"}})
    return jsonify({"status": "Success" if res.modified_count > 0 else "Failed"})

if __name__ == "__main__":
    app.run(debug=True, port=5000)