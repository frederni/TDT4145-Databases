import mysql.connector

def connect():
    global mydb
    try:
        mydb = mysql.connector.connect(
        host="localhost",
        user="root",
        password="indmat4ever",
        database="piazza"
        )
    except: # In case the piazza database is not yet created (though it usually is)
        mydb = mysql.connector.connect(
        host="localhost",
        user="root",
        password="indmat4ever"
        )
        restartDB(loadTables=False)

def restartDB(loadTables=True):
    c = mydb.cursor()
    c.execute("DROP DATABASE piazza") # Maybe this should be in try block (since we cant drop a dropped db)
    c.execute("CREATE DATABASE piazza")
    mydb.database="piazza"
    if loadTables:
        for line in open("piazza_setup.sql", 'r').read().split(';\n')[:-1]:
            #Looks scary, but we just find all queries and execute them one by one, ignoring the last split since it's empty
            c.execute(line)

head="""
        _                    
       (_)                   
  _ __  _  __ _ __________ _ 
 | '_ \| |/ _` |_  /_  / _` |
 | |_) | | (_| |/ / / / (_| |
 | .__/|_|\__,_/___/___\__,_|
 | |                         
 |_|                         
"""

def main():
    print(head)
    connect()
    restartDB()

if __name__ == '__main__':
    main()