from flask import Flask, render_template, request, redirect, url_for, jsonify, session
import mysql.connector
import random
import datetime

app = Flask(__name__)
app.secret_key = 'supersecretkey'  # Needed for session

# --- Helper for train/station suggestions (static for now) ---
TRAIN_SUGGESTIONS = [
    {"number": "1235", "name": "Rajdhani Express"},
    {"number": "1201", "name": "Shatabdi Express"},
    {"number": "1102", "name": "Duronto Express"},
    {"number": "1405", "name": "Garib Rath"},
]
STATION_SUGGESTIONS = [
    {"code": "YPR", "name": "Bangalore Yesvantpur Junction"},
    {"code": "GKP", "name": "Gorakhpur Junction"},
    {"code": "NDLS", "name": "New Delhi"},
    {"code": "BCT", "name": "Mumbai Central"},
]

# List of common Indian cities (for generating random train examples)
INDIAN_CITIES = [
    "Delhi", "Mumbai", "Bangalore", "Chennai", "Hyderabad", "Pune",
    "Jaipur", "Ahmedabad", "Kolkata", "Lucknow", "Chandigarh", "Nagpur",
    "Bhopal", "Indore", "Surat", "Thiruvananthapuram", "Coimbatore"
]

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/book', methods=['GET', 'POST'])
def book():
    if request.method == 'POST':
        train_no = request.form['train_no']
        name = request.form['name']
        mobile = request.form['mobile']
        adhaar = request.form['adhaar']
        ticket_class = request.form['class']
        date = datetime.datetime.now().strftime('%d-%m-%y')
        booking_id = random.randint(1000, 9999)
        # Store booking info in session for payment
        session['booking'] = {
            'train_no': train_no,
            'name': name,
            'mobile': mobile,
            'adhaar': adhaar,
            'ticket_class': ticket_class,
            'date': date,
            'booking_id': booking_id
        }
        return redirect(url_for('payment'))
    return render_template('book.html', train_suggestions=TRAIN_SUGGESTIONS, station_suggestions=STATION_SUGGESTIONS)

@app.route('/payment', methods=['GET', 'POST'])
def payment():
    booking = session.get('booking')
    if not booking:
        return redirect(url_for('book'))
    if request.method == 'POST':
        # Insert into MySQL
        try:
            conn = mysql.connector.connect(host='localhost', user='root', password='', database='railway')
            cur = conn.cursor()
            cur.execute("INSERT INTO bookings (Train_No, Passenger_Name, Mobile_No, Passenger_Adhaar, Date_Of_Booking, Booking_ID, Class) VALUES (%s, %s, %s, %s, %s, %s, %s)",
                        (booking['train_no'], booking['name'], booking['mobile'], booking['adhaar'], booking['date'], booking['booking_id'], booking['ticket_class']))
            conn.commit()
            cur.close()
            conn.close()
            # Clear session booking after success
            session.pop('booking', None)
            return render_template('success.html', name=booking['name'], train_no=booking['train_no'], booking_id=booking['booking_id'], ticket_class=booking['ticket_class'], date=booking['date'])
        except Exception as e:
            return render_template('payment.html', booking=booking, error=str(e))
    return render_template('payment.html', booking=booking)

@app.route('/cancel', methods=['GET', 'POST'])
def cancel():
    message = None
    booking_details = None
    if request.method == 'POST':
        booking_id = request.form.get('booking_id')
        confirm_cancel = request.form.get('confirm_cancel') # Check for confirmation flag

        if not booking_id:
            message = ('error', 'Please enter a Booking ID.')
        elif confirm_cancel:
            # User confirmed cancellation, proceed to delete
            try:
                conn = mysql.connector.connect(host='localhost', user='root', password='', database='railway')
                cur = conn.cursor()
                cur.execute('DELETE FROM bookings WHERE Booking_ID=%s', (booking_id,))
                conn.commit()
                if cur.rowcount > 0:
                    message = ('success', f'Booking ID {booking_id} cancelled successfully!')
                else:
                    message = ('error', f'No booking found with ID {booking_id}. No cancellation performed.')
                cur.close()
                conn.close()
            except Exception as e:
                message = ('error', f'Error cancelling booking: {str(e)}')
        else:
            # Booking ID submitted, fetch details to show for confirmation
            try:
                conn = mysql.connector.connect(host='localhost', user='root', password='', database='railway')
                cur = conn.cursor()
                cur.execute('SELECT Train_No, Passenger_Name, Mobile_No, Passenger_Adhaar, Date_Of_Booking, Booking_ID, Class FROM bookings WHERE Booking_ID=%s', (booking_id,))
                booking = cur.fetchone()
                cur.close()
                conn.close()
                if booking:
                    # Convert tuple to dictionary for easier access in template
                    booking_details = {
                        'Train_No': booking[0],
                        'Passenger_Name': booking[1],
                        'Mobile_No': booking[2],
                        'Passenger_Adhaar': booking[3],
                        'Date_Of_Booking': booking[4],
                        'Booking_ID': booking[5],
                        'Class': booking[6],
                    }
                else:
                    message = ('error', f'No booking found with ID {booking_id}.')
            except Exception as e:
                 message = ('error', f'Error fetching booking details: {str(e)}')

    # Pass booking_details and message to the template
    return render_template('cancel.html', message=message, booking_details=booking_details)

