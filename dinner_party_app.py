
from flask import Flask, render_template, url_for, request, redirect, flash, jsonify
from flask_wtf import FlaskForm

from wtforms import StringField, SelectField, widgets, validators
from wtforms.widgets import html_params, Select, HTMLString
from wtforms.widgets.core import escape
from wtforms.fields.html5 import DateField, EmailField
app = Flask(__name__)

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


from dinner_party_db_create import Appetizer, Base, Entree, Meal

engine = create_engine('sqlite:///recipes.db')

# Bind the engine to the metadata of the Base class so that the
# declaratives can be accessed 	through a DBSession instance
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()



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
	entrees = session.query(Entree).all()

	return render_template('kuikMealHome.html', entrees=entrees)


@app.route('/allMeals')
def allMeals():
	meals = session.query(Meal).all()
	return render_template('allMeals.html', meals=meals)


@app.route('/mealEdit/<int:mealid>', methods=['GET', 'POST'])
def mealEdit(mealid):
	form = MyForm()
	entrees = session.query(Entree).all()
	appetizers = session.query(Appetizer).all()
	form.entree.choices = [(i.id,i.name, i.photo_path) for i in entrees]
	form.appetizer.choices = [(i.id,i.name) for i in appetizers ]

	if request.method == 'GET':
		mealEdit = session.query(Meal).filter_by(id=mealid).one()
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
			mealEdit = session.query(Meal).filter_by(id=mealid).one()
			mealEdit.guest = form.guest_name.data
			mealEdit.date = form.date.data
			mealEdit.email = form.email.data
			mealEdit.entree = session.query(Entree).filter(Entree.id == form.entree.data).one() 
			mealEdit.appetizer = session.query(Appetizer).filter(Appetizer.id == form.appetizer.data).one()
			session.add(mealEdit)
			session.commit()
			return redirect(url_for('mealDetails', mealid = mealid))
	return render_template('editMeal.html', form=form)







@app.route('/mealCreate', methods=['GET', 'POST'])
def mealCreate():
	form = MyForm()
	entrees = session.query(Entree).all()
	appetizers = session.query(Appetizer).all()
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
			entree1 = session.query(Entree).filter(Entree.id == form.entree.data).one() 
			appetizer1 = session.query(Appetizer).filter(Appetizer.id == form.appetizer.data).one()
			meal1 = Meal(guest=guest1, entree=entree1, appetizer=appetizer1, date=date1, email=email1)
			session.add(meal1)
			session.commit()
			return redirect(url_for('mealDetails', mealid = meal1.id))
	return render_template('mealCreate.html', form=form)

@app.route('/meal/<int:mealid>/details')
def mealDetails(mealid):
	meal1 = session.query(Meal).filter(Meal.id==mealid).one()
	return render_template('mealDetail.html', meal=meal1)


