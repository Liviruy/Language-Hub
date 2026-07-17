import sqlite3, pathlib
db = pathlib.Path("database/language.db")
print(f"File size: {db.stat().st_size} bytes")
conn = sqlite3.connect(str(db))
conn.row_factory = sqlite3.Row
tables = conn.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name").fetchall()
print("Tables:", [t["name"] for t in tables])
langs = conn.execute("SELECT * FROM languages").fetchall()
for l in langs:
    print(f'  Lang: {l["code"]} -> {l["name"]}')
migs = conn.execute("SELECT * FROM _migrations").fetchall()
for m in migs:
    print(f'  Migration: v{m["version"]} - {m["name"]}')
words_schema = conn.execute("SELECT sql FROM sqlite_master WHERE name='words'").fetchone()[0]
print("Words table: OK")
indexes = conn.execute("SELECT name FROM sqlite_master WHERE type='index' AND tbl_name='words'").fetchall()
print("Indexes:", [r[0] for r in indexes])
conn.close()
print("Database verified successfully")
