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
    """
    Session-class to store all information for the current user together with member functions.
    """
    def __init__(self, cursor, course, loginUser=None):
        """
        Initialization of session.
        :param loginUser: None by default, and changes to the logged in user's UserID.
        :param cursor: Cursor object used by the Python MySQL connector
        :param course: The ID(?) of the course the session is connected to
        """
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

    def getlastInd(self, table): #Dont know if this works, maybe?
        """
        Helper function to retrieve the last ID from a given table, e.g. useful when assigning a some ID to a new tuple
        """
        self.c.execute("SELECT MAX(SHOW KEYS FROM %s WHERE Key_name = 'PRIMARY')", table)
        return self.c.fetchall()


    def login(self):
        """
        Login-method. Greets the user with the Piazza "logo" and asks for username and password.
        Continues asking until a correct combination has been given, and updates loginUser to the userID.
        """
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
    
    def createThread(self):
        """
        Method for creating a thread. Asks for Thread title, tag, folder and content and ensures legal types.
        """
        title = input("Title: ")

        tag = ""
        legalTags = ["question", "announcement", "homework", "homework solution", "lectures notes", "general announcement"]
        while tag not in legalTags:
            tag = input("Tag: ").lower()
            print("Tags can only be question, announcement, homework, homework solution, lectures notes or general announcement.")
        
        self.c.execute("SELECT FolderID, FolderName FROM folder WHERE CourseID=%s",self.course)
        courseFolders = self.c.fetchall()
        courseFolders = np.array(courseFolders).reshape(len(courseFolders),2)
        print("Select folder: (", end='')
        for f in courseFolders[:,1]: # This loop simply prints all folder names in current course
            print(f, end=' ')
        print(")")
        
        folder = ""
        while folder not in courseFolders[:,1]:
            print("Invalid folder name, try again.")
            folder = input("Folder: ")
        folderID = np.where(courseFolders==folder)[0][0]
        question = input("Enter post message: ")
        
        # Now that we have all data we need, we need to insert new tuples
        Threadsql = "INSERT INTO thread VALUES ({}, {}, {}, {})"
        self.c.execute(Threadsql.format(self.getlastInd("thread")+1, title, tag, folderID))
        #self.c.execute("INSERT INTO POST VALUES ({}, {}, {},")
        mydb.commit()

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



    #Teste-ting
    a = [("someID", "navn1"), ("id2", "navn2"), ("id3", "gucci")]
    a = np.array(a).reshape(len(a),2)
    print(a[:,0])

if __name__ == '__main__':
    main()