drop table if exists credit;
drop table if exists chapters;
drop table if exists comments;
drop table if exists reviews;
drop table if exists taglink;
drop table if exists tags;
drop table if exists works;
drop table if exists users;

create table users (
    uid int not null auto_increment primary key,
    username varchar(30), 
    passhash BINARY(64),
    commentscore DECIMAL
)

ENGINE = InnoDB;

create table works (
    sid int not null auto_increment,
    uid int not NULL,
    title VARCHAR(200),
    updated date,
    summary varchar(2000),
    stars float,
    PRIMARY KEY (sid),
    index(uid),
    foreign key (uid) references users(uid)
        on UPDATE CASCADE
        on delete cascade
)

ENGINE = InnoDB;

create table credit (
    uid int not null,
    sid int not null,
    foreign key (uid) references users(uid)
        on update cascade,
    foreign key (sid) references works(sid)
        on update cascade
)

ENGINE = InnoDB;

create table chapters (
    cid int not null auto_increment,
    cnum int,
    sid int not NULL,
    filename varchar(50),

    PRIMARY KEY (cid),
    index(sid),
    foreign key (sid) references works(sid)
        on update cascade
        on delete cascade
)

Engine = InnoDB;

create table tags (
    tid int not null auto_increment primary key,
    ttype varchar(20) not null,
    tname varchar(50) not null unique
)

Engine = InnoDB;

create table taglink (
    tid int not null,
    sid int not null,

    foreign key(sid) references works(sid)
        on update CASCADE
        on delete cascade,
    foreign key(tid) references tags(tid)
        on update CASCADE
        on delete cascade
)

Engine = InnoDB;

-- create table comments (
--     cid int not null,
--     commenter int not null,
--     ishelpful int,
--     txt varchar(2000)
-- )

-- create table reviews (
--     sid int not null
-- )