@app.route('/fares', methods=['GET', 'POST'])
def fares():
    results = []
    from_station_input = request.form.get('from_station', '')
    to_station_input = request.form.get('to_station', '')
    page = request.args.get('page', 1, type=int)
    per_page = 7 # Number of results per page
    all_fares = [] # Store all generated fares

    # List of common Indian routes (for generating random examples)
    INDIAN_ROUTES = [
        ("Delhi", "Mumbai"), ("Mumbai", "Bangalore"), ("Bangalore", "Chennai"),
        ("Chennai", "Hyderabad"), ("Hyderabad", "Pune"), ("Pune", "Jaipur"),
        ("Jaipur", "Ahmedabad"), ("Ahmedabad", "Kolkata"), ("Kolkata", "Lucknow"),
        ("Lucknow", "Chandigarh"), ("Chandigarh", "Nagpur"), ("Nagpur", "Bhopal"),
        ("Bhopal", "Indore"), ("Indore", "Surat"), ("Surat", "Thiruvananthapuram"),
        ("Thiruvananthapuram", "Coimbatore")
    ]

    # Generate all potential fake train fares (more than 15 to allow for filtering)
    import random
    # Generate more random routes to increase the chance of matching user input
    for i in range(100): # Generate 100 potential fares
        route_pair = random.choice(INDIAN_ROUTES)
        from_station = route_pair[0]
        to_station = route_pair[1]

        distance = random.randint(100, 2000)
        sleeper_fare = round(distance * 1.5 + random.randint(50, 200), 0)
        ac3_fare = round(distance * 2 + random.randint(100, 400), 0)
        ac2_fare = round(distance * 3 + random.randint(200, 600), 0)
        ac1_fare = round(distance * 4 + random.randint(400, 1000), 0)

        min_hours = max(1, distance // 100 * 2)
        max_hours = min_hours + random.randint(2, 6)
        journey_time = f"{min_hours}-{max_hours} hrs"

        all_fares.append({
            'from': from_station,
            'to': to_station,
            'distance': distance,
            'sleeper': sleeper_fare,
            'ac3': ac3_fare,
            'ac2': ac2_fare,
            'ac1': ac1_fare,
            'journey_time': journey_time
        })

    # Filter fares based on user input
    filtered_fares = all_fares
    if from_station_input or to_station_input:
        filtered_fares = [f for f in all_fares
                          if (not from_station_input or from_station_input.lower() in f['from'].lower())
                          and (not to_station_input or to_station_input.lower() in f['to'].lower())]

    # Implement pagination
    total_fares = len(filtered_fares)
    start_index = (page - 1) * per_page
    end_index = start_index + per_page
    paginated_fares = filtered_fares[start_index:end_index]
    total_pages = (total_fares + per_page - 1) // per_page

    # Render the page, passing paginated results, input values, and pagination info
    return render_template('fares.html', results=paginated_fares, from_station=from_station_input, to_station=to_station_input, page=page, total_pages=total_pages)

@app.route('/suggest_cities')
def suggest_cities():
    query = request.args.get('query', '').lower()
    suggestions = [city for city in INDIAN_CITIES if query in city.lower()]
    return jsonify(suggestions)

@app.route('/bookings', methods=['GET'])
def bookings():
    mobile = request.args.get('mobile')
    bookings = None
    if mobile:
        try:
            conn = mysql.connector.connect(host='localhost', user='root', password='', database='railway')
            cur = conn.cursor()
            cur.execute('SELECT * FROM bookings WHERE Mobile_No=%s', (mobile,))
            bookings = cur.fetchall()
            cur.close()
            conn.close()
        except Exception as e:
            bookings = []
    return render_template('bookings.html', bookings=bookings, mobile=mobile)

@app.route('/trains', methods=['GET'])
def trains():
    results = None
    from_station_input = request.args.get('from_station', '')
    to_station_input = request.args.get('to_station', '')
    travel_date = request.args.get('travel_date', '')
    travel_class = request.args.get('class', '')
    page = request.args.get('page', 1, type=int)
    per_page = 7 # Number of results per page
    all_trains = [] # Store all generated trains

    # Generate a larger set of fake trains
    import random
    from datetime import datetime, timedelta

    for i in range(100): # Generate 100 potential trains
        # Select random cities for the route
        from_city = random.choice(INDIAN_CITIES)
        to_city = random.choice([city for city in INDIAN_CITIES if city != from_city])

        train_no = random.randint(10000, 99999) # 5-digit train number
        train_name = random.choice(["Express", "Mail", "Superfast", "Duronto", "Rajdhani"]) + f" {random.randint(100, 999)}"

        # Generate realistic departure and arrival times
        dep_hour = random.randint(0, 23)
        dep_min = random.randint(0, 59)
        departure_time = f"{dep_hour:02d}:{dep_min:02d}"

        # Ensure arrival is after departure (possibly next day)
        travel_hours = random.randint(1, 36) # Random journey up to 36 hours
        arrival_hour = (dep_hour + travel_hours) % 24
        arrival_min = random.randint(0, 59)
        arrival_time = f"{arrival_hour:02d}:{arrival_min:02d}"

        # Calculate duration
        dep_dt = datetime.strptime(departure_time, '%H:%M')
        arr_dt = datetime.strptime(arrival_time, '%H:%M')
        if arr_dt < dep_dt:
            arr_dt += timedelta(days=1)
        duration_td = arr_dt - dep_dt
        duration_hours = duration_td.seconds // 3600
        duration_mins = (duration_td.seconds % 3600) // 60
        duration = f"{duration_hours}h {duration_mins}m"

        # Generate fake fares/availability for classes
        distance = random.randint(100, 2000) # Needed for fare calculation base
        fares = {
            'SL': {'price': round(distance * 0.8 + random.randint(50, 200), 0), 'availability': f'GNWL {random.randint(10, 200)}' if random.random() > 0.2 else 'AVL', 'status': 'Available' if random.random() > 0.2 else 'Waitlist'},
            '3A': {'price': round(distance * 1.5 + random.randint(100, 400), 0), 'availability': f'GNWL {random.randint(5, 100)}' if random.random() > 0.4 else 'AVL', 'status': 'Available' if random.random() > 0.4 else 'Waitlist'},
            '2A': {'price': round(distance * 2.5 + random.randint(200, 600), 0), 'availability': f'GNWL {random.randint(2, 50)}' if random.random() > 0.6 else 'AVL', 'status': 'Available' if random.random() > 0.6 else 'Waitlist'},
            '1A': {'price': round(distance * 4.0 + random.randint(400, 1000), 0), 'availability': f'GNWL {random.randint(1, 20)}' if random.random() > 0.8 else 'AVL', 'status': 'Available' if random.random() > 0.8 else 'Waitlist'},
        }

        all_trains.append({
            'train_no': train_no,
            'train_name': train_name,
            'from': from_city,
            'to': to_city,
            'departure': departure_time,
            'arrival': arrival_time,
            'duration': duration,
            'fares': fares
        })

    # Filter trains based on user input
    filtered_trains = all_trains
    if from_station_input:
        filtered_trains = [t for t in filtered_trains if from_station_input.lower() in t['from'].lower()]
    if to_station_input:
        filtered_trains = [t for t in filtered_trains if to_station_input.lower() in t['to'].lower()]
    # Note: Filtering by date and class would require more complex logic with fake data generation
    # For now, we filter by from/to stations only

    # Implement pagination
    total_trains = len(filtered_trains)
    start_index = (page - 1) * per_page
    end_index = start_index + per_page
    paginated_trains = filtered_trains[start_index:end_index]
    total_pages = (total_trains + per_page - 1) // per_page

    # Render the page, passing paginated results, input values, and pagination info
    return render_template('trains.html', results=paginated_trains, from_station=from_station_input, to_station=to_station_input, travel_date=travel_date, travel_class=travel_class, page=page, total_pages=total_pages)

if __name__ == '__main__':
    app.run(debug=True) 