# Import Flask Library
from flask import Flask, render_template, request, session, url_for, redirect, flash
import pymysql.cursors
from datetime import datetime

# Program To show How can we use different derivatives
# Multiple at a time and single at a time


# importing the srtftime() and gmtime()
# if not used the gm time, time changes
# to the local time

from time import strftime

# for uploading photo:
from app import app
#from flask import Flask, flash, request, redirect, render_template
from werkzeug.utils import secure_filename

import bcrypt

ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])


# Initialize the app from Flask
##app = Flask(__name__)
##app.secret_key = "secret key"

# Configure MySQL
conn = pymysql.connect(host='localhost',
                       port=3306,
                       user='root',
                       password='root',
                       db='CookZilla',
                       charset='utf8mb4',
                       cursorclass=pymysql.cursors.DictCursor)


def allowed_image(filename):

    if not "." in filename:
        return False

    ext = filename.rsplit(".", 1)[1]

    if ext.upper() in app.config["ALLOWED_IMAGE_EXTENSIONS"]:
        return True
    else:
        return False


def allowed_image_filesize(filesize):

    if int(filesize) <= app.config["MAX_IMAGE_FILESIZE"]:
        return True
    else:
        return False


# Define a route to hello function
@app.route('/')
def hello():
    return render_template('index.html')

# Define route for login


@app.route('/login')
def login():
    return render_template('login.html')

# Define route for register


@app.route('/register')
def register():
    return render_template('register.html')


@app.route('/post')
def post():
    return render_template('post.html')

# Authenticates the login


@app.route('/loginAuth', methods=['GET', 'POST'])
def loginAuth():
    # grabs information from the forms
    username = request.form['username']
    password = request.form['password']

    # cursor used to send queries
    #cursor = conn.cursor()
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    # executes query
    '''query = 'SELECT * FROM user WHERE username = %s and password = %s'
    #cursor.execute(query, (username, password))
    cursor.execute(query, (username, hashedPassword))
    #stores the results in a variable
    data = cursor.fetchone()'''

    query = 'SELECT * FROM person WHERE username = %s'
    cursor.execute(query, (username))

    if cursor.rowcount != 1:
        error = 'Invalid username'
        return render_template('login.html', error=error)

    #user = cursor[0]['password']
    for row in cursor:
        user_pass = row['password']
    passwordBytes = password.encode('utf-8')
    hashedPWInBytes = user_pass.encode('utf-8')
    passwordMatches = bcrypt.checkpw(passwordBytes, hashedPWInBytes)

    # use fetchall() if you are expecting more than 1 data row
    cursor.close()
    error = None

    # if(data):
    if(passwordMatches):
        # creates a session for the the user
        # session is a built in
        session['username'] = username
        return redirect(url_for('home'))
    else:
        # returns an error message to the html page
        error = 'Invalid login or username'
        return render_template('login.html', error=error)

# Authenticates the register


@app.route('/registerAuth', methods=['GET', 'POST'])
def registerAuth():
    # grabs information from the forms
    username = request.form['username']
    password = request.form['password']
    fname = request.form['fname']
    lname = request.form['lname']
    email = request.form['email']
    profile = request.form['profile']

    passwordBytes = password.encode('utf-8')
    hashedPassword = bcrypt.hashpw(passwordBytes, bcrypt.gensalt())

    # cursor used to send queries
    cursor = conn.cursor()
    # executes query
    query = 'SELECT * FROM person WHERE username = %s'
    cursor.execute(query, (username))
    # stores the results in a variable
    data = cursor.fetchone()
    # use fetchall() if you are expecting more than 1 data row
    error = None
    if(data):
        # If the previous query returns data, then user exists
        error = "This user already exists"
        return render_template('register.html', error=error)
    else:
        ins = 'INSERT INTO person VALUES(%s, %s, %s, %s, %s, %s)'
        #cursor.execute(ins, (username, password))
        cursor.execute(ins, (username, hashedPassword,
                       fname, lname, email, profile))
        conn.commit()
        cursor.close()
        return render_template('index.html')


@app.route('/home')
def home():
    user = session['username']
    cursor = conn.cursor()
    query = 'SELECT recipeID, title, numServings FROM recipe WHERE postedBy = %s ORDER BY recipeID DESC'
    cursor.execute(query, (user))
    data = cursor.fetchall()
    cursor.close()
    return render_template('home.html', username=user, posts=data)
    # return render_template('home.html', username=user)


###########################################################
######################### Wei Zhao ########################
###########################################################

# Join or Create a group
@app.route('/group')
def group():
    user = session['username']
    cursor = conn.cursor()
    query = 'SELECT gName, gCreator, gDesc FROM Groupp ORDER BY gName'
    cursor.execute(query)
    data = cursor.fetchall()
    cursor.close()
    return render_template('group.html', username=user, posts=data)


