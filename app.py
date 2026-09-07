from flask import Flask, render_template, request, session, redirect
from digital_makeup import Maquille
from face_recognize import FaceRecognize
import random
import string
from subprocess import check_output
from myplace import Myplace
from bs4 import BeautifulSoup
import subprocess
import os
from yourappdb import query_db, get_db
from flask import g

app = Flask(__name__)
app.secret_key="any string"
def init_db():
    with app.app_context():
        db = get_db()
        with app.open_resource('schema.sql', mode='r') as f:
            db.cursor().executescript(f.read())
        db.commit()
init_db()

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

@app.route("/")
def hello_world():
    user = query_db('select * from contacts')
    the_username = "anonyme"
    one_user = query_db('select * from contacts where first_name = ?',
                [the_username], one=True)
    return render_template("hey.html", users=user, one_user=one_user, the_title="my title")
@app.route("/add_one_user", methods=["GET","POST"])
def add_one_user():

    if request.method == 'POST':

        the_username = "anonyme"
        hey=dict(request.form)

        uploaded_file = request.files['pic']
        if uploaded_file.filename != '':
            uploaded_file.save(os.path.join('static/photos', uploaded_file.filename))

        hey["pic"]=uploaded_file.filename


        touslescountry= query_db("select * from country")

        one_user = query_db("insert into user (username,password,email,phone,country_id,pic) values (:username,:password,:email,:phone,:country_id,:pic)",hey, one=True)
        mylastrowid=str(one_user["myid"])
        user = query_db('select * from user')


        last_user = query_db("select * from user where email = ? and password = ?",[hey["email"], hey["password"]], one=True)
        session["current_user_id"]=last_user["id"]
        for x in ['username','password','email','phone','country_id','pic']:
            session[x]=hey[x]


        return render_template("userform.html", users=user, one_user=one_user, the_title="add new user", touslescountry=touslescountry)


    touslescountry= query_db("select * from country")

    user = query_db('select * from user')
    one_user = query_db("select * from user limit 1", one=True)
    return render_template("userform.html", users=user, one_user=one_user, the_title="add new user", touslescountry=touslescountry)


@app.route("/user_sign_out", methods=["GET","POST"])
def user_sign_out():
    if request.method == 'POST':
        session["current_user_id"]=""
        for x in ['username','password','email','phone','country_id','pic']:
            session[x]=""
        return redirect("/")


@app.route("/user_log_in", methods=["GET","POST"])
def user_login():
    if request.method == 'POST':
        hey=request.form
        last_user = query_db("select * from user where email = ? and password = ?",[hey["email"], hey["password"]], one=True)
        try:
            session["current_user_id"]=last_user["id"]
            for x in ['username','password','email','phone','country_id','pic']:
                session[x]=hey[x]
        except:
            return render_template("userlogin.html")
    return render_template("userlogin.html")
@app.route("/add_one_country", methods=["GET","POST"])
def add_one_country():

    if request.method == 'POST':

        the_username = "anonyme"
        hey=dict(request.form)


        one_user = query_db("insert into country (name) values (:name)",hey, one=True)
        mylastrowid=str(one_user["myid"])
        user = query_db('select * from country')


        return render_template("countryform.html", countrys=user, one_user=one_user, the_title="add new country")


    user = query_db('select * from country')
    one_user = query_db("select * from country limit 1", one=True)
    return render_template("countryform.html", countrys=user, one_user=one_user, the_title="add new country")

@app.route("/add_one_scores", methods=["GET","POST"])
def add_one_scores():

    if request.method == 'POST':

        the_username = "anonyme"
        hey=dict(request.form)


        one_user = query_db("insert into scores (user_id,time_signature,key_signature,mytext,pic) values (:user_id,:time_signature,:key_signature,:mytext,:pic)",hey, one=True)
        mylastrowid=str(one_user["myid"])
        user = query_db('select * from scores')


        file_pointer = open("./samplescoreexample.ly")
        contents = file_pointer.read()
        contents=contents.replace("KEYSCOREHERE", request.form["key_signature"].replace(" "," \\")).replace("TIMESCOREHERE", request.form["time_signature"]).replace("CONTENTSCOREHERE", request.form["mytext"])
        file_pointer = open("./static/scores/scores_mytext_sample_"+mylastrowid+".ly", "w")
        file_pointer.write(contents)
        file_pointer.close()
        file_pointer = open("./static/scores/scores_mytext_sample_"+mylastrowid+".html", "w")
        file_pointer.write("<lilypond staffsize=34>"+contents+"</lilypond>")
        file_pointer.close()
        subprocess.run(["lilypond-book", "static/scores/scores_mytext_sample_"+mylastrowid+".html", "-f", "html", "--output", "static/scores/samplescorescores_mytext"+mylastrowid]) 

        try:
            f= open("static/scores/samplescorescores_mytext"+mylastrowid+"/scores_mytext_sample_"+mylastrowid+".html")
            s = f.read()
            soup = BeautifulSoup(s)

            picvalue=dict({'pic': "static/scores/samplescoremyscore_mymusic"+mylastrowid+"/"+soup.find('img').get("src"), 'id': mylastrowid})
        except:
            picvalue=dict({'pic': "", "id": mylastrowid})
        print(picvalue)

        hello_there = query_db("update scores set pic = :pic where id = :id",picvalue, one=True)

        return render_template("scoresform.html", scoress=user, one_user=one_user, the_title="add new scores")


    user = query_db('select * from scores')
    one_user = query_db("select * from scores limit 1", one=True)
    return render_template("scoresform.html", scoress=user, one_user=one_user, the_title="add new scores")

