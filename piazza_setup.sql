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
    Time_stamp float,
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
insert into Piazza_user values (1,"marit@ntnu.no","marit456","Marit Johnsen","student");
insert into Piazza_user values (2, "per@ntnu.no","per123","Per Hansen", "student");
insert into Piazza_user values (3, "kari@ntnu.no", "kari123","Kari Nilsen", "instructor");
insert into Piazza_user values (4, "petter@ntnu.no","petter456","Petter Jakobsen","instructor");
insert into Piazza_user values (5, "anna@ntnu.no","anna789","Anna Pedersen","student");
insert into Course values (4145, "Databaser","2021V",1);
insert into Course values (4180, "Optimering", "2021V",0);
insert into Course values (4267, "Lineare statistiske modeller","2021V",0);
insert into CourseMember values (4,4180);
insert into CourseMember values (5,4180);
insert into CourseMember values (1,4145);
insert into CourseMember values (1,4180);
insert into CourseMember values (3,4145);
insert into CourseMember values (2,4145);
insert into Folder values (12,"Exercise1",4145,NULL);
insert into Folder values (21,"Exam",4180,NULL);
insert into Folder values (22,"Exercise1",4180,NULL);

insert into Thread (Title,ThreadTag,FolderID) values ("Problem 1 in exam 2020","question",21);
insert into Post values (211,last_insert_id(),1,"op","Can anyone help with this problem?");
insert into Post values (212,last_insert_id(),0,"answer", "Yes, you have to do this...");
insert into Post values (213,last_insert_id(),0,"followup", "Another approach is...");

insert into Thread (Title,ThreadTag,FolderID) values ("Solution to exercise1","homework solution",12);
insert into Post values (214,last_insert_id(),0,"op", "LF...");

insert into Thread (Title,ThreadTag,FolderID) values ("help with problem 3 in exam 2020","question",21);
insert into Post values (216,last_insert_id(),0,"op", "How do you solve this...");

insert into Thread (Title,ThreadTag,FolderID) values ("deadline for exercise1","announcement",22);
insert into Post values (215,last_insert_id(),0,"op", "The deadliinteractwithpostne is...");

insert into interactwith values (last_insert_id(),215,4,1616577126.596736,"create");
insert into interactwith values (last_insert_id()-1, 216,1,1616577842.2352426,"create");
insert into interactwith values (last_insert_id()-2,214,3, 1616578173.643487, "create");
insert into interactwith values (last_insert_id()-3,211,1,1616578501.3076324,"create");
insert into interactwith values (last_insert_id()-3,212,3, 1616578536.6857567, "create");
insert into interactwith values (last_insert_id()-3,213,2, 1616578559.7238562, "create");