import sqlite3
from datetime import datetime


DB_PATH="data/vns.db"

def connect_db():
    return sqlite3.connect(DB_PATH)