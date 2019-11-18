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

def searchWorks(conn, searchterm):
    '''finds works with title including searchterm'''
    curs = dbi.dictCursor(conn)
    curs.execute(''' select * from (select sid, uid, title, 
                 genre, audience, warnings, isFin, updated,                                                                                                            summary, stars, count(sid) from                                                                                                                       (select * from works where title like %s)                                                                                                             as q1 left outer join chapters using(sid)                                                                                                             group by sid) as q2 left outer join 
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