@app.route("/add_one_mysunglassesphoto", methods=["GET","POST"])
def add_one_mysunglassesphoto():

    if request.method == 'POST':

        the_username = "anonyme"
        hey=dict(request.form)

        uploaded_file = request.files['pic']


        char_set = string.ascii_uppercase + string.digits
        myfilename=''.join(random.sample(char_set*6, 6))+'.'+uploaded_file.filename.split('.')[-1]
        if uploaded_file.filename != '':
            uploaded_file.save(os.path.join('static/photos', myfilename))



        hey["pic"]=myfilename
        try:
            #x=subprocess.Popen(["/usr/bin/python3","addsunglasses.py",hey["pic"]])
            x=subprocess.check_output(["/home/mary/miniconda3/bin/python3","addsunglasses.py",hey["pic"]])

            print("no error:",x)
            hey["mycomment"]=x
        except Exception as e:
            print("ereeeuuuuur!!! ooowow!",e)


        one_user = query_db("insert into mysunglassesphoto (pic,user_id,mycomment) values (:pic,:user_id,:mycomment)",hey, one=True)
        mylastrowid=str(one_user["myid"])
        user = query_db('select * from mysunglassesphoto')


        return render_template("mysunglassesphotoform.html", mysunglassesphotos=user, one_user=one_user, the_title="add new mysunglassesphoto")


    user = query_db('select * from mysunglassesphoto')
    one_user = query_db("select * from mysunglassesphoto limit 1", one=True)
    return render_template("mysunglassesphotoform.html", mysunglassesphotos=user, one_user=one_user, the_title="add new mysunglassesphoto")

@app.route("/add_one_maquillephoto", methods=["GET","POST"])
def add_one_maquillephoto():

    if request.method == 'POST':

        the_username = "anonyme"
        hey=dict(request.form)

        uploaded_file = request.files['pic']
        if uploaded_file.filename != '':
            uploaded_file.save(os.path.join('static/photos', uploaded_file.filename))
        x=Maquille(uploaded_file.filename).find_landmarks()

        hey["pic"]=uploaded_file.filename


        one_user = query_db("insert into maquillephoto (pic,user_id) values (:pic,:user_id)",hey, one=True)
        mylastrowid=str(one_user["myid"])
        user = query_db('select * from maquillephoto')


        return render_template("maquillephotoform.html", maquillephotos=user, one_user=one_user, the_title="add new maquillephoto")


    user = query_db('select * from maquillephoto')
    one_user = query_db("select * from maquillephoto limit 1", one=True)
    return render_template("maquillephotoform.html", maquillephotos=user, one_user=one_user, the_title="add new maquillephoto")

@app.route("/add_one_reconnaitphoto", methods=["GET","POST"])
def add_one_reconnaitphoto():
    touslesuser= query_db("select * from user")

    if request.method == 'POST':

        the_username = "anonyme"
        hey=dict(request.form)
        print(hey)

        uploaded_file = request.files['pic']
        if uploaded_file.filename != '':
            uploaded_file.save(os.path.join('static/photos', uploaded_file.filename))

        hey["pic"]=uploaded_file.filename


        knownpicuser= []
        print(request.form["user_id"])
        findpicuser= query_db("select x.pic from user x where x.id = ?", [request.form["user_id"]], one=True)
        print(dict(findpicuser))
        #findpicuser= query_db("select x.pic from user x ) #optional compare photo with all users from the relational table
        #for x in findpicuser:
        #    knownpicuser.append(x["pic"])

        knownpicuser.append(findpicuser["pic"])
        unknownpic=hey["pic"]
        x=FaceRecognize(knownpicuser, unknownpic).get_results()
        print("recognized", x)
        hey["face_recognized"]="recognized" if x[0] else "not recognized"


        one_user = query_db("insert into reconnaitphoto (user_id,pic,face_recognized) values (:user_id,:pic,:face_recognized)",hey, one=True)
        mylastrowid=str(one_user["myid"])
        user = query_db('select x.*, username from reconnaitphoto x left join user u on u.id = x.user_id')


        return render_template("reconnaitphotoform.html", touslesuser=touslesuser, reconnaitphotos=user, one_user=one_user, the_title="add new reconnaitphoto")




    user = query_db('select x.*, username from reconnaitphoto x left join user u on u.id = x.user_id')
    one_user = query_db("select * from reconnaitphoto limit 1", one=True)
    return render_template("reconnaitphotoform.html", touslesuser=touslesuser,  reconnaitphotos=user, one_user=one_user, the_title="add new reconnaitphoto")

