from flask import Flask, render_template, request, redirect, url_for, flash, session
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import pyodbc

app = Flask(__name__)
app.secret_key = "agrishare_secure_session_key"

# SQL Server Connection Configuration
CONN_STR = (
    "DRIVER={ODBC Driver 17 for SQL Server};"
    "SERVER=localhost;"
    "DATABASE=AgriShareDB;"
    "Trusted_Connection=yes;"
)

def get_db_connection():
    return pyodbc.connect(CONN_STR)


# ==========================================
# AUTHENTICATION ROUTES
# ==========================================

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email'].strip()
        password = request.form['password']

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT UserID, FullName, PasswordHash FROM Users WHERE Email = ?", (email,))
        user = cursor.fetchone()
        conn.close()

        if user and check_password_hash(user[2], password):
            session['user_id'] = user[0]
            session['user_name'] = user[1]
            flash(f"Welcome back, {user[1]}!", "success")
            return redirect(url_for('dashboard'))
        else:
            flash("Invalid email or password.", "danger")

    return render_template('login.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        full_name = request.form['full_name'].strip()
        email = request.form['email'].strip()
        password = request.form['password']
        phone = request.form['phone'].strip()
        village = request.form['village'].strip()

        hashed_password = generate_password_hash(password)

        conn = get_db_connection()
        cursor = conn.cursor()

        # Check if email exists
        cursor.execute("SELECT UserID FROM Users WHERE Email = ?", (email,))
        if cursor.fetchone():
            flash("An account with this email already exists.", "danger")
            conn.close()
            return redirect(url_for('register'))

        cursor.execute("""
            INSERT INTO Users (FullName, Email, PasswordHash, PhoneNumber, VillageName)
            VALUES (?, ?, ?, ?, ?)
        """, (full_name, email, hashed_password, phone, village))

        conn.commit()
        conn.close()

        flash("Registration successful! Please login.", "success")
        return redirect(url_for('login'))

    return render_template('register.html')


@app.route('/logout')
def logout():
    session.clear()
    flash("You have been logged out.", "info")
    return redirect(url_for('login'))


# ==========================================
# CHANGE PASSWORD ROUTE
# ==========================================

@app.route('/change-password', methods=['GET', 'POST'])
def change_password():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        current_password = request.form['current_password']
        new_password = request.form['new_password']
        confirm_password = request.form['confirm_password']

        if new_password != confirm_password:
            flash("New password and confirmation do not match.", "danger")
            return redirect(url_for('change_password'))

        if len(new_password) < 6:
            flash("New password must be at least 6 characters long.", "danger")
            return redirect(url_for('change_password'))

        user_id = session['user_id']
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT PasswordHash FROM Users WHERE UserID = ?", (user_id,))
        row = cursor.fetchone()

        if not row:
            conn.close()
            flash("User not found.", "danger")
            return redirect(url_for('logout'))

        current_hash = row[0]

        if not check_password_hash(current_hash, current_password):
            conn.close()
            flash("Current password is incorrect.", "danger")
            return redirect(url_for('change_password'))

        new_hashed = generate_password_hash(new_password)
        cursor.execute("UPDATE Users SET PasswordHash = ? WHERE UserID = ?", (new_hashed, user_id))
        conn.commit()
        conn.close()

        flash("Password updated successfully!", "success")
        return redirect(url_for('dashboard'))

    return render_template('change_password.html', user_name=session.get('user_name'))


# ==========================================
# CORE DASHBOARD & BOOKING ROUTES
# ==========================================

@app.route('/')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    user_id = session['user_id']
    village_filter = request.args.get('village', '').strip()
    category_filter = request.args.get('category', '').strip()

    conn = get_db_connection()
    cursor = conn.cursor()

    # 1. Fetch Stats Counters
    cursor.execute("SELECT COUNT(*) FROM Equipment WHERE IsAvailable = 1")
    total_equipment = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM Bookings WHERE RenterID = ? AND BookingStatus = 'Approved'", (user_id,))
    active_rentals = cursor.fetchone()[0]

    # 2. Query Equipment Listings (Excluding machinery owned by current user)
    query = """
        SELECT e.EquipmentID, e.Title, e.Category, e.HourlyRate, e.DailyRate, u.VillageName, u.FullName
        FROM Equipment e
        JOIN Users u ON e.OwnerID = u.UserID
        WHERE e.IsAvailable = 1 AND e.OwnerID != ?
    """
    params = [user_id]

    if village_filter:
        query += " AND u.VillageName LIKE ?"
        params.append(f"%{village_filter}%")
    if category_filter:
        query += " AND e.Category = ?"
        params.append(category_filter)

    cursor.execute(query, params)
    equipment_list = cursor.fetchall()

    # 3. Query Bookings Made BY Current User (As Renter)
    cursor.execute("""
        SELECT b.BookingID, e.Title, u.FullName, u.PhoneNumber, b.StartDate, b.EndDate, b.TotalCost, b.BookingStatus
        FROM Bookings b
        JOIN Equipment e ON b.EquipmentID = e.EquipmentID
        JOIN Users u ON e.OwnerID = u.UserID
        WHERE b.RenterID = ?
        ORDER BY b.BookingID DESC
    """, (user_id,))
    my_bookings = cursor.fetchall()

    # 4. Query Requests FOR Current User's Machinery (As Owner)
    cursor.execute("""
        SELECT b.BookingID, e.Title, u.FullName, u.PhoneNumber, b.StartDate, b.EndDate, b.TotalCost, b.BookingStatus
        FROM Bookings b
        JOIN Equipment e ON b.EquipmentID = e.EquipmentID
        JOIN Users u ON b.RenterID = u.UserID
        WHERE e.OwnerID = ?
        ORDER BY b.BookingID DESC
    """, (user_id,))
    owner_requests = cursor.fetchall()

    # 5. Query Current User's OWN Equipment Listings
    cursor.execute("""
        SELECT e.EquipmentID, e.Title, e.Category, e.HourlyRate, e.DailyRate, e.IsAvailable
        FROM Equipment e
        WHERE e.OwnerID = ?
        ORDER BY e.EquipmentID DESC
    """, (user_id,))
    my_equipment = cursor.fetchall()

    conn.close()

    return render_template(
        'dashboard.html',
        equipment=equipment_list,
        bookings=my_bookings,
        owner_requests=owner_requests,
        my_equipment=my_equipment,
        stats={'total': total_equipment, 'active': active_rentals},
        selected_village=village_filter,
        selected_category=category_filter,
        user_name=session.get('user_name')
    )


# ==========================================
# EQUIPMENT MANAGEMENT ROUTES
# ==========================================

@app.route('/add-equipment', methods=['GET', 'POST'])
def add_equipment():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        category = request.form.get('category', '').strip()
        hourly_rate = request.form.get('hourly_rate')
        daily_rate = request.form.get('daily_rate')

        if not title or not category or not hourly_rate:
            flash("Please fill in all required fields.", "danger")
            return redirect(url_for('add_equipment'))

        owner_id = session['user_id']

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO Equipment (Title, Category, HourlyRate, DailyRate, OwnerID, IsAvailable)
            VALUES (?, ?, ?, ?, ?, 1)
        """, (title, category, hourly_rate, daily_rate if daily_rate else None, owner_id))
        conn.commit()
        conn.close()

        flash(f"🎉 '{title}' has been published to the marketplace!", "success")
        return redirect(url_for('dashboard'))

    return render_template('add_equipment.html', user_name=session.get('user_name'))


@app.route('/delete-equipment/<int:equipment_id>', methods=['POST'])
def delete_equipment(equipment_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))

    conn = get_db_connection()
    cursor = conn.cursor()

    # Only allow the owner to delete their own equipment
    cursor.execute("SELECT Title FROM Equipment WHERE EquipmentID = ? AND OwnerID = ?", (equipment_id, session['user_id']))
    row = cursor.fetchone()

    if not row:
        conn.close()
        flash("Equipment not found or you don't have permission to delete it.", "danger")
        return redirect(url_for('dashboard'))

    cursor.execute("DELETE FROM Bookings WHERE EquipmentID = ?", (equipment_id,))
    cursor.execute("DELETE FROM Equipment WHERE EquipmentID = ?", (equipment_id,))
    conn.commit()
    conn.close()

    flash(f"🗑️ '{row[0]}' has been removed from the marketplace.", "info")
    return redirect(url_for('dashboard'))


@app.route('/create-booking', methods=['POST'])
def create_booking():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    equipment_id = request.form.get('equipment_id')
    start_date_str = request.form.get('start_date')
    end_date_str = request.form.get('end_date')
    renter_id = session['user_id']

    # Safely convert HTML datetime string format ('YYYY-MM-DDTHH:MM') to Python datetime objects
    fmt = '%Y-%m-%dT%H:%M'
    start_dt = datetime.strptime(start_date_str, fmt)
    end_dt = datetime.strptime(end_date_str, fmt)

    # Calculate rental duration in hours
    hours = max(1, int((end_dt - start_dt).total_seconds() / 3600))

    conn = get_db_connection()
    cursor = conn.cursor()

    # Only allow booking if the equipment is currently available.
    cursor.execute("SELECT HourlyRate, IsAvailable FROM Equipment WHERE EquipmentID = ?", (equipment_id,))
    eq_row = cursor.fetchone()

    if not eq_row:
        conn.close()
        flash("⚠️ Equipment not found.", "danger")
        return redirect(url_for('dashboard'))

    rate, is_available = eq_row

    if not is_available:
        conn.close()
        flash("⚠️ This equipment is currently not available for booking. Please try again later.", "danger")
        return redirect(url_for('dashboard'))

    total_cost = hours * rate

    # Prevent double-booking: reject if this equipment already has an
    # overlapping booking that is Approved or Returned (in the active window).
    cursor.execute("""
        SELECT BookingID FROM Bookings
        WHERE EquipmentID = ?
          AND BookingStatus IN ('Approved', 'Returned')
          AND StartDate < ? AND EndDate > ?
    """, (equipment_id, end_dt, start_dt))
    if cursor.fetchone():
        conn.close()
        flash("⚠️ This equipment is already booked for the selected time slot. Please choose a different time.", "danger")
        return redirect(url_for('dashboard'))

    # Insert new booking record using native datetime objects
    cursor.execute("""
        INSERT INTO Bookings (EquipmentID, RenterID, StartDate, EndDate, TotalCost, BookingStatus)
        VALUES (?, ?, ?, ?, ?, 'Pending')
    """, (equipment_id, renter_id, start_dt, end_dt, total_cost))

    conn.commit()
    conn.close()

    flash("Booking request submitted successfully!", "success")
    return redirect(url_for('dashboard'))


@app.route('/approve-booking/<int:booking_id>')
def approve_booking(booking_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))

    conn = get_db_connection()
    cursor = conn.cursor()

    # Fetch the booking details to verify ownership and check for time conflicts.
    # The owner is the one approving, so only the equipment owner may approve.
    cursor.execute("""
        SELECT b.EquipmentID, b.StartDate, b.EndDate, e.OwnerID
        FROM Bookings b
        JOIN Equipment e ON b.EquipmentID = e.EquipmentID
        WHERE b.BookingID = ?
    """, (booking_id,))
    row = cursor.fetchone()

    if not row:
        conn.close()
        flash("Booking not found.", "danger")
        return redirect(url_for('dashboard'))

    equipment_id, b_start, b_end, owner_id = row

    if owner_id != session['user_id']:
        conn.close()
        flash("You don't have permission to approve this booking.", "danger")
        return redirect(url_for('dashboard'))

    # Reject approval if another Approved/Returned booking overlaps this one.
    cursor.execute("""
        SELECT BookingID FROM Bookings
        WHERE EquipmentID = ?
          AND BookingID != ?
          AND BookingStatus IN ('Approved', 'Returned')
          AND StartDate < ? AND EndDate > ?
    """, (equipment_id, booking_id, b_end, b_start))
    if cursor.fetchone():
        conn.close()
        flash("⚠️ Cannot approve: this time slot overlaps with an already-approved booking.", "danger")
        return redirect(url_for('dashboard'))

    cursor.execute("""
        UPDATE Bookings
        SET BookingStatus = 'Approved'
        WHERE BookingID = ?
    """, (booking_id,))

    # Mark equipment as unavailable while it is rented out
    cursor.execute("UPDATE Equipment SET IsAvailable = 0 WHERE EquipmentID = ?", (equipment_id,))

    conn.commit()
    conn.close()

    flash("Booking request approved!", "success")
    return redirect(url_for('dashboard'))


@app.route('/reject-booking/<int:booking_id>')
def reject_booking(booking_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE Bookings
        SET BookingStatus = 'Cancelled'
        WHERE BookingID = ?
    """, (booking_id,))

    conn.commit()
    conn.close()

    flash("Booking request rejected.", "info")
    return redirect(url_for('dashboard'))


