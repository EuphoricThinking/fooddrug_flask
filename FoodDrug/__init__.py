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

	@app.route("/products_most_interactions")
	def products_most_interactions():
		data = db.get_db()
		data.row_factory = sqlite3.Row
		cur = data.cursor()
		cur.execute("select Inter_produkty_spozywcze, COUNT(*) from interakcje_produkty_spozywcze_leki WHERE Inter_produkty_spozywcze <> '' GROUP BY Inter_produkty_spozywcze ORDER BY COUNT(*) DESC")
		rows = cur.fetchall()
		return render_template("products_most_interactions.html", rows = rows)



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



	@app.route("/dataDrugRequest", methods = ["POST", "GET"])
	def dataDrugRequest():
		return render_template("formularzLekDane.html")

	@app.route("/dataDrug", methods = ["POST", "GET"])
	def dataDrug():
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
				cur.execute("select Nazwa_polska, Nazwa_miedzynarodowa from substancja_aktywna where Nazwa_polska in "
					+ " (select Nazwa_polska from zawartosc_leku WHERE Nazwa_handlowa = '{}')".format(name))
				print("PO execute", flush=True)
				rows = cur.fetchall()

				cur.execute("select COUNT(DISTINCT Inter_produkty_spozywcze) from interakcje_produkty_spozywcze_leki " +
							"WHERE Inter_produkty_spozywcze <> '' AND Nazwa_handlowa = '{}'".format(name))
				count1 = cur.fetchone()

				cur.execute("select COUNT(DISTINCT Inter_substancja_aktywna) from interakcje_leki WHERE " +
							"Inter_substancja_aktywna <> '' AND Substancja_aktywna_leku IN " +
							"(select Nazwa_polska from zawartosc_leku WHERE Nazwa_handlowa = '{}')".format(name))
				count2 = cur.fetchone()

				cur.execute("select Dzialanie from leczenie WHERE Nazwa_handlowa = '{}'".format(name))
				indirections = cur.fetchall()

				ind_to_dict = [dict(x) for x in indirections]
				if indirections[0][0] == '':
					ind_to_dict[0].update({'Dzialanie': 'Brak danych'})

				# cur.execute("select distinct Inter_produkty_spozywcze from interakcje_produkty_spozywcze_leki "
				# 	+ "WHERE Nazwa_handlowa = '{}'".format(name))
				# food = cur.fetchall()
				# food_to_dict = [dict(x) for x in food]
				# if food[0][0] == '':
				# 	food_to_dict[0].update({'Inter_produkty_spozywcze': 'Brak danych'})
				#
				# cur.execute("select distinct Inter_substancja_aktywna from interakcje_leki WHERE Substancja_aktywna_leku IN " +
				# 			"(select Nazwa_polska from zawartosc_leku WHERE Nazwa_handlowa = '{}')".format(name))
				# inters = cur.fetchall()
				# inters_to_dict = [dict(x) for x in inters]
				# if inters[0][0] == '':
				# 	inters_to_dict[0].update({'Inter_substancja_aktywna': 'Brak danych'})
				cur.execute("select Strona from lek where Nazwa_handlowa = '{}'".format(name))
				address = cur.fetchone()

				if len(rows) == 0:
					msg = "Brak wskazanego leku"
					return render_template("blad.html", msg=msg)
				else:
					return render_template("wypiszDane.html", rows = rows, name = name, count = int(count1[0]) + int(count2[0]),
										   inds = ind_to_dict, addr = address[0])
				data.close_db()
			except Exception as e:
				msg = "Nie można znaleźć leku"
				print(repr(e), flush=True)
				return render_template("blad.html", msg = msg)
				data.close_db()



	@app.route("/findInteractionsRequest", methods = ["POST", "GET"])
	def findInteractionsRequest():
		return render_template("findInteractionsRequest.html")

	@app.route("/findInteractions", methods=["POST", "GET"])
	def findInteractions():
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

				cur.execute("select * from lek where Nazwa_handlowa = '{}'".format(name))
				rows = cur.fetchall()
				if len(rows) == 0:
					msg = "Brak wskazanego leku"
					return render_template("blad.html", msg=msg)

				cur.execute("select COUNT(DISTINCT Inter_produkty_spozywcze) from interakcje_produkty_spozywcze_leki " +
							"WHERE Inter_produkty_spozywcze <> '' AND Nazwa_handlowa = '{}'".format(name))
				count1 = cur.fetchone()

				cur.execute("select COUNT(DISTINCT Inter_substancja_aktywna) from interakcje_leki WHERE " +
							"Inter_substancja_aktywna <> '' AND Substancja_aktywna_leku IN " +
							"(select Nazwa_polska from zawartosc_leku WHERE Nazwa_handlowa = '{}')".format(name))
				count2 = cur.fetchone()

				cur.execute("select distinct Inter_produkty_spozywcze from interakcje_produkty_spozywcze_leki "
					+ "WHERE Nazwa_handlowa = '{}'".format(name))
				food = cur.fetchall()
				food_to_dict = [dict(x) for x in food]
				if food[0][0] == '':
					food_to_dict[0].update({'Inter_produkty_spozywcze': 'Brak danych'})

				cur.execute("select distinct Inter_substancja_aktywna from interakcje_leki WHERE Substancja_aktywna_leku IN " +
							"(select Nazwa_polska from zawartosc_leku WHERE Nazwa_handlowa = '{}')".format(name))
				inters = cur.fetchall()
				inters_to_dict = [dict(x) for x in inters]
				if inters[0][0] == '':
					inters_to_dict[0].update({'Inter_substancja_aktywna': 'Brak danych'})

				else:
					return render_template("wypiszInterakcje.html", name=name, count=int(count1[0]) + int(count2[0]), food=food_to_dict,
										   inters=inters_to_dict)
				data.close_db()
			except Exception as e:
				msg = "Nie można znaleźć leku"
				print(repr(e), flush=True)
				return render_template("blad.html", msg=msg)
				data.close_db()


