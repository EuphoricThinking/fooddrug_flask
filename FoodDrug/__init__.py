import os, sqlite3

from flask import Flask, render_template

def create_app(test_config=None):
	app = Flask(__name__, instance_relative_config=True)
	app.config.from_mapping(
		SECRET_KEY='dev',
		DATABASE=os.path.join(app.instance_path, 'FoodDrug.sqlite'),
	)

	if (test_config is None):
		app.config.from_pyfile('config.py', silent=True)
	else:
		app.config.from_mapping(test_config)

	try:
		os.makedirs(app.instance_path)
	except OSError:
		pass
        
	@app.route('/hello')
	def hello():
		return 'I want this to WORRRRRK'
		
	@app.route("/")
	def home():
		return "Hello! this is the main page <h1>HELLO<h1>"

	from . import db
	db.init_app(app)

	@app.route('/list_lek')
	def list_lek():
		data = db.get_db()
		data.row_factory = sqlite3.Row
		cur = data.cursor()
		cur.execute("select * from lek")
		rows = cur.fetchall();
		return render_template("list_lek.html",rows = rows)

	return app
