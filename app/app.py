from flask import Flask, jsonify
import psycopg2
import os

app = Flask(__name__)

# Fetch database connection details from environment variables
db_user = os.getenv('POSTGRES_USER', 'postgres')
db_password = os.getenv('POSTGRES_PASSWORD', 'password')
db_name = os.getenv('POSTGRES_DB', 'sampledb')
db_host = os.getenv('POSTGRES_HOST', 'db')
db_port = os.getenv('POSTGRES_PORT', '5432')

def get_db_connection():
    conn = psycopg2.connect(
        host=db_host,
        database=db_name,
        user=db_user,
        password=db_password,
        port=db_port
    )
    return conn

@app.route('/')
def hello():
    return "Hello, World! \nA sample Flask application running in Docker. - from $USER"

@app.route('/users')
def get_users():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users;')
    users = cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify(users)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
