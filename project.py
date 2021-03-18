import mysql.connector
import numpy as np

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
    def __init__(self, cursor, course, loginUser=None):
        self.loginUser = loginUser
        self.c = cursor
        self.course = course
        self.head = """                    
           _                    
          (_)                   
    _ __  _  __ _ __________ _ 
    | '_ \| |/ _` |_  /_  / _` |
    | |_) | | (_| |/ / / / (_| |
    | .__/|_|\__,_/___/___\__,_|
    | |                         
    |_|                                                 
    """
    #NB Need to ensure that we don't give users ID "0"

    def login(self):
        print(self.head)
        while not self.loginUser:
            email = input("E-mail: ")
            password = input("Password: ")
            self.c.execute("SELECT Email, Passkey FROM piazza_user;")
            legalcombos = self.c.fetchall()
            print(legalcombos)
            if (email, password) in legalcombos:
                self.c.execute("SELECT UserID FROM piazza_user WHERE (Email=%s & Passkey=%s)", (email, password))
                self.loginUser = self.c.fetchall()
                break
            else:
                print("Invalid username or password")
    
    def createThread():
        title = input("Title: ")

        tag = ""
        legalTags = ["question", "announcement", "homework", "homework solution", "lectures notes", "general announcement"]
        while tag not in legalTags:
            tag = input("Tag: ").lower()
            print("Tags can only be question, announcement, homework, homework solution, lectures notes or general announcements.")
        
        self.c.execute("SELECT FolderID, FolderName FROM folder WHERE CourseID=%s",self.course)
        courseFolders = c.fetchall()
        courseFolders = np.array(courseFolders).reshape(len(courseFolders),2)
        print("Select folder: (", end='')
        for f in courseFolders[:,1]:
            print(f, end=' ')
        print(")")
        folder = ""
        while folder not in courseFolders[:,1]:
            print("Invalid folder name, try again.")
            folder = input("Folder: ")
        
        # Not finished!
        

    def search():
        pass

    def displayThread():
        pass

    def viewStats():
        pass



def main():
    #connect()
    #restartDB()
    #mySession = session(mydb.cursor())
    #mySession.login()
    a = [("someID", "navn1"), ("id2", "navn2"), ("id3", "gucci")]
    a = np.array(a).reshape(len(a),2)
    print(a[:,0])

if __name__ == '__main__':
    main()