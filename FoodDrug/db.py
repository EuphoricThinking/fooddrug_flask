import sqlite3, click, csv, os

from flask import current_app, g
from flask.cli import with_appcontext

def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect(
            current_app.config['DATABASE'],
            detect_types=sqlite3.PARSE_DECLTYPES
        )
        g.db.row_factory = sqlite3.Row

    return g.db

def close_db(e=None):
    db = g.pop('db', None)

    if db is not None:
        db.close()

def init_db():
    db = get_db()

    db.execute("DROP TABLE IF EXISTS lek;")
    db.execute("CREATE TABLE lek (Nazwa_handlowa VARCHAR(20) PRIMARY KEY, Strona VARCHAR(100) NOT NULL);")
    with open('FoodDrug/lek.csv', 'r') as fin:
        dr = csv.DictReader(fin)
        to_db = [(i['Nazwa_handlowa'], i['Strona']) for i in dr]

    db.executemany("INSERT INTO lek (Nazwa_handlowa, Strona) VALUES (?, ?);", to_db)
    db.commit()

    db.execute("DROP TABLE IF EXISTS substancja_aktywna;")
    db.execute("CREATE TABLE substancja_aktywna (Nazwa_polska VARCHAR(20) PRIMARY KEY, Nazwa_miedzynarodowa VARCHAR(20));")
    with open('FoodDrug/subst_akt.csv', 'r') as fin:
        dr = csv.DictReader(fin)
        to_db = [(i['Nazwa_polska'], i['Nazwa_miedzynarodowa']) for i in dr]

    db.executemany("INSERT INTO substancja_aktywna (Nazwa_polska, Nazwa_miedzynarodowa) VALUES (?, ?);", to_db)
    db.commit()

    db.execute("DROP TABLE IF EXISTS zawartosc_leku;")
    db.execute("CREATE TABLE zawartosc_leku ( Nazwa_handlowa NOT NULL REFERENCES lek, " +
               "Nazwa_polska NOT NULL REFERENCES substancja_aktywna, " +
               "CONSTRAINT id PRIMARY KEY (Nazwa_handlowa, Nazwa_polska) );")
    db.commit()

    db.execute("DROP TABLE IF EXISTS interakcje_leki;")
    db.execute(
        "CREATE TABLE interakcje_leki (Inter_substancja_aktywna VARCHAR(30), Substancja_aktywna_leku VARCHAR(30)," +
        "CONSTRAINT id_inter PRIMARY KEY (Inter_substancja_aktywna, Substancja_aktywna_leku));")
    with open('FoodDrug/inter_subst_akt_prepared.csv', 'r') as fin:
        dr = csv.DictReader(fin)
        to_db = [(i['Inter_substancja_aktywna'], i['Substancja_aktywna_leku']) for i in dr]
    db.executemany("INSERT INTO interakcje_leki (Inter_substancja_aktywna, Substancja_aktywna_leku) VALUES (?, ?);", to_db)
    db.commit()

    db.execute("DROP TABLE IF EXISTS interakcje_produkty_spozywcze_leki;")
    db.execute(
        "CREATE TABLE interakcje_produkty_spozywcze_leki (Nazwa_handlowa VARCHAR(30) NOT NULL, Inter_produkty_spozywcze VARCHAR(30)," +
        "CONSTRAINT sp_id PRIMARY KEY (Nazwa_handlowa, Inter_produkty_spozywcze));")
    with open('FoodDrug/inter_prod_spoz_leki.csv', 'r') as fin:
        dr = csv.DictReader(fin)
        to_db = [(i['Nazwa_handlowa'], i['Inter_produkty_spozywcze']) for i in dr]
    db.executemany("INSERT INTO interakcje_produkty_spozywcze_leki (Nazwa_handlowa, Inter_produkty_spozywcze) VALUES (?, ?);",
                   to_db)
    db.commit()

    db.close()

@click.command('init-db')
@with_appcontext
def init_db_command():
    init_db()
    click.echo("Initialized the database")

def init_app(app):
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)




