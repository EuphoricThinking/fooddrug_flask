import os, sqlite3

from flask import Flask, render_template, request

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
		return render_template("home.html");

	from . import db
	db.init_app(app)

	@app.route('/list_lek')
	def list_lek():
		data = db.get_db()
		data.row_factory = sqlite3.Row
		cur = data.cursor()
		#cur.execute("select * from lek")
		cur.execute("select * from zawartosc_leku WHERE Nazwa_handlowa = 'Abakawir'")
		rows = cur.fetchall()
		return render_template("list_lek.html",rows = rows)

	@app.route("/trzy_najbardziej_niebezpieczne_produkty")
	def trzy_najbardziej_niebezpieczne_produkty():
		data = db.get_db()
		data.row_factory = sqlite3.Row
		cur = data.cursor()
		cur.execute("select Inter_produkty_spozywcze, COUNT(*) from interakcje_produkty_spozywcze_leki WHERE Inter_produkty_spozywcze <> '' GROUP BY Inter_produkty_spozywcze ORDER BY COUNT(*) DESC")
		rows = cur.fetchall()
		return render_template("trzy_najbardziej_niebezpieczne_produkty.html", rows = rows)

	@app.route("/insertDrug", methods = ["POST","GET"])
	def insertDrug():
		return render_template("formularzLek.html")

	@app.route("/saveDrugName", methods = ["POST", "GET"])
	def insertDrug2():
		data = db.get_db()
		print("robie cos", flush=True)
		if request.method == "POST":
			try:
				print("robie cos w srodku", flush=True)
				name = request.form["drugSearch"]

				if name == "":
					msg = "Brak podanej nazwy leku"
					return render_template("blad.html", msg=msg)

				data.row_factory = sqlite3.Row
				cur = data.cursor()
				#select nazwa polska
				print("nazwa"+name, flush=True)
				#name zamiast Abakawir
				cur.execute("select Nazwa_polska from zawartosc_leku WHERE Nazwa_handlowa = '{}'".format(name))
				print("PO execute", flush=True)
				rows = cur.fetchall()
				if len(rows) == 0:
					msg = "Brak wskazanego leku"
					return render_template("blad.html", msg=msg)
				else:
					return render_template("wypiszSubstAkt.html", rows = rows, name = name)
				data.close_db()
			except:
				msg = "Nie można znaleźć leku"
				return render_template("blad.html", msg = msg)
				data.close_db()

	@app.route("/insertProduct", methods = ["POST","GET"])
	def insertProduct():
		return render_template("formularzProdukt.html")

	@app.route("/saveProductName", methods = ["POST", "GET"])
	def insertProduct2():
		data = db.get_db()
		print("robie cos", flush=True)
		if request.method == "POST":
			try:
				print("robie cos w srodku", flush=True)
				name = request.form["productSearch"]

				if name == "":
					msg = "Brak podanej nazwy produktu"
					return render_template("blad.html", msg=msg)

				data.row_factory = sqlite3.Row
				cur = data.cursor()
				#select nazwa polska
				print("nazwa"+name, flush=True)
				#name zamiast Abakawir
				cur.execute("select Nazwa_handlowa from interakcje_produkty_spozywcze_leki WHERE Inter_produkty_spozywcze = '{}'".format(name))
				print("PO execute", flush=True)
				rows = cur.fetchall()
				if len(rows) == 0:
					msg = "Brak wskazanego produktu"
					return render_template("blad.html", msg=msg)
				else:
					return render_template("wypiszNazwa_handlowa.html", rows = rows, name = name)
				data.close_db()
			except:
				msg = "Nie można znaleźć produktu"
				return render_template("blad.html", msg = msg)
				data.close_db()


	return app

