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

lock = Lock()

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

app.secret_key = ''.join([ random.choice(('ABCDEFGHIJKLMNOPQRSTUVXYZ' +
                                          'abcdefghijklmnopqrstuvxyz' +
                                          '0123456789'))
                           for i in range(20) ])

# This gets us better error messages for certain common request errors
app.config['TRAP_BAD_REQUEST_ERRORS'] = True

app.config['PERMANENT_SESSION_LIFETIME'] =  300000 #about a month

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
            return render_template('main.html', page_title="Welcome to Critiq")

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
        
        #password policy
        #This policy was not always in effect, so if you want to,
        #you can test with legacy shorter username/password pairs
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

            unwanted = lookup.getPrefs(conn, uid, True)
            session['filters'] = unwanted
            print (session)

            session['logged_in'] = True
            session.permanent = True
            return redirect( url_for('recommendations') )
        else:
            flash('Login incorrect. Try again or join')
            return redirect( url_for('index'))
    except Exception as err:
        flash('Form submission error: '+str(err))
        return redirect( url_for('index') )


@app.route('/profile/<username>', methods = ["GET", "POST"]) #allow everyone to access all profiles, only let logged in users change own data
def profile(username):
    conn = lookup.getConn(CONN)
    try:
        if request.method == "POST":
            # if either prefs or warnings were updated
            if 'uid' in session:
                uid = session['uid']

                if request.form.get('submit-btn') == "Update Preferences":
                    lookup.updatePrefs(conn, uid, request.form.getlist('pref[]'), False)
                else:
                    lookup.updatePrefs(conn, uid, request.form.getlist('warning[]'), True)
                    
                    session['filters'] = lookup.getPrefs(conn, uid, True)                

                flash('Your preferences have been updated!')      
        
        # don't trust the URL; it's only there for decoration
        if 'username' in session:
            currentUsername = session['username']
            uid = lookup.getUID(conn, username)
            
            # retrieve user's current prefs and content filters
            prefs = lookup.getPrefs(conn, uid, False)
            warns = lookup.getPrefs(conn, uid, True)

            # get all genre tags and warnings
            allTags = lookup.getTags(conn, 'genre')

            allWarns = lookup.getTags(conn, 'warnings')

            # default values if profile does not already have any prefs or content filters 
            prefTags = [(tag, False) for tag in allTags]
            warnTags = [(tag, False) for tag in allWarns]

            # set up current prefs and content filters for auto-population
            if prefs: 
                prefTags = ([((tag, True) if tag['tid'] in prefs else (tag, False))
                            for tag in allTags])

            if warns:
                warnTags = ([((tag, True) if tag['tid'] in warns else (tag, False))
                            for tag in allWarns])
            

            stories = lookup.getStories(conn, uid)
            return render_template('profile.html',
                                page_title="{}'s Profile".format(username),
                                username=username, uid=uid, prefs=prefTags, 
                                warnings=warnTags, stories=stories, 
                                currentUsername=currentUsername
                                )
        else:
            flash('You are not logged in. Please login or join')
            return redirect( url_for('index') )
    except Exception as err:
        flash('Some kind of error '+str(err))
        return redirect( url_for('index') )

@app.route('/updateProfile/', methods=["POST"])
def updateProfile():
    conn = lookup.getConn(CONN)
    uid = session['uid']
    dob = request.form.get('dob')

    lookup.updateProfile(conn, uid, dob)
    username = session['username']
    return redirect( url_for('profile', username=username))

