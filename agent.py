from flask import Flask, request, jsonify
import pandas as pd
from datetime import datetime

app = Flask(__name__)

# Load appointments
appointments = pd.read_csv("appointments.csv")

@app.route('/chat', methods=['POST'])
def chat():
    data = request.get_json()
    user_message = data['message']['content']
    chat_id = data['message']['id']

    # Process the message and determine the response
    if "book" in user_message.lower():
        # Simplified booking process example
        appointment_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        new_appointment = {
            'Name': 'User',
            'Date': appointment_time.split()[0],
            'Start': appointment_time.split()[1],
            'End': (datetime.now().replace(hour=datetime.now().hour + 1)).strftime('%H:%M:%S')
        }
        global appointments
        appointments = pd.concat([appointments, pd.DataFrame([new_appointment])], ignore_index=True)
        response_message = f"Appointment booked for {new_appointment['Date']} from {new_appointment['Start']} to {new_appointment['End']}"
    else:
        response_message = "I can help you book an appointment. Please let me know the date and time."

    return jsonify({'message': {'content': response_message, 'id': chat_id}})

if __name__ == '__main__':
    app.run(debug=True, port=8000)