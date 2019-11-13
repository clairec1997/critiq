drop table if exists works;
drop table if exists users;


create table users {
    int uid not null auto_increment primary key,
    varchar username, 
    BINARY(64) passhash,
    float commentscore
}

ENGINE = InnoDB;

create table works {
    int sid not null auto_increment,
    int uid not NULL primary key,
    set genre ('Romance','Fantasy','Horror','Sci-Fi','Historical','Mystery','Humor','Literary', 
            'Thriller','Suspense','Poetry'),
    set audience('General','Young Adult','18+'),
    set warnings('Violence','Gore','Rape/Sexual Assault','Sexual Content','Racism','Homophobia',
            'Suicidal Content','Abuse', 'Animal Cruelty', 'Self-Harm', 'Eating Disorder',
            'Incest','Child Abuse/Pedophilia', 'Death/Dying','Pregnancy/Childbirth',
            'Miscarriages/Abortion','Mental Illness'),

    index(uid)
    foreign key (uid) references users(uid)
        on UPDATE CASCADE
        on delete cascade
}

ENGINE = InnoDB;

create table chapters {
    int cnum
    int sid not NULL    

    index(sid)
    foreign key (sid) references works(sid)
        on update cascade
        on delete cascade

    Primary key (cnum, sid)
}