@app.route('/manage/')
def manage():
    try:
        if 'uid' in session:
            uid = session['uid']
            conn = lookup.getConn(CONN)
            stories = lookup.getStories(conn, uid)
            return render_template('manage.html', stories=stories, page_title="Manage My Stories")
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
                return render_template('add.html', warnings=warnings, 
                                    genre=genre, audience=audience, isFin=isFin, page_title="Add a Story")
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
            if status == 32:
                status = 1
            elif status == 33:
                status = 0
        
            conn = lookup.getConn(CONN)
            sid = lookup.addStory(conn, uid, title, summary, status)[0]
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
                    with open(chapter['filename'], 'r') as infile:
                        print("From db: "+chapter['filename'])
                        story = infile.read()
                        print("Read for Update" + story)
                allch = lookup.getChapters(conn, sid)
                title = lookup.getTitle(conn, sid)
                return render_template('write.html', sid=sid, cnum=cnum, story=story, 
                                        allch=allch, title=title['title'], page_title="Update '{}'".format(title['title']))

            if request.method=="POST":
                sometext = request.form['write']
                somehtml = bleach.clean(sometext, #allowed tags, attributes, and styles
                    tags=['b','blockquote','i','em','strong','p','ul','br','li','ol','span', 'pre'], 
                    attributes=['style'],
                    styles=['text-decoration', 'text-align'])

                dirname = os.path.dirname(__file__)
                relative = 'uploaded/'+'sid'+str(sid)+'cnum'+str(cnum)+'.html'
                filename = os.path.join(dirname, relative)
                print(filename)

                with open(filename, 'w') as outfile:
                    outfile.write(somehtml)
                    print("Where it's written:" + filename)
                    print("Write for Update" + somehtml)
                
                chapter = lookup.getChapter(conn,sid,cnum)

                if chapter:
                    cid = chapter['cid']
                if not chapter:
                    cid = None

                lookup.setChapter(conn, sid, cnum, cid, filename)
                print("ok i got this")
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

    try:
        chapter = lookup.getChapter(conn, sid, cnum)
        cid = chapter['cid']
        try:
            #check if they're logged in
            if 'username' not in session:
                return redirect(url_for('index'))

            uid = session['uid']

            #add to history
            print(lookup.addToHistory(conn, uid, sid, cid))

            #check if they've rated the piece already
            rating = lookup.getRating(conn, sid, uid)
            if rating is not None:
                rating = rating['rating']
                avgRating = float(lookup.calcAvgRating(conn, sid)['avg(rating)'])
            else:
                avgRating = None

            #these are the comments the user has posted on this chapter
            comments = lookup.getComments(conn, uid, cid)

            story = ""

            with open(chapter['filename'], 'r') as infile:
                story = infile.read()
                # print("Read for Reading:" + story)

            isBookmarked = lookup.isBookmarked(conn,sid,uid)

            allch = lookup.getChapters(conn,sid)
            numChap = lookup.getNumChaps(conn, sid)['count(cid)']
            work = lookup.getStory(conn, sid)
            
            #only display all comments on a work if the author is viewing
            #otherwise, users can only see the comments they've written
            if uid == work['uid']:
                allComments = lookup.getAllComments(conn, cid)
            else:
                allComments = None

            if session['username'] == work['username']:
                isUpdate = True
            else:
                isUpdate = False
            return render_template('read.html', 
                                    page_title=work['title'], 
                                    story=story,
                                    chapter=chapter,
                                    author=work['username'],
                                    cnum=cnum,
                                    isBookmark=isBookmarked,
                                    sid=sid,
                                    update=isUpdate,
                                    allch=allch,
                                    comments=comments,
                                    uid=uid,
                                    maxCh=numChap,
                                    allComments=allComments,
                                    old_rating=rating,
                                    avgRating=avgRating)
        except Exception as err:
            print(err)
            return redirect( url_for('index') )
    except Exception as err:
        return redirect( url_for('notFound') )

@app.route('/404/')
def notFound():
    '''Lets user know that something is wrong when they try to
    access a chapter/story that doesn't exist; 
    redirecting them to index would be confusing.'''
    return render_template('404.html', page_title='404')

@app.route('/bookmarks/')
def bookmarks():
    if 'uid' in session:
        uid = session['uid']
        conn = lookup.getConn(CONN)
        username = session['username'] if 'username' in session else ''

        books = lookup.getBookmarks(conn, uid)
              
        if not books:
            flash("No bookmarked works were found")
        
        return render_template('bookmarks.html',
                                res=books,
                                page_title="{}'s Bookmarks".format(username))
    else:
        flash("Please log in")
        return redirect(url_for('index'))

@app.route('/recommendations/', methods=["GET", "POST"])
def recommendations():
    if 'uid' in session:
        uid = session['uid']
        conn = lookup.getConn(CONN)
        warnings = lookup.getTags(conn, 'warnings')
        username = session['username'] if 'username' in session else ''

        recs = lookup.getRecs(conn, uid, session['filters'])
              
        if not recs:
            flash("No works fitting your preferences were found")
        
        return render_template('search.html',
                                    resKind="Recs", res = recs, warnings=[],
                                    page_title="{}'s Home".format(username))

    return redirect(url_for('index'))

