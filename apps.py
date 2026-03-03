from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_mail import Mail, Message
import mysql.connector
import traceback

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
    return jsonify({"status": "Flask backend running"})

@app.route("/api/submit", methods=["POST"])
def submit():
    try:
        data = request.get_json()

        if not data:
            return jsonify({"success": False, "message": "No data received"}), 400

      
        fields = [
            "destination", "duration", "budget",
            "accommodationType", "experienceType",
            "specialRequests", "needFlights",
            "airportTransfer", "fullName",
            "email", "phone"
        ]

        for field in fields:
            if field not in data:
                return jsonify({"success": False, "message": f"Missing {field}"}), 400

      
        need_flights = 1 if str(data["needFlights"]).lower() in ["yes", "true", "1", "on"] else 0
        airport_transfer = 1 if str(data["airportTransfer"]).lower() in ["yes", "true", "1", "on"] else 0

        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()

        sql = """
        INSERT INTO trip_submission
        (destination, duration, budget, accommodationType, experienceType,
         specialRequests, needFlights, airportTransfer, fullName, email, phone)
        VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
        """

        values = (
            data["destination"],
            data["duration"],
            data["budget"],
            data["accommodationType"],
            data["experienceType"],
            data["specialRequests"],
            need_flights,
            airport_transfer,
            data["fullName"],
            data["email"],
            data["phone"]
        )

        cursor.execute(sql, values)
        conn.commit()

        cursor.close()
        conn.close()

        msg = Message(
            subject="New Trip Submission",
            recipients=["gidionmasanja35@gmail.com"]
        )

        msg.body = f"""
New Trip Submission

Name: {data["fullName"]}
Email: {data["email"]}
Phone: {data["phone"]}
Destination: {data["destination"]}
Duration: {data["duration"]}
Budget: {data["budget"]}
Accommodation: {data["accommodationType"]}
Experience: {data["experienceType"]}
Need Flights: {need_flights}
Airport Transfer: {airport_transfer}
Special Requests: {data["specialRequests"]}
"""

        mail.send(msg)

        return jsonify({"success": True, "message": "Saved & email sent"})

    except mysql.connector.Error as e:
        print("MYSQL ERROR:", e)
        return jsonify({"success": False, "message": "Database error"}), 500

    except Exception:
        traceback.print_exc()
        return jsonify({"success": False, "message": "Server error"}), 500



if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)