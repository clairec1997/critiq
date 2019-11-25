from flask import (Flask, render_template, make_response, url_for, request,
                   redirect, flash, session, send_from_directory, jsonify
                   )
import dbi
from werkzeug import secure_filename
import sys,os,random

import lookup
import bleach
import bcrypt
from pathlib import Path

UPLOAD_FOLDER = '/uploaded/'
ALLOWED_EXTENSIONS = {'txt', 'png', 'jpg', 'jpeg', 'gif'}

#CONN = 'sbussey_db'
#CONN = 'ccannatt_db'
#CONN = 'spulavar_db'

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

app.secret_key = 'your secret here'
# replace that with a random key
app.secret_key = ''.join([ random.choice(('ABCDEFGHIJKLMNOPQRSTUVXYZ' +
                                          'abcdefghijklmnopqrstuvxyz' +
                                          '0123456789'))
                           for i in range(20) ])

# This gets us better error messages for certain common request errors
app.config['TRAP_BAD_REQUEST_ERRORS'] = True

@app.route('/', methods=["GET", "POST"])
def index():
    if request.method == "POST":
        term = request.form.get('search_term')
        kind = request.form.get('search_kind')
        return redirect(url_for('worksByTerm', search_kind=kind, search_term=term))    
    else:
        if 'username' in session:
            return redirect( url_for('recommendations'))
        else:
            return render_template('main.html',title='Hello')
        
@app.route('/join/', methods=["POST"])
def join():
    try:
        username = request.form['username']
        passwd1 = request.form['password1']
        passwd2 = request.form['password2']
        if passwd1 != passwd2:
            flash('passwords do not match')
            return redirect( url_for('index'))
        hashed = bcrypt.hashpw(passwd1.encode('utf-8'), bcrypt.gensalt())
        hashed_str = hashed.decode('utf-8')
        print(type(hashed_str))
        print(passwd1, type(passwd1), hashed, hashed_str)

        conn = lookup.getConn(CONN)
        try:
            lookup.insertPass(conn, username, hashed_str)
        except Exception as err: # this is not getting thrown
            flash('That username is taken.')#: {}'.format(repr(err)))
            return redirect(url_for('index'))
        uid = lookup.getUIDFirst(conn)
        # print(uid)
        flash('FYI, you were issued UID {}'.format(uid))
        session['username'] = username
        session['uid'] = uid
        session['logged_in'] = True
        # session['visits'] = 1
        return redirect( url_for('profile', uid=uid) ) #should put username in instead? more readable
    except Exception as err:
        flash('form submission error '+str(err))
        return redirect( url_for('index') )

@app.route('/login/', methods=["POST"])
def login():
    try:
        username = request.form['username']
        passwd = request.form['password']
        conn = lookup.getConn(CONN)
        row = lookup.getLogin(conn, username)
        if row is None:
            # Same response as wrong password,
            # so no information about what went wrong
            flash('login incorrect. Try again or join')
            return redirect( url_for('index'))
        hashed = row['passhash'] 
        print(type(hashed))
        print('hashed: {} {}'.format(hashed,type(hashed)))
        print('passwd: {}'.format(passwd))
        print('hashed.encode: {}'.format(hashed.encode('utf-8')))
        
        hashed2 = bcrypt.hashpw(passwd.encode('utf-8'),hashed.encode('utf-8'))#.encode('utf-8'))
        hashed2_str = hashed2.decode('utf-8')
        print('bcrypt: {}'.format(hashed2))
        print('str(bcrypt): {}'.format(str(hashed)))
        print('bc.decode: {}'.format(hashed2.decode('utf-8')))
        print('equal? {}'.format(hashed==hashed2.decode('utf-8')))
        if hashed2_str == hashed:
            flash('successfully logged in as '+username)
            session['username'] = username
            session['uid'] = row['uid']
            print(session['uid'])
            session['logged_in'] = True
            session['visits'] = 1
            return redirect( url_for('profile', uid=session['uid']) )
        else:
            flash('login incorrect. Try again or join')
            return redirect( url_for('index'))
    except Exception as err:
        flash('form submission error: '+str(err))
        return redirect( url_for('index') )


@app.route('/profile/<uid>') #allow everyone to access all profiles, but only if logged in can change data
def profile(uid):
    try:
        # don't trust the URL; it's only there for decoration
        if 'username' in session:
            username = session['username']
            # uid = session['uid']
            # session['visits'] = 1+int(session['visits'])
            return render_template('profile.html',
                                   page_title="{}'s Profile".format(username),
                                   username=username
                                   )

        else:
            flash('you are not logged in. Please login or join')
            return redirect( url_for('index') )
    except Exception as err:
        flash('some kind of error '+str(err))
        return redirect( url_for('index') )

@app.route('/manage/')
def manage():
    try:
        if 'uid' in session:
            uid = session['uid']
            conn = lookup.getConn(CONN)
            stories = lookup.getStories(conn, uid)
            return render_template('manage.html', title="Hello", stories=stories)
        else: 
            flash("Please log in or join")
            return redirect(url_for('index'))
    except Exception as err:
        flash('error: '+str(err))
        return redirect( url_for('index') )
    
