from flask import (Flask, render_template, make_response, url_for, request,
                   redirect, flash, session, send_from_directory, jsonify
                   )
import dbi
from werkzeug import secure_filename
import sys,os,random
from threading import Thread, Lock

import lookup
import bleach
import bcrypt

UPLOAD_FOLDER = '/uploaded/'
ALLOWED_EXTENSIONS = {'txt', 'png', 'jpg', 'jpeg', 'gif'}

CONN = 'critiq_db'
# CONN = 'ccannatt_db'

lock = Lock()

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
        print ("term", term)

        return redirect(url_for('worksByTerm', search_kind=kind, search_term=term))    
    else:
        if 'username' in session:
            return redirect( url_for('recommendations'))
        else:
            return render_template('main.html',title='Hello')

@app.route('/getTags/', methods=["POST"])
def getTags():
    conn = lookup.getConn(CONN)
    tags = lookup.getTags(conn, 'genre')

    return jsonify( {'tags': tags} )

@app.route('/join/', methods=["POST"])
def join():
    try:
        username = request.form['username']
        passwd1 = request.form['password1']
        passwd2 = request.form['password2']
        if passwd1 != passwd2:
            flash('Passwords do not match')
            return redirect( url_for('index'))
        if len(passwd1) < 12:
            flash('Passwords must be at least 12 characters long')
            return redirect( url_for('index'))
        hashed = bcrypt.hashpw(passwd1.encode('utf-8'), bcrypt.gensalt())
        hashed_str = hashed.decode('utf-8')

        conn = lookup.getConn(CONN)
        lock.acquire()
        try:
            lookup.insertPass(conn, username, hashed_str)
        except Exception as err: # this is not getting thrown
            flash('That username is taken.')#: {}'.format(repr(err)))
            return redirect(url_for('index'))
        uid = lookup.getUIDFirst(conn)
        lock.release()
        # print(uid)
        flash('FYI, you were issued UID {}'.format(uid))
        session['username'] = username
        session['uid'] = uid
        session['logged_in'] = True
        # session['visits'] = 1
        return redirect( url_for('profile', username=username) )
    except Exception as err:
        flash('Form submission error '+str(err))
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
            flash('Login incorrect. Try again or join')
            return redirect( url_for('index'))
        hashed = row['passhash'] 
        
        hashed2 = bcrypt.hashpw(passwd.encode('utf-8'),hashed.encode('utf-8'))#.encode('utf-8'))
        hashed2_str = hashed2.decode('utf-8')
        
        if hashed2_str == hashed:
            flash('Successfully logged in as '+username)
            session['username'] = username
            session['uid'] = row['uid']
            uid=session['uid']
            # print(session['uid'])
            session['logged_in'] = True
            # session['visits'] = 1
            return redirect( url_for('recommendations') )
        else:
            flash('Login incorrect. Try again or join')
            return redirect( url_for('index'))
    except Exception as err:
        flash('Form submission error: '+str(err))
        return redirect( url_for('index') )


#we should make this by username, not uid
@app.route('/profile/<username>', methods = ["GET", "POST"]) #allow everyone to access all profiles, but only if logged in can change data
def profile(username):
    conn = lookup.getConn(CONN)
    # try:
    if request.method == "POST":
        if 'uid' in session:
            uid = session['uid']
            # conn = lookup.getConn(CONN)
            lookup.updatePrefs(conn, uid, request.form.getlist('pref[]'))
            flash('Your preferences have been updated!')      
    
    # don't trust the URL; it's only there for decoration
    if 'username' in session:
        currentUsername = session['username']
        uid = lookup.getUID(conn, username)#session['uid']
        prefs = lookup.getPrefs(conn, uid)
        tids = [tag['tid'] for tag in prefs]
        allTags = [tag for tag in lookup.getTags(conn, 'genre')
                        if tag['tid'] not in tids]
        stories = lookup.getStories(conn, uid)
        # session['visits'] = 1+int(session['visits'])
        if prefs:
            return render_template('profile.html',
                                page_title="{}'s Profile".format(username),
                                username=username, uid=uid, prefs=prefs,
                                allTags=allTags, stories=stories, currentUsername=currentUsername
                                )
        else:
            return render_template('profile.html',
                                page_title="{}'s Profile".format(username),
                                username=username, uid=uid, prefs={},
                                allTags=allTags, stories=stories, currentUsername=currentUsername
                                )

    else:
        flash('You are not logged in. Please login or join')
        return redirect( url_for('index') )
    # except Exception as err:
    #     flash('Some kind of error '+str(err))
    #     return redirect( url_for('index') )

