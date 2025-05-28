import sqlite3

def init_db():
    conn = sqlite3.connect("wallets.db")
    conn.execute("""CREATE TABLE IF NOT EXISTS wallets (
        address TEXT PRIMARY KEY,
        name TEXT,
        last_signature TEXT
    )""")
    conn.commit()
    conn.close()

def add_wallet(address, name):
    conn = sqlite3.connect("wallets.db")
    conn.execute("INSERT OR IGNORE INTO wallets (address, name) VALUES (?, ?)", (address, name))
    conn.commit()
    conn.close()

def get_wallets():
    conn = sqlite3.connect("wallets.db")
    result = conn.execute("SELECT address, name FROM wallets").fetchall()
    conn.close()
    return result

def delete_wallet(address):
    conn = sqlite3.connect("wallets.db")
    conn.execute("DELETE FROM wallets WHERE address=?", (address,))
    conn.commit()
    conn.close()

def update_signature(address, signature):
    conn = sqlite3.connect("wallets.db")
    conn.execute("UPDATE wallets SET last_signature=? WHERE address=?", (signature, address))
    conn.commit()
    conn.close()

def get_last_signature(address):
    conn = sqlite3.connect("wallets.db")
    result = conn.execute("SELECT last_signature FROM wallets WHERE address=?", (address,)).fetchone()
    conn.close()
    return result[0] if result else None
