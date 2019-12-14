import dbi
from datetime import *

DSN = None

# We need to add transaction locking eventually

def getConn(db):
    '''returns a database connection to the given database'''
    global DSN
    if DSN is None:
        DSN = dbi.read_cnf()
    conn = dbi.connect(DSN)
    conn.select_db(db)
    return conn

def insertPass(conn, username, hashed_str):
    '''inserts user into database when they make an account'''
    curs = dbi.cursor(conn)
    curs.execute('''INSERT INTO users(uid,username,passhash)
                            VALUES(null,%s,%s)''',
                         [username, hashed_str])

def getUIDFirst(conn):
    '''gets last inserted uid'''
    curs = dbi.cursor(conn)
    curs.execute('select LAST_INSERT_ID()')
    row = curs.fetchone()
    print(row)
    uid = row[0]
    return uid

def getUID(conn, username):
    curs = dbi.cursor(conn)
    curs.execute('''select uid from users where username=%s''', [username])
    return curs.fetchone()

def getLogin(conn, username):
    '''gets hashed password to check for login'''
    curs = dbi.dictCursor(conn)
    curs.execute('''SELECT uid,passhash
                      FROM users
                      WHERE username = %s''',
                     [username])
    return curs.fetchone()

def updateProfile(conn, uid, dob):
    curs = dbi.dictCursor(conn)
    curs.execute('''update users
                    set dob=%s
                    where uid=%s''', [dob, uid])

def searchWorks(conn, kind, searchterm, filters):
    '''finds works with title including searchterm or tag = searchterm 
        takes chosen filters into acct'''
    curs = dbi.dictCursor(conn)

    dofilter = ("where sid not in (select sid from taglink where tid in %s)" 
                if filters else "")

    searchParam =  (['%' + searchterm + '%'] if kind == "work" 
                        else [searchterm])     

    params = ([searchParam, filters] if filters else [searchParam])

    if kind == "work":
        curs.execute('''select * from (select sid, uid, title, updated, 
                    summary, stars, wip, count(sid) from
                    (select * from works where title like %s) as q1 
                    left outer join chapters using(sid) group by sid) as q2 
                    left outer join (select uid, username from users) as q3 
                    using(uid)''' + dofilter, 
                params)
    else:
        curs.execute('''select * from (select sid, uid, title, updated, 
                        summary, stars, wip, count(sid) from 
                        (select tid from tags where tname = %s) as q1 
                        left outer join taglink using(tid) 
                        left outer join works using(sid)
                        left outer join chapters using(sid) group by sid) as q3
                        left outer join (select uid, username from users) as q4
                        using(uid)''' + dofilter, 
                        params)
            
    return curs.fetchall()


# def searchWorks(conn, kind, searchterm, filters=None):
#     '''finds works with title including searchterm or tag = searchterm'''
#     curs = dbi.dictCursor(conn)
    
#     curs.execute('''select * from 
#                     (select sid from taglink where tid not in %s group by sid) as q1
#                     left outer join works using (sid)
#                     where title like %s''', 
#                     [filters, '%' + searchterm + '%'])
#     else:
#         curs.execute('''select * from 
#                     (select sid, uid, title, updated, 
#                     summary, stars, count(sid) from
#                     (select * from works where title like %s) 
#                     as q1 left outer join chapters using(sid) group by sid) 
#                     as q2 left outer join 
#                     (select uid, username from users) as q3 using(uid)''', 
#                     ['%' + searchterm + '%'])
#         curs.execute('''select * from (select sid, uid, title, updated, 
#                         summary, stars, count(sid) from 
#                         (select tid from tags where tname = %s) as q1 
#                         left outer join (select tid, sid from taglink) as q2
#                         using(tid) 
#                         left outer join works using(sid)
#                         left outer join chapters using(sid) group by sid) as q3
#                         left outer join (select uid, username from users) as q4
#                         using(uid)''', [searchterm])
        
#     return curs.fetchall()


