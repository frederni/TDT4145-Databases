create table Piazza_user(
	UserID	integer,
    Email	varchar(30) ,
    Passkey varchar(30) ,
    DisplayName varchar(30),
    Usertype varchar(15) not null, 
    constraint Piazza_user_pk primary key(UserID)
    );
    
create table Course(
	CourseID integer,
    CourseName varchar(30),
    Term	varchar(15),
    AllowsAnonPosts boolean,
    constraint Course_pk primary key(CourseID)
    );

create table CourseMember(
	UserID integer,
    CourseID integer,
    constraint CourseMember_pk primary key(UserID, CourseID),
    constraint CourseMember_fk1 foreign key(UserID) references Piazza_user(UserID)
		on update cascade
		on delete cascade,
    constraint CourseMember_fk2 foreign key(CourseID) references Course(CourseID)
		on update cascade
        on delete cascade
    );
    
create table Folder(
	FolderID integer,
    FolderName varchar(30),
    CourseID integer not null,
    ParentfolderID integer,
    constraint Folder_pk primary key(FolderID),
    constraint Folder_fk1 foreign key(CourseID) references Course(CourseID)
		on update cascade
        on delete cascade,
	constraint Folder_fk2 foreign key(ParentfolderID) references Folder(FolderID)
		on update cascade
        on delete cascade
	);
    
create table Thread(
	TID integer NOT NULL AUTO_INCREMENT,
    Title varchar(40),
    ThreadTag varchar(20),
    FolderID integer not null,
    constraint Thread_pk primary key(TID),
    constraint Thread_fk1 foreign key(FolderID) references Folder(FolderID)
		on update cascade
        on delete cascade
    );
    
create table Post(
	PostNo integer,
    TID integer,
    IsAnonymous boolean,
    PostTag varchar(20),
    Textfield varchar(500),
    constraint Post_pk primary key(PostNo, TID),
    constraint Post_fk1 foreign key(TID) references Thread(TID)
		on update cascade
        on delete cascade
	);

create table InteractWith(
	TID integer,
    PostNo integer,
    UserID integer,
    Time_stamp varchar(10),
    InteractionType varchar(10),
    constraint InteractWith_pk primary key(TID,PostNo,UserID),
    constraint InteractWith_fk1 foreign key(TID) references Thread(TID)
		on update cascade
        on delete cascade,
	constraint InteractWith_fk2 foreign key(PostNo) references Post(PostNo)
		on update cascade
        on delete cascade,
	constraint InteractWith_fk3 foreign key(UserID) references Piazza_user(UserID)
		on update cascade
        on delete cascade
        );

INSERT INTO piazza_user VALUES (1, "em", "pwhei", "kul gutt", "student");
INSERT INTO course VALUES (123, "DBMOD", "V21", 1);
INSERT INTO folder VALUES (101, "exam", 123, NULL);
INSERT INTO folder VALUES (102, "ex1", 123, NULL);