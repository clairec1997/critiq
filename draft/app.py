from flask import (Flask, render_template, make_response, url_for, request,
                   redirect, flash, session, send_from_directory, jsonify
                   )
import dbi
from werkzeug import secure_filename
import sys,os,random

import lookup
import bleach
import bcrypt

UPLOAD_FOLDER = '/uploaded/'
ALLOWED_EXTENSIONS = {'txt', 'png', 'jpg', 'jpeg', 'gif'}

# CONN = 'sbussey_db'
# CONN = 'ccannatt_db'
CONN = 'spulavar_db'

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
        kind = request.form.get('search_kind')
        term = (request.form.get('select_tag') if kind == "tag" 
                else request.form.get('search_term'))

        return redirect(url_for('worksByTerm', search_kind=kind, search_term=term))    
    else:
        if 'username' in session:
            return redirect( url_for('recommendations'))
        else:
            return render_template('main.html',title='Hello')

@app.route('/getTags/', methods=["POST"])
def getTags():
    conn = lookup.getConn(CONN)
    tags = lookup.getTagsAjax(conn)

    return jsonify( {'error': False, 'tags': tags} )

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
        
        hashed2 = bcrypt.hashpw(passwd.encode('utf-8'),hashed.encode('utf-8'))#.encode('utf-8'))
        hashed2_str = hashed2.decode('utf-8')
        
        if hashed2_str == hashed:
            flash('successfully logged in as '+username)
            session['username'] = username
            session['uid'] = row['uid']
            print(session['uid'])
            session['logged_in'] = True
            # session['visits'] = 1
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
        conn = lookup.getConn(CONN)
        authorid = lookup.getAuthorId(conn,sid)[0]
        print(authorid, session['uid'])

        if 'uid' in session and session['uid']==authorid:
            if request.method=="GET":
                chapter = lookup.getChapter(conn, sid, cnum)
                story = ""
                if chapter:
                    infile = open(chapter['filename'], 'r')
                    story = infile.read()
                    infile.close()
                allch = lookup.getChapters(conn, sid)
                return render_template('write.html', title='Update Story',
                                sid=sid, cnum=cnum, story=story, allch=allch)

            if request.method=="POST":
                ctitle = request.form['title']
                sometext = request.form['write']
                somehtml = bleach.clean(sometext, #allowed tags, attributes, and styles
                    tags=['b','blockquote','i','em','strong','p','ul','br','li','ol','span'], 
                    attributes=['style'],
                    styles=['text-decoration', 'text-align'])

                dirname = os.path.dirname(__file__)
                relative = 'uploaded/'+'sid'+str(sid)+'cnum'+str(cnum)+'.html'
                filename = os.path.join(dirname, relative)

                outfile = open(filename, 'w')
                outfile.write(somehtml)
                outfile.close()
                
                chapter = lookup.getChapter(conn,sid,cnum)

                if not chapter:
                    lookup.setChapter(conn, sid, cnum, filename)

                return redirect(url_for('read', sid=sid, cnum=cnum))
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
    chapter = lookup.getChapter(conn, sid, cnum)

    infile = open(chapter['filename'], 'r')
    story = infile.read()
    infile.close()

    allch = lookup.getChapters(conn,sid)
    
    work = lookup.getStory(conn, sid)

    if 'username' not in session:
        return redirect(url_for('index'))
    if session['username'] == work['username']:
        return render_template('read.html', 
                            title="Hello", 
                            story=story,
                            author=work['username'],
                            cnum=cnum,
                            sid=sid,
                            update=True,
                            allch=allch)
    else:
        return render_template('read.html', 
                            title="Hello", 
                            story=story,
                            author=author['username'],
                            cnum=cnum,
                            sid=sid,
                            update=False,
                            allch=allch)

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

@app.route('/addComment/', methods=["POST"])
def addComment():
    conn = lookup.getConn(CONN)
    commentText = request.form.get("commentText")
    # print(commentText)
    cid = request.form.get('cid')
    cnum = request.form.get('cnum')
    sid = request.form.get('sid')
    if 'uid' in session:
        uid = session['uid']
        lookup.addComment(conn, commentText, uid, cid)
        flash('Comment submitted!')
        return redirect( url_for('read', cnum=cnum, sid=sid))

@app.route('/addCommentAjax/', methods=["POST"])
def addCommentAjax():
    conn = lookup.getConn(CONN)
    commentText = request.form.get("commentText")
    print(commentText)
    cid = request.form.get('cid')
    cnum = request.form.get('cnum')
    sid = request.form.get('sid')
    try:
        if 'uid' in session:
            uid = session['uid']
            lookup.addComment(conn, commentText, uid, cid)
            flash('Comment submitted!')
            return jsonify(error=False,
                            commentText=commentText,
                            uid=uid,
                            cid=cid
                            )
        else:
            flash("Log in before commenting.")
            return redirect(url_for('index'))
    except Exception as err:
        print(err)
        return jsonify( {'error': True, 'err': str(err) } )

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
    
    res = (lookup.searchAuthors(conn, term) if kind == "author" 
    else lookup.searchWorks(conn, kind, term))

    resKind = "Authors" if kind == "author" else "Works"
    nm = "Tag" if (kind == "tag") else "Term"
    if not res:
        flash("No {} Found Including {}: {} :( ".format(resKind, nm, term))
    #return "<p>{}</p>".format(res)
    return render_template('search.html', resKind=resKind, term=term, res=res)

if __name__ == '__main__':

    if len(sys.argv) > 1:
        # arg, if any, is the desired port number
        port = int(sys.argv[1])
        assert(port>1024)
    else:
        port = os.getuid()
    app.debug = True
    app.run('0.0.0.0',port)