def searchAuthors(conn, author):
    '''finds authorsmathing name'''
    curs = dbi.dictCursor(conn)
    curs.execute('''select uid, username from users where 
                 username like %s''', 
                 ['%' + author + '%'])
    return curs.fetchall()

def getStories(conn, uid):
    '''Returns all works associated with an account'''
    curs=dbi.dictCursor(conn)
    curs.execute('''select * from works
                where uid = %s''', [uid])
    return curs.fetchall()

def getStory(conn, sid):
    '''Returns a work with given sid'''
    curs=dbi.dictCursor(conn)
    curs.execute('''select * from works inner join users
                    on users.uid=works.uid where sid=%s''', [sid])
    return curs.fetchone()

def getChapter(conn, sid, cnum):
    '''returns a chapter of a story'''
    curs = dbi.dictCursor(conn)
    curs.execute('''select works.title as title,
                    works.wip as wip,
                    works.summary as summary, 
                    works.wip as wip,
                    works.title as title, 
                    chapters.filename as filename,
                    chapters.cid as cid 
                    from works inner join chapters using (sid)
                    where sid=%s and cnum=%s
                    ''', [sid, cnum])
    return curs.fetchone()

def setChapter(conn, sid, cnum, filename):
    '''Given sid, cnum, filename, sets the chapter'''
    curs = dbi.cursor(conn)
    curs.execute('''insert into chapters(sid, cnum, filename)
                values (%s, %s, %s)''',
                [sid, cnum, filename])

def getAuthor(conn, sid):
    '''given an sid, gets the username'''
    curs = dbi.dictCursor(conn)
    curs.execute('''select username from works inner join users using (uid)
                    where sid=%s''', [sid])
    return curs.fetchone()

def getAuthorId(conn, sid):
    '''given an sid, gets the uid'''
    curs = dbi.cursor(conn)
    curs.execute('''select uid from works inner join users using (uid)
                    where sid=%s''', [sid])
    return curs.fetchone()

def getTags(conn, type):
    '''given a tag type, gets tags of that type'''
    curs=dbi.dictCursor(conn)
    curs.execute('select * from tags where ttype=%s',[type])
    return curs.fetchall()

def addStory(conn, uid, title, summary, isFin):
    '''given a uid, title, summary, adds the story'''
    curs = dbi.cursor(conn)
    curs.execute('''insert into works(uid, title, summary, wip)
                    values (%s, %s, %s, %s)''', 
                    [uid, title, summary, isFin])
    curs.execute('select last_insert_id()')
    return curs.fetchone()

# def getTagsAjax(conn):
#     '''given a conn, gets all tag names'''
#     curs = dbi.dictCursor(conn)
#     curs.execute('''select tname from tags''')
#     return curs.fetchall()
    
def addTags(conn, sid, genre, warnings, audience, isFin):
    '''adds tags to a story'''
    curs = dbi.cursor(conn)
    tagslist = [*genre, *warnings, *audience, *isFin]
    for i in tagslist:
        curs.execute('''insert into taglink(tid, sid)
        values (%s, %s)''', [i, sid])

def getStoryTags(conn, sid):
    '''gets a story's tags'''
    curs = dbi.cursor(conn)
    pass

def addComment(conn, commentText, uid, cid):
    '''adds a comment to a chapter'''
    curs = dbi.cursor(conn)
    # print(uid)
    # print(cid)
    curs.execute('''insert into reviews(commenter, reviewText) values(%s, %s)''', [uid, commentText])
    curs.execute('select LAST_INSERT_ID()')
    row = curs.fetchone()
    rid = row[0]
    curs.execute('''insert into reviewCredits values(%s, %s)''', [rid, cid])

def getChapters(conn, sid):
    '''given sid, gets all chapters'''
    curs = dbi.dictCursor(conn)
    curs.execute('''select * from chapters 
                where sid=%s
                order by cnum asc''',[sid])
    return curs.fetchall()

def getPrefs(conn, uid, wantsWarnings):
    '''given uid, retrieves users prefs or warning'''
    curs = dbi.dictCursor(conn)
    curs.execute('''select tid, tname from 
                prefs left outer join tags 
                using(tid) where uid=%s and isWarning=%s''', 
                [uid, wantsWarnings])
    return curs.fetchall()
    
