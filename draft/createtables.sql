drop table if exists credit;
drop table if exists chapters;
drop table if exists works;
drop table if exists users;
drop table if exists comments;
drop table if exists reviews;


create table users (
    uid int not null auto_increment primary key,
    username varchar(30), 
    passhash BINARY(64),
    commentscore float
)

ENGINE = InnoDB;

create table works (
    sid int not null auto_increment,
    uid int not NULL,
    title VARCHAR(200),
    genre set ('Romance','Fantasy','Horror','Sci-Fi','Historical','Mystery','Humor','Literary', 
            'Thriller','Suspense','Poetry'),
    audience set ('General','Young Adult','18+'),
    warnings set ('Violence','Gore','Rape/Sexual Assault','Sexual Content','Racism','Homophobia',
            'Suicidal Content','Abuse', 'Animal Cruelty', 'Self-Harm', 'Eating Disorder',
            'Incest','Child Abuse/Pedophilia', 'Death/Dying','Pregnancy/Childbirth',
            'Miscarriages/Abortion','Mental Illness'),
    isFin enum ('Finished','Work in Progress'),
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
    filename varchar(50)

    PRIMARY KEY (cid),
    index(sid),
    foreign key (sid) references works(sid)
        on update cascade
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