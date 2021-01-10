from flask import g
import sqlite3

def connect_db(): #connects to the database
    sql = sqlite3.connect('/Users/Dmitry/Desktop/food_tracker_app/food_log.db')
    sql.row_factory = sqlite3.Row #to get dictionaries instead of tuples when you access the rows
    return sql


def get_db():
    if not hasattr(g, 'sqlite3_db'):#checks if global object 'sqlite3_db' is in the database
        g.sqlite_db = connect_db()
    return g.sqlite_db

