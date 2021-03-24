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
            print(line, end='\n-')
            #Looks scary, but we just find all queries and execute them one by one
            self.c.execute(line)
        self.connection.commit()

class Session(object):
    """
    Session-class to store all information for the current user together with member functions.
    """
    def __init__(self, db, autofill=False, loginUser=None):
        """
        Initialization of session.
        :param loginUser: None by default, and changes to the logged in user's UserID.
        :param loginUserType: None by default, and changes to the logged in user's user type (student or instructor).
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
                email, password = "kari@ntnu.no", "kari123"
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
            print("Welcome! Select course:", courseName) # TODO auto select if user only has 1 course or list legal choices
        else: courseName = input("Welcome! Select course: ")
        self.c.execute("SELECT CourseID FROM course WHERE CourseName=%s", (courseName, ))
        self.course = int(self.c.fetchall()[0][0])

    def getlastInd(self):
        self.c.execute("SELECT LAST_INSERT_ID()")
        return int(self.c.fetchall()[0][0])

    def getUserInfo(self, UID, getName=False, getInstructor=False):
        self.c.execute("SELECT DisplayName, Usertype FROM piazza_user WHERE UserID=%s", (UID, ))
        tup = self.c.fetchall()
        if len(tup) == 0:
            return None
        tup = list(tup[0]) # Cast to list so we may modify last item
        tup[1] = tup[1] == 'instructor'
        if getName and getInstructor:
            return tup
        elif getName:
            return tup[0]
        elif getInstructor:
            return tup[1]
        return None

    def getFolderFromID(self, FID):
        self.c.execute("SELECT FolderName FROM folder WHERE FolderID=%s", (FID, ))
        return self.c.fetchall()[0][0]

    def askUserInput(self):
        if self.autofill:
            text = "Generic question/answer by autofill"
            isAnon = False            
        else:
            question = input("Enter post message: ")
            self.c.execute("SELECT AllowsAnonPosts from Course where CourseID = %s", (self.course, ))
            if int(self.c.fetchall()[0][0]): # If global course settings allow anon posts
                isAnon = int(input("Anonymous? (Y/N) ").lower() == "y") # Boolean casted as int
        return text, isAnon

    
    def like(self, TID, postNo):
        #Not a usecase and unfortunately not enough time to implement
        raise NotImplementedError

    def reply(self, TID, postNo):
        # First find the largest postID to our thread
        self.c.execute("SELECT MAX(PostNo) FROM post WHERE TID=%s",(TID ,))
        largestPostNo = self.c.fetchall()[0][0]
        print("Replying to post", postNo)
        text, isAnon = askUserInput()
        # Need to check if the post we're replying to is followup or not
        # We basically inherit the same post tag as the post we're replying to
        self.c.execute("SELECT PostTag FROM post WHERE (PostNo, TID)=(%s,%s)", (postNo, TID))
        postTag = self.c.fetchall()[0][0]
        self.c.execute("INSERT INTO post VALUES (%s, %s, %s, %s, %s)", (
            postNo,
            TID,
            isAnon,
            PostTag,
            text)
        )
        self.c.execute("INSERT INTO interactwith VALUES (%s, %s, %s, %s, %s)", (
            TID,
            largestPostNo + 1,
            self.loginUser,
            time.time(),
            'create')
        )
        self.db.connection.commit()
        return postNo # We return the post number
    


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
        text, isAnon = askUserInput()
        if self.autofill:
            folder = "exam"
            print("Folder:", folder)
        else:
            folder = ""
            while folder not in courseFolders[:,1]:
                folder = input("Folder: ")
                if folder not in courseFolders[:,1]:
                    print("Invalid folder name, try again.")
        folderID = courseFolders[np.where(courseFolders==folder)[0][0], 0]
        
        # Now that we have all data we need, we need to insert new tuples
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

        self.c.execute("INSERT INTO InteractWith VALUES (%s, %s, %s, %s, %s)", # Creation of post
            (self.getlastInd(), # TID
            1, #PostNo
            self.loginUser,
            time.time(),
            "create")
        )


        self.db.connection.commit() # Required to make actual changes to database

    def search(self):
        keyword = input("Search for: ")
        padded = '%' + keyword + '%'
        self.c.execute("SELECT * FROM post WHERE Textfield LIKE %s", (padded, ))
        results = self.c.fetchall()
        if len(results) !=0:
            print("Found", len(results), "matching posts")
            self.displayThread(results)
        else:
            print("No results")
        
        

    def displayThread(self, results):
        """
        We display all posts in a thread with search match
        """
        for res in results:
            uniqueThreadIDs = list(set([results[i][1] for i in range(len(results))]))
        for TID in uniqueThreadIDs:
            self.c.execute("SELECT * FROM thread NATURAL JOIN post NATURAL JOIN interactwith WHERE TID=%s", (TID, ))
            #[TID, PostNo, Title, ThreadTag, FolderID, IsAnonymous, PostTag, Textfield, UserID, Time_stamp, InteractionType]
            #[ 0 ,   1   ,   2  ,     3    ,    4    ,    5       ,    6   ,    7     ,   8   ,   9       ,       10       ]
            postTab = self.c.fetchall() # All posts belonging to thread
            # We print the first post uniquely
            title, tTag, timestamp, folder = postTab[0][2], postTab[0][3], time.ctime(postTab[0][9]), postTab[0][4]
            print(tTag[0].upper() + tTag[1:], " : ", title, " (In folder ", self.getFolderFromID(folder),")", sep='')
            
            #Determine status (color) of thread
            studentReply, instructorReply = False, False # Default bool flags to false that is used to color thread
            for post in postTab:
                if post[6] == 'answer' and self.getUserInfo(post[8], getInstructor=True):
                    instructorReply = True
                elif post[6] == 'answer':
                    studentReply = True
            statusStr = "Status: "
            if studentReply: statusStr += "(GREEN)"
            if instructorReply: statusStr += "(ORANGE)"
            if not (studentReply and instructorReply): statusStr += "(RED)"
            print(statusStr)

            # Print all posts
            for post in postTab: 
                postnumber, isAnon, pTag, text, UID, timestamp, interType = post[1], post[5], post[6], post[7], post[8], post[9], post[10]
                timestamp = time.ctime(timestamp) # Convert to easily readable time
                postedBy = self.getUserInfo(UID, getName=True)
                print("#" + str(postnumber) + "[" + pTag[0].upper() + pTag[1:] + "]", end=' ')
                print("Posted by:", "Anonymous" if isAnon else postedBy, end=' ')
                print(timestamp)
                print(text)
                print(15*'-')
            action = input("enter post number followed by 'R' or 'L' to reply or like a post, e.g. '1R' or '2L'")
            if action[-1] == 'L':
                excludePID = self.like(TID=TID, postNo=int(action[:-1]))
            elif action[-1] == 'R':
                excludePID = self.reply(TID=TID, postNo=int(action[:-1]))
            # Log that user has read all posts
            for post in postTab:
                self.c.execute("INSERT INTO interactwith values (%s, %s, %s, %s, %s)",
                (post[0], #TID
                post[1], #PostNo
                self.loginUser,
                time.time(),
                'view')
                )
            self.db.connection.commit()


    def viewStats(self): #A suggestion, most likely needs editing
        while not self.getUserInfo(self.loginUser, getInstructor=True): #Need to find out wether the logged in user is an instructor or not
            
            print("You need to be logged in to view statistics.")
            self.login()
            if not self.getUserInfo(self.loginUser, getInstructor=True):
                print("Only instructors can view statistics.")
            else: break 
        
        
        self.c.execute("SELECT DisplayName,COUNT(PostNo) AS Amount FROM Piazza_user LEFT OUTER JOIN InteractWith ON Piazza_user.userID=InteractWith.userID WHERE InteractionType='create' GROUP BY piazza_user.UserID ORDER BY Amount DESC")
        createResult = self.c.fetchall()
        self.c.execute("SELECT DisplayName,COUNT(PostNo) AS Amount FROM Piazza_user LEFT OUTER JOIN InteractWith ON Piazza_user.userID=InteractWith.userID GROUP BY piazza_user.UserID ORDER BY Amount DESC")
        viewResult = self.c.fetchall()
        print(viewResult)
        print(createResult)
        for ind, res in enumerate(viewResult):
            try:
                print("User:", res[0], "\tViewed:", res[1], "\tCreated:", createResult[ind][1])
            except IndexError:
                print("User:", res[0], "\tViewed:", res[1], "\tCreated:", 0)



def main():
    UserDB = Database(host="localhost", usr="root", pw="indmat4ever", db="piazza")
    UserSession = Session(UserDB, autofill=True)



if __name__ == '__main__':
    main()