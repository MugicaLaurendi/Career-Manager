import duckdb

con = duckdb.connect('\data\database.duckdb')

print("------------------ TEST START ------------------")

query = (f"""

    UPDATE users SET wallet = wallet + 1000000 WHERE id = 1;
    -- DROP TABLE IF EXISTS USERS;



""")
test = con.execute(query).fetchall()
print(test)



# Etat final
tables = con.execute("SHOW TABLES").fetchall()
print("FINAL STATE :")
print(tables)


print("------------------ TEST END ------------------")