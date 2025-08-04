from datetime import datetime, timedelta
from flask import Flask, flash, redirect, render_template, request, session, url_for
from app import app
import math
from application.database import db
from application.models import ParkingSpot, Reservation, SpotStatus, User, ParkingLot

import io
import base64
import matplotlib.pyplot as plt


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        print("Form Submitted")
        email = request.form['email']
        password = request.form['password']
        user = User.query.filter_by(email=email).first()
        if user and user.password == password:
            session['user_id'] = user.id
            session['user_email'] = user.email
            session['username'] = user.username
            session['user_address'] = user.address
            session['user_password'] = user.password
            session['user_pincode'] = user.pincode
            session['user_role'] = user.role
            flash("Login Successful")
            return redirect(url_for('dashboard'))
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        address = request.form['address']
        pincode = request.form['pincode']
        user = User(username=username, email=email, password=password, address=address, pincode=pincode, role= 'user')
        db.session.add(user)
        db.session.commit()
        flash("Registration Successful")
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/dashboard')
def dashboard():
    if "user_id" not in session:
        return redirect(url_for('login'))

    role = session['user_role']
    username = session['username']

    if role == 'admin':
        parking_lot = ParkingLot.query.all()
        return render_template('dashboard.html', username=username, role=role, parking_lot=parking_lot)

    elif role == 'user':
        lots = ParkingLot.query.all()
        reservations = Reservation.query.filter_by(user_id=session['user_id'], status='active').all()
        return render_template('dashboard.html', username=username, role=role, parking_lots=lots, reservations=reservations)

    return render_template('index.html')


@app.route('/logout')
def logout():
    session.pop('user_id', None)
    session.pop('user_email', None)
    session.pop('user_password', None)
    session.pop('user_role', None)
    session.pop('username', None)
    session.pop('user_address', None)
    session.pop('pincode', None)
    return render_template('index.html')

@app.route('/user')
def user():
    all_users = User.query.filter(User.role != 'admin').all()
    return render_template('user.html', users=all_users)

@app.route('/search', methods=['GET', 'POST'])
def search_page():
    results = []
    if request.method == 'POST':
        search_by = request.form['search_by']
        query = request.form['query']

        if search_by == 'user_id':
            results = User.query.filter(User.id == query).all()
        elif search_by == 'username':
            results = User.query.filter(User.username.ilike(f"%{query}%")).all()
        elif search_by == 'address':
            results = User.query.filter(User.address.ilike(f"%{query}%")).all()
        elif search_by == 'prime_location':
            results = ParkingLot.query.filter(ParkingLot.prime_location.ilike(f"%{query}%")).all()

    return render_template('search_page.html', results=results)


@app.route('/summary')
def summary():
    if "user_id" not in session:
        return redirect(url_for('login'))

    lots = ParkingLot.query.all()

    lot_names = []
    revenue = []
    available = []
    occupied = []

    for lot in lots:
        lot_names.append(lot.prime_location)

        a_count = o_count = 0
        for spot in lot.spots:
            if spot.status.value == 'A':
                a_count += 1
            elif spot.status.value == 'O':
                o_count += 1

        available.append(a_count)
        occupied.append(o_count)

        # Revenue = price * occupied spots
        lot_revenue = o_count * lot.price
        revenue.append(lot_revenue)

    # ---------- Pie Chart: Available vs Occupied ----------
    total_available = sum(available)
    total_occupied = sum(occupied)

    slot_labels = ['Available', 'Occupied']
    slot_sizes = [total_available, total_occupied]

    if total_available == 0 and total_occupied == 0:
        donut_chart = ""
    else:
        fig1, ax1 = plt.subplots(facecolor='black')
        ax1.set_facecolor('black')
        ax1.pie(slot_sizes, labels=slot_labels, autopct='%1.1f%%', startangle=90, textprops={'color': 'white'})
        ax1.axis('equal')
        buf1 = io.BytesIO()
        plt.savefig(buf1, format='png', facecolor=fig1.get_facecolor())
        buf1.seek(0)
        donut_chart = base64.b64encode(buf1.read()).decode('utf-8')
        plt.close(fig1)

    # ---------- Bar Chart: Revenue per Lot ----------
    valid_lot_names = []
    valid_revenue = []
    for name, rev in zip(lot_names, revenue):
        if rev is not None and not (isinstance(rev, float) and math.isnan(rev)):
            valid_lot_names.append(name)
            valid_revenue.append(rev)

    fig2, ax2 = plt.subplots(facecolor='black')
    ax2.set_facecolor('black')
    x = range(len(valid_lot_names))
    ax2.bar(x, valid_revenue, color='gold')
    ax2.set_xticks(x)
    ax2.set_xticklabels(valid_lot_names, rotation=45, ha='right', color='white')
    ax2.set_title('Revenue by Parking Lot', color='white')
    ax2.set_ylabel('₹ Revenue', color='white')
    ax2.tick_params(colors='white')

    plt.tight_layout()
    buf2 = io.BytesIO()
    plt.savefig(buf2, format='png', facecolor=fig2.get_facecolor())
    buf2.seek(0)
    bar_chart = base64.b64encode(buf2.read()).decode('utf-8')
    plt.close(fig2)

    return render_template(
        'summary.html',
        donut_chart=donut_chart,
        bar_chart=bar_chart,
        role=session.get("user_role"),
        username=session.get("username")
    )

