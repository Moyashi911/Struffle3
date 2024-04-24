import os,sys
import mimetypes
from flask import Flask, render_template, request, redirect, url_for, session,flash
from flask_mysqldb import MySQL
import re
from datetime import timedelta
from sqlalchemy.orm import sessionmaker,DeclarativeBase
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import Integer, String,Boolean
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
import base64
import io
app = Flask(__name__,static_folder="templates/static/images")
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///VotingSite.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
app.permanent_session_lifetime = timedelta(minutes=10)
app.secret_key = "Yohei911"
#dbゾーン------------------------------------------------------------
class Base(DeclarativeBase):
  pass
db = SQLAlchemy(model_class=Base)
db.init_app(app)
class User(db.Model):
    userid: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    email: Mapped[str] = mapped_column(String,nullable=False)
    password: Mapped[str] = mapped_column(String,nullable=False)
    vote:Mapped[int] = mapped_column(Integer,default=1)
class Candidate(db.Model):
    number:Mapped[int] = mapped_column(Integer, primary_key=True)
    Candidateid:Mapped[int] = mapped_column(Integer)
    vote:Mapped[int] = mapped_column(Integer)
with app.app_context():
    db.create_all()
#-------------------------------------
with app.app_context():
    if  db.session.query(Candidate).count() == 0:
            print("Do")
            candidate1 = Candidate(Candidateid=1,vote=0)
            candidate2 = Candidate(Candidateid=2,vote=0)
            db.session.add(candidate1)
            db.session.commit()
            db.session.add(candidate2)
            db.session.commit()
@app.route('/')
def index():
    return redirect("/login")
@app.route('/login', methods =['GET', 'POST'])
def login():
    mesage = ''
    if request.method == 'POST' and 'email' in request.form and 'password' in request.form:
        email = request.form['email']
        password = request.form['password']
        user = User.query.filter_by(email = email, password = password).first()
        if user:
            mesage = '正常にログインしました'
            session['loggedin'] = True
            session["email"] = email
            session["username"] = user.name
            #return render_template('candidate2.html', mesage = mesage)
            return redirect("/user")
        else:
            mesage = '正しいパスワード/メールアドレスを入力してください'
    return render_template('login.html', mesage = mesage)
  
@app.route('/logout')
def logout():
    session.pop('loggedin', None)
    session.pop('userid', None)
    session.pop('email', None)
    return redirect(url_for('login'))
  
@app.route('/register', methods =['GET', 'POST'])
def register():
    mesage = ''
    if request.method == 'POST' and 'name' in request.form and 'password' in request.form and 'email' in request.form :
        userName = request.form['name']
        password = request.form['password']
        email = request.form['email']
        session["email"] = email
        session["username"] = userName
        account = User(name=userName,email=email,password=password)
        confirm_account = User.query.filter_by(email=email).first()
        confirm_username = User.query.filter_by(name=userName).first()
        if confirm_account:
            mesage = 'そのメールアドレスは既に存在しています'
        elif confirm_username:
            mesage = 'その名前は既に使用されています'
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            mesage = '正しいメールアドレスを入力してください'
        elif not userName or not password or not email:
            mesage = 'フォームを埋めてください'
        else:
            db.session.add(account)
            db.session.commit()
            mesage = '登録が完了しました'
            return redirect("/user")
    elif request.method == 'POST':
        mesage = 'フォームを埋めてください'
    return render_template('register.html', mesage = mesage)

@app.route("/user",methods=["GET","POST"])
def user():
    vote1 = 0
    vote2 = 0
    a = db.session.query(Candidate).filter_by(number = 1)
    for i in a:
        vote1= i.vote
    b = db.session.query(Candidate).filter_by(number = 2)
    for i in b:
        vote2= i.vote
    fig = plt.figure()
    ax = fig.add_subplot()
    x = [1, 2]
    y = [vote1, vote2]
    label = ["cat","dog"]
    plt.cla()
    plt.title('result of vote')
    plt.bar(x, y, tick_label=label)
    plt.legend()
    plt.savefig("templates/static/images/sample.png")
    if(session):
       mesage = "こんにちは"
       return render_template('candidate2.html',mesage=mesage,plt=plt)
    else:
        return redirect("/login")
@app.route("/candidate_naiyo1",methods=["GET","POST"])
def candidate():
    a = db.session.query(Candidate).filter_by(number = 1)
    for i in a:
        vote = i.vote
    return render_template("candidate_naiyo1.html",vote=vote)
@app.route("/candidate_naiyo2",methods=["GET","POST"])
def candidate2():
    a = db.session.query(Candidate).filter_by(number = 2)
    for i in a:
        vote = i.vote
    return render_template("candidate_naiyo2.html",vote=vote)
@app.route("/vote/<int:id>",methods=["GET","POST"])
def vote(id):
    a = db.session.query(Candidate).filter_by(number = id).first()
    if a:
        b = db.session.query(User).filter_by(name = session["username"]).first()
        if(b.vote > 0):
            a.vote += 1
            b.vote -= 1
            db.session.commit()
            flash("投票しました")
        else :
            flash("投票回数の上限を超えています")
        url = "/candidate_naiyo" + str(id)
        return redirect(url)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port="5000")
