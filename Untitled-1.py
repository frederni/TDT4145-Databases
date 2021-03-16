import mysql.connector

def connect():
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
    try:
        c.execute("DROP DATABASE piazza")
        #Need to nest in try block in case db is already dropped
    c.execute("CREATE DATABASE piazza")
    mydb.database="piazza"
    if loadTables:
        for line in open("piazza_setup.sql", 'r').read().split(';\n')[:-1]:
            #Looks scary, but we just find all queries and execute them one by one, ignoring the last split since it's empty
            c.execute(line)


def main():
    connect()
    restartDB()

if __name__ == '__main__':
    main()