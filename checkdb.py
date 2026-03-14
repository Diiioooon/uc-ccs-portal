import sqlite3

conn = sqlite3.connect('database.db')

# Select all columns except the auto-generated id
rows = conn.execute('SELECT idnum, lastname, firstname, midname, email, course, level, address FROM users').fetchall()

if len(rows) == 0:
    print("\n No users registered yet.\n")
else:
    print(f"\n Total users: {len(rows)}\n")
    print(f"{'IDNUM':<15} {'LAST NAME':<15} {'FIRST NAME':<15} {'MIDDLE':<12} {'EMAIL':<25} {'COURSE':<8} {'LEVEL':<10} {'ADDRESS'}")
    print('-' * 115)
    for row in rows:
        print(f"{row[0]:<15} {row[1]:<15} {row[2]:<15} {row[3]:<12} {row[4]:<25} {row[5]:<8} {row[6]:<10} {row[7]}")

conn.close()