@app.route('/addComment/', methods=["POST"])
def addComment():
    conn = lookup.getConn(CONN)
    commentText = request.form["commentText"]
    cid = request.form['chapcid']

    if 'uid' in session:
        uid = session['uid']
        lookup.addComment(conn, commentText, uid, cid)
        flash('Comment submitted!')
        return redirect(request.referrer)
    else:
        return redirect(url_for('index'))

@app.route('/rateAjax/', methods=["POST"])
def rateAjax():
    conn = lookup.getConn(CONN)
    rating = request.form.get('rating')
    sid = request.form.get('sid')
    uid = session['uid']

    lookup.addRating(conn, uid, sid, rating)
    avgRating = float(lookup.calcAvgRating(conn, sid)['avg(rating)'])
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

@app.route('/search/<search_kind>/', defaults={'search_term': ""}, methods=["GET", "POST"])
@app.route('/search/<search_kind>/<search_term>', methods=["GET", "POST"])
def worksByTerm(search_kind, search_term):
    '''searches for works by work, author or tag. if no term then default to all'''
    term = search_term

    kind = search_kind
    conn = lookup.getConn(CONN)
    
    filters = []
    completion = None
    audience = None
    sortBy = None
    exclude = session['filters'] if 'filters' in session else []
    
    if (request.method == "POST") and not (kind == "author"):
        filters = request.form.getlist('warnings[]')
        sortBy = request.form.get('sortby')
        completion = request.form.get('finished')
        audience = request.form.get('audience')

    res = (lookup.searchAuthors(conn, term) if kind == "author" 
    else lookup.searchWorks(conn, kind, term, set(filters + exclude))
    )
    print (str(res))

    if not kind == "author":
        print("pre everything\n", str(res))
        if completion:

            res = ([work for work in res if not work['wip']] 
                    if completion == 'wip' else
                    [work for work in res if work['wip']])
        print ("completion\n", str(res))
        if audience:
            res = [work for work in res if work['audience'] == audience]


        if sortBy:
            if sortBy == 'avgRating':
                for work in res:
                    if work.get('avgRating') == None:
                        work.update({'avgRating': 0})
            
            print ("checking\n {}".format(str(res)))

            res = sorted(res, reverse = True, key = lambda work: work[sortBy])
            print ("sorted byyyyy\n {}".format(str(res)))


    resKind = "Authors" if kind == "author" else "Works"
    nm = "Tag" if (kind == "tag") else "Term"

    if not res:
        flash("No {} Found Including {}: {} :( ".format(resKind, nm, term))
    
    return render_template('search.html', resKind=resKind, term=term, 
                            res=res, warnings=lookup.getTags(conn, 'warnings'),
                            page_title="Search")

@app.route('/chapIndex/', methods=["POST"])
def chapIndex():
    sid = request.form.get('sid')
    cnum = request.form.get('cid')
    print(sid, cnum)
    return redirect( url_for('read', sid=sid, cnum=cnum))

@app.route('/history/', methods = ["GET"])
def history():
    if 'uid' in session:
        uid = session['uid']
        conn = lookup.getConn(CONN)
        hist = lookup.getHistory(conn, uid)
        username = session['username'] if 'username' in session else ""
        return render_template('history.html',
                                history=hist,
                                page_title="{}'s History".format(username))
    else:
        return redirect(url_for('index'))

@app.route('/markHelpful/', methods=["POST"])
def markHelpful():
    '''allows authors to mark particular comments as helpful or unhelpful'''
    conn = lookup.getConn(CONN)

    helpful = request.form.get('helpful')
    rid = request.form.get('rid') #review id
    
    lookup.changeHelpful(conn, rid, helpful)
    return jsonify(helpful=helpful, rid=rid)

@app.route('/addBookmark/', methods=["POST"])
def addBookmark():
    book = request.form['changemark']
    uid = session['uid']
    sid = request.form['sid']

    conn = lookup.getConn(CONN)
    isBooked = lookup.isBookmarked(conn, sid, uid)

    if isBooked and book == "Bookmarked":
        lookup.removeBookmark(conn, sid, uid)
        flash("Bookmark removed")
    elif isBooked is None and book == "Add Bookmark":
        lookup.addBookmark(conn, sid, uid)
        flash("Bookmark added")
    else:
        flash("Bookmark unchanged")

    return redirect(request.referrer)

if __name__ == '__main__':

    if len(sys.argv) > 1:
        # arg, if any, is the desired port number
        port = int(sys.argv[1])
        assert(port>1024)
    else:
        port = os.getuid()
    app.debug = True
    app.run('0.0.0.0',port)
