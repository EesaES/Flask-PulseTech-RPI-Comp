from flask import Flask, render_template, flash, request, redirect, url_for
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin, login_user, LoginManager, login_required, logout_user, current_user
from webforms import LoginForm, PostForm, UserForm, PasswordForm, NamerForm, SearchForm
from flask_ckeditor import CKEditor
from werkzeug.utils import secure_filename
import uuid as uuid
import os

# Flask Instance
app = Flask(__name__)
# add editor rich
ckeditor = CKEditor(app)
# add database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SECRET_KEY'] = "kes2127"
# init datbase

UPLOAD_FOLDER = 'static/images/'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

db = SQLAlchemy(app)
migrate = Migrate(app, db)
app.app_context().push()
# flask login stuff
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

with open('static/uploads/hr.txt', 'r') as fin:
  data = fin.read().splitlines(True)
with open('static/uploads/hr.txt', 'w') as fout:
  fout.writelines(data[15:])

@login_manager.user_loader
def load_user(user_id):
  return Users.query.get(int(user_id))

@app.route('/testing')
def testing():
  return render_template('testing.html', title='testing')

@app.route('/missing')
def missing():
  return render_template('missing.html', title='missing')

@app.route('/gauntlet')
@app.route('/')
def product():
  return render_template('product.html', title='product')

@app.route('/health')
@login_required
def health():
    file = open("static/uploads/hr.txt","r")
    data = file.read().splitlines() #data will be an array of lines from text file
    #print(data)
    total = 0
    count = 0
    for i in range(5, len(data)-1):#loop through all lines execept last
        print(data[i])
        total = total + float(data[i])
        count = count + 1

    
    average = round(total / count,0)
    warning = "Congratulations, you're Heartrate is normal keep going" 
    color = "green"
    advice = "A normal adult heart rate is between 60 and 100 bpm while resting. Your heart rate can change every minute and what’s ‘normal’ is different for everyone because of their age and health. Your lifestyle - such as whether you smoke, exercise and how much alcohol you drink - also affects your heart rate."
    if average > 100:
        warning = "Your heart rate is averaging to High, Take a break now and then."
        color = "red"
        advice = "A resting heart rate above 100 bpm is too fast for most people. A fast heart rate, also known as tachycardia, can be caused by health conditions. These conditions can include infection, anaemia (a lack of red blood cells carrying oxygen in your blood) and an overactive thyroid (where too many hormones are made)"
    elif average < 60:
        warning = "Your heart rate is averaging to Low, walk around throughout your day"
        color = "red"
        advice = "A heart rate below 60 bpm while resting is too slow for most people. A slow heart rate, also known as bradycardia, can be normal for people like athletes who are very fit. If you have a slow heart rate and are experiencing symptoms like fainting and tiredness, you should make an appointment with your GP."
      
#    with open("avg.txt", "w") as file:
#        print("This is a test")
#        file.write(average)


    return render_template('health.html', title='health', average = average, warning = warning, color = color, advice = advice)

@app.route('/module')
@login_required
def module():
  return render_template('module.html', title='module')

@app.route('/infocard')
@login_required
def infocard():
  return render_template('infocard.html', title='infocard')

@app.route('/charger')
@login_required
def charger():
  return render_template('charger.html', title='charger')

# games routes #
@app.route('/games')
@login_required
def games():
  return render_template('games.html', title='games')

@app.route('/blockjump')
@login_required
def blockjump():
  return render_template('blockjump.html', title='blockjump')

@app.route('/bubble')
@login_required
def bubble():
  return render_template('bubble.html', title='bubble')

@app.route('/doodle')
@login_required
def doodle():
  return render_template('doodle.html', title='doodle')

@app.route('/pong')
@login_required
def pong():
  return render_template('pong.html', title='pong')

@app.route('/tetris')
@login_required
def tetris():
  return render_template('tetris.html', title='tetris')
