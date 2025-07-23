from app import db
from app.models import Product

p1 = Product(name="Laptop", description="Dell Latitude E5500", price=999.99)
p2 = Product(name="Smartphone", description="Samsung Galaxy S24", price=799.99)

db.session.add_all([p1, p2])
db.session.commit()