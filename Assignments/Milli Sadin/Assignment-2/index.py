from flask import Flask, render_template, request, session
import ibm_db
import re

app = Flask(__name__)
app.secret_key = 'a'

try:
    conn = ibm_db.connect("DATABASE=bludb;HOSTNAME=19af6446-6171-4641-8aba-9dcff8e1b6ff.c1ogj3sd0tgtu0lqde00.databases.appdomain.cloud;PORT=30699;SECURITY=SSL;SSLServerCertificate=DigiCertGlobalRootCA.crt;UID=gpf28409;PWD=G9IH9SYk8j8QnHJi;", "", "")
    print("Connected to DB")
except:
    print("Unabl to connect to the db")




@app.route('/')
def home():
    return render_template('home.html')

@app.route("/register",methods=["GET","POST"])
def register():
    msg = " "
    if request.method=="POST":
        username = request.form['username']
        email = request.form['email']
        regno=request.form['regno']
        password = request.form['password']
        print(username,email,regno,password)
        sql = "SELECT * FROM USERS WHERE username =?"
        stmt = ibm_db.prepare(conn,sql)
        ibm_db.bind_param(stmt,1,username)
        ibm_db.execute(stmt)
        account = ibm_db.fetch_assoc(stmt)
        print(account)
        if account:
            msg="Account already exists!"
        elif not re.match(r'[^@]+@[^@]+\.[^@]+',email):
            msg = "Invalid Email Address!"
        elif not re.match(r'[A-Za-z0-9]+',username):
            msg = "name must contain only characters and numbers"
        else:
            insert_sql = "INSERT INTO USERS VALUES(?,?,?,?)"
            prep_stmt = ibm_db.prepare(conn,insert_sql)
            ibm_db.bind_param(prep_stmt,1,username)
            ibm_db.bind_param(prep_stmt,2,email)
            ibm_db.bind_param(prep_stmt,3,regno)
            ibm_db.bind_param(prep_stmt,4,password)
            ibm_db.execute(prep_stmt)
            msg = "You have successfully Logged In"
            return render_template('dashboard.html',msg=msg,username = username)
    elif request.method=="POST":
        msg = "Please fill out the form!"
    return render_template('Register.html',msg=msg)

@app.route("/login",methods=["GET","POST"])
def login():
    global userid
    msg = " "
    if request.method=="POST":
        username = request.form['username']
        password = request.form['password']
        print(username,password)
        sql = "SELECT * FROM USERS WHERE username =? AND userpassword=?"
        stmt = ibm_db.prepare(conn,sql)
        ibm_db.bind_param(stmt,1,username)  
        ibm_db.bind_param(stmt,2,password)
        ibm_db.execute(stmt)
        account = ibm_db.fetch_assoc(stmt)
        print(account)
        if account:
            session['Loggedin'] = True
            session['id'] = account ['USERNAME']
            userid = account["USERNAME"]
            session['username'] = account["USERNAME"]
            msg = "Logged IN successfully!"
            return render_template('dashboard.html',msg=msg,username = session['username'])
        else:
            msg = "Incorrect Username or Password"
    return render_template('login.html',msg=msg)



@app.route('/dashboard')
def dashboard():
    return render_template('Dashboard.html')

@app.route('/logout')
def logout():
    session.pop('loggedin',None)
    session.pop('id',None)
    session.pop('username',None)
    return render_template('Register.html')


if __name__ == "__main__":
    app.run('0.0.0.0', debug=True)
