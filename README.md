# Vehicle Parking System

A comprehensive multi-user web application for managing parking lots, parking spots, and vehicle reservations for 4-wheelers. Built with Flask and SQLAlchemy.

## Features

### Admin Features

- **Dashboard Management**: View and manage all parking lots
- **Parking Lot Management**:
  - Add new parking lots with location, address, price, and maximum spots
  - Edit existing parking lot details
  - Delete parking lots
  - Real-time spot status visualization (Available/Occupied)
- **User Management**: View all registered users
- **Search System**: Search by user ID, username, address, or prime location
- **Analytics**:
  - Parking slot status charts (Available vs Occupied)
  - Revenue analysis by parking lot
- **Spot Management**: Delete individual parking spots
- **Profile Management**: Edit admin profile details

### User Features

- **Slot Booking**: Book available parking spots with vehicle number
- **Active Reservations**: View current bookings with lot details and timestamps
- **Slot Release**: Release booked slots with automatic cost calculation
- **Personal Analytics**: View total spending per parking lot with visual charts
- **Profile Management**: Edit user profile information

### General Features

- **Responsive Design**: Modern UI with Bootstrap and custom CSS
- **Real-time Status**: Live parking spot availability tracking
- **Secure Authentication**: Role-based access control (Admin/User)
- **Data Visualization**: Interactive charts and graphs using Matplotlib

## Technology Stack

- **Backend**: Python Flask
- **Database**: SQLAlchemy with SQLite
- **Frontend**: HTML5, CSS3, Bootstrap 5.3.3
- **Data Visualization**: Matplotlib
- **Authentication**: Flask Sessions

## Database Schema

### Users Table

- `id` (Primary Key)
- `username`
- `email` (Unique)
- `password`
- `address`
- `pincode`
- `role` (admin/user)

### Parking Lots Table

- `id` (Primary Key)
- `prime_location`
- `address`
- `pincode`
- `price` (per hour)
- `max_spot`

### Parking Spots Table

- `id` (Primary Key)
- `lot_id` (Foreign Key)
- `status` (Available/Occupied)

### Reservations Table

- `id` (Primary Key)
- `spot_id` (Foreign Key)
- `user_id` (Foreign Key)
- `parking_timestamp`
- `leaving_timestamp`
- `packing_cost`
- `vehicle_number`
- `status` (active/inactive)

## Installation

1. **Clone the repository**

   ```bash
   git clone <repository-url>
   cd vehicle-parking-system
   ```

2. **Create virtual environment**

   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**

   ```bash
   pip install flask flask-sqlalchemy matplotlib
   ```

4. **Add background image**
   - Place your background image as `p1.jpg` in `static/images/` directory

5. **Run the application**

   ```bash
   python app.py
   ```

6. **Access the application**
   - Open your browser and navigate to `http://localhost:5000`

## Default Admin Account

The application automatically creates a default admin account:

- **Email**: <23f2003507@iitm.study.ac.in>
- **Password**: admin1234
- **Username**: Mohammed Talib

## Usage

### For Administrators

1. **Login** with admin credentials
2. **Add Parking Lots**: Use the "+ Add Lot" button to create new parking facilities
3. **Manage Spots**: View real-time spot status, delete spots, or edit lot details
4. **View Users**: Access user management to see all registered users
5. **Search**: Use the search functionality to find specific users or locations
6. **Analytics**: View summary page for business insights and revenue analysis

### For Users

1. **Register** a new account or **Login** with existing credentials
2. **Book Slots**: Select a parking lot and provide vehicle number to reserve a spot
3. **Manage Bookings**: View active reservations and release slots when done
4. **View Analytics**: Check personal spending summary across different parking lots
5. **Update Profile**: Edit personal information as needed

## Key Features Explained

### Dynamic Spot Management

- Spots are automatically created when a parking lot is added
- Real-time status updates (Green = Available, Red = Occupied)
- Automatic cost calculation based on parking duration

### Revenue Tracking

- Hourly billing system
- Comprehensive revenue reports for administrators
- Personal spending analytics for users

### Search Functionality

- Multi-criteria search (User ID, Username, Address, Location)
- Real-time filtering and results display

### Data Visualization

- Donut charts for slot availability
- Bar charts for revenue analysis
- Personal spending breakdowns

## Security Features

- Role-based access control
- Session management
- Input validation and error handling
- Secure password handling

## Customization

### Styling

- Modify CSS files in the `static/` directory
- Update Bootstrap classes in HTML templates
- Replace background images in `static/images/`

### Configuration

- Database settings in `application/config.py`
- Modify default admin credentials in `app.py`

### Feature

- Add new routes in `application/routes.py`
- Extend database models in `application/models.py`
