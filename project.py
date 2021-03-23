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
            #Looks scary, but we just find all queries and execute them one by one
            self.c.execute(line)

class Session(object):
    """
    Session-class to store all information for the current user together with member functions.
    """
    def __init__(self, db, autofill=False, loginUser=None, loginUserType=None):
        """
        Initialization of session.
        :param loginUser: None by default, and changes to the logged in user's UserID.
        :param loginUserType: None by default, and changes to the logged in user's user type (student or instructor).
        :param cursor: Database object
        :param autofill: Determines wether or not we should ask for user input or auto-complete
        :param course: The ID(?) of the course the session is connected to
        """
        self.loginUser = loginUser
        self.loginUserType=loginUserType
        self.c = db.connection.cursor(prepared=True)
        self.db = db
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
        self.usecaseMenu()

    def usecaseMenu(self):
        answer = ""
        while answer != "q":
            print("Usecase menu - enter q to quit.")
            print("1 \t Login", "2 \t Create a thread", "3 \t Reply to thread", "4 \t Search", "5 \t View stats", sep='\n')
            answer = input("Select usecase: ").lower()
            if answer == "1":
                self.login()
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
            if self.autofill:
                email, password = "ola@ntnu.no", "passord123"
                print("E-mail:", email, "\nPassword:", password)
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
        if self.autofill:
            courseName = "Databaser"
            print("Welcome! Select course:", courseName)
        else: courseName = input("Welcome! Select course: ")
        self.c.execute("SELECT CourseID FROM course WHERE CourseName=%s", (courseName, ))
        self.course = int(self.c.fetchall()[0][0])

    def getlastInd(self):
        self.c.execute("SELECT LAST_INSERT_ID()")
        return int(self.c.fetchall()[0][0])

    def createThread(self):
        """
        Method for creating a thread. Asks for Thread title, tag, folder and content and ensures legal types.
        """
        if not self.loginUser:
            print("You need to be logged in to create a thread.")
            self.login()


        if self.autofill:
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
        
        self.c.execute("SELECT FolderID, FolderName FROM folder WHERE CourseID=%s", (self.course,))
        courseFolders = self.c.fetchall()
        courseFolders = np.array(courseFolders).reshape(len(courseFolders),2)
        print("Select folder: (", end='')
        for f in courseFolders[:,1]: # This loop simply prints all folder names in current course
            print(f, end=', ')
        print(")")
        if self.autofill:
            folder = "exam"
            print("Folder:", folder)
            question = "I don't quite understand task 4c. Does anyone know how to solve it?"
            print("Enter post message:", question)
            isAnon = False
            print("Anonymous? (Y/N): n")
        else:
            folder = ""
            while folder not in courseFolders[:,1]:
                folder = input("Folder: ")
                if folder not in courseFolders[:,1]:
                    print("Invalid folder name, try again.")
            question = input("Enter post message: ")
            isAnon = int(input("Anonymous? (Y/N) ").lower() == "y") # Boolean casted as int
            # TODO only allow anon posts if global settings are ok 


        folderID = courseFolders[np.where(courseFolders==folder)[0][0], 0] # TODO fix this
        
        # Now that we have all data we need, we need to insert new tuples
        print(folderID)
        self.c.execute("INSERT INTO thread (Title, ThreadTag, FolderID) VALUES (%s, %s, %s)",
            (title,
            tag,
            folderID)
        )

        self.c.execute("INSERT INTO post VALUES (%s, %s, %s, %s, %s)",
            (1, # First post in thread always
            self.getlastInd(), # TID
            isAnon,
            "op",
            question)
        )

        self.c.execute("INSERT INTO InteractWith VALUES (%s, %s, %s, %s, %s)",
            (self.getlastInd(), # TID
            1, #PostNo
            self.loginUser,
            time.time(),
            "create")
        )

        self.db.connection.commit() # Required to make actual changes to database

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

    def viewStats(self): #A suggestion, most likely needs editing
        while self.loginUserType != "Instructor": #Need to find out wether the logged in user is an instructor or not
            
            print("You need to be logged in to view statistics.")
            self.login()
            self.c.execute("SELECT type FROM Piazza_user WHERE userID=%s",(self.loginUser, ))
            self.loginUserType = self.c.fetchall()[0][0] 
            if self.loginUserType != "Instructor":
                print("Only instructors can view statistics.")
            else: break 
        
        #Not sure about the following SQL
        self.c.execute("SELECT DisplayName,COUNT(PostNo) FROM Piazza_user LEFT OUTER JOIN InteractWith ON Piazza_user.userID=InteractWith.userID WHERE InteractionType='create' GROUP BY UserID")
        self.c.fetchall()
        self.c.execute("SELECT DisplayName,COUNT(PostNo) FROM Piazza_user LEFT OUTER JOIN InteractWith ON Piazza_user.userID=InteractWith.userID WHERE InteractionType='view' GROUP BY UserID")
        self.c.fetchall()


                

            



        
        

        pass



def main():
    UserDB = Database(host="localhost", usr="root", pw="indmat4ever", db="piazza")
    UserSession = Session(UserDB, autofill=False)



if __name__ == '__main__':
    main()