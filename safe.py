from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_mail import Mail, Message
import mysql.connector
import os

app = Flask(__name__)
CORS(app)

app.config["MAIL_SERVER"] = "smtp.gmail.com"
app.config["MAIL_PORT"] = 587
app.config["MAIL_USE_TLS"] = True
app.config["MAIL_USERNAME"] = "gidionmasanja35@gmail.com"
app.config["MAIL_PASSWORD"] = "avas jkgf riid ycug"  
app.config["MAIL_DEFAULT_SENDER"] = "gidionmasanja35@gmail.com"

mail = Mail(app)

db_config = {
    "host": "localhost",
    "user": "flask_user",
    "password": "NewPassword123!",
    "database": "travel_db"
}

@app.route("/")
def home():
    return jsonify({"message": "Flask server running"})

@app.route("/api/submit", methods=["POST"])
def submit_trip():
    try:
        data = request.get_json()

        if not data:
            return jsonify({"success": False, "message": "No JSON received"}), 400

        required_fields = [
            "destination", "duration", "budget", "accommodationType",
            "experienceType", "specialRequests", "needFlights",
            "airportTransfer", "fullName", "email", "phone"
        ]

        for field in required_fields:
            if field not in data:
                return jsonify({
                    "success": False,
                    "message": f"Missing field: {field}"
                }), 400

        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()

        sql = """
        INSERT INTO trip_submission
        (destination, duration, budget, accommodationType, experienceType,
         specialRequests, needFlights, airportTransfer, fullName, email, phone)
        VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
        """

        values = tuple(data[field] for field in required_fields)
        cursor.execute(sql, values)
        conn.commit()

        cursor.close()
        conn.close()

        msg = Message(
            subject="New Trip Submission",
            recipients=["gidionmasanja35@gmail.com"]
        )

        msg.html = "<h3>New Trip Submission</h3>" + "".join(
            f"<p><b>{key}:</b> {data[key]}</p>"
            for key in required_fields
        )

        mail.send(msg)

        return jsonify({
            "success": True,
            "message": "Trip submitted and email sent"
        })

    except mysql.connector.Error as e:
        print("MYSQL ERROR:", e)
        return jsonify({
            "success": False,
            "message": "Database error"
        }), 500

    except Exception as e:
        print("GENERAL ERROR:", e)
        return jsonify({
            "success": False,
            "message": "Server error"
        }), 500


if __name__ == "__main__":
   app.run(host="0.0.0.0", port=5000)