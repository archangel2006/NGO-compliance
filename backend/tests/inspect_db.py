import sqlite3, sys, os

db_path = sys.argv[1] if len(sys.argv) > 1 else "./ngo_compliance.db"

if not os.path.exists(db_path):
    print(f"[ERROR] Database file not found: {db_path}")
    sys.exit(1)

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name;")
tables = cursor.fetchall()

print(f"\n--- Tables in {db_path} ---")
for (name,) in tables:
    cursor.execute(f"PRAGMA table_info({name});")
    cols = [row[1] for row in cursor.fetchall()]
    cursor.execute(f"SELECT COUNT(*) FROM {name};")
    count = cursor.fetchone()[0]
    print(f"\n  {name}  ({count} rows)")
    print(f"    cols: {cols}")

conn.close()
