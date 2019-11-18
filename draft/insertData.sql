

--  (cid, cnum, sid),

insert into users values (null, 'sophia', 010101, 0),
    (null, 'claire', 0101, 0),
    (null, 'svetha', 10111, 0);
-- (sid, uid, title, genre ('Romance','Fantasy','Horror','Sci-Fi','Historical','Mystery','Humor','Literary', 
--             'Thriller','Suspense','Poetry'), 
--             audience ('General','Young Adult','18+'),
--             warnings ('Violence','Gore','Rape/Sexual Assault','Sexual Content','Racism','Homophobia',
--             'Suicidal Content','Abuse', 'Animal Cruelty', 'Self-Harm', 'Eating Disorder',
--             'Incest','Child Abuse/Pedophilia', 'Death/Dying','Pregnancy/Childbirth',
--             'Miscarriages/Abortion','Mental Illness'),
--              isFin, updated, summary, stars), 
insert into works values (null, 1, 'test work 1', 'Romance, Horror', 'General', 
    'Violence, Death/Dying, Mental Illness', 'Finished', NOW(), 
    'Smth a story', 0), (null, 1, 'test work 2', 'Suspense, Thriller, Poetry', 
    '18+', 'Violence, Pregnancy/Childbirth, Sexual Content', 'Finished', 
    NOW(), 'Story', 0), (null, 1, 'test work 3', 'Fantasy, Thriller, Suspense', 
    'Young Adult', 'Violence, Death/Dying, Sexual Content, Self-Harm, 
    Thriller, Mental Illness', 'Finished', NOW(), 'test storyyyy', 0);

insert into chapters values (null, 1, 1), (null,2, 1),
    (null, 3, 1), (null, 4, 1), (null, 1, 2),(null, 2, 2),
     (null, 1, 3), (null, 2, 3), (null, 3, 3);
 