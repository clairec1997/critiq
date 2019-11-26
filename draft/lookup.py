import dbi

DSN = None

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

def getLogin(conn, username):
    '''gets hashed password to check for login'''
    curs = dbi.dictCursor(conn)
    curs.execute('''SELECT uid,passhash
                      FROM users
                      WHERE username = %s''',
                     [username])
    return curs.fetchone()

def searchWorks(conn, kind, searchterm):
    '''finds works with title including searchterm or tag = searchterm'''
    curs = dbi.dictCursor(conn)
    if kind == "work":
        curs.execute(''' select * from 
                        (select sid, uid, title, updated, 
                        summary, stars, count(sid) from
                                (select * from works where title like %s) 
                        as q1 left outer join chapters using(sid) group by sid) 
                        as q2 left outer join 
                        (select uid, username from users) as q3 using(uid)''', 
                        ['%' + searchterm + '%'])
    else:
        curs.execute('''select * from (select sid, uid, title, updated, 
                        summary, stars, count(sid) from 
                        (select tid from tags where tname = %s) as q1 
                        left outer join (select tid, sid from taglink) as q2
                        using(tid) 
                        left outer join works using(sid)
                        left outer join chapters using(sid) group by sid) as q3
                        left outer join (select uid, username from users) as q4
                        using(uid)''', [searchterm])
        
    return curs.fetchall()

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

def getChapter(conn, sid, cnum):
    '''returns a chapter of a story'''
    curs = dbi.dictCursor(conn)
    curs.execute('''select works.summary as summary, 
                    works.title as title, 
                    chapters.filename as filename,
                    chapters.cid as cid 
                from works inner join chapters using (sid)
                where sid=%s and cnum=%s
                ''', [sid, cnum])
    return curs.fetchone()

def setChapter(conn, sid, cnum, filename):
    curs = dbi.cursor(conn)
    curs.execute('''insert into chapters(sid, cnum, filename)
                values (%s, %s, %s)''',
                [sid, cnum, filename])

def getAuthor(conn, sid):
    curs = dbi.dictCursor(conn)
    curs.execute('''select username from works inner join users using (uid)
                    where sid=%s''', [sid])
    return curs.fetchone()

def getAuthorId(conn, sid):
    curs = dbi.cursor(conn)
    curs.execute('''select uid from works inner join users using (uid)
                    where sid=%s''', [sid])
    return curs.fetchone()

def getTags(conn, type):
    curs=dbi.dictCursor(conn)
    curs.execute('select * from tags where ttype=%s',[type])
    return curs.fetchall()

def addStory(conn, uid, title, summary):
    curs = dbi.cursor(conn)
    curs.execute('''insert into works(uid, title, summary)
                    values (%s, %s, %s)''', 
                    [uid, title, summary])
    curs.execute('select last_insert_id()')
    return curs.fetchone()

def getTagsAjax(conn):
    curs = dbi.dictCursor(conn)
    curs.execute('''select tname from tags''')
    return curs.fetchall()
    
def addTags(conn, sid, genre, warnings, audience, isFin):
    curs = dbi.cursor(conn)
    tagslist = [*genre, *warnings, *audience, *isFin]
    for i in tagslist:
        curs.execute('''insert into taglink(tid, sid)
        values (%s, %s)''', [i, sid])

def getStoryTags(conn, sid):
    curs = dbi.cursor(conn)
    pass

def addComment(conn, commentText, uid, cid,):
    curs = dbi.cursor(conn)
    curs.execute('''insert into reviews(commenter, reviewText) values(%s, %s)''', [uid, commentText])
    curs.execute('select LAST_INSERT_ID()')
    row = curs.fetchone()
    # print(row)
    rid = row[0]
    curs.execute('''insert into reviewCredits values(%s, %s)''', [rid, cid])