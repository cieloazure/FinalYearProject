from flask import Flask,render_template,request
import json
import vector
import pymongo
import jinja2


app = Flask(__name__)

@app.route('/',methods=['GET','POST'])
def index():
    if request.method == 'GET':
         return render_template('index.html',categories=cats)

    elif request.method == 'POST':
        checked = []
        for value in cats:
            t = request.form.getlist(value['Name'])
            if len(t) != 0:
                checked.append(t[0])

        demo_user_collection = db['demoUsers']

        ini_vec = []
        for cat in checked:
            score = vector.tfidf(cat,checked,corpus)
            cat_dict[cat] = score

        for key,value in cat_dict.iteritems():
            ini_vec.append(value)


        for key,value in cat_dict.iteritems():
            cat_dict[key] = 0

        demo_user_collection.insert_one({'email':request.form['email'],'vector':ini_vec})
        return json.dumps({'email':request.form['email'],'vector':ini_vec})


@app.route('/user',methods=['GET','POST'])
def users():
    if request.method == 'GET':
        user_collection = db['demoUsers']
        users = []

        for user in user_collection.find():
            users.append(user)

        return render_template('select-user.html',users=users)
    elif request.method == 'POST':
        t = request.form.getlist('user')
        print t[0]

        user,places =  vector.calculate_similarity(t[0])
        return render_template('display-recommendations.html',user=user,places=places,categories_user=zip(cat_dict.keys(),user['vector'])) 

if __name__ == '__main__':
    global cats
    global cat_dict
    global corpus
    #client = ''
    global client
    global db
    #db = ''


    cats = vector.get_categories()
    cat_dict = vector.create_vector()
    corpus = vector.create_corpus()
    client,db = vector.initiate_connection()
    app.run(host='0.0.0.0',debug=True)
