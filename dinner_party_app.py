
from flask import Flask, render_template, url_for, request, redirect, flash, jsonify
from flask_wtf import FlaskForm

from wtforms import StringField, SelectField, widgets, validators
from wtforms.widgets import html_params, Select, HTMLString
from wtforms.widgets.core import escape
from wtforms.fields.html5 import DateField, EmailField

from flask.ext.sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine
#from sqlalchemy.orm import db.sessionmaker


from dinner_party_db_create import Appetizer, Base, Entree, Meal

from flask.ext.heroku import Heroku

#app.config['SQLALCHEMY_DATABASE_URI'] = os.environ['DATABASE_URL']

#engine = create_engine('postgresql:///dinner')

# Bind the engine to the metadata of the Base class so that the
# declaratives can be accessed 	through a DBdb.session instance
#Base.metadata.bind = engine
#DBdb.session = db.sessionmaker(bind=engine)
#db.session = DBdb.session()

app = Flask(__name__)
#app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///dinner'
heroku = Heroku(app)
db = SQLAlchemy(app)


class SelectOptionRender(object):
    """
    Renders a select field.

    If `multiple` is True, then the `size` property should be specified on
    rendering to make the field useful.

    The field must provide an `iter_choices()` method which the widget will
    call on rendering; this method must yield tuples of
    `(value, label, selected, disabled)`.
    """
    def __init__(self, multiple=False):
        self.multiple = multiple

    def __call__(self, field, **kwargs):
        kwargs.setdefault('id', field.id)
        if self.multiple:
            kwargs['multiple'] = 'multiple'
        html = [u'<select %s>' % widgets.html_params(name=field.name, **kwargs)]
        for val, label, photo_file_path in field.iter_choices():
            html.append(self.render_option(val, label, photo_file_path))
        html.append(u'</select>')
        return widgets.HTMLString(u''.join(html))

    @classmethod
    def render_option(cls, val, label, photo_file_path):
        options = {'value': val}
        if photo_file_path:
            options['data-img-src'] = photo_file_path
        return widgets.HTMLString(u'<option %s>%s</option>' % (widgets.html_params(**options), escape(unicode(label))))



class SelectFieldCustomOptions(SelectField):
    widget = SelectOptionRender()

    def iter_choices(self):
        for value, label, photo_file_path in self.choices:
            yield (value, label, photo_file_path)

    def pre_validate(self, form):
    	new_choices = []
    	for x in self.choices:
    		y = (x[0], x[1])
    		new_choices.append(y)
    	for v, _ in new_choices:
            if self.data == v:
                break
        else:
            raise ValueError(self.gettext('Not a valid choice'))
   

class MyForm(FlaskForm):
	guest_name = StringField('Name', [validators.DataRequired()]) 
	entree = SelectFieldCustomOptions('Entree', coerce=int)
	appetizer = SelectField('Appetizer', coerce=int)
	date = DateField('Date', [validators.DataRequired()])
	email = EmailField('Email to best reach you', [validators.Email(message="Not a valid email")])


@app.route('/')
@app.route('/home')
def home():
	entrees = db.session.query(Entree).all()

	return render_template('kuikMealHome.html', entrees=entrees)


@app.route('/allMeals')
def allMeals():
	meals = db.session.query(Meal).all()
	return render_template('allMeals.html', meals=meals)


@app.route('/mealEdit/<int:mealid>', methods=['GET', 'POST'])
def mealEdit(mealid):
	form = MyForm()
	entrees = db.session.query(Entree).all()
	appetizers = db.session.query(Appetizer).all()
	form.entree.choices = [(i.id,i.name, i.photo_path) for i in entrees]
	form.appetizer.choices = [(i.id,i.name) for i in appetizers ]

	if request.method == 'GET':
		mealEdit = db.session.query(Meal).filter_by(id=mealid).one()
		form.guest_name.data = mealEdit.guest
		form.email.data = mealEdit.email
		form.date.data = mealEdit.date
		form.entree.data = mealEdit.entree
		entree = mealEdit.entree_id
		return render_template('editMeal.html', form=form, entree=entree, mealid=mealid)



	if request.method == 'POST':
		if form.validate() == False:
			for fieldName, errorMessages in form.errors.iteritems():
				for err in errorMessages:
					print "field name:%s" % fieldName
					print "error:%s" % err
		else:
			mealEdit = db.session.query(Meal).filter_by(id=mealid).one()
			mealEdit.guest = form.guest_name.data
			mealEdit.date = form.date.data
			mealEdit.email = form.email.data
			mealEdit.entree = db.session.query(Entree).filter(Entree.id == form.entree.data).one() 
			mealEdit.appetizer = db.session.query(Appetizer).filter(Appetizer.id == form.appetizer.data).one()
			db.session.add(mealEdit)
			db.session.commit()
			return redirect(url_for('mealDetails', mealid = mealid))
	return render_template('editMeal.html', form=form)







@app.route('/mealCreate', methods=['GET', 'POST'])
def mealCreate():
	form = MyForm()
	entrees = db.session.query(Entree).all()
	appetizers = db.session.query(Appetizer).all()
	form.entree.choices = [(i.id,i.name, i.photo_path) for i in entrees]
	form.appetizer.choices = [(i.id,i.name) for i in appetizers ]

	if request.method == 'POST':
		if form.validate() == False:
			for fieldName, errorMessages in form.errors.iteritems():
				for err in errorMessages:
					print "field name:%s" % fieldName
					print "error:%s" % err
		else:
			guest1 = form.guest_name.data
			date1 = form.date.data
			email1 = form.email.data
			entree1 = db.session.query(Entree).filter(Entree.id == form.entree.data).one() 
			appetizer1 = db.session.query(Appetizer).filter(Appetizer.id == form.appetizer.data).one()
			meal1 = Meal(guest=guest1, entree=entree1, appetizer=appetizer1, date=date1, email=email1)
			db.session.add(meal1)
			db.session.commit()
			return redirect(url_for('mealDetails', mealid = meal1.id))
	return render_template('mealCreate.html', form=form)

@app.route('/meal/<int:mealid>/details')
def mealDetails(mealid):
	meal1 = db.session.query(Meal).filter(Meal.id==mealid).one()
	return render_template('mealDetail.html', meal=meal1)


if __name__ == '__main__':
	app.secret_key = "secret_key"
	app.debug = True
	app.run(host = '0.0.0.0', port = 8000)
