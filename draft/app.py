from flask import (Flask, render_template, make_response, url_for, request,
                   redirect, flash, session, send_from_directory, jsonify
                   )
import dbi
from werkzeug import secure_filename
import sys,os,random
# <<<<<<< HEAD
import lookup
import bleach
import bcrypt

UPLOAD_FOLDER = '/uploaded/'
ALLOWED_EXTENSIONS = {'txt', 'png', 'jpg', 'jpeg', 'gif'}

#CONN = lookup.getConn('sbussey_db')
#CONN = lookup.getConn('ccannatt_db')
#CONN = lookup.getConn('spulavar_db')


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

DSN = None

def getConn():
    global DSN
    if DSN is None:
        DSN = dbi.read_cnf()
    return dbi.connect(DSN)

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
        print(passwd1, type(passwd1), hashed, hashed_str)
        conn = getConn()
        curs = dbi.cursor(conn)
        try:
            curs.execute('''INSERT INTO userpass(uid,username,hashed)
                            VALUES(null,%s,%s)''',
                         [username, hashed_str])
        except Exception as err:
            flash('That username is taken: {}'.format(repr(err)))
            return redirect(url_for('index'))
        curs.execute('select last_insert_id()')
        row = curs.fetchone()
        uid = row[0]
        flash('FYI, you were issued UID {}'.format(uid))
        session['username'] = username
        session['uid'] = uid
        session['logged_in'] = True
        session['visits'] = 1
        return redirect( url_for('profile', username=username) )
    except Exception as err:
        flash('form submission error '+str(err))
        return redirect( url_for('index') )

@app.route('/login/', methods=["POST"])
def login():
    try:
        username = request.form['username']
        passwd = request.form['password']
        conn = getConn()
        curs = dbi.dictCursor(conn)
        curs.execute('''SELECT uid,hashed
                      FROM userpass
                      WHERE username = %s''',
                     [username])
        row = curs.fetchone()
        if row is None:
            # Same response as wrong password,
            # so no information about what went wrong
            flash('login incorrect. Try again or join')
            return redirect( url_for('index'))
        hashed = row['hashed']
        print('hashed: {} {}'.format(hashed,type(hashed)))
        print('passwd: {}'.format(passwd))
        print('hashed.encode: {}'.format(hashed.encode('utf-8')))
        bc = bcrypt.hashpw(passwd.encode('utf-8'),hashed.encode('utf-8'))
        print('bcrypt: {}'.format(bc))
        print('str(bcrypt): {}'.format(str(bc)))
        print('bc.decode: {}'.format(bc.decode('utf-8')))
        print('equal? {}'.format(hashed==bc.decode('utf-8')))
        hashed2 = bcrypt.hashpw(passwd.encode('utf-8'),hashed.encode('utf-8'))
        hashed2_str = hashed2.decode('utf-8')
        if hashed2_str == hashed:
            flash('successfully logged in as '+username)
            session['username'] = username
            session['uid'] = row['uid']
            session['logged_in'] = True
            session['visits'] = 1
            return redirect( url_for('profile', username=username) )
        else:
            flash('login incorrect. Try again or join')
            return redirect( url_for('index'))
    except Exception as err:
        flash('form submission error '+str(err))
        return redirect( url_for('index') )


@app.route('/profile/')#<username>')
def profile():#username):
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

@app.route('/add/', methods=["GET", "POST"])
def add(): #only if user
    return render_template('main.html',title='Hello')

@app.route('/update/<sid>/<cid>/', methods=["GET","POST"])
def update(sid, cid): #only if user
    return render_template('main.html',title='Hello')

@app.route('/read/<sid>', defaults={'cid': 1})
@app.route('/read/<sid>/<cid>/')
def read(sid, cid): #if writer, create a button to update.
    return render_template('main.html', title="Hello")

@app.route('/bookmarks/')
def bookmarks():
    return render_template('main.html',title='Hello')

@app.route('/recommendations/')
def recommendations():
    recommendations = [
                        {'title': '', 
                            'sid': 0,
                            'summary': '',
                            'tags': [],
                            'rating': 0}
                       ]    
    return render_template('recommendations.html',
                            recommendations=recommendations)

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

@app.route('/greet/', methods=["GET", "POST"])
def greet():
    if request.method == 'GET':
        return render_template('greet.html', title='Customized Greeting')
    else:
        try:
            username = request.form['username'] # throws error if there's trouble
            flash('form submission successful')
            return render_template('greet.html',
                                   title='Welcome '+username,
                                   name=username)

        except Exception as err:
            flash('form submission error'+str(err))
            return redirect( url_for('index') )

@app.route('/search/<search_kind>', defaults={'search_term': ""})
@app.route('/search/<search_kind>/<search_term>', methods=["GET"])
def worksByTerm(search_kind, search_term):
     term = search_term
     kind = search_kind
    
     #search for works like the search term
     #if no search term, defaults to all movies 
     
     res = lookup.searchWorks(CONN, term) if (kind=="work") else lookup.searchAuthors(CONN, term)
     
    
     if not res:
         flash("No {} found including: {} :( ".format(kind, term))

     return render_template('search.html', kind=kind, res=res)


# @app.route('/formecho/', methods=['GET','POST'])
# def formecho():
#     if request.method == 'GET':
#         return render_template('form_data.html',
#                                method=request.method,
#                                form_data=request.args)
#     elif request.method == 'POST':
#         return render_template('form_data.html',
#                                method=request.method,
#                                form_data=request.form)
#     else:
#         return render_template('form_data.html',
#                                method=request.method,
#                                form_data={})

# @app.route('/testform/')
# def testform():
#     return render_template('testform.html')


if __name__ == '__main__':

    if len(sys.argv) > 1:
        # arg, if any, is the desired port number
        port = int(sys.argv[1])
        assert(port>1024)
    else:
        port = os.getuid()
    app.debug = True
    app.run('0.0.0.0',port)