def updatePrefs(conn, uid, prefs):
    curs = dbi.dictCursor(conn)
    curs.execute('''delete from prefs where uid=%s''',
                [uid])
    for pref in prefs:
        curs.execute('''insert into prefs values(%s, %s)''',
                    [uid, pref])
    # return getPrefs(conn, uid)

def getRecs(conn, uid):
    curs = dbi.dictCursor(conn)
    tags = tuple([tag['tid'] for tag in getPrefs(conn, uid, False)])
    print (tags)
    curs.execute('''select sid, uid, title, updated, summary, 
                stars, count(sid), username from 
                    (select sid from taglink where tid in %s group by sid) as q1 
                left outer join works using(sid) 
                left outer join 
                    (select uid, username from users) as q2 
                using (uid) 
                left outer join chapters using(sid) group by sid
                order by stars desc''', 
                [tags])
                
    res = curs.fetchall()
    print (res)
    return res

def getComments(conn, uid, cid):
    curs = dbi.dictCursor(conn)
    curs.execute('''select reviewText from reviews inner join reviewCredits using(rid)
                    where commenter=%s and cid=%s
                    ''', [uid, cid])
    return curs.fetchall()

def calcAvgRating(conn, sid):
    curs = dbi.dictCursor(conn)
    curs.execute('''select avg(rating) from ratings
                        inner join works using(sid)
                        where sid=%s''', [sid])
    return curs.fetchone()

def updateAvgRating(conn, sid, avg):
    curs = dbi.dictCursor(conn)
    curs.execute('''update works set avgRating=%s 
                    where sid=%s''', [avg, sid])

def addRating(conn, uid, sid, rating):
    curs = dbi.dictCursor(conn)
    curs.execute('''select * from ratings where sid=%s and uid=%s''', [sid, uid])
    if curs.fetchone() is not None:
        curs.execute('''update ratings set rating=%s 
                    where sid=%s and uid=%s''', [rating, sid, uid])
    else:
        curs.execute('''insert into ratings(uid, sid, rating) 
                        values(%s, %s, %s)''', [uid, sid, rating])

def getNumChaps(conn, sid):
    curs = dbi.dictCursor(conn)
    curs.execute('''select count(cid) from chapters where sid=%s''', [sid])
    return curs.fetchone()

def addToHistory(conn, uid, sid):
    now = datetime.now()
    #frmat = now.strftime('%Y-%m-%d %H:%M:%S')
    curs = dbi.dictCursor(conn)
    curs.execute('''insert into history values(%s, %s, %s) 
                    on duplicate key update visited = %s''',
                    [uid, sid, now, now])
def getHistory(conn, uid):
    curs = dbi.dictCursor(conn)
    curs.execute('''select sid, uid, title, updated, summary, 
                    stars, count(sid), username, visited from  
                    (select sid, visited from history where uid = %s) as q1
                    left outer join works using(sid)
                    left outer join 
                    (select uid, username from users) as q2 
                    using(uid) 
                    left outer join chapters using(sid) group by sid
                    order by visited''', 
                    [uid])
    return curs.fetchall()
    
def getAllComments(conn, cid):
    curs = dbi.dictCursor(conn)
    curs.execute('''select reviews.reviewText as text, users.username as author, reviewCredits.cid as cid
                        from reviews inner join reviewCredits using (rid)
                        inner join users on reviews.commenter=users.uid where reviewCredits.cid=%s''', [cid])
    return curs.fetchall()

def getWarnings(conn, uid):
    '''given uid, retrieves users prefs'''
    curs = dbi.dictCursor(conn)
    curs.execute('''select tid, tname from 
                prefs left outer join tags 
                using(tid) where uid=%s''', 
                [uid])
    return curs.fetchall()

def getTitle(conn, sid):
    '''retrieves story title'''
    curs = dbi.dictCursor(conn)
    curs.execute('''select title from works where sid=%s''', [sid])
    return curs.fetchone()