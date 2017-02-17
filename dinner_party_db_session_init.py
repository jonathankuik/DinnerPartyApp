from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from dinner_party_db_create import Entree, Meal, Appetizer, Base

engine = create_engine('postgres:///dinner')

# Bind the engine to the metadata of the Base class so that the
# declaratives can be accessed through a DBSession instance
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)

session = DBSession()


##grab all meals##

meals = session.query(Meal).all()

for meal in meals:
	print meal.guest
	print meal.entree
	print meal.appetizer 
	print meal.date 


###simeple query that grabs all menu itmes and prints them


for item in session.query(MenuItem): 
	print(item.name, item.price)


####################Joins########################
##create an object that joins the MenuItem and Restaurant table on the Restaurant
UrbanBurger = session.query(MenuItem).join(Restaurant).filter(Restaurant.name=='Urban Burger').all()

##Print the names of the items in the object
for items in UrbanBurger:
		print items.name


####################Update#######################
##Get an object with all the veggie burgers
veggieBurger = session.query(MenuItem).filter(MenuItem.name == 'Veggie Burger')


##Figure out the id for all the veggie burgers
for item in veggieBurger:
     print item.id
     print item.name
     print item.restaurant.name
     print item.price
     print "\n"

##Get an object with Andala's veggie burger only
AndalasVeggieBurger = session.query(MenuItem).filter_by(id=36).one()

##Change the price of the object
AndalasVeggieBurger.price="100"

##Add it to the session and commit
session.add(AndalasVeggieBurger)
session.commit()

##loop to update
for veggie in veggieBurger:
	if veggie.price != '$2.99':
		veggie.price = '$2.99'
		session.add(veggie)
		session.commit()



#######################Delete#########################

##Find the entry
spinach = session.query(MenuItem).filter_by(name = 'Spinach Ice Cream').one()

session.delete(Spinach)
session.commit()
