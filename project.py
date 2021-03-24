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
    def __init__(self, db, autofill=False, loginUser=None):
        """
        Initialization of session.
        :param loginUser: None by default, and changes to the logged in user's UserID.
        :param cursor: Database object
        :param autofill: Determines wether or not we should ask for user input or auto-complete
        :param course: The ID(?) of the course the session is connected to
        """
        self.loginUser = loginUser
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

    def getUserInfo(self, UID, getName=False, getInstructor=False):
        self.c.execute("SELECT DisplayName, Usertype FROM piazza_user WHERE UserID=%s", (UID, ))
        tup = list(self.c.fetchall()[0]) # Cast to list so we may modify last item
        tup[1] = tup[1] == 'instructor'
        if getName and getInstructor:
            return tup
        elif getName:
            return tup[0]
        elif getInstructor:
            return tup[1]
        return None

    def getFolderFromID(self, FID):
        raise NotImplementedError
    
    def like(self, TID, postNo):
        raise NotImplementedError

    def reply(self, TID, postNo):
        raise NotImplementedError
    


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
        # courseFolders puts the folderID and folderName in an array of type
        # [id1, name1]
        # [id2, name2]
        # [...,  ... ]
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
            self.c.execute("SELECT AllowsAnonPosts from Course where CourseID = %s", (self.course, ))
            if int(c.fetchall()[0][0]): # If global course settings allow anon posts
                isAnon = int(input("Anonymous? (Y/N) ").lower() == "y") # Boolean casted as int


        folderID = courseFolders[np.where(courseFolders==folder)[0][0], 0]
        
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
        keyword = input("Search for: ")
        padded = '%' + keyword + '%'
        self.c.execute("SELECT * FROM post WHERE Textfield LIKE %s", (keyword, ))
        results = c.fetchall
        if len(results) !=0:
            print("Found", len(results), "matching posts")
            displayThread(results)
        else:
            print("No results")
        
        

    def displayThread(self, results):
        """
        We display all posts in a thread with search match
        """
        for res in results: # results = ((val_11, val_12), (val_21, val-22), ...)
            uniqueThreadIDs = list(set([res[i][1] for i in range(len(results))]))
        for TID in uniqueThreadIDs:
            self.c.execute("SELECT * FROM thread NATURAL JOIN post NATURAL JOIN interactwith WHERE TID=%s", (TID, ))
            #[TID, PostNo, Title, ThreadTag, FolderID, IsAnonymous, PostTag, Textfield, UserID, Time_stamp, InteractionType]
            #[ 0 ,   1   ,   2  ,     3    ,    4    ,    5       ,    6   ,    7     ,   8   ,   9       ,       10       ]
            postTab = self.c.fetchall() # All posts belonging to thread
            # We print the first post uniquely
            title, tTag, timestamp, folder = postTab[0][2], postTab[0][3], time.ctime(postTab[0][9]), postTab[0][4]
            print(ttag[0].upper() + ttag[1:], " : ", title, " (In folder ", self.getFolderFromID(folder),")", sep='') #TODO implement that fnc
            
            #Determine status (color) of thread
            studentReply, instructorReply = False, False # Default bool flags to false that is used to color thread
            for post in postTab:
                if post[10] == 'answer' and self.getUserInfo(post[8], getInstructor=True): instructorReply = True
                elif post[10] == 'answer': studentReply = True
            statusStr = "Status: "
            if studentReply: statusStr += "(GREEN)"
            if instructorReply: statusStr += "(ORANGE)"
            if not (studentReply and instructorReply): statusStr += "(RED)"
            print(statusStr)

            # Print all posts
            for post in postTab: 
                postnumber, isAnon, pTag, text, UID, timestamp, interType = post[1], post[5:]
                timestamp = time.ctime(timestamp) # Convert to easily readable time
                postedBy = self.getUserInfo(UID, getName=True)
                print("#" + postnumber + "[" + pTag[0].upper() + pTag[1:] + "]", end=' ')
                print("Posted by:", "Anonymous" if isAnon else postedBy, end=' ')
                print(timestamp)
                print(text)
                print(15*'-')
                # TODO consider implementing something to show amount of likes
            action = input("enter post number followed by 'R' or 'L' to reply or like a post, e.g. '1R' or '2L'")
            if action[1] == 'L':
                self.like(TID=TID, postNo=int(action[0]))
            elif action[1] == 'R':
                self.reply(TID=TID, postNo=int(action[0]))
            # Not finished!


    def viewStats(self):
        if not self.loginUser:
            print("You need to be logged in to view statistics.")
            self.login()
        
        #need to find out wether the logged in user is an instructor or not
        

        pass



def main():
    UserDB = Database(host="localhost", usr="root", pw="indmat4ever", db="piazza")
    UserSession = Session(UserDB, autofill=False)



if __name__ == '__main__':
    main()