from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import time, os
from datetime import date


from dinner_party_db_create import Appetizer, Entree, Meal

from flask.ext.heroku import Heroku
from flask.ext.sqlalchemy import SQLAlchemy
from flask import Flask



#engine = create_engine('postgresql:///dinner')

# Bind the engine to the metadata of the Base class so that the
# declaratives can be accessed     through a DBdb.session instance
#Base.metadata.bind = engine
#DBdb.session = db.sessionmaker(bind=engine)
#db.session = DBdb.session()

app = Flask(__name__)
#app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///dinner'
heroku = Heroku(app)
db = SQLAlchemy(app)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ['DATABASE_URL']


# Menu for UrbanBurger
entree1 = Entree(name="Double Broccolsui Quinoa", 
       description="""Broccoli and Quinoa served with a broccoli pesto. 
       Served with your choice of toppings which include toasted almonds, 
       parmesan cheese, and avacado.""", photo_path="http://placehold.it/350x150")

session.add(entree1)
session.commit()

entree2 = Entree(name="Stuffed Peppers", 
       description="""Bell Peppers stuffed with quinoa, black beans, and cheese!""", photo_path="http://placehold.it/350x150")

session.add(entree2)
session.commit()

appetizer1 = Appetizer(name="Bruschetta", description="Classic Italian appetizer.")

session.add(appetizer1)
session.commit()

date1 = date(2017, 1, 7)

meal1 = Meal(guest="Ethan and Robyn Ax", date=date1, entree=entree1, appetizer=appetizer1, email="ax@gmail.com")

session.add(meal1)
session.commit()