@app.route('/updateProfile/', methods=["POST"])
def updateProfile():
    conn = lookup.getConn(CONN)
    uid = session['uid']
    dob = request.form.get('dob')

    lookup.updateProfile(conn, uid, dob)
    username = session['username']
    return redirect( url_for('profile', username=username))

@app.route('/prefs/<uid>', methods=["GET"])
def prefs(uid):
    try:
        if 'uid' in session:
            uid = session['uid']
            conn = lookup.getConn(CONN)
            prefs = lookup.getPrefs(conn, uid)
            tids = [tag['tid'] for tag in prefs]
            allTags = [tag for tag in lookup.getTags(conn, 'genre')
                         if tag['tid'] not in tids]
            if prefs:
                return render_template('profile.html', uid=uid, prefs=prefs, allTags=allTags)
            else:
                return render_template('profile.html', uid=uid, prefs={}, allTags=allTags)
        else: 
            flash("Please log in or join")
            return redirect(url_for('index'))
    except Exception as err:
        flash('Error: '+str(err))
        return redirect(url_for('index'))


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
        flash('Error: '+str(err))
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
            lock.acquire()
            sid = lookup.addStory(conn, uid, title, summary, status)[0]
            lock.release()
            lookup.addTags(conn, sid, genre, warnings, audience, status)

            return redirect(url_for('update', sid=sid))
    except Exception as err:
        flash('Error: '+str(err))
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
        flash('Some kind of error '+str(err))
        return redirect( url_for('index') )

@app.route('/read/<int:sid>', defaults={'cnum': 1}, methods=["GET", "POST"])
@app.route('/read/<int:sid>/<int:cnum>/', methods=["GET", "POST"])
def read(sid, cnum): 
    conn = lookup.getConn(CONN)
    # print("sid: "+str(sid))
    # print("cnum: "+str(cnum))
    try:
        chapter = lookup.getChapter(conn, sid, cnum)
        # print('Chapter dict:')
        # print(chapter)
        cid = chapter['cid']
        # print(cid)
        try:
            uid = session['uid']

            #add to history
            print(lookup.addToHistory(conn, uid, sid))

            comments = lookup.getComments(conn, uid, cid)
            
            # print('Comments:')
            # print(comments)
            infile = open(chapter['filename'], 'r')
            story = infile.read()
            infile.close()

            allch = lookup.getChapters(conn,sid)
            numChap = lookup.getNumChaps(conn, sid)['count(cid)']
            # print(numChap)
            work = lookup.getStory(conn, sid)
            print(work)
            if uid == work['uid']:
                allComments = lookup.getAllComments(conn, cid)
            else:
                allComments = None

            if 'username' not in session:
                return redirect(url_for('index'))
            if session['username'] == work['username']:
                return render_template('read.html', 
                                        title=work['title'], 
                                        story=story,
                                        chapter=chapter,
                                        author=work['username'],
                                        cnum=cnum,
                                        sid=sid,
                                        update=True,
                                        allch=allch,
                                        comments=comments,
                                        uid=uid,
                                        maxCh=numChap,
                                        allComments=allComments)
            else:
                return render_template('read.html', 
                                        title=work['title'], 
                                        story=story,
                                        chapter=chapter,
                                        author=work['username'],
                                        cnum=cnum,
                                        sid=sid,
                                        update=False,
                                        allch=allch,
                                        comments=comments,
                                        uid=uid,
                                        maxCh=numChap,
                                        allComments=allComments)
        except Exception as err:
            print(err)
            return redirect( url_for('index') )
    except Exception as err:
        return redirect( url_for('notFound') )

@app.route('/404/')
def notFound():
    return render_template('404.html', title='404')

@app.route('/bookmarks/')
def bookmarks():
    return render_template('main.html',title='Hello')

