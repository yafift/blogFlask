from flask import Flask, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy 
from datetime import datetime


app = Flask(__name__)
app.secret_key = "PendingDeprecationWarning"
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///blog.db'

db = SQLAlchemy(app)

class Blogpost(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(50))
    subtitle = db.Column(db.String(50))
    author = db.Column(db.String(20))
    date_posted = db.Column(db.DateTime)
    post_update = db.Column(db.DateTime)
    content = db.Column(db.Text)
    img_url = db.Column(db.Text)

class Tags(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    tag = db.Column(db.String(50))
    
class TagtoPost(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    id_post = db.Column(db.Integer)
    id_tag = db.Column(db.Integer)
    
    
@app.route('/')
def index():
    posts = Blogpost.query.order_by(Blogpost.date_posted.desc()).all()
    i=0
    for post in posts:
        idpost = post.id
        tags = TagtoPost.query.filter(TagtoPost.id_post == idpost).join(Tags,  Tags.id==TagtoPost.id_tag).add_columns(Tags.tag).all()
        posts[i].tags = tags
        i=i+1
    
    if 'status' in session:
        if session['status'] == 'authorized':
            return render_template('adm_index.html', posts=posts,pagen=1)
    return render_template('index.html', posts=posts, pagen=1)

@app.route('/tagfilter/<tag>')
def tagfilter(tag):
    posts = Blogpost.query.order_by(Blogpost.date_posted.desc()).join(TagtoPost,  Blogpost.id==TagtoPost.id_post).join(Tags,  Tags.id==TagtoPost.id_tag).filter(Tags.tag == tag).all()
    i=0
    for post in posts:
        idpost = post.id
        tags = TagtoPost.query.filter(TagtoPost.id_post == idpost).join(Tags,  Tags.id==TagtoPost.id_tag).add_columns(Tags.tag).all()
        posts[i].tags = tags
        i=i+1
    pagen = int(request.args.get('pagen'))
    if 'status' in session:
        if session['status'] == 'authorized':
            return render_template('adm_index.html', posts=posts, pagen=pagen)
    return render_template('index.html', posts=posts, pagen=pagen)

@app.route('/posts/<int:pagen>')
def posts(pagen):
    posts = Blogpost.query.order_by(Blogpost.date_posted.desc()).all()
    i=0
    for post in posts:
        idpost = post.id
        tags = TagtoPost.query.filter(TagtoPost.id_post == idpost).join(Tags,  Tags.id==TagtoPost.id_tag).add_columns(Tags.tag).all()
        posts[i].tags = tags
        i=i+1
    if 'status' in session:
        if session['status'] == 'authorized':
            return render_template('adm_index.html', posts=posts, pagen=pagen)
    return render_template('index.html', posts=posts, pagen=pagen)

@app.route('/panel')
def panel():
    posts = Blogpost.query.order_by(Blogpost.date_posted.desc()).all()
    tags = Tags.query.order_by(Tags.id.desc()).all()
    if 'status' in session:
        if session['status'] == 'authorized':
            return render_template('panel.html', posts=posts , tags = tags)
    return redirect(url_for('index'))

@app.route('/post/<int:post_id>')
def post(post_id):
    post = Blogpost.query.filter_by(id=post_id).one()

    tags = TagtoPost.query.filter(TagtoPost.id_post == post_id).join(Tags,  Tags.id==TagtoPost.id_tag).add_columns(Tags.tag).all()
    post.tags = tags

    if 'status' in session:
        if session['status'] == 'authorized':
            return render_template('adm_post.html', post=post)
    return render_template('post.html', post=post)

@app.route('/edit/<int:post_id>')
def edit(post_id):
    if 'status' in session:
        if session['status'] == 'authorized':
            post = Blogpost.query.filter_by(id=post_id).one()
            tags = TagtoPost.query.filter(TagtoPost.id_post == post_id).join(Tags,  Tags.id==TagtoPost.id_tag).add_columns(Tags.tag).all()
            post.tags = tags
            return render_template('edit.html', post=post)
    else:
        return redirect(url_for('index'))

@app.route('/editpost/<int:post_id>', methods=['POST'])
def editpost(post_id):
    if 'status' in session:
        if session['status'] == 'authorized':
                post = Blogpost.query.filter_by(id=post_id).one()
                dateposted=post.date_posted
                db.session.delete(post)
                db.session.commit()
                title = request.form['title']
                subtitle = request.form['subtitle']
                author = request.form['author']
                content = request.form['content']
                img_url = request.form['imageurl']
                helpdata = datetime.now()
                post = Blogpost(id=post_id, title=title, subtitle=subtitle, author=author,img_url=img_url, content=content, date_posted=dateposted, post_update=helpdata)
                db.session.add(post)
                db.session.commit()
                post = Blogpost.query.filter_by(id=post_id).one()
                return redirect(url_for('edit', post_id=post_id))
    else:
        return redirect(url_for('index'))

@app.route('/add')
def add():
    if 'status' in session:
        if session['status'] == 'authorized':
            return render_template('add.html')
    return redirect(url_for('index'))

@app.route('/addpost', methods=['POST'])
def addpost():
    if 'status' in session:
        if session['status'] == 'authorized':
                title = request.form['title']
                subtitle = request.form['subtitle']
                author = request.form['author']
                content = request.form['content']
                img_url = request.form['imageurl']
                helpdata = datetime.now()
                post = Blogpost(title=title, subtitle=subtitle, author=author,img_url=img_url, content=content, date_posted=helpdata, post_update=helpdata)

                db.session.add(post)
                db.session.commit()

    return redirect(url_for('index'))

@app.route('/delete/<int:post_id>')
def delete(post_id):
    if 'status' in session:
        if session['status'] == 'authorized':
            post = Blogpost.query.filter_by(id=post_id).one()
            tags = TagtoPost.query.filter(TagtoPost.id_post == post_id).join(Tags,  Tags.id==TagtoPost.id_tag).add_columns(Tags.tag).all()
            post.tags = tags
            return render_template('delete.html', post=post)
    else:
        return redirect(url_for('index'))

@app.route('/deletepost/<int:post_id>', methods=['POST'])
def deletepost(post_id):
    if 'status' in session:
        if session['status'] == 'authorized':
                post = Blogpost.query.filter_by(id=post_id).one()
                db.session.delete(post)
                db.session.commit()
    return redirect(url_for('panel'))

@app.route('/aut')
def aut():
    return render_template('aut.html')
    
@app.route('/aut', methods=['POST'])
def login():
    log = request.form['login']
    password = request.form['password']
    admin_login = 'admin'
    admin_pass = 'admin'
    if log == admin_login and password == admin_pass:
        session['status'] = 'authorized'
        return redirect(url_for('index'))
    else:
        session['status'] = 'none'
        return render_template('aut.html')
    
    
if __name__ == '__main__':
    app.run(debug=True)