######################################################################################################################
	@app.route("/myDrugsMenu", methods=["POST", "GET"])
	def myDrugsMenu():
		return render_template("myDrugsMenu.html")

	@app.route("/addMyDrugForm", methods=["POST", "GET"])
	def addMyDrugForm():
		return render_template("addMyDrug.html")

	@app.route("/addMyDrug", methods=["POST", "GET"])
	def addMyDrug():
		data = db.get_db()
		print("robie cos", flush=True)
		if request.method == "POST":
			try:
				print("robie cos w srodku", flush=True)
				name = request.form["drugSearch"]

				if name == "":
					msg = "Brak podanej nazwy leku"
					return render_template("successAdded.html", msg = msg)

				data.row_factory = sqlite3.Row
				cur = data.cursor()

				cur.execute("CREATE TABLE IF NOT EXISTS moje_leki (Nazwa_handlowa VARCHAR(20) PRIMARY KEY);")
				print("Stworzyłem", flush=True)
				cur.execute("SELECT * FROM moje_leki WHERE Nazwa_handlowa = '{}'".format(name))
				print("Szukałem w moich lekach", flush=True)
				rows = cur.fetchall()

				if (len(rows) > 0):
					msg = "Podany lek znajduje się już w bazie"
					return render_template("successAdded.html", msg=msg)

				cur.execute("SELECT * FROM lek WHERE Nazwa_handlowa = '{}'".format(name))
				print("Szukałem w leku", flush=True)
				rows = cur.fetchall()

				if (len(rows) == 0):
					msg = "Podany lek nie został dodany; nie jest jeszcze obsługiwany przez naszą bazę"
					return render_template("successAdded.html", msg=msg)

				cur.execute("INSERT INTO moje_leki (Nazwa_handlowa) VALUES (?);", (name,))
				#WHERE NOT EXISTS (SELECT * FROM moje_leki" +" WHERE Nazwa_handlowa = '{}')".format(name, name)
				print("Dodałem", flush=True)
				data.commit()

				msg = "Twój lek został dodany"
				return render_template("successAdded.html", msg = msg)
				data.close_db()
			except Exception as e:
				msg = "Nie można znaleźć leku"
				print(repr(e), flush=True)
				return render_template("blad.html", msg=msg)
				data.close_db()



	@app.route("/deleteDrugForm", methods=["POST", "GET"])
	def deleteDrugForm():
		return render_template("deleteDrugForm.html")

	@app.route("/deleteMyDrug", methods=["POST", "GET"])
	def deleteMyDrug():
		data = db.get_db()
		print("robie cos", flush=True)
		if request.method == "POST":
			try:
				print("robie cos w srodku", flush=True)
				name = request.form["drugSearch"]

				if name == "":
					msg = "Brak podanej nazwy leku"
					return render_template("deleteFailure.html", msg=msg)

				data.row_factory = sqlite3.Row
				cur = data.cursor()

				cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='moje_leki';")
				# print("Pokaż leki", flush=True)
				rows = cur.fetchall()
				print("Pokaż leki po fetch", flush=True)

				if len(rows) == 0:
					msg = "Brak leków do usunięcia"
					print("Nie znalezione moje_leki", flush=True)
					return render_template("deleteFailure.html", msg=msg)

				cur.execute("SELECT * FROM moje_leki WHERE Nazwa_handlowa = '{}'".format(name))
				print("Szukałem w moich lekach", flush=True)
				rows = cur.fetchall()

				if (len(rows) == 0):
					msg = "Podany lek nie znajduje się w bazie"
					return render_template("deleteFailure.html", msg=msg)

				cur.execute("DELETE FROM moje_leki WHERE Nazwa_handlowa = '{}';".format(name))
				# WHERE NOT EXISTS (SELECT * FROM moje_leki" +" WHERE Nazwa_handlowa = '{}')".format(name, name)
				print("Usunąłem", flush=True)
				data.commit()

				deleted = {}
				deleted['Nazwa_handlowa'] = name
				print(deleted, flush=True)
				return render_template("deleteSuccess.html", rows = [deleted])
				data.close_db()
			except Exception as e:
				msg = "Nie można znaleźć leku"
				print(repr(e), flush=True)
				return render_template("blad.html", msg=msg)
				data.close_db()



	@app.route("/askToDelete", methods=["POST", "GET"])
	def askToDelete():
		return render_template("askDelete.html")

	@app.route("/deleteMyDatabse", methods=["POST", "GET"])
	def deleteMyDatabse():
		data = db.get_db()
		print("robie cos", flush=True)
		if request.method == "POST":
			try:
				print("robie cos w srodku", flush=True)
				answer = request.form["Answer"]

				if answer == "Nie":
					msg = "Leki nie zostały usunięte"
					return render_template("deleteFailure.html", msg=msg)
				else:
					data.row_factory = sqlite3.Row
					cur = data.cursor()

					#Checks whether the table exists
					cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='moje_leki';")
					#print("Pokaż leki", flush=True)
					rows = cur.fetchall()
					print("Pokaż leki po fetch", flush=True)

					if len(rows) == 0:
						msg = "Brak leków do usunięcia"
						print("Nie znalezione moje_leki", flush=True)
						return render_template("deleteFailure.html", msg=msg)
					# cur.execute("SELECT * FROM moje_leki")
					# print("Wybieram wszystko w moich lekach", flush=True)
					# rows = cur.fetchall()
					# print("Zebrałem wiersze", flush=True)
					#
					#
					# if (len(rows) == 0):
					# 	msg = "Brak leków do usunięcia"
					# 	return render_template("deleteFailure.html", msg=msg)
					cur.execute("SELECT Nazwa_handlowa FROM moje_leki;")
					rows = cur.fetchall()

					cur.execute("DROP TABLE IF EXISTS moje_leki;")
					# WHERE NOT EXISTS (SELECT * FROM moje_leki" +" WHERE Nazwa_handlowa = '{}')".format(name, name)
					print("Usunąłem", flush=True)
					data.commit()

					return render_template("deleteSuccess.html", rows=rows)
					data.close_db()
			except Exception as e:
				msg = "Nie można znaleźć leku"
				print(repr(e), flush=True)
				return render_template("blad.html", msg=msg)
				data.close_db()

	@app.route("/listAllInteractions")
	def listAllInteractions():
		data = db.get_db()

		try:
			print("robie cos w srodku", flush=True)

			data.row_factory = sqlite3.Row
			cur = data.cursor()

			cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='moje_leki';")
			rows = cur.fetchall()
			print("Pokaż leki po fetch", flush=True)

			if len(rows) == 0:
				msg = "Brak dodanych leków"
				print("Nie znalezione moje_leki", flush=True)
				return render_template("myDrugsMessage.html", msg=msg)

			cur.execute("select DISTINCT Inter_produkty_spozywcze from interakcje_produkty_spozywcze_leki " +
						"WHERE Inter_produkty_spozywcze <> '' AND Nazwa_handlowa IN (select Nazwa_handlowa from moje_leki);")
			food = cur.fetchall()
			food_to_dict = [dict(x) for x in food]
			if food[0][0] == '':
				food_to_dict[0].update({'Inter_produkty_spozywcze': 'Brak danych'})

			cur.execute("select DISTINCT Inter_substancja_aktywna from interakcje_leki WHERE " +
						"Inter_substancja_aktywna <> '' AND Substancja_aktywna_leku IN " +
						"(select Nazwa_polska from zawartosc_leku WHERE Nazwa_handlowa IN (SELECT Nazwa_handlowa from" +
						" moje_leki));")
			inters = cur.fetchall()
			inters_to_dict = [dict(x) for x in inters]
			if inters[0][0] == '':
				inters_to_dict[0].update({'Inter_substancja_aktywna': 'Brak danych'})

			# l_food = len(food)
			# l_inters = len(inters)
			# if l_inters + l_food == 0:
			# 	msg = "Brak interakcji"

			return render_template("listAllInteractionsMyDrugs.html", count=len(food) + len(inters),
									   food=food_to_dict,
									   inters=inters_to_dict)
			data.close_db()
		except Exception as e:
			msg = "Nie można znaleźć leku"
			print(repr(e), flush=True)
			return render_template("blad.html", msg=msg)
			data.close_db()



	@app.route("/findMyInteractionsForm", methods=["POST", "GET"])
	def findMyInteractionsForm():
		return render_template("findMyInteractionsForm.html")

	@app.route("/findMyInteractions", methods=["POST", "GET"])
	def findMyInteractions():
		data = db.get_db()

		print("robie cos", flush=True)
		if request.method == "POST":
			try:
				print("robie cos w srodku", flush=True)
				name = request.form["drugSearch"]

				if name == "":
					msg = "Brak podanej nazwy"
					return render_template("findMyInteractionsMessage.html", msg=msg)

				print("robie cos w srodku", flush=True)

				data.row_factory = sqlite3.Row
				cur = data.cursor()

				cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='moje_leki';")
				rows = cur.fetchall()
				print("Pokaż leki po fetch", flush=True)

				if len(rows) == 0:
					msg = "Brak dodanych leków"
					print("Nie znalezione moje_leki", flush=True)
					return render_template("myDrugsMessage.html", msg=msg)

				print("Przed food", flush=True)
				cur.execute("select DISTINCT Nazwa_handlowa from interakcje_produkty_spozywcze_leki " +
							"WHERE Nazwa_handlowa IN (SELECT Nazwa_handlowa from moje_leki) AND Inter_produkty_spozywcze = '{}'".format(name))
				food = cur.fetchall()
				print("select food", flush=True)

				cur.execute("select DISTINCT C.Nazwa_handlowa from (select A.Nazwa_handlowa, B.Nazwa_polska from moje_leki A " +
					"left join zawartosc_leku B on A.Nazwa_handlowa = B.Nazwa_handlowa) C, interakcje_leki D " +
					"WHERE C.Nazwa_polska = D.Substancja_aktywna_leku AND D.Inter_substancja_aktywna = '{}'".format(name))
				inters = cur.fetchall()
				print("select subst akt", flush=True)

				cur.execute(
					"select DISTINCT C.Nazwa_handlowa from (select A.Nazwa_handlowa, B.Nazwa_polska from moje_leki A " +
					"left join zawartosc_leku B on A.Nazwa_handlowa = B.Nazwa_handlowa) C, interakcje_leki D " +
					"WHERE C.Nazwa_polska = D.Substancja_aktywna_leku AND D.Inter_substancja_aktywna IN "
					+ "(SELECT Nazwa_polska FROM zawartosc_leku WHERE Nazwa_handlowa = '{}');".format(name))
				drugs_inter = cur.fetchall()
				count = len(drugs_inter) + len(inters) + len(food)
				print(count)
				if count == 0:
					msg = "Brak znalezionych interakcji"
					return render_template("myDrugsMessage.html", msg=msg)
				print("before")
				print(food)
				food_to_dict = [dict(x) for x in food]
				print("food to dict")
				print(inters)
				inters_to_dict = [dict(x) for x in inters]
				print("inters to dict")
				drugs_inter_to_dict = [dict(x) for x in drugs_inter]
				#result.update(dict(food)).update(dict(drugs_inter)).update(dict(inters))
				print("drugs to dict")
				result = food_to_dict + inters_to_dict + drugs_inter_to_dict
				print("added")

				return render_template("listAllInteractionsMyDrugsSuppliedInput.html", count = count, inters = result)

				data.close_db()
			except Exception as e:
				msg = "Nie można znaleźć leku"
				print(repr(e), flush=True)
				return render_template("blad.html", msg=msg)
				data.close_db()

	return app

