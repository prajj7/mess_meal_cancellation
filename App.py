from flask import Flask, request, jsonify, session, send_file
from flask_cors import CORS
from datetime import datetime, timedelta
import sqlite3
import pdfkit

app = Flask(__name__)
app.secret_key = 'your_secret_key'
CORS(app)

# Connect to SQLite
def get_db_connection():
    conn = sqlite3.connect('mess.db')
    conn.row_factory = sqlite3.Row
    return conn

# Login Route
@app.route('/login', methods=['POST'])
def login():
    data = request.json
    user_id = data['id']
    password = data['password']
    conn = get_db_connection()
    
    if user_id == 'admin':  # Admin Login
        admin = conn.execute('SELECT * FROM admin WHERE username = ? AND password = ?', (user_id, password)).fetchone()
        if admin:
            session['user'] = user_id
            session['role'] = 'admin'
            return jsonify({'success': True, 'role': 'admin'})
    else:  # Customer Login
        customer = conn.execute('SELECT * FROM customers WHERE id = ? AND password = ?', (user_id, password)).fetchone()
        if customer:
            session['user'] = user_id
            session['role'] = 'customer'
            return jsonify({'success': True, 'role': 'customer'})
    
    return jsonify({'success': False})

# Cancel Meal
@app.route('/cancel_meal', methods=['POST'])
def cancel_meal():
    if 'user' not in session or session['role'] != 'customer':
        return jsonify({'success': False, 'message': 'Unauthorized'}), 401

    data = request.json
    cancel_date = datetime.strptime(data['date'], '%Y-%m-%d').date()
    today = datetime.today().date()
    if cancel_date < today:
        return jsonify({'success': False, 'message': 'Cannot cancel past meals.'})

    if cancel_date > today + timedelta(days=30):
        return jsonify({'success': False, 'message': 'Cannot cancel more than 30 days ahead.'})

    conn = get_db_connection()
    conn.execute('INSERT INTO cancellations (customer_id, cancel_date) VALUES (?, ?)', (session['user'], cancel_date))
    conn.commit()
    conn.close()

    return jsonify({'success': True})

# View Cancellation History
@app.route('/cancellation_history')
def cancellation_history():
    if 'user' not in session or session['role'] != 'customer':
        return jsonify({'success': False}), 401

    conn = get_db_connection()
    cancellations = conn.execute('SELECT cancel_date FROM cancellations WHERE customer_id = ?', (session['user'],)).fetchall()
    conn.close()
    history = [row['cancel_date'] for row in cancellations]
    return jsonify({'history': history})

# Meal Summary (admin)
@app.route('/meal_summary')
def meal_summary():
    if 'role' not in session or session['role'] != 'admin':
        return jsonify({'success': False}), 401

    today = datetime.today().date()
    conn = get_db_connection()
    total_customers = conn.execute('SELECT COUNT(*) FROM customers').fetchone()[0]
    cancelled = conn.execute('SELECT COUNT(DISTINCT customer_id) FROM cancellations WHERE cancel_date = ?', (today,)).fetchone()[0]
    conn.close()
    meals_to_prepare = total_customers - cancelled
    return jsonify({'count': meals_to_prepare})

# Customer List (admin)
@app.route('/customer_list')
def customer_list():
    if 'role' not in session or session['role'] != 'admin':
        return jsonify({'success': False}), 401

    conn = get_db_connection()
    customers = conn.execute('SELECT id FROM customers').fetchall()
    conn.close()
    return jsonify({'customers': [{'id': c['id']} for c in customers]})

# Delete Customer (admin)
@app.route('/delete_customer', methods=['POST'])
def delete_customer():
    if 'role' not in session or session['role'] != 'admin':
        return jsonify({'success': False}), 401

    data = request.json
    conn = get_db_connection()
    conn.execute('DELETE FROM customers WHERE id = ?', (data['id'],))
    conn.commit()
    conn.close()
    return jsonify({'success': True})

# Download PDF Report
@app.route('/download_pdf')
def download_pdf():
    if 'role' not in session or session['role'] != 'admin':
        return jsonify({'success': False}), 401

    # Generate dummy HTML
    html = "<h1>Meal Report</h1><p>Details go here...</p>"
    pdfkit.from_string(html, 'report.pdf')
    return send_file('report.pdf', as_attachment=True)

# Logout
@app.route('/logout')
def logout():
    session.clear()
    return '', 204

if __name__ == '__main__':
    app.run(debug=True)