@app.route('/joinGroup', methods=['GET', 'POST'])
def joinGroup():
    # grabs information from the forms
    user = session['username']
    memberName = request.form['memberName']
    gName = request.form['gName']
    gCreator = request.form['gCreator']
    cursor2 = conn.cursor()
    query2 = 'SELECT gName, gCreator, gDesc FROM Groupp ORDER BY gName'
    cursor2.execute(query2)
    data2 = cursor2.fetchall()

    cursor = conn.cursor()
    query = 'SELECT * FROM GroupMembership WHERE memberName = %s and gName = %s and gCreator = %s'
    cursor.execute(query, (memberName, gName, gCreator))
    data = cursor.fetchone()
    error1 = None
    remind1 = None

    if(data):
        error1 = "You have already joined this Group!"
        return render_template('group.html', error1=error1, username=user, posts=data2)
    else:
        query = 'INSERT INTO GroupMembership VALUES(%s, %s, %s)'
        cursor.execute(query, (memberName, gName, gCreator))
        conn.commit()
        cursor.close()
        remind1 = "You have joined this Group successfully!"
        return render_template('group.html', remind1=remind1, username=user, posts=data2)


@app.route('/CreateGroup', methods=['GET', 'POST'])
def CreateGroup():
    # grabs information from the forms
    user = session['username']
    gName = request.form['gName']
    gDesc = request.form['gDesc']
    cursor2 = conn.cursor()
    query2 = 'SELECT gName, gCreator, gDesc FROM Groupp ORDER BY gName'
    cursor2.execute(query2)
    data2 = cursor2.fetchall()

    cursor = conn.cursor()
    query = 'SELECT gName FROM Groupp WHERE gCreator = %s and gName = %s'
    cursor.execute(query, (user, gName))
    data = cursor.fetchone()
    error2 = None
    remind2 = None

    if(data):
        error2 = "You have already created this Group!"
        return render_template('group.html', error2=error2, username=user, posts=data2)
    else:
        query = 'INSERT INTO Groupp VALUES(%s, %s, %s)'
        cursor.execute(query, (gName, user, gDesc))
        conn.commit()
        query = 'INSERT INTO GroupMembership VALUES(%s, %s, %s)'
        cursor.execute(query, (user, gName, user))
        conn.commit()
        cursor.close()
        cursor2 = conn.cursor()
        query2 = 'SELECT gName, gCreator, gDesc FROM Groupp ORDER BY gName'
        cursor2.execute(query2)
        data2 = cursor2.fetchall()
        remind2 = "You have created this Group successfully!"
        return render_template('group.html', remind2=remind2, username=user, posts=data2)


# Reservation *** build after group and event
@app.route('/event')
def event():
    user = session['username']
    cursor = conn.cursor()
    query = 'SELECT eID, eName, eDesc,eDate FROM Eventt ORDER BY eID DESC'
    cursor.execute(query)
    data = cursor.fetchall()
    cursor.close()
    return render_template('event.html', username=user, posts=data)


@app.route('/createEvent', methods=['GET', 'POST'])
def createEvent():
    username = session['username']
    cursor = conn.cursor()
    query = 'Select gName From Groupp Where gCreator = %s'
    cursor.execute(query, (username))
    groupnames = cursor.fetchall()
    remind = None
    query = 'SELECT gCreator,gName FROM Groupp WHERE gCreator = %s'
    cursor.execute(query, (username))
    userinfo = cursor.fetchone()
    error1 = None

    if (userinfo):
        if request.method == "POST":
            eName = request.form['eName']
            eDesc = request.form.get('eDesc')
            eDate = request.form.get('eDate')
            gName = request.form.get('gName')
            query = 'INSERT INTO Eventt (eName, eDesc, eDate, gName, gCreator) VALUES(%s, %s, %s, %s, %s)'
            cursor.execute(query, (eName, eDesc, eDate, gName, username))
            conn.commit()
            query = 'select * from Eventt where eID = (select max(eID) from Eventt)'
            cursor.execute(query)
            for row in cursor:
                eID = row['eID']
                eName = row['eName']
                username = row['gCreator']
            cursor.close()
            remind = "You have created this Event successfully!"
        return render_template('createEvent.html', username=username, groupnames=groupnames, remind=remind)
    else:
        error1 = "You don't have this access!"
        return render_template('createEvent.html', error1=error1, username=username)


