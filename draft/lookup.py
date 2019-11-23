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
    curs = dbi.cursor(conn)
    curs.execute('''INSERT INTO userpass(uid,username,hashed)
                            VALUES(null,%s,%s)''',
                         [username, hashed_str])

def getUIDFirst(conn):
    curs = dbi.cursor(conn)
    curs.execute('select last_insert_id()')
    row = curs.fetchone()
    uid = row[0]
    return uid

def getLogin(conn, username):
    curs = dbi.dictCursor(conn)
    curs.execute('''SELECT uid,hashed
                      FROM userpass
                      WHERE username = %s''',
                     [username])
    return curs.fetchone()

def searchWorks(conn, searchterm):
    '''finds works with title including searchterm'''
    curs = dbi.dictCursor(conn)
    curs.execute(''' select * from 
                        (select sid, uid, title, updated, 
                        summary, stars, count(sid) from
                                (select * from works where title like %s) 
                        as q1 left outer join chapters using(sid) group by sid) 
                        as q2 left outer join 
                 (select uid, username from users) as q3 using(uid)''', 
                 ['%' + searchterm + '%'])
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
    curs.execute('''select * from users 
                inner join credit on (users.uid = credit.uid) 
                inner join works on (credit.sid = credit.uid) 
                where uid = %s''', [uid])
    return curs.fetchall()

def getTags(conn, type):
    curs=dbi.dictCursor(conn)
    curs.execute('select * from tags where ttype=%s',[type])
    return curs.fetchall()