@app.route('/recommendations/', methods=["GET", "POST"])
def recommendations():
    if 'uid' in session:
        if request.method=="POST":
            filters = tuple(request.form.getlist('warnings[]'))
            
        else:
            uid = session['uid']
            conn = lookup.getConn(CONN)
            warnings = lookup.getTags(conn, 'warnings')

            recs = lookup.getRecs(conn, uid)
            return render_template('search.html',
                                    resKind="Recs", res = recs, warnings=[])
    else:
        return redirect(url_for('index'))

@app.route('/addComment/', methods=["POST"])
def addComment():
    conn = lookup.getConn(CONN)
    commentText = request.form["commentText"]
    cid = request.form['cid']
    # print(commentText)
    if 'uid' in session:
        uid = session['uid']
        lock.acquire()
        lookup.addComment(conn, commentText, uid, cid)
        lock.release()
        flash('Comment submitted!')
        return redirect(request.referrer)
    else:
        return redirect(url_for('index'))

# @app.route('/addCommentAjax/', methods=["POST"])
# def addCommentAjax():
#     conn = lookup.getConn(CONN)
#     commentText = request.form.get("commentText")
#     print(commentText)
#     cid = request.form.get('cid')
#     cnum = request.form.get('cnum')
#     sid = request.form.get('sid')
#     try:
#         if 'uid' in session:
#             uid = session['uid']
#             lookup.addComment(conn, commentText, uid, cid)
#             flash('Comment submitted!')
#             return jsonify(error=False,
#                             commentText=commentText,
#                             uid=uid,
#                             cid=cid
#                             )
#         else:
#             flash("Log in before commenting.")
#             return redirect(url_for('index'))
#     except Exception as err:
#         print(err)
#         return jsonify( {'error': True, 'err': str(err) } )

@app.route('/rateAjax/', methods=["POST"])
def rateAjax():
    # print('rateAjax called')
    conn = lookup.getConn(CONN)
    rating = request.form.get('rating')
    sid = request.form.get('sid')
    uid = session['uid']
    # print("rating to add:")
    # print(rating)
    lookup.addRating(conn, uid, sid, rating)
    avgRating = float(lookup.calcAvgRating(conn, sid)['avg(rating)'])
    # print("average rating for sid " + str(sid))
    # print(avgRating)
    lookup.updateAvgRating(conn, sid, avgRating)
    return jsonify(rating=rating, avgRating=avgRating)
    

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
            flash('You are not logged in. Please login or join')
            return redirect( url_for('index') )
    except Exception as err:
        flash('Some kind of error '+str(err))
        return redirect( url_for('index') )

@app.route('/search/<search_kind>/', defaults={'search_term': ""})
@app.route('/search/<search_kind>/<search_term>', methods=["GET", "POST"])
def worksByTerm(search_kind, search_term):
    term = search_term
    print ("term ", term)
    kind = search_kind
    conn = lookup.getConn(CONN)
    if (request.method == "POST") and not (kind == "author"):
        filters = tuple(request.form.getlist('warnings[]'))
        res = lookup.searchWorks(conn, kind, term, filters)
        print (res)
    # if no search term, defaults to all movies
    # if request.form.getlist('warnings[]'):

    else:
        res = (lookup.searchAuthors(conn, term) if kind == "author" 
        else lookup.searchWorks(conn, kind, term, []))
    resKind = "Authors" if kind == "author" else "Works"
    nm = "Tag" if (kind == "tag") else "Term"
    if not res:
        flash("No {} Found Including {}: {} :( ".format(resKind, nm, term))
    return render_template('search.html', resKind=resKind, term=term, 
                            res=res, warnings=lookup.getTags(conn, 'warnings'))

@app.route('/chapIndex/', methods=["POST"])
def chapIndex():
    sid = request.form.get('sid')
    cnum = request.form.get('cid')
    print(sid, cnum)
    return redirect( url_for('read', sid=sid, cnum=cnum))

if __name__ == '__main__':

    if len(sys.argv) > 1:
        # arg, if any, is the desired port number
        port = int(sys.argv[1])
        assert(port>1024)
    else:
        port = os.getuid()
    app.debug = True
    app.run('0.0.0.0',port)
