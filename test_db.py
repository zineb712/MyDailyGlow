import sqlite3

DATABASE = 'database/mydailyglow.db'

def test_db():
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    # Vérifier les tables
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = [t[0] for t in cursor.fetchall()]
    print("Tables existantes :", tables)

    # Vérifier que la table routines fonctionne
    cursor.execute("SELECT * FROM routines;")
    routines = cursor.fetchall()
    print("\nContenu de la table 'routines' :")
    for row in routines:
        print(row)

    # Vérifier que la table historique fonctionne
    cursor.execute("SELECT * FROM historique;")
    historique = cursor.fetchall()
    print("\nContenu de la table 'historique' :")
    for row in historique:
        print(row)

    # Vérifier que la table produits fonctionne
    cursor.execute("SELECT * FROM produits;")
    produits = cursor.fetchall()
    print("\nContenu de la table 'produits' :")
    for row in produits:
        print(row)

    conn.close()
    print("\n✅ Test terminé : la base est accessible et les tables répondent correctement.")

if __name__ == "__main__":
    test_db()
    

