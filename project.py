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

class session(object):
    def __init__(self, loginUser=None):
        self.loginUser = loginUser
        #NB Need to ensure that we don't give users ID "0"

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

    def login():
        print(head)
        while not self.loginUser:
            email = input("E-mail: ")
            password = input("Password: ")
        # if (username, password) in SELECT email, password from piazza_user:
            # loggedInUser = userID elns
            # return 0
        # else
            # print("Invalid username or password.")
    def createThread():
        pass

    def search():
        pass

    def displayThread():
        pass

    def viewStats():
        pass



def main():
    print(head)
    connect()
    restartDB()

if __name__ == '__main__':
    main()

print("hei")