# ==========================================
# RETURN FLOW ROUTES
# ==========================================

@app.route('/return-equipment/<int:booking_id>', methods=['POST'])
def return_equipment(booking_id):
    """Renter marks the equipment as handed back to the owner."""
    if 'user_id' not in session:
        return redirect(url_for('login'))

    conn = get_db_connection()
    cursor = conn.cursor()

    # Only the renter of this booking can mark it as returned
    cursor.execute(
        "SELECT BookingStatus FROM Bookings WHERE BookingID = ? AND RenterID = ?",
        (booking_id, session['user_id'])
    )
    row = cursor.fetchone()

    if not row:
        conn.close()
        flash("Booking not found or you don't have permission.", "danger")
        return redirect(url_for('dashboard'))

    if row[0] != 'Approved':
        conn.close()
        flash("You can only return equipment that is currently approved.", "danger")
        return redirect(url_for('dashboard'))

    cursor.execute("UPDATE Bookings SET BookingStatus = 'Returned' WHERE BookingID = ?", (booking_id,))
    conn.commit()
    conn.close()

    flash("✅ Equipment marked as returned. The owner will confirm receipt.", "success")
    return redirect(url_for('dashboard'))


@app.route('/confirm-return/<int:booking_id>', methods=['POST'])
def confirm_return(booking_id):
    """Owner confirms they received the equipment back, making it available again."""
    if 'user_id' not in session:
        return redirect(url_for('login'))

    conn = get_db_connection()
    cursor = conn.cursor()

    # Only the owner of the equipment can confirm the return
    cursor.execute("""
        SELECT b.EquipmentID, e.OwnerID
        FROM Bookings b
        JOIN Equipment e ON b.EquipmentID = e.EquipmentID
        WHERE b.BookingID = ?
    """, (booking_id,))
    row = cursor.fetchone()

    if not row:
        conn.close()
        flash("Booking not found.", "danger")
        return redirect(url_for('dashboard'))

    equipment_id, owner_id = row

    if owner_id != session['user_id']:
        conn.close()
        flash("You don't have permission to confirm this return.", "danger")
        return redirect(url_for('dashboard'))

    cursor.execute("UPDATE Bookings SET BookingStatus = 'Completed' WHERE BookingID = ?", (booking_id,))
    cursor.execute("UPDATE Equipment SET IsAvailable = 1 WHERE EquipmentID = ?", (equipment_id,))
    conn.commit()
    conn.close()

    flash("✅ Equipment received back. It is now available for other bookings.", "success")
    return redirect(url_for('dashboard'))


if __name__ == '__main__':
    app.run(debug=True)
