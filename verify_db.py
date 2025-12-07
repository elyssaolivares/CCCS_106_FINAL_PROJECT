import sqlite3

conn = sqlite3.connect('app_database.db')
cursor = conn.cursor()

# Get all tables
cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name;")
tables = cursor.fetchall()

print("\n=== Database Tables ===")
for table in tables:
    print(f"  - {table[0]}")

# Check for user_activity table structure
print("\n=== user_activity Table Structure ===")
cursor.execute("PRAGMA table_info(user_activity);")
columns = cursor.fetchall()
for col in columns:
    print(f"  - {col[1]} ({col[2]})")

# Check for user_login_stats table structure
print("\n=== user_login_stats Table Structure ===")
cursor.execute("PRAGMA table_info(user_login_stats);")
columns = cursor.fetchall()
for col in columns:
    print(f"  - {col[1]} ({col[2]})")

# Check for failed_login_attempts table structure
print("\n=== failed_login_attempts Table Structure ===")
cursor.execute("PRAGMA table_info(failed_login_attempts);")
columns = cursor.fetchall()
for col in columns:
    print(f"  - {col[1]} ({col[2]})")

conn.close()
print("\nDatabase verification complete!")
