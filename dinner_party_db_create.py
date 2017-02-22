
###################Configuration Code########################
from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy
 
app = Flask(__name__)
db = SQLAlchemy(app)

app.config['SQLALCHEMY_DATABASE_URI'] = os.environ['DATABASE_URL']

#####################Class Code##############################

class Appetizer(db.Model):
	__tablename__ = 'appetizer'
	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String, nullable = False)
	description = db.Column(db.String)
	@property
	def serialize(self):
	    return {'id': self.id,
	    		'name': self.name,
	    		'description': self.description,
	    		}

class Entree(db.Model):
	__tablename__ = 'entree'
	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String, nullable=False)
	description = db.Column(db.String)
	photo_path = db.Column(db.String)
	@property
	def serialize(self):
	    return {'id': self.id,
	    		'name': self.name,
	    		'description': self.description,
	    		}


class Meal(db.Model):
	__tablename__ = 'meal'
	id = db.Column(db.Integer, primary_key=True)
	guest = db.Column(db.String, nullable=False)
	date = db.Column(db.Date, nullable=False)
	entree_id = db.Column(db.Integer, db.ForeignKey("entree.id"), nullable=False)
	entree = db.relationship(Entree)
	appetizer_id = db.Column(db.Integer, db.ForeignKey("appetizer.id"))
	appetizer = db.relationship(Appetizer)
	email = db.Column(db.String)

