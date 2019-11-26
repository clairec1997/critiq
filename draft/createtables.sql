drop table if exists reviewCredits;
drop table if exists reviews;
drop table if exists taglink;
drop table if exists tags;
drop table if exists chapters;
drop table if exists works;
drop table if exists users;

create table users (
    uid int not null auto_increment primary key,
    username varchar(30), 
    passhash char(60),
    unique(username),
    index(username),
    commentscore DECIMAL
);

create table works (
    sid int not null auto_increment primary key,
    uid int not null,
    title VARCHAR(200),
    updated date,
    summary varchar(2000),
    stars float,
    index(uid),
    foreign key (uid) references users(uid)
        on UPDATE cascade
        on delete cascade
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

ENGINE = InnoDB;

create table tags (
    tid int not null auto_increment primary key,
    ttype varchar(20) not null,
    tname varchar(50) not null unique
)

ENGINE = InnoDB;

create table taglink (
    tid int not null,
    sid int not null,

    foreign key(sid) references works(sid)
        on update cascade
        on delete cascade,
    foreign key(tid) references tags(tid)
        on update cascade
        on delete cascade
)

ENGINE = InnoDB;

create table reviews (
    rid int not null auto_increment primary key,
    commenter int not null,
    ishelpful int,
    reviewText varchar(2000),
    foreign key(commenter) references users(uid)
)

ENGINE = InnoDB;

create table reviewCredits ( 
    rid int not null,
    cid int not null,

    primary key(rid, cid),

    foreign key(rid) references reviews(rid)
        on update cascade
        on delete cascade,
    foreign key(cid) references chapters(cid)
        on update cascade
        on delete cascade
)

ENGINE = InnoDB;