# end of games routes #
# People's About Page #

@app.route('/eesa')
def eesa():
  return render_template('eesa.html', title='eesa')

@app.route('/benji')
def benji():
  return render_template('benji.html', title='benji')

@app.route('/jenson')
def jenson():
  return render_template('jenson.html', title='jenson')
# End Of People's About Page #

# start of setup routes #

@app.route('/setup')
@login_required
def setup():
  return render_template('setup.html', title='setup')

# pass
@app.context_processor
def base():
  form = SearchForm()
  return dict(form=form)

# Create Admin Page
@app.route('/admin')
@login_required
def admin():
  id = current_user.id
  if id == 1:
    return render_template("admin.html")
  else:
    flash("Sorry, you must be the Admin to access the Admin Page")
    return redirect(url_for('dashboard'))

# search
@app.route('/search', methods=["POST"])
def search():
  form = SearchForm()
  posts = Posts.query
  if form.validate_on_submit():
    # get db
    post.searched = form.searched.data
    # query data
    posts = posts.filter(Posts.content.like('%' + post.searched + '%'))
    posts = posts.order_by(Posts.title).all()
    return render_template("search.html",
                           form=form,
                           searched=post.searched,
                           posts=posts)

# login page
@app.route('/login', methods=['GET', 'POST'])
def login():
  form = LoginForm()
  if form.validate_on_submit():
    user = Users.query.filter_by(username=form.username.data).first()
    if user:
      # check hash
      if check_password_hash(user.password_hash, form.password.data):
        login_user(user)
        flash("Logged In")
        return redirect(url_for('dashboard'))
      else:
        flash("Wrong Password")
    else:
      flash("No User Found")

  return render_template('login.html', form=form)

# logout
@app.route('/logout', methods=['GET', 'POST'])
@login_required
def logout():
  logout_user()
  flash('Logged Out')
  return redirect(url_for('login'))

# dashboard page
@app.route('/dashboard', methods=['GET', 'POST'])
@login_required
def dashboard():
  form = UserForm()
  id = current_user.id
  name_to_update = Users.query.get_or_404(id)
  if request.method == "POST":
    name_to_update.name = request.form['name']
    name_to_update.email = request.form['email']
    #name_to_update.favourite_color = request.form['favourite_color']
    name_to_update.username = request.form['username']
    name_to_update.about_author = request.form['about_author']

    # check for pf pic
    if request.files['profile_pic']:
      name_to_update.profile_pic = request.files['profile_pic']
      # image name
      pic_filename = secure_filename(name_to_update.profile_pic.filename)
      # set uuid
      pic_name = str(uuid.uuid1()) + "_" + pic_filename
      saver = request.files['profile_pic']

      # change to string db
      name_to_update.profile_pic = pic_name
      try:
        db.session.commit()
        saver.save(os.path.join(app.config['UPLOAD_FOLDER'], pic_name))
        flash("User Updated!")
        return render_template("dashboard.html",
                               form=form,
                               name_to_update=name_to_update)
      except:
        db.session.commit()
        flash("Error Please Try Again!")
        return render_template("dashboard.html",
                               form=form,
                               name_to_update=name_to_update)
    else:
      db.session.commit()
      flash("User Updated")
      return render_template("dashboard.html",
                             form=form,
                             name_to_update=name_to_update)
  else:
    return render_template("dashboard.html",
                           form=form,
                           name_to_update=name_to_update,
                           id=id)

@app.route('/posts/delete/<int:id>')
@login_required
def delete_post(id):
  post_to_delete = Posts.query.get_or_404(id)
  id = current_user.id 
  if id == post_to_delete.poster.id or id == 1:
    try:
      db.session.delete(post_to_delete)
      db.session.commit()
      flash("Blog Was Deleted")
      posts = Posts.query.order_by(Posts.date_posted)
      return render_template("posts.html", posts=posts)

    except:
      flash("Unable To Delete Post")
      posts = Posts.query.order_by(Posts.date_posted)
      return render_template("posts.html", posts=posts)
  else:
    flash("Not Authorised")
    posts = Posts.query.order_by(Posts.date_posted)
    return render_template("posts.html", posts=posts)