@app.route('/add/', methods=["GET", "POST"])
def add():
    try:
        if request.method == "GET":
            if 'uid' in session:
                uid = session['uid']
                conn = lookup.getConn(CONN)
                genre = lookup.getTags(conn, 'genre')
                warnings = lookup.getTags(conn, 'warnings')
                audience = lookup.getTags(conn, 'audience')
                isFin = lookup.getTags(conn, 'isFin')
                return render_template('add.html',title='Add Story', warnings=warnings, 
                                    genre=genre, audience=audience, isFin=isFin)
            else:
                flash("Please log in or join")
                return redirect(url_for('index'))
        if request.method == "POST":
            uid = session['uid']
            title = request.form['title']
            summary = request.form['summary']
            genre = request.form.getlist('genre')
            audience = request.form['audience']
            warnings = request.form.getlist('warnings')
            status = request.form['isFin']
        
            conn = lookup.getConn(CONN)
            sid = lookup.addStory(conn, uid, title, summary)
            lookup.addTags(conn, sid, genre, warnings, audience, status)

            return redirect(url_for('update', sid=sid))
    except Exception as err:
        flash('error: '+str(err))
        return redirect( url_for('index') )

@app.route('/update/<int:sid>/', defaults={'cnum':1}, methods=["GET","POST"])
@app.route('/update/<int:sid>/<int:cnum>/', methods=["GET","POST"])
def update(sid, cnum):
    try:
        if 'uid' in session:
            uid = session['uid']

            if request.method=="GET":
                conn = lookup.getConn(CONN)
                #filename = lookup.getChapter(uid, sid, cnum)['filename']
                story = None
                #if the file exists, get the file

                return render_template('write.html', title='Update Story',
                                sid=sid, cnum=cnum, story=story)

            if request.method=="POST":
                sometext = request.form['write']
                somehtml = bleach.clean(sometext, #allowed tags, attributes, and styles
                    tags=['b','blockquote','i','em','strong','p','ul','li','ol','span'], 
                    attributes=['style'],
                    styles=['text-decoration', 'text-align'])
                
                #save the file

                return render_template('write.html')
        else: 
            flash('''You are not authorized to edit this work. 
                    Please log in with the account associated with this work''')
            return redirect(url_for('index'))
    except Exception as err:
        flash('some kind of error '+str(err))
        return redirect( url_for('index') )

@app.route('/read/<int:sid>', defaults={'cnum': 1})
@app.route('/read/<int:sid>/<int:cnum>/')
def read(sid, cnum): 
    conn = lookup.getConn(CONN)
    story = lookup.getChapter(conn, sid, cnum)
    author = lookup.getAuthor(conn, sid)
    print(author)
    if 'username' not in session:
        return redirect(url_for('index'))
    if session['username'] == author['username']:
        return render_template('read.html', 
                            title="Hello", 
                            story=story,
                            author=author['username'],
                            cnum=cnum,
                            sid=sid,
                            update=True)
    else:
        return render_template('read.html', 
                            title="Hello", 
                            story=story,
                            author=author['username'],
                            cnum=cnum,
                            sid=sid,
                            update=False)

@app.route('/bookmarks/')
def bookmarks():
    return render_template('main.html',title='Hello')

@app.route('/recommendations/')
def recommendations():
    recommendation = [
                        {'title': '', 
                            'sid': 0,
                            'summary': '',
                            'tags': [],
                            'rating': 0}
                       ]    
    return render_template('recommendations.html',
                            recommendations=recommendation)

@app.route('/uploaded/<filename>')
def uploaded(filename):
    pass

@app.route('/addComment/', methods=["POST"])
def addComment():
    conn = lookup.getConn(CONN)
    commentText = request.form.get("commentText")
    print(commentText)
    cid = request.form.get('cid')
    cnum = request.form.get('cnum')
    sid = request.form.get('sid')
    if 'uid' in session:
        uid = session['uid']
        lookup.addComment(conn, commentText, uid, cid)
        flash('Comment submitted!')
        return redirect( url_for('read', cnum=cnum, sid=sid))

@app.route('/logout/')
def logout():
    try:
        if 'username' in session:
            username = session['username']
            session.pop('username')
            session.pop('uid')
            session.pop('logged_in')
            flash('You are logged out')
            return redirect(url_for('index'))
        else:
            flash('you are not logged in. Please login or join')
            return redirect( url_for('index') )
    except Exception as err:
        flash('some kind of error '+str(err))
        return redirect( url_for('index') )

@app.route('/search/<search_kind>', defaults={'search_term': ""})
@app.route('/search/<search_kind>/<search_term>', methods=["GET"])
def worksByTerm(search_kind, search_term):
     term = search_term
     kind = search_kind
     conn = lookup.getConn(CONN)
    
     #search for works like the search term
     #if no search term, defaults to all movies 
     
     res = lookup.searchWorks(conn, term) if (kind=="work") else lookup.searchAuthors(conn, term)
     
    
     if not res:
         flash("No {} found including: {} :( ".format(kind, term))

     return render_template('search.html', kind=kind, res=res)

if __name__ == '__main__':

    if len(sys.argv) > 1:
        # arg, if any, is the desired port number
        port = int(sys.argv[1])
        assert(port>1024)
    else:
        port = os.getuid()
    app.debug = True
    app.run('0.0.0.0',port)
