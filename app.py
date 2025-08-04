from flask import Flask, render_template
from application.database import db

app = Flask(__name__)
app.config.from_object('application.config.Config')

db.init_app(app)

def create_admin():
    user = User.query.filter_by(role='admin').first()
    if not user:
        admin = User(username='Mohammed Talib', email='23f2003507@iitm.study.ac.in', password='admin1234', address='Robertsganj, Sonbhadra, Uttar Pradesh', pincode='231216', role='admin')
        db.session.add(admin)
        db.session.commit()
        print('Admin User Created')
    else:
        print('Admin Already Exist')


with app.app_context():
    from application.models import *
    db.create_all()
    create_admin()

from application.routes import *

if __name__ == '__main__':
    app.run(debug=True)