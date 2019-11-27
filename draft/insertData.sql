

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

