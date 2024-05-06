from flask import Flask, render_template, request, redirect, url_for
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user,current_user 
from flask_mysqldb import MySQL 
from flask_bcrypt import Bcrypt 



app = Flask(__name__)
app.secret_key = 'abc12345abcpqrs'

app.config["MYSQL_HOST"] = "localhost"
app.config["MYSQL_USER"] = "root"
app.config["MYSQL_PASSWORD"] = "mysql"
app.config["MYSQL_DB"] = "my_logging"

mysql =MySQL(app)
login_manage = LoginManager()
login_manage.init_app(app)
bcrypt = Bcrypt(app)


# User loader function 
@login_manage.user_loader
def load_user(user_id):
    return User.get(user_id)

class User(UserMixin):
    def __init__(self, user_id, name, email, password):
        self.user_id = user_id
        self.name = name
        self.email = email
        self.password = password
        
    def get_id(self):
        return str(self.user_id)
        

    @staticmethod
    def get(user_id):
        cursor = mysql.connection.cursor()
        cursor.execute("SELECT name, email from users WHERE id = %s", (user_id))
        result = cursor.fetchone()
        cursor.close()
        if result:
            return User(user_id, result[0], result[1])    

@app.route("/login", methods = ["GET", "POST"])
def login():
    if request.method == "POST":
       
        email = request.form['email']
        password = request.form['password']
        
        curser = mysql.connection.cursor()
        
        curser.execute("SELECT id, name, email, password from users WHERE email=%s",(email,))
        user_data = curser.fetchone()
        curser.close()
        
        if user_data and bcrypt.check_password_hash(user_data[3], password):
            users = User(user_data[0], user_data[1], user_data[2])
            login_user(users)
            return redirect(url_for('dashboard'))
        
        
    return render_template('login.html')


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        # Fetching data from form
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        
        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
    
        cursor = mysql.connection.cursor()
        cursor.execute("INSERT INTO users (name, email, password) VALUES(%s, %s, %s)", (name, email, hashed_password))
        mysql.connection.commit()
        cursor.close()
        return redirect(url_for('login'))
        
    
        
    
    return render_template('register.html')


@app.route("/dashboard")
def dashboard():
    return render_template('dashboard.html')


if __name__ == '__main__':
    app.run(debug=True)