@app.route('/posts')
def posts():
  # grab post and post
  posts = Posts.query.order_by(Posts.date_posted)
  return render_template("posts.html", posts=posts)

@app.route('/posts/<int:id>')
def post(id):
  post = Posts.query.get_or_404(id)
  return render_template('post.html', post=post)

@app.route('/posts/edit/<int:id>', methods=['GET', 'POST'])
def edit_post(id):
  post = Posts.query.get_or_404(id)
  form = PostForm()
  if form.validate_on_submit():
    post.title = form.title.data
    post.slug = form.slug.data
    post.content = form.content.data
    # update datab
    db.session.add(post)
    db.session.commit()
    flash("Post Updated")
    return redirect(url_for('post', id=post.id))

  if current_user.id == post.poster_id or current_user.id == 1:
    form.title.data = post.title
    form.slug.data = post.slug
    form.content.data = post.content
    return render_template('edit_post.html', form=form)

  else:
    flash("Not Authorised")
    post = Posts.query.get_or_404(id)
    return render_template('post.html', post=post)

# add post
@app.route('/add-post', methods={'GET', 'POST'})
def add_post():
  form = PostForm()

  if form.validate_on_submit():
    poster = current_user.id
    post = Posts(title=form.title.data,
                 content=form.content.data,
                 poster_id=poster,
                 slug=form.slug.data)
    # clear form
    form.title.data = ''
    form.content.data = ''
    form.slug.data = ''

    # add to db
    db.session.add(post)
    db.session.commit()

    flash("Blog Submitted")

    # redirect
  return render_template("add_post.html", form=form)

@app.route('/delete/<int:id>')
@login_required
def delete(id):
  if id == current_user.id:
    user_to_delete = Users.query.get_or_404(id)
    name = None
    form = UserForm()

    try:
      db.session.delete(user_to_delete)
      db.session.commit()
      flash("User Deleted")

      our_users = Users.query.order_by(Users.date_added)
      return render_template("add_user.html",
                             form=form,
                             name=name,
                             our_users=our_users)

    except:
      flash("Unable To Delete")
      our_users = Users.query.order_by(Users.date_added)
      return render_template("add_user.html",
                             form=form,
                             name=name,
                             our_users=our_users)
  else:
    flash("Unauthorised Access")
    return redirect(url_for('dashboard'))

# update users
@app.route('/update/<int:id>', methods=['GET', 'POST'])
@login_required
def update(id):
  form = UserForm()
  name_to_update = Users.query.get_or_404(id)
  if request.method == "POST":
    name_to_update.name = request.form['name']
    name_to_update.email = request.form['email']
    name_to_update.favourite_color = request.form['favourite_color']
    name_to_update.username = request.form['username']
    try:
      db.session.commit()
      flash("User Updated!")
      return render_template("update.html",
                             form=form,
                             name_to_update=name_to_update)
    except:
      db.session.commit()
      flash("Error Please Try Again!")
      return render_template("update.html",
                             form=form,
                             name_to_update=name_to_update)
  else:
    return render_template("update.html",
                           form=form,
                           name_to_update=name_to_update,
                           id=id)

# stuff
@app.route('/user/add', methods=['GET', 'POST'])
def add_user():
  name = None
  form = UserForm()
  if form.validate_on_submit():
    user = Users.query.filter_by(email=form.email.data).first()
    if user is None:
      # hash
      hashed_pw = generate_password_hash(form.password_hash.data, "sha256")
      user = Users(username=form.username.data,
                   name=form.name.data,
                   email=form.email.data,
                   favourite_color=form.favourite_color.data,
                   password_hash=hashed_pw)
      db.session.add(user)
      db.session.commit()
    name = form.name.data
    form.name.data = ''
    form.username.data = ''
    form.email.data = ''
    form.favourite_color.data = ''
    form.password_hash.data = ''
    flash("User Added!")
  our_users = Users.query.order_by(Users.date_added)
  return render_template("add_user.html",
                         form=form,
                         name=name,
                         our_users=our_users)

