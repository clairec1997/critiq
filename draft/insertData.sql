--  (cid, cnum, sid),
insert into users values (null, 'sophia', 010101, 0),
    (null, 'claire', 0101, 0),
    (null, 'svetha', 10111, 0);
 --(sid, uid, title, updated, summary, stars), 

insert into works values (null, 1, 'test work 1', NOW(), 'Smth a story', 0), 
    (null, 1, 'test work 2', NOW(), 'Story', 0),
    (null, 1, 'test work 3', NOW(), 'test storyyyy', 0),
    (null, 2, 'test work 2.5', NOW(), 'Story', 0),
    (null, 3, 'test work 2.5', NOW(), 'Story', 0);

-- note that the files will be .html not .txt 

insert into chapters values (null, 1, 1, '1_1.txt'), (null,2, 1,'1_2.txt'),
    (null, 3, 1, '1_3.txt'), (null, 4, 1, '1_4.txt'), (null, 1, 2, '2_1.txt'),(null, 2, 2, '2_2.txt'),
    (null, 1, 3, '3_1.txt'), (null, 2, 3, '3_2.txt'), (null, 3, 3, '3_3.txt');

-- genre ('Romance','Fantasy','Horror','Sci-Fi','Historical','Mystery','Humor','Literary', 
--             'Thriller','Suspense','Poetry'), 
-- audience ('General','Young Adult','18+'),
-- warnings ('Violence','Gore','Rape/Sexual Assault','Sexual Content','Racism','Homophobia',
--             'Suicidal Content','Abuse', 'Animal Cruelty', 'Self-Harm', 'Eating Disorder',
--             'Incest','Child Abuse/Pedophilia', 'Death/Dying','Pregnancy/Childbirth',
--             'Miscarriages/Abortion','Mental Illness'),
-- isFin, 

insert into tags values (null, 'genre', 'Romance'), (null, 'genre', 'Fantasy'), 
    (null, 'genre', 'Horror'), (null, 'genre', 'Sci-Fi'), (null, 'genre', 'Historical'),
    (null, 'genre', 'Mystery'), (null, 'genre', 'Humor'), (null, 'genre', 'Literary'),
    (null, 'genre', 'Thriller'), (null, 'genre', 'Suspense'), (null, 'genre', 'Poetry');

insert into tags values (null, 'audience', 'General'), (null, 'audience', 'Young Adult'),
    (null, 'audience', '18+');

insert into tags values (null, 'warnings', 'Violence'), (null, 'warnings', 'Gore'), 
    (null, 'warnings', 'Rape or Sexual Assault'), (null, 'warnings', 'Sexual Content'),  
    (null, 'warnings', 'Racism'), (null, 'warnings', 'Homophobia'), 
    (null, 'warnings', 'Suicidal Content'), (null, 'warnings', 'Abuse'), 
    (null, 'warnings', 'Animal Cruelty'), (null, 'warnings', 'Self-Harm'),
    (null, 'warnings', 'Eating Disorder'), (null, 'warnings', 'Incest'),
    (null, 'warnings', 'Child Abuse or Pedophilia'), (null, 'warnings', 'Death or Dying'),
    (null, 'warnings', 'Pregnancy or Childbirth'),(null, 'warnings', 'Miscarriages orAbortion'),
    (null, 'warnings', 'Mental Illness');

insert into tags values (null, 'isFin', 'Finished'), (null, 'isFin', 'Work in Progress');

-- genre ids from 1 to 11, audience from 12 to 14, warnings from 15 to 31, isFin either 32 or 33
insert into taglink values (1, 1), (1, 2), (8, 1), (13, 1), (18, 1), (28, 1), (17, 1), (32, 1),
    (33, 2), (14, 2), (7, 2), (11, 2), (15, 2), (17, 2), (19,2),
    (33, 3), (19, 3), (18, 3), (12, 3), (25, 3), (10, 3);