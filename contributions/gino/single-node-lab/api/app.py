from flask import Flask, jsonify, request
import os
import psycopg2

app = Flask(__name__)


def get_connection():
    return psycopg2.connect(
        host=os.environ["PGHOST"],
        port=os.environ.get("PGPORT", "5432"),
        dbname=os.environ["PGDATABASE"],
        user=os.environ["PGUSER"],
        password=os.environ["PGPASSWORD"],
    )


def initialize_database():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS patients (
            id SERIAL PRIMARY KEY,
            patient_id VARCHAR(20) UNIQUE NOT NULL,
            name VARCHAR(100) NOT NULL,
            department VARCHAR(100) NOT NULL,
            status VARCHAR(50) NOT NULL
        )
    """)

    cursor.execute("""
        INSERT INTO patients (patient_id, name, department, status)
        VALUES
            ('P1001', 'John Doe', 'Cardiology', 'Active'),
            ('P1002', 'Jane Smith', 'Neurology', 'Active'),
            ('P1003', 'Robert Johnson', 'Emergency', 'Discharged')
        ON CONFLICT (patient_id) DO NOTHING
    """)

    conn.commit()
    cursor.close()
    conn.close()


@app.route("/health", methods=["GET"])
def health():
    return jsonify({
        "service": "healthcare-api",
        "status": "healthy"
    })


@app.route("/patients", methods=["GET"])
def get_patients():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT patient_id, name, department, status
        FROM patients
        ORDER BY id
    """)

    patients = cursor.fetchall()

    cursor.close()
    conn.close()

    return jsonify([
        {
            "patient_id": row[0],
            "name": row[1],
            "department": row[2],
            "status": row[3]
        }
        for row in patients
    ])


@app.route("/patients/<patient_id>", methods=["GET"])
def get_patient(patient_id):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT patient_id, name, department, status
        FROM patients
        WHERE patient_id = %s
    """, (patient_id,))

    patient = cursor.fetchone()

    cursor.close()
    conn.close()

    if patient is None:
        return jsonify({"error": "Patient not found"}), 404

    return jsonify({
        "patient_id": patient[0],
        "name": patient[1],
        "department": patient[2],
        "status": patient[3]
    })


@app.route("/patients", methods=["POST"])
def create_patient():
    data = request.get_json()

    required_fields = ["patient_id", "name", "department", "status"]

    if not data or not all(field in data for field in required_fields):
        return jsonify({
            "error": "Missing required fields",
            "required": required_fields
        }), 400

    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("""
            INSERT INTO patients
                (patient_id, name, department, status)
            VALUES
                (%s, %s, %s, %s)
            RETURNING patient_id, name, department, status
        """, (
            data["patient_id"],
            data["name"],
            data["department"],
            data["status"]
        ))

        patient = cursor.fetchone()
        conn.commit()

    except psycopg2.errors.UniqueViolation:
        conn.rollback()
        cursor.close()
        conn.close()

        return jsonify({
            "error": "Patient ID already exists"
        }), 409

    cursor.close()
    conn.close()

    return jsonify({
        "patient_id": patient[0],
        "name": patient[1],
        "department": patient[2],
        "status": patient[3]
    }), 201


if __name__ == "__main__":
    initialize_database()

    app.run(
        host="0.0.0.0",
        port=5000
    )