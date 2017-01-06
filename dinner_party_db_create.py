
###################Configuration Code########################
import sys

from sqlalchemy import Column, ForeignKey, Integer, String, Date
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine

Base = declarative_base()

#####################Class Code##############################

class Appetizer(Base):
	__tablename__ = 'appetizer'
	id = Column(Integer, primary_key=True)
	name = Column(String, nullable = False)
	description = Column(String)
	@property
	def serialize(self):
	    return {'id': self.id,
	    		'name': self.name,
	    		'description': self.description,
	    		}

class Entree(Base):
	__tablename__ = 'entree'
	id = Column(Integer, primary_key=True)
	name = Column(String, nullable=False)
	description = Column(String)
	photo_path = Column(String)
	@property
	def serialize(self):
	    return {'id': self.id,
	    		'name': self.name,
	    		'description': self.description,
	    		}


class Meal(Base):
	__tablename__ = 'meal'
	id = Column(Integer, primary_key=True)
	guest = Column(String, nullable=False)
	date = Column(Date, nullable=False)
	entree_id = Column(Integer, ForeignKey("entree.id"), nullable=False)
	entree = relationship(Entree)
	appetizer_id = Column(Integer, ForeignKey("appetizer.id"))
	appetizer = relationship(Appetizer)
	email = Column(String)

engine = create_engine('sqlite:///recipes.db')	
Base.metadata.create_all(engine)