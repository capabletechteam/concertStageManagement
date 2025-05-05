from flask import Flask, render_template, request, jsonify, url_for
from werkzeug.utils import secure_filename
import sqlite3
import json
import os

app = Flask(__name__)

UPLOAD_FOLDER = 'static/uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route('/upload_background', methods=['POST'])
def upload_background():
    if 'backgroundImage' not in request.files:
        return jsonify(success=False, message='No file part'), 400
    file = request.files['backgroundImage']
    if file.filename == '' or not file.filename:
        return jsonify(success=False, message='No selected file'), 400
    filename = secure_filename(file.filename)
    filepath = os.path.join(UPLOAD_FOLDER, filename)
    file.save(filepath)
    return jsonify(success=True, path=url_for('static', filename=f'uploads/{filename}'))

# Initialize the SQLite database
def init_db():
    with sqlite3.connect("layouts.db") as conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS layouts (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                data TEXT NOT NULL
            )
        """)
    conn.close()

init_db()

# Route to render the main page
@app.route('/')
def index():
    return render_template('index.html')

# help page
@app.route('/help')
def help_page():
    return render_template('help.html')

# Route to save a layout
@app.route('/save_layout', methods=['POST'])
def save_layout():
    if not request.json or 'data' not in request.json or 'name' not in request.json:
        return jsonify({"message": "Invalid request"}), 400
    layout_data = request.json.get('data')
    layout_name = request.json.get('name')
    with sqlite3.connect("layouts.db") as conn:

        # if layout name already exists, UPDATE it
        cursor = conn.cursor()

        cursor.execute("SELECT id FROM layouts WHERE name=?", (layout_name,))
        existing_layout = cursor.fetchone()

        if existing_layout:
            cursor.execute("UPDATE layouts SET data = ? WHERE id = ?", (json.dumps(layout_data), existing_layout[0]))
        else: 
            cursor.execute("INSERT INTO layouts (name, data) VALUES (?, ?)", (layout_name, json.dumps(layout_data)))
    return jsonify({"message": "Layout saved!"}), 200

# Route to get all layouts
@app.route('/get_layouts', methods=['GET'])
def get_layouts():
    with sqlite3.connect("layouts.db") as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id, name FROM layouts")
        layouts = [{"id": row[0], "name": row[1]} for row in cursor.fetchall()]
    return jsonify(layouts)

# Route to get a specific layout by ID
@app.route('/get_layout', methods=['GET'])
def get_layout():
    layout_id = request.args.get('id')
    with sqlite3.connect("layouts.db") as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT name, data FROM layouts WHERE id=?", (layout_id,))
        name, data = cursor.fetchone()
    if data:
        return jsonify({"data": data, "name": name})
    else:
        return jsonify({"message": "Layout not found"}), 404

# Route to delete a specific layout by ID
@app.route('/delete_layout', methods=['DELETE'])
def delete_layout():
    layout_id = request.args.get('id')
    with sqlite3.connect("layouts.db") as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM layouts WHERE id=?", (layout_id,))
        conn.commit()
    return jsonify({"message": "Layout deleted!"}), 200

if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0")
