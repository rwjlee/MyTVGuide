import re, bcrypt
from flask_wtf import CSRFProtect
from flask import Flask, session, request, redirect, render_template, flash, url_for
import db.data_layer as db


app = Flask(__name__)
app.secret_key = 'garbage'

EMAIL_REGEX = re.compile(r'^([a-zA-Z0-9_\-\.]+)@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.)|(([a-zA-Z0-9\-]+\.)+))([a-zA-Z]{2,4}|[0-9]{1,3})(\]?)$')

csrf = CSRFProtect(app)

@app.route('/')
def index():
    if session:
        return redirect(url_for('user_page', user_id = session['user_id']))
    return render_template('index.html')

@app.route('/register')
def register():
    return render_template('register.html')

@app.route('/register_authenticate', methods = ['POST'])
def register_authenticate():
    server_email = request.form['html_email']
    server_username = request.form['html_username']
    server_password = request.form['html_password']
    server_confirm = request.form['html_confirm']

    is_valid = True

    if not EMAIL_REGEX.match(server_email):
        flash('invalid e-mail address')
        is_valid = False

    if server_password != server_confirm:
        flash('passwords are not the same')
        is_valid = False

    if is_empty('email', request.form):
        is_valid = False

    if is_empty('username', request.form):
        is_valid = False

    if is_empty('password', request.form):
        is_valid = False

    if not is_valid:
        return redirect(url_for('register'))

    encoded_utf8 = server_password.encode('UTF-8')
    encrypted = bcrypt.hashpw(encoded_utf8, bcrypt.gensalt())

    user = db.create_user(server_email, server_username, encrypted)

    session['user_id'] = user.id
    session['username'] = user.name

    return redirect(url_for('index'))

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/login_authenticate', methods = ['POST'])
def login_authenticate():
    try:
        user = db.get_user_by_email(request.form['html_email'])
        encoded_utf8 = request.form['html_password'].encode('UTF-8')
        if bcrypt.checkpw(encoded_utf8, user.password):
            session['user_id'] = user.id
            session['username'] = user.name
            return redirect(url_for('index'))
    except:
        pass

    flash('invalid login')
    return redirect(url_for('login'))

@app.route('/user_page/<user_id>')
def user_page(user_id):
    user = db.get_user_by_id(user_id)
    db_likes = user.likes_shows
    db_shows=[]
    for like in db_likes:
        show = db.get_show_by_id(like.show_id)
        print("++++++{}+++++".format(show.title))
        db_shows.append(show)
    return render_template('user_page.html', shows = db_shows, user = user)

@app.route('/search')
def search():
    return redirect(url_for('search_results', query=request.args['html_query']))

@app.route('/results/<query>')
def search_results(query):
    if len(query)==0:
        return render_templates('search_results.html')

    db_shows = db.search_by_title(query)
    
    return render_template('search_results.html', shows = db_shows)

def is_empty(name, form):
    key = 'html_{}'.format(name)
    empty = not len(form[key])>0
    if empty:
        flash('{} is empty'.format(name))

    return empty

@app.route('/likes_show/<show_id>')
def likes_show(show_id):
    user_id = session['user_id']
    user = db.get_user_by_id(user_id)
    db.create_like(user_id, show_id)
    return redirect(url_for('user_page', user_id = user_id))

@app.route('/unlike_show/<show_id>')
def unlikes_show(show_id):
    user_id = session['user_id']
    db.delete_like(user_id, show_id)
    return redirect(url_for('user_page', user_id = user_id))

@app.route('/show_page/<show_id>')
def show_page(show_id):
    db_followers = db.get_followers_by_show(show_id)
    db_show = db.get_show_by_id(show_id)
    return render_template('show_page.html', followers = db_followers, show = db_show)
    

if __name__ == '__main__':
    app.jinja_env.auto_reload = True
    app.config['TEMPLATES_AUTO_RELOAD']=True
    app.run(debug=True, use_reloader=True)