"""
Table Viewer Utility for NGO Compliance Verification System.
Allows quick inspection of all 13 database tables and their contents.

Usage:
  python -m backend.tests.view_tables                 # Summary of all 13 tables
  python -m backend.tests.view_tables <table_name>   # Dump contents of a specific table
"""

import sys, os, json
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from dotenv import load_dotenv
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), "..", ".env"))

import sqlite3

DB_PATH = os.environ.get("DATABASE_URL", "sqlite:///./ngo_compliance.db").replace("sqlite:///", "")

def get_connection():
    if not os.path.exists(DB_PATH):
        print(f"\n[ERROR] Database file '{DB_PATH}' not found. Run seed script first!\n")
        sys.exit(1)
    return sqlite3.connect(DB_PATH)

def list_tables():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name;")
    tables = [r[0] for r in cursor.fetchall()]
    
    print("\n" + "="*70)
    print("  NGO COMPLIANCE VERIFICATION SYSTEM — DATABASE TABLES OVERVIEW")
    print("="*70)
    print(f" Database File: {DB_PATH}\n")
    print(f" {'#':<3} | {'Table Name':<38} | {'Rows':<6}")
    print("-" * 55)
    
    total_rows = 0
    for idx, name in enumerate(tables, 1):
        cursor.execute(f"SELECT COUNT(*) FROM {name};")
        count = cursor.fetchone()[0]
        total_rows += count
        print(f" {idx:<3} | {name:<38} | {count:<6}")
    
    print("-" * 55)
    print(f" Total Tables: {len(tables)} | Total Records: {total_rows}\n")
    print(" To view data inside a specific table, run:")
    print("   .venv\\Scripts\\python.exe -m backend.tests.view_tables <table_name>\n")
    conn.close()

def dump_table(table_name):
    conn = get_connection()
    cursor = conn.cursor()
    
    # Verify table exists
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?;", (table_name,))
    if not cursor.fetchone():
        print(f"\n[ERROR] Table '{table_name}' does not exist.")
        conn.close()
        return

    cursor.execute(f"PRAGMA table_info({table_name});")
    cols = [col[1] for col in cursor.fetchall()]

    cursor.execute(f"SELECT * FROM {table_name};")
    rows = cursor.fetchall()

    print("\n" + "="*80)
    print(f" TABLE: {table_name.upper()} ({len(rows)} rows)")
    print("="*80)

    if not rows:
        print(" [Table is empty]\n")
        conn.close()
        return

    for idx, row in enumerate(rows, 1):
        print(f"\n--- [Row {idx}] ---")
        for col_name, val in zip(cols, row):
            # Pretty-print JSON strings if possible
            if isinstance(val, str) and (val.startswith("{") or val.startswith("[")):
                try:
                    parsed = json.loads(val)
                    val = json.dumps(parsed, indent=2)
                except Exception:
                    pass
            print(f"  {col_name:<28}: {val}")

    print("\n" + "="*80 + "\n")
    conn.close()

if __name__ == "__main__":
    if len(sys.argv) > 1:
        dump_table(sys.argv[1])
    else:
        list_tables()
