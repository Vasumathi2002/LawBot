from flask import Flask, jsonify
from flask_cors import CORS
import mysql.connector

app = Flask(__name__)
CORS(app)  # Enable CORS so your HTML can fetch data

# MySQL connection config
db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': '',
    'database': 'chatbot_db'
}

@app.route('/counts')
def get_counts():
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT district, value FROM district_counts")  # Adjust table/columns
        results = cursor.fetchall()

        counts = {row['district']: float(row['value']) for row in results}

        cursor.close()
        conn.close()
        return jsonify(counts)

    except mysql.connector.Error as err:
        return jsonify({"error": str(err)}), 500

if __name__ == '__main__':
    app.run(debug=True)
