import pandas as pd
from datetime import datetime, timedelta
import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from flask import Flask, request, jsonify, send_from_directory
import os

nltk.download('punkt')
nltk.download('stopwords')

app = Flask(__name__)
appointments_file = 'appointments.csv'
stop_words = set(stopwords.words('english'))

def load_appointments():
    if os.path.exists(appointments_file):
        return pd.read_csv(appointments_file)
    return pd.DataFrame(columns=['Name', 'Date', 'Start', 'End'])

def save_appointments(appointments):
    appointments.to_csv(appointments_file, index=False)

def parse_datetime(message):
    tokens = word_tokenize(message)
    tokens = [word for word in tokens if word.lower() not in stop_words]
    now = datetime.now()
    if 'today' in tokens or 'later' in tokens:
        return now + timedelta(hours=1)
    if 'tomorrow' in tokens:
        return now + timedelta(days=1)
    if 'next' in tokens and 'week' in tokens:
        return now + timedelta(weeks=1)
    return now

def find_available_slot(requested_datetime):
    appointments = load_appointments()
    requested_date = requested_datetime.date()
    office_hours_start = 9
    office_hours_end = 18

    for hour in range(office_hours_start, office_hours_end):
        slot_start = datetime.combine(requested_date, datetime.min.time()) + timedelta(hours=hour)
        slot_end = slot_start + timedelta(hours=1)
        if not ((appointments['Start'] <= slot_start.strftime('%H:%M:%S')) & (appointments['End'] > slot_start.strftime('%H:%M:%S')) & (appointments['Date'] == requested_date.strftime('%Y-%m-%d'))).any():
            return slot_start
    return None

@app.route('/chat', methods=['POST'])
def chat():
    data = request.json['message']
    message = data['content']
    chat_id = data['id']
    
    datetime_requested = parse_datetime(message)
    available_slot = find_available_slot(datetime_requested)
    
    if available_slot:
        client_name = "User"  # For simplicity, we use a default client name
        appointment = {
            'Name': client_name,
            'Date': available_slot.strftime('%Y-%m-%d'),
            'Start': available_slot.strftime('%H:%M:%S'),
            'End': (available_slot + timedelta(hours=1)).strftime('%H:%M:%S')
        }
        appointments = load_appointments()
        appointments = appointments.append(appointment, ignore_index=True)
        save_appointments(appointments)
        response = f"Appointment booked for {client_name} at {available_slot.strftime('%Y-%m-%d %H:%M:%S')}"
    else:
        response = "No available slots for the requested time."
    
    return jsonify({'message': {'content': response, 'id': chat_id}})

@app.route('/')
def index():
    return send_from_directory('.', 'index.html')

if __name__ == '__main__':
    app.run(debug=True, port=8000)