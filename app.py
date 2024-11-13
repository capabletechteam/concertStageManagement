from flask import Flask, render_template, request, jsonify
import sqlite3
import json

app = Flask(__name__)

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

# Route to save a layout
@app.route('/save_layout', methods=['POST'])
def save_layout():
    layout_data = request.json.get('data')
    layout_name = request.json.get('name')
    with sqlite3.connect("layouts.db") as conn:
        cursor = conn.cursor()
        cursor.execute("INSERT INTO layouts (name, data) VALUES (?, ?)", (layout_name, json.dumps(layout_data)))
    return jsonify({"message": "Layout saved!"}), 200

# Route to get all layouts
@app.route('/get_layouts', methods=['GET'])
def get_layouts():
    with sqlite3.connect("layouts.db") as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id, name, data FROM layouts")
        layouts = [{"id": row[0], "name": row[1], "data": json.loads(row[2])} for row in cursor.fetchall()]
    return jsonify(layouts)

# Route to get a specific layout by ID
@app.route('/get_layout', methods=['GET'])
def get_layout():
    layout_id = request.args.get('id')
    with sqlite3.connect("layouts.db") as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT data FROM layouts WHERE id=?", (layout_id,))
        data = cursor.fetchone()
    return jsonify(json.loads(data[0]))

if __name__ == '__main__':
    app.run(debug=True)
