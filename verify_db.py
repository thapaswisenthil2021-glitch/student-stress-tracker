import sqlite3

# Connect to database
conn = sqlite3.connect('stress_data.db')
cursor = conn.cursor()

# Get all tables
cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = cursor.fetchall()

print("=" * 60)
print("DATABASE VERIFICATION - Student Stress Tracker")
print("=" * 60)

print("\n✓ Tables Created:")
for table in tables:
    print(f"  - {table[0]}")

# Get detailed info about stress_records table
print("\n✓ stress_records table structure:")
cursor.execute('PRAGMA table_info(stress_records)')
columns = cursor.fetchall()
for col in columns:
    col_id, name, type_, notnull, dflt_value, pk = col
    print(f"  - {name} ({type_})")

# Get record count
cursor.execute("SELECT COUNT(*) FROM stress_records")
count = cursor.fetchone()[0]
print(f"\n✓ Records in database: {count}")

# Show chart_cache table structure
print("\n✓ chart_cache table structure:")
cursor.execute('PRAGMA table_info(chart_cache)')
columns = cursor.fetchall()
for col in columns:
    col_id, name, type_, notnull, dflt_value, pk = col
    print(f"  - {name} ({type_})")

print("\n" + "=" * 60)
print("✓ DATABASE SUCCESSFULLY INITIALIZED!")
print("=" * 60)

conn.close()