# Create a route decorator
@app.route('/about')
def index():
  return render_template("about.html")

# localhost/user/John
@app.route('/user/<name>')
def user(name):
  return render_template("user.html", user_name=name)

# error pages
# invalid url
@app.errorhandler(404)
def page_not_found(e):
  return render_template("404.html"), 404

# page error
@app.errorhandler(500)
def page_not_found(e):
  return render_template("500.html"), 500

# create password test page
@app.route('/test_pw', methods=['GET', 'POST'])
def test_pw():
  email = None
  password = None
  pw_to_check = None
  passed = None
  form = PasswordForm()

  # validate
  if form.validate_on_submit():
    email = form.email.data
    password = form.password_hash.data
    form.email.data = ''
    form.password_hash.data = ''
    pw_to_check = Users.query.filter_by(email=email).first()
    # check hash pw
    passed = check_password_hash(pw_to_check.password_hash, password)
  return render_template("test_pw.html",
                         email=email,
                         password=password,
                         form=form,
                         pw_to_check=pw_to_check,
                         passed=passed)

# create name page
@app.route('/name', methods=['GET', 'POST'])
def name():
  name = None
  form = NamerForm()
  # validate
  if form.validate_on_submit():
    name = form.name.data
    form.name.data = ''
    flash("Form Submitted")

  return render_template("name.html", name=name, form=form)

# blog post model
class Posts(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  title = db.Column(db.String(100))
  content = db.Column(db.Text)

  date_posted = db.Column(db.DateTime, default=datetime.utcnow)
  slug = db.Column(db.String(225))
  # foreign key link user
  poster_id = db.Column(db.Integer, db.ForeignKey('users.id'))

# model
class Users(db.Model, UserMixin):
  id = db.Column(db.Integer, primary_key=True)
  username = db.Column(db.String(20), nullable=False, unique=True)
  name = db.Column(db.String(200), nullable=False)
  email = db.Column(db.String(120), nullable=False, unique=True)
  favourite_color = db.Column(db.String(120))
  about_author = db.Column(db.Text(500), nullable=True)
  date_added = db.Column(db.DateTime, default=datetime.utcnow)
  profile_pic = db.Column(db.String(), nullable=True)
  # password#
  password_hash = db.Column(db.String(128))
  # user more than one post
  posts = db.relationship('Posts', backref='poster')

  @property
  def password(self):
    raise AttributeError('Password Not Readable')

  @password.setter
  def password(self, password):
    self.password_hash = generate_password_hash(password)

  def verify_password(self, password):
    return check_password_hash(self.password_hash, password)

  # create string
  def __repr__(self):
    return '<Name %r>' % self.name

# recieve data from pi
@app.route("/upload", methods=['POST'])
def upload_file():
  from werkzeug.datastructures import FileStorage
  FileStorage(request.stream).save(os.path.join('static/uploads', "hr.txt"))
  return 'OK', 200

with app.app_context():
  db.create_all()

# file process
@app.route("/processfile")
def process_file():
    file = open("static/uploads/hr.txt","r")
    data = file.read().splitlines() #data will be an array of lines from text file
    #print(data)
    total = 0
    count = 0
    for i in range(5, len(data)-1):#loop through all lines execept last
        print(data[i])
        total = total + float(data[i])
        count = count + 1

    average = total / count
    return("Average heart rate is " + str(average) )

#THIS LINE NEEDS TO BE AT THE BOTTOM! - Mrs J
if __name__ == '__main__':
  app.run(host='0.0.0.0', port=8080, debug=True)