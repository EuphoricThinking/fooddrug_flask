import os

from flask import Flask

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
	@app.route('/list_lek')
	def list_lek():
		con = sql.connect("database.db")
		con.row_factory = sql.Row
		cur = con.cursor()
		cur.execute("select * from lek")
		rows = cur.fetchall();
		return render_template("lek.html",rows = rows)
	from . import db
	db.init_app(app)

	return app
