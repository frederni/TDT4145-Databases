import mysql.connector # Connector
import numpy as np # For array management
import time # To generate timestamp

class Database(object):
    def __init__(self, host, usr, pw, db):
        self.host = host
        self.user = usr
        self.password = pw
        self.database = db
        self.connect()

    def connect(self):
        self.connection = mysql.connector.connect(
        host=self.host,
        user=self.user,
        password=self.password,
        )
        self.c = self.connection.cursor()
        self.restartDB()


    def restartDB(self):
        try:
            self.c.execute("DROP DATABASE {}".format(self.database))
        except mysql.connector.errors.DatabaseError:
            pass # We don't worry about dropping a non-existing database
        self.c.execute("CREATE DATABASE {}".format(self.database))
        self.connection.database=self.database
        for line in open("piazza_setup.sql", 'r').read().split(';\n'):
            #Looks scary, but we just find all queries and execute them one by one, ignoring the last split since it's empty
            self.c.execute(line)

class Session(object):
    """
    Session-class to store all information for the current user together with member functions.
    """
    def __init__(self, db, autofill=False loginUser=None):
        """
        Initialization of session.
        :param loginUser: None by default, and changes to the logged in user's UserID.
        :param cursor: Database object
        :param autofill: Determines wheter or not we should ask for user input or auto-complete
        :param course: The ID(?) of the course the session is connected to
        """
        self.loginUser = loginUser
        self.c = db.connection.cursor()
        self.course = None
        self.autofill = autofill
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
        self.usecaseMenu() # TODO implement this

    def usecaseMenu(self):
        answer = ""
        while answer != "q":
            print("", end="", flush=True)
            print("Usecase menu - enter q to quit.")
            print("1 \t Login", "2 \t Create a thread", "3 \t Reply to thread", "4 \t Search", "5 \t View stats", sep='\n')
            answer = input("Select usecase: ").lower()
            if answer == "1":
                self.login()
                print("self.loginUser", self.loginUser)
            elif answer == "2":
                self.createThread()
            elif answer == "3":
                print("Not yet implemented:)")
            elif answer == "4":
                self.search()
            elif answer == "5":
                self.viewStats()


    def login(self):
        """
        Login-method. Greets the user with the Piazza "logo" and asks for username and password.
        Continues asking until a correct combination has been given, and updates loginUser to the userID.
        """
        print(self.head)
        while not self.loginUser:
            if autofill:
                email, password = "ola@ntnu.no", "passord123"
            else:
                email = input("E-mail: ")
                password = input("Password: ")
            self.c.execute("SELECT Email, Passkey FROM piazza_user")
            legalcombos = self.c.fetchall()
            if (email, password) in legalcombos:
                self.c.execute("SELECT UserID FROM piazza_user WHERE (Email=%s && Passkey=%s)", (email, password))
                self.loginUser = self.c.fetchall()[0][0]
                break
            else:
                print("Invalid username or password")
        if autofill: courseName = "Databaser"
        else: courseName = input("Welcome! Select course: ")
        self.c.execute("SELECT CourseID FROM course WHERE CourseName='{}'".format(courseName))
        self.course = self.c.fetchall()[0][0]

    def getlastInd(self):
        self.c.execute("SELECT LAST_INSERT_ID()")
        return self.c.fetchall()[0][0]

    def createThread(self):
        """
        Method for creating a thread. Asks for Thread title, tag, folder and content and ensures legal types.
        """
        if not self.loginUser:
            print("You need to be logged in to create a thread.")
            self.login()


        if autofill:
            title = "Please help me!"
            tag = "question"
        else:
            title = input("Title: ")
            tag = ""
            legalTags = ["question", "announcement", "homework", "homework solution", "lectures notes", "general announcement"]
            while tag not in legalTags:
                tag = input("Tag: ").lower()
                if tag not in legalTags:
                    print("Tags can only be question, announcement, homework, homework solution, lectures notes or general announcement.")
        
        self.c.execute("SELECT FolderID, FolderName FROM folder WHERE CourseID='{}'".format(self.course))
        courseFolders = self.c.fetchall()
        courseFolders = np.array(courseFolders).reshape(len(courseFolders),2)
        print("Select folder: (", end='')
        for f in courseFolders[:,1]: # This loop simply prints all folder names in current course
            print(f, end=', ')
        print(")")
        if autofill:
            folder = "exam"
            print("Folder:", folder)
            question = "I don't quite understand task 4c. Does anyone know how to solve it?"
            print("Enter post message:", question)
        else:
            folder = ""
            while folder not in courseFolders[:,1]:
                folder = input("Folder: ")
                if folder not in courseFolders[:,1]:
                    print("Invalid folder name, try again.")
            question = input("Enter post message: ")
            isAnon = int(input("Anonymous? (Y/N) ").lower() == "y") # Boolean casted as int
            # TODO only allow anon posts if global settings are ok 


        folderID = np.where(courseFolders==folder)[0][0] # TODO fix this
        
        # Now that we have all data we need, we need to insert new tuples
        print(folderID)
        self.c.execute("INSERT INTO thread (Title, ThreadTag, FolderID) VALUES ('{}', '{}', {})".format(
            title,
            tag,
            folderID
        ))

        self.c.execute("INSERT INTO post VALUES ({}, {}, {}, {}, {})".format(
            1, # First post in thread always
            self.getlastInd(), # TID
            isAnon,
            "op",
            question
        ))

        self.c.execute("INSER INTO interact_with VALUES ({}, {}, {}, {}, {}".format(
            self.getlastInd(), # TID
            1, #PostNo
            self.loginUser,
            time.time(),
            "create"
        ))

        mydb.commit() # Required to make actual changes to database

    def search():
        pass

    def displayThread():
        # Forslag til hvordan vi kan displaye det:
        # <ThreadTag> : <Title>
        # Status: No replies (RED) / Student reply (GREEN) / Instructor reply (ORANGE)
        # for Post in posts:
        #   <Post.PostTag> | Posted by: <Interactwith.UserID>, time.ctime(<Interactwith.timestamp>)
        #   <Post.Textfield>
        #   print("-------")
        # action = input("PostNo to like Post, 'r' to reply, 'n' to view next thread)
        pass

    def viewStats():
        pass



def main():
    UserDB = Database(host="localhost", usr="root", pw="indmat4ever", db="piazza")
    UserSession = Session(UserDB)



if __name__ == '__main__':
    main()