# Reservation *** build after group and event
@app.route('/rsvp', methods=['GET', 'POST'])
def rsvp():
    user = session['username']
    responses = ['Y', 'N']
    remind = None
    cursor = conn.cursor()
    query = 'SELECT eID, eName, eDesc,eDate FROM Eventt ORDER BY eID DESC'
    cursor.execute(query)
    data = cursor.fetchall()

    query = 'SELECT Eventt.eID, eName, eDesc,eDate,response FROM Eventt join RSVP On Eventt.eID = RSVP.eID Where username = %s'
    cursor.execute(query, (user))
    rsvps = cursor.fetchall()

    if request.method == "POST":
        eID = request.form['eID']
        response = request.form.get('response')
        query = 'INSERT INTO RSVP VALUES(%s, %s, %s)'
        cursor.execute(query, (user, eID, response))
        conn.commit()
        cursor.close()
        remind = "You have created this Event successfully!"

        cursor1 = conn.cursor()
        query = 'SELECT Eventt.eID, eName, eDesc,eDate,response FROM Eventt join RSVP On Eventt.eID = RSVP.eID Where username = %s'
        cursor1.execute(query, (user))
        rsvps = cursor1.fetchall()

    return render_template('rsvp.html', username=user, posts=data, responses=responses, remind=remind, rsvps=rsvps)


@app.route('/postRecipe', methods=['GET', 'POST'])
def postRecipe():
    username = session['username']
    cursor = conn.cursor()
    title = request.form['title']
    numServings = request.form['servings']
    query = 'INSERT INTO recipe (title, numServings, postedBy) VALUES(%s, %s, %s)'
    cursor.execute(query, (title, numServings, username))
    conn.commit()

    query = 'select * from recipe where recipeID = (select max(recipeID) from recipe)'
    cursor.execute(query)
    for row in cursor:
        recipeID = row['recipeID']
        title = row['title']
        numServings = row['numServings']

    cursor.close()

    session['recipeID'] = recipeID
    session['title'] = title
    session['numServings'] = numServings
    session['stepNo'] = 0

    return render_template('recipeStepsTags.html', recipeID=recipeID, title=title, numServings=numServings, stepNo=0)
    # return redirect(url_for('recipeStepsTags'))


@app.route('/recipeSteps', methods=['GET', 'POST'])
def recipeSteps():
    stepDescription = request.form['stepDescription']
    recipeID = session['recipeID']
    stepNo = session['stepNo']
    title = session['title']
    numServings = session['numServings']
    stepNo += 1

    cursor = conn.cursor()
    query = 'insert into step VALUES(%s, %s, %s)'
    cursor.execute(query, (stepNo, recipeID, stepDescription))
    conn.commit()

    query = 'select * from step where recipeID = %s order by stepNo'
    cursor.execute(query, (recipeID))
    data = cursor.fetchall()

    query = 'select * from recipetag where recipeID = %s'
    cursor.execute(query, (recipeID))
    tagdata = cursor.fetchall()

    cursor.close()
    session['stepNo'] = stepNo

    return render_template('recipeStepsTags.html', recipeID=recipeID, title=title, numServings=numServings, steps=data, tags=tagdata)


@app.route('/recipeTags', methods=['GET', 'POST'])
def recipeTags():
    tagText = request.form['tagText']
    recipeID = session['recipeID']
    title = session['title']
    numServings = session['numServings']

    cursor = conn.cursor()
    query = 'insert into recipetag VALUES(%s, %s)'
    cursor.execute(query, (recipeID, tagText))
    conn.commit()

    query = 'select * from step where recipeID = %s order by stepNo'
    cursor.execute(query, (recipeID))
    data = cursor.fetchall()

    query = 'select * from recipetag where recipeID = %s'
    cursor.execute(query, (recipeID))
    tagdata = cursor.fetchall()

    cursor.close()

    return render_template('recipeStepsTags.html', recipeID=recipeID, title=title, numServings=numServings, steps=data, tags=tagdata)


@app.route('/select_blogger')
def select_blogger():
    # check that user is logged in
    #username = session['username']
    # should throw exception if username not found

    cursor = conn.cursor()
    query = 'SELECT DISTINCT username FROM blog'
    cursor.execute(query)
    data = cursor.fetchall()
    cursor.close()
    return render_template('select_blogger.html', user_list=data)


@app.route('/show_posts', methods=["GET", "POST"])
def show_posts():
    poster = request.args['poster']
    cursor = conn.cursor()
    query = 'SELECT ts, blog_post FROM blog WHERE username = %s ORDER BY ts DESC'
    cursor.execute(query, poster)
    data = cursor.fetchall()
    cursor.close()
    return render_template('show_posts.html', poster_name=poster, posts=data)


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/')
def upload_form():
    return render_template('upload.html')


@app.route('/', methods=['POST'])
def upload_file():
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        if file.filename == '':
            flash('No file selected for uploading')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            flash('File successfully uploaded')
            return redirect('/')
        else:
            flash('Allowed file types are txt, pdf, png, jpg, jpeg, gif')
            return redirect(request.url)


@app.route('/logout')
def logout():
    session.pop('username')
    return redirect('/')


app.secret_key = 'some key that you will never guess'
# Run the app on localhost port 5000
# debug = True -> you don't have to restart flask
# for changes to go through, TURN OFF FOR PRODUCTION
if __name__ == "__main__":
    app.run('127.0.0.1', 5000, debug=True)
