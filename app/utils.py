from app.models import User, db
from werkzeug.security import generate_password_hash

def create_admin():
    admin = User.query.filter_by(role='admin').first()
    if not admin:
        default_admin = User(
            username='admin',
            password=generate_password_hash('admin123'),
            email='admin@example.com',
            role='admin',
            is_active=True
        )
        db.session.add(default_admin)
        db.session.commit()
