import click, os
from flask import current_app, g
import pymysql

def get_db():
    if 'db' not in g:
        g.db = pymysql.connect(
            host = os.environ['MYSQL_ENDPOINT'], 
            user = os.environ['MYSQL_USER'], 
            password = os.environ['MYSQL_PASSWORD'], 
            database = "hwdb",
            cursorclass=pymysql.cursors.DictCursor)
    return g.db


def close_db(e=None):
    db = g.pop('db', None)

    if db is not None:
        db.close()

def init_db():
    db = get_db()
    cursor = db.cursor()

    with current_app.open_resource('schema.sql') as f:
        sql_queries = f.read()

    # Split the SQL file content into individual queries
    queries = sql_queries.split(b';')

    # Iterate over the queries and execute them
    for query in queries:
        try:
            if query.strip() != '':
                cursor.execute(query)
                db.commit()
                print("Query executed successfully!")
        except Exception as e:
            print("Error executing query:", str(e))

    # Close the cursor and the database connection
    cursor.close()
    #db.close()



@click.command('init-db')
def init_db_command():
    """Clear the existing data and create new tables."""
    init_db()
    click.echo('Initialized the database.')


def init_app(app):
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)        