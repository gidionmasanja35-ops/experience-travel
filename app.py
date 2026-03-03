from flask import Flask, request, jsonify
from flask_cors import CORS
import mysql.connector
import smtplib
from email.message import EmailMessage

app = Flask(__name__)
CORS(app)

EMAIL = "gidionmasanja35@gmail.com"
PASSWORD = "hvzvcazqgnclhpbu"  

db_config = {
    "host": "localhost",
    "user": "root",
    "password": "",
    "database": "bookingdb"
}

@app.route("/", methods=["GET"])
def home():
    return jsonify({
        "status": "ok",
        "message": "Backend running ✅"
    })

@app.route("/send", methods=["POST"])
def send():
    try:
        data = request.get_json(force=True, silent=True)

        if not data:
            return jsonify({
                "status": "error",
                "message": "No JSON received"
            }), 400

        print("RECEIVED DATA:", data)

        name = data.get("name")
        email = data.get("email")
        phone = data.get("phone")
        package = data.get("package")
        date = data.get("date")
        people = data.get("people")
        message = data.get("message")

        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO bookings (name, email, phone, package, date, people, message)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (name, email, phone, package, date, people, message))

        conn.commit()
        cursor.close()
        conn.close()

        print("DATABASE SAVED ✅")

        msg = EmailMessage()
        msg["Subject"] = "New Tour Booking"
        msg["From"] = EMAIL
        msg["To"] = EMAIL

        msg.set_content(f"""
NEW TOUR BOOKING RECEIVED

Name: {name}
Email: {email}
Phone: {phone}
Package: {package}
Date: {date}
People: {people}

Message:
{message}
""")

        server = smtplib.SMTP_SSL("smtp.gmail.com", 465, timeout=30)
        server.login(EMAIL, PASSWORD)
        server.send_message(msg)
        server.quit()

        print("EMAIL SENT ✅")

        return jsonify({
            "status": "success",
            "message": "Message sent successfully ✅"
        })

    except Exception as e:
        print("ERROR ❌:", e)
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)