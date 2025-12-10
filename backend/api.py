from flask import Flask, jsonify
from flask_cors import CORS
import psycopg2, os

app = Flask(__name__)
CORS(app)

def get_connection():
    return psycopg2.connect(
        dbname=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASS"),
        host=os.getenv("DB_HOST"),
        port=os.getenv("DB_PORT")
    )

@app.route("/api")
def get_all_data():
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM data ORDER BY timestamp")
            columns = [desc[0] for desc in cur.description]
            rows = cur.fetchall()
            
            result = [dict(zip(columns, row)) for row in rows]
            for r in result:
                if r.get("timestamp"):
                    r["timestamp"] = r["timestamp"].isoformat()
            
            return jsonify(result)

if __name__ == "__main__":
    app.run(debug=True, port=5000)