@app.route('/add_lot', methods=['POST'])
def add_lot():
    prime_location = request.form["prime_location"]
    price = float(request.form["price"])
    address = request.form["address"]
    pincode = request.form["pincode"]
    max_spot = request.form["max_spot"]
    parking_lot = ParkingLot(prime_location=prime_location, price=price, address=address, pincode=pincode, max_spot=max_spot)
    db.session.add(parking_lot)

    for _ in range(int(max_spot)):
        spot = ParkingSpot(lot=parking_lot)  # status by default AVAILABLE
        db.session.add(spot)
    
    db.session.commit()
    flash("Lot Created Successfully")
    return redirect(url_for('dashboard'))

@app.route('/edit_profile', methods=['POST'])
def edit_profile():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    user = User.query.get(session['user_id'])
    user.username = request.form['username']
    user.password = request.form['password']
    user.address = request.form['address']
    user.pincode = request.form['pincode']

    session['username'] = user.username
    session['user_address'] = user.address
    session['user_pincode'] = user.pincode

    db.session.commit()
    flash("Profile updated successfully")
    return redirect(url_for('dashboard'))


@app.route('/delete_lot/<int:lot_id>', methods=['POST'])
def delete_lot(lot_id):
    lot = ParkingLot.query.get_or_404(lot_id)
    db.session.delete(lot)
    db.session.commit()
    flash("Lot deleted successfully")
    return redirect(url_for('dashboard'))

@app.route('/edit_lot/<int:lot_id>', methods=['POST'])
def edit_lot(lot_id):
    lot = ParkingLot.query.get_or_404(lot_id)

    # Get updated values
    lot.prime_location = request.form['prime_location']
    lot.address = request.form['address']
    lot.pincode = request.form['pincode']
    lot.price = float(request.form['price'])
    new_max_spot = int(request.form['max_spot'])

    current_spots = len(lot.spots)
    lot.max_spot = new_max_spot

    if new_max_spot > current_spots:
        # Add new available spots
        for _ in range(new_max_spot - current_spots):
            new_spot = ParkingSpot(lot=lot)
            db.session.add(new_spot)

    elif new_max_spot < current_spots:
        # Delete only extra spots (those that are available)
        # Get available spots first
        available_spots = [spot for spot in lot.spots if spot.status.value == 'A']
        spots_to_delete = new_max_spot - current_spots
        for spot in available_spots[:abs(spots_to_delete)]:
            db.session.delete(spot)

    db.session.commit()
    flash("Lot updated successfully")
    return redirect(url_for('dashboard'))


from datetime import datetime