"""
		    $(document).ready(function(){
		      var date_input=$('input[name="date"]'); //our date input has the name "date"

		      var options={
		        format: {
				    toDisplay: function (date, format, language) {
				        var d = new Date(date);
				        d.setDate(d.getDate() - 7);
				        return d.toISOString();
				    },
				    toValue: function (date, format, language) {
				        var d = new Date(date);
				        d.setDate(d.getDate() + 7);
				        return new Date(d);
				    }
				  },	
		        autoclose: true,
		      };
		      date_input.datepicker(options);
		    });


<script>
		    $(document).ready(function(){
		      var date_input=$('input[name="date"]'); //our date input has the name "date"

		      var options={
		        format: 'mm/dd/yyyy',
		        autoclose: true,
		      };
		      date_input.datepicker(options);
		    })
		</script>


			    <!--
			    <div>

			    	{{form.date.label}}

			    <div class="input-group date" data-provide="datepicker" data-date-autoclose='true'>
    				{{form.date(class="form-control")}}
    					<div class="input-group-addon">
        				<span class="glyphicon glyphicon-th"></span>
    					</div>
				</div>
				</div>
				-->

class Meal(Base):
	__tablename__ = 'meal'
	id = Column(Integer, primary_key=True)
	guest = Column(String, nullable=False)
	date = Column(Date, nullable=False)
	entree_id = Column(Integer, ForeignKey("entree.id"))
	entree = relationship(Entree)
	appetizer_id = Column(Integer, ForeignKey("appetizer.id"))
	appetizer = relationship(Appetizer)

@app.route('/restaurants/<int:restaurantid>/menu')
def restaurantmenu(restaurantid):
	restaurant = session.query(Restaurant).filter_by(id=restaurantid).one()
	menu_items = session.query(MenuItem).filter_by(restaurant_id = restaurantid)
	menu_item_list = createList(menu_items)
	menu_item_list = chunks(menu_item_list, 3)
	#menu_items_grouped = chunkIt(menu_item_list, 3)
	#menu_items_grouped = sorted(menu_items_grouped, key=len, reverse=True)
	print "*************"
	print menu_item_list
	return render_template('menu.html', restaurant = restaurant, items = menu_item_list)

@app.route('/restaurants/<int:restaurantid>/menu/JSON')
def jsonMenu(restaurantid):
	menu_items = session.query(MenuItem).filter_by(restaurant_id = restaurantid)
	
	return jsonify(MenuItems=[i.serialize for i in menu_items])

@app.route('/restaurants/<int:restaurantid>/menu/<int:menuid>/JSON')
def jsonMenuItem(restaurantid,menuid):
	menu_item = session.query(MenuItem).filter_by(id=menuid).one()
	return jsonify(MenuItem=menu_item.serialize)

@app.route('/restaurants/JSON')
def jsonRestaurant():
	restaurants = session.query(Restaurant).all()
	return jsonify(Restaurants=[i.serialize for i in restaurants])


@app.route('/<int:restaurant_id>/new', methods = ['GET', 'POST'])
def newMenuItem(restaurant_id):
	
	if request.method == 'POST':
		restaurant = session.query(Restaurant).filter_by(id=restaurant_id).one()
		menuItem2 = MenuItem(name=request.form['name'], restaurant=restaurant)
		session.add(menuItem2)
		session.commit()
		flash("New menu item created") 
		return redirect(url_for('restaurantmenu', restaurantid = restaurant_id))
	else:
		restaurant = session.query(Restaurant).filter_by(id=restaurant_id).one()
		return render_template('newMenuItem.html', restaurant=restaurant)


@app.route('/<int:restaurant_id>/<int:menu_id>/edit', methods = ['GET', 'POST'])
def editMenuItem(restaurant_id, menu_id):
	if request.method == 'POST':
		menuItem = session.query(MenuItem).filter_by(id=menu_id).one()
		oldname = menuItem.name
		newname = request.form['name']
		menuItem.name = newname
		session.commit()
		message = "%s was changed to %s" % (oldname, newname)
		flash(message)
		return redirect(url_for('restaurantmenu', restaurantid = restaurant_id))
	else:
		restaurant = session.query(Restaurant).filter_by(id=restaurant_id).one()
		item = session.query(MenuItem).filter_by(id=menu_id).one()

		return render_template('editMenuItem.html', restaurant=restaurant, item=item)

@app.route('/<int:restaurant_id>/<int:menu_id>/delete', methods = ['GET', 'POST'])
def deleteMenuItem(restaurant_id, menu_id):
	if request.method == 'POST':
		menuItem = session.query(MenuItem).filter_by(id=menu_id).one()
		session.delete(menuItem)
		session.commit()
		flash("Menu item deleted")
		return redirect(url_for('restaurantmenu', restaurantid = restaurant_id))
	else:
		restaurant = session.query(Restaurant).filter_by(id=restaurant_id).one()
		item = session.query(MenuItem).filter_by(id=menu_id).one()

		return render_template('deleteMenuItem.html', restaurant=restaurant, item=item)
"""

if __name__ == '__main__':
	app.secret_key = "secret_key"
	app.debug = True
	app.run(host = '0.0.0.0', port = 8000)