import sqlite3

conn = sqlite3.connect('database/mydailyglow.db')
c = conn.cursor()

# Table routines
c.execute('''
CREATE TABLE IF NOT EXISTS routines (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    periode TEXT NOT NULL,
    etape TEXT NOT NULL
)
''')

# Table historique
c.execute('''
CREATE TABLE IF NOT EXISTS historique (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    date TEXT NOT NULL,
    periode TEXT NOT NULL,
    etape TEXT NOT NULL
)
''')

# Table produits
c.execute('''
CREATE TABLE IF NOT EXISTS produits (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nom TEXT NOT NULL,
    type TEXT NOT NULL,
    note INTEGER
)
''')

conn.commit()
conn.close()
print("Base initialisée ✅")