@app.route('/book_slot', methods=['POST'])
def book_slot():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    lot_id = request.form['lot_id']
    vehicle_number = request.form['vehicle_number']

    # Step 1: Find an available spot in this lot
    spot = ParkingSpot.query.filter_by(lot_id=lot_id, status=SpotStatus.AVAILABLE).first()
    if not spot:
        flash("No available spot in this lot")
        return redirect(url_for('dashboard'))

    # Step 2: Mark spot as occupied
    spot.status = SpotStatus.OCCUPIED

    # Step 3: Get the lot to calculate price
    lot = ParkingLot.query.get(lot_id)
    
    # Step 4: Create reservation with proper timestamps and cost
    from datetime import datetime, timedelta
    
    start_time = datetime.now()
    end_time = start_time + timedelta(hours=1)  # 1 hour minimum booking
    cost = lot.price  # Cost for 1 hour
    
    reservation = Reservation(
        spot_id=spot.id,
        user_id=session['user_id'],
        parking_timestamp=start_time,
        leaving_timestamp=end_time,
        packing_cost=cost,
        vehicle_number=vehicle_number,
        status='active'
    )
    
    db.session.add(reservation)
    db.session.commit()

    flash("Slot booked successfully!")
    return redirect(url_for('dashboard'))



@app.route('/release_slot/<int:reservation_id>', methods=['POST'])
def release_slot(reservation_id):
    reservation = Reservation.query.get_or_404(reservation_id)

    if reservation.user_id != session.get('user_id'):
        flash("Unauthorized")
        return redirect(url_for('dashboard'))

    now = datetime.now()
    reservation.leaving_timestamp = now
    reservation.status = 'inactive'

    duration = now - reservation.parking_timestamp
    hours_parked = math.ceil(duration.total_seconds() / 3600)

    spot = reservation.spot
    lot_price = spot.lot.price
    total_charge = hours_parked * lot_price

    spot.status = SpotStatus.AVAILABLE

    db.session.commit()

    flash(f"Slot released. Total charge: ₹{int(total_charge)} for {hours_parked} hour(s).")
    return redirect(url_for('dashboard'))


@app.route('/user_summary')
def user_summary():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    user_id = session['user_id']
    username = session['username']

    # Get all reservations of this user
    reservations = Reservation.query.filter_by(user_id=user_id).all()

    lot_costs = {}
    for res in reservations:
        lot_name = res.spot.lot.prime_location
        cost = res.packing_cost or 0
        lot_costs[lot_name] = lot_costs.get(lot_name, 0) + cost

    lot_names = list(lot_costs.keys())
    total_costs = list(lot_costs.values())
    grand_total = sum(total_costs)

    # Bar chart
    fig, ax = plt.subplots(facecolor='black')
    ax.set_facecolor('black')

    x = range(len(lot_names))
    bars = ax.bar(x, total_costs, color='orange')

    ax.set_xticks(x)
    ax.set_xticklabels(lot_names, rotation=45, ha='right', color='white')
    ax.set_title("Total Cost per Parking Lot", color='white')
    ax.tick_params(colors='white')

    # Value labels on top of bars
    for bar in bars:
        yval = bar.get_height()

    buf = io.BytesIO()
    plt.tight_layout()
    plt.savefig(buf, format='png', facecolor=fig.get_facecolor())
    buf.seek(0)
    chart_img = base64.b64encode(buf.read()).decode('utf-8')
    plt.close(fig)

    return render_template('user_summary.html', chart=chart_img, username=username, total_cost=grand_total)

@app.route('/delete_spot/<int:spot_id>', methods=['POST'])
def delete_spot(spot_id):
    spot = ParkingSpot.query.get_or_404(spot_id)

    if spot.status.value == 'O':
        flash("Cannot delete an occupied spot.")
        return redirect(url_for('dashboard'))

    lot = spot.lot  # us lot ko get kro jiska yeh spot hai
    db.session.delete(spot)

    # max_spot ko 1 se kam kro
    if lot.max_spot > 0:
        lot.max_spot -= 1

    db.session.commit()
    flash(f"Spot {spot_id} deleted successfully and max_spot updated.")
    return redirect(url_for('dashboard'))
