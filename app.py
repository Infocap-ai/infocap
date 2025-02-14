from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import psycopg2

app = Flask(__name__)
CORS(app)  # Enable CORS

@app.route("/")
def home():
    return render_template("index.html")  # Ensure index.html exists in 'templates' folder

# Database connection parameters
db_params = {
    "dbname": "postgres",
    "user": "postgres",
    "password": "admin",
    "host": "localhost",
    "port": "5432"
}

# Function to connect to the database
def get_db_connection():
    return psycopg2.connect(**db_params)

# Create table if not exists
with get_db_connection() as conn:
    with conn.cursor() as cur:
        cur.execute("""
            CREATE TABLE IF NOT EXISTS employees (
                id SERIAL PRIMARY KEY,
                name VARCHAR(100) NOT NULL,
                age INT DEFAULT 0,
                department VARCHAR(50) NOT NULL
            );
        """)
        conn.commit()

@app.route("/employees", methods=["GET"])
def get_all_employees():
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM employees;")
            employees = [{"id": row[0], "name": row[1], "age": row[2], "department": row[3]} for row in cur.fetchall()]
    return jsonify(employees)

@app.route("/employee/<int:id>", methods=["GET"])
def get_employee(id):
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM employees WHERE id = %s;", (id,))
            row = cur.fetchone()
    if row:
        return jsonify({"id": row[0], "name": row[1], "age": row[2], "department": row[3]})
    return jsonify({"error": "Employee not found"}), 404

@app.route("/employee", methods=["POST"])
def create_employee():
    data = request.json
    name = data.get("name", "").strip()
    age = data.get("age", 0)
    department = data.get("department", "").strip()

    if not name or not department:
        return jsonify({"error": "Name and department cannot be empty"}), 400

    try:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "INSERT INTO employees (name, age, department) VALUES (%s, %s, %s) RETURNING id;",
                    (name, age, department)
                )
                emp_id = cur.fetchone()[0]
                conn.commit()
        return jsonify({"message": "Employee added successfully!", "id": emp_id})
    except psycopg2.Error as e:
        return jsonify({"error": str(e)}), 500

@app.route("/employee/<int:id>", methods=["PUT"])
def update_employee(id):
    data = request.json
    name = data.get("name", "").strip()
    age = data.get("age", 0)
    department = data.get("department", "").strip()

    if not name or not department:
        return jsonify({"error": "Name and department cannot be empty"}), 400

    try:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "UPDATE employees SET name = %s, age = %s, department = %s WHERE id = %s;",
                    (name, age, department, id)
                )
                conn.commit()
        return jsonify({"message": "Employee updated successfully!"})
    except psycopg2.Error as e:
        return jsonify({"error": str(e)}), 500

@app.route("/employee/<int:id>", methods=["DELETE"])
def delete_employee(id):
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("DELETE FROM employees WHERE id = %s;", (id,))
                conn.commit()
        return jsonify({"message": "Employee deleted successfully!"})
    except psycopg2.Error as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)
