import sqlite3
import os
import main
conn = sqlite3.connect(os.path.join(os.path.dirname(os.path.realpath(__file__)), "data", "user_information.db"))
conn.execute("delete from user_information where emailid='majmals1998@gmail.com'")
conn.commit()
print(conn.execute("select fullname from user_information").fetchall())