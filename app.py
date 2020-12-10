from flask import Flask, render_template, request, redirect, session, abort
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime 
from flask_admin import Admin, BaseView, expose
from flask_admin.contrib.sqla import ModelView

## DATABASE SET UP
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///elib.db'
app.config['FLASK_ADMIN_SWATCH'] = 'cerulean'
app.config['SECRET_KEY'] = 'cisco'
db = SQLAlchemy(app)

class books(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    isbn = db.Column(db.String, nullable=False)
    author = db.Column(db.String(20), nullable=False, default='N/A')
    yearPublished = db.Column(db.String(20), nullable=False, default='N/A')

    def __repr__(self):
        return 'Book ID: '+str(self.id)+' ISBN: '+self.isbn+' Title: '+self.title+' Author: '+self.author+' Year Published: '+str(self.yearPublished)
    
class users(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    password = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String, nullable=False)

    def __repr__(self):
        return f"Register('{self.username}', '{self.email}')"

    
## SUPER ADMIN DASHBOARD
class SuperAdmin(ModelView):
    def is_accessible(self):
        if "logged_in" in session:
            return True
        else:
            abort(403)
            
class AdminDashboard(BaseView):
    @expose('/')
    def index(self):
        return self.render('adminpage.html')

admin = Admin(app, name='eLib', template_mode='bootstrap3')
admin.add_view(SuperAdmin(users, db.session))
admin.add_view(SuperAdmin(books, db.session))
admin.add_view(AdminDashboard(name='Admin Dashboard', endpoint='adminpage'))
   
    
## WEB PAGES
@app.route("/", methods=['GET', 'POST'])
def index():
    if "logged_in" in session:
        all_books = books.query.order_by(books.title).all()
        if request.method == 'POST':
            bookTitle = request.form['searchField']
            print('search field: ', bookTitle)
            searchedBook = books.query.filter(books.title.like('%' + bookTitle + '%')).all()
            print(searchedBook)
            all_books = searchedBook
        return render_template('viewBook.html', books=all_books)
    else:
        return redirect('/signup')
    
@app.route("/about")
def about():
    return render_template("about.html")

@app.route("/register", methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = users(email=email, password=password)
        db.session.add(user)
        db.session.commit()
        return redirect('/viewBook')
    return render_template("register.html")
    
@app.route("/signup", methods=['GET', 'POST'])
def signup():
    return render_template('register.htmL')  

@app.route("/signin", methods=["GET", "POST"])
def signin():
    if request.method == "POST":
        if request.form.get("email") == "test@test.com" and request.form.get("password") == "123":
            session['logged_in'] = True
            return render_template("viewBook.html")
        else:
            return render_template("signin.html", failed=True)
    return render_template('signin.html')  

@app.route("/login", methods=["GET", "POST"])
def login():
    if "logged_in" in session:
        if request.method == "POST":
            all_books = books.query.order_by(books.title).all()
            return render_template('adminpage.html', login=all_books)
    else:
        if request.method == "POST":
            if request.form.get("id") == "1001" and request.form.get("password") == "123":
                session['logged_in'] = True
                return render_template("adminpage.html")
        else:
            return render_template("login.html", failed=True)
    return render_template("login.html")
    
@app.route("/login/delete/<int:id>")
def delete(id):
    book = books.query.get_or_404(id)
    db.session.delete(book)
    db.session.commit()
    return redirect("/login")

@app.route('/login/edit/<int:id>', methods=['GET', 'POST'])
def edit(id):
    book = books.query.get_or_404(id)
    if request.method == 'POST':
        book.title = request.form['title']
        book.author = request.form['author']
        book.yearPublished = request.form['yearPublished']
        book.isbn = request.form['isbn']
        db.session.commit()
        return redirect("/login")
    else:
        return render_template('editBook.html', book=book)

@app.route("/login/addBook", methods=['GET', 'POST'])
def addBook():
    if request.method == 'POST':
        book_title = request.form['title']
        book_author = request.form['author']
        book_isbn = request.form['isbn']
        book_yearPublished = request.form['yearPublished']
        bookAdd = books(title=book_title, author=book_author, isbn=book_isbn, yearPublished=book_yearPublished)
        db.session.add(bookAdd)
        db.session.commit()
        return redirect('/login')
    else:
        return render_template("addbook.html")
    
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

    
# Running the app in debug modeapp.debug = True
app.run(debug=True)
app.run()



