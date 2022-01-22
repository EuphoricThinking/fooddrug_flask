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

    db.close()

@click.command('init-db')
@with_appcontext
def init_db_command():
    init_db()
    click.echo("Initialized the database")

def init_app(app):
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)




