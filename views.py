import json
import os
from pyresparser import ResumeParser
from flask import render_template, redirect, request, jsonify, make_response
import pandas as pd
import re
from ftfy import fix_text
from nltk.corpus import stopwords
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.neighbors import NearestNeighbors
from pandas import DataFrame
from bson import json_util
from bson.objectid import ObjectId
import jsonpickle

from db import user_collection, job_collection, write_new_pdf
from application import app
from job_similarity import get_similarity


stopw = set(stopwords.words('english'))

df = pd.read_csv('./others/job_final.csv')
df['test'] = df['Job_Description'].apply(lambda x: ' '.join(
    [word for word in str(x).split() if len(word) > 2 and word not in (stopw)]))


def parse_json(data):
    return json.loads(json_util.dumps(data))


@app.route('/')
def hello():
    return render_template("index.html")


@app.route('/suggested-jobs')
def suggestedJobs():
    return render_template("suggested-jobs.html")


@app.route("/home")
def home():
    return redirect('/')


@app.route("/auth/register", methods=['POST'])
def register_user():
    if request.method == 'POST':

        user = request.get_json()

        if user['email'] == "":
            return jsonify({'error': "Email is required"}), 400
        if user['password'] == "":
            return jsonify({'error': "Password is required"}), 400

        isUserExist = user_collection.find({"email": user['email']}).count()

        if isUserExist > 0:
            return jsonify({'error': "Email already exist"}), 400

        if user['isRecruiter'] == True:
            isCompanyExist = user_collection.find(
                {"company.name": user['company']['name']}).count()

            if isCompanyExist > 0:
                return jsonify({'error': "Company already exist"}), 400

        else:
            user['company'] = None

        try:
            user_collection.insert_one(user)
            return jsonify({'message': "Created Successfully"})
        except:
            return jsonify({'error': "Something went wrong"}), 404


@app.route("/auth/login", methods=['POST'])
def login_user():
    if request.method == 'POST':

        user = request.get_json()

        if user['email'] == "":
            return jsonify({'error': "Email is required"}), 400
        if user['password'] == "":
            return jsonify({'error': "Password is required"}), 400

        isUserExist = user_collection.find_one(
            {"email": user['email'], "password": user['password']})

        if isUserExist is None:
            return jsonify({'error': "Invalid credentials"}), 401

        uuid = parse_json(isUserExist)['uuid']
        return jsonify({'message': "Login Successfully", 'token': uuid})


@app.route("/profile")
def profile():

    token = ""

    if 'Authorization' in request.headers:
        token = request.headers['Authorization']
        token = token.split(" ")[1]
        print(token)

        isUserExist = user_collection.find_one(
            {'uuid': token})

        if isUserExist is None:
            return ""

        isUserExist['_id'] = str(isUserExist['_id'])
        user = parse_json(isUserExist)
        del user['password']

        return user
    else:
        return ""


@app.route("/jobs")
def get_jobs():

    allJobs = []

    try:
        jobs = job_collection.find({})

        for job in jobs:
            job['owner'] = user_collection.find_one({
                '_id': job['owner']
            })

            job['_id'] = str(job['_id'])

            del job['owner']['password']

            allJobs.append(job)

        return jsonpickle.encode(allJobs)
    except:
        return jsonify({'error': "Something went wrong"}), 400


@app.route("/jobs/<job_id>")
def get_job(job_id):

    try:
        job = job_collection.find_one({'_id': ObjectId(job_id)})

        if job is None:
            return jsonify({'error': "Job not found"}), 400

        job['_id'] = str(job['_id'])
        job['owner'] = user_collection.find_one({
            '_id': job['owner']
        })

        job['_id'] = str(job['_id'])
        job['owner']['_id'] = str(job['owner']['_id'])

        del job['owner']['password']
        job = parse_json(job)

        return job
    except:
        return jsonify({'error': "Something went wrong"}), 400


@app.route("/job/create", methods=['POST'])
def create_job():
    if request.method == 'POST':

        job = request.get_json()
        job['owner'] = ObjectId(job['owner'])

        try:
            job_collection.insert_one(job)
            return jsonify({'message': "Job posted successfully"})
        except:
            return jsonify({'error': "Something went wrong while posting job"})


@app.route("/job/similarity", methods=['POST'])
def job_similarity():
    if request.method == 'POST':
        resume = request.files['resume']

        filePath = os.path.join("./UPLOADED_RESUME/", resume.filename)

        resume.save(filePath)

        job_id = request.form['jobId']

        job = job_collection.find_one({'_id': ObjectId(job_id)})
        job_description = job["description"]

        result = get_similarity(filePath, job_description)

        return jsonify({'data': result})

        # job = request.get_json()
        # job['owner'] = ObjectId(job['owner'])

        # try:
        #     job_collection.insert_one(job)
        #     return jsonify({'message': "Job posted successfully"})
        # except:
        #     return jsonify({'error': "Something went wrong while posting job"})


@app.route('/submit', methods=['POST'])
def submit_data():
    if request.method == 'POST':

        f = request.files['userfile']
        f.save(f.filename)

        print(f.name)

        data = ResumeParser(f.filename).get_extracted_data()

        resume = data['skills']
        print(type(resume))

        skills = []
        skills.append(' '.join(word for word in resume))
        org_name_clean = skills

        def ngrams(string, n=3):
            string = fix_text(string)  # fix text
            # remove non ascii chars
            string = string.encode("ascii", errors="ignore").decode()
            string = string.lower()
            chars_to_remove = [")", "(", ".", "|", "[", "]", "{", "}", "'"]
            rx = '[' + re.escape(''.join(chars_to_remove)) + ']'
            string = re.sub(rx, '', string)
            string = string.replace('&', 'and')
            string = string.replace(',', ' ')
            string = string.replace('-', ' ')
            string = string.title()  # normalise case - capital at start of each word
            # get rid of multiple spaces and replace with a single
            string = re.sub(' +', ' ', string).strip()
            string = ' ' + string + ' '  # pad names for ngrams...
            string = re.sub(r'[,-./]|\sBD', r'', string)
            ngrams = zip(*[string[i:] for i in range(n)])
            return [''.join(ngram) for ngram in ngrams]
        vectorizer = TfidfVectorizer(
            min_df=1, analyzer=ngrams, lowercase=False)
        tfidf = vectorizer.fit_transform(org_name_clean)
        print('Vecorizing completed...')

        def getNearestN(query):
            queryTFIDF_ = vectorizer.transform(query)
            distances, indices = nbrs.kneighbors(queryTFIDF_)
            return distances, indices
        nbrs = NearestNeighbors(n_neighbors=1, n_jobs=-1).fit(tfidf)
        unique_org = (df['test'].values)
        distances, indices = getNearestN(unique_org)
        unique_org = list(unique_org)
        matches = []
        for i, j in enumerate(indices):
            dist = round(distances[i][0], 2)

            temp = [dist]
            matches.append(temp)
        matches = pd.DataFrame(matches, columns=['Match confidence'])
        df['match'] = matches['Match confidence']
        df1 = df.sort_values('match')
        df2 = df1[['Position', 'Company', 'Location']].head(10).reset_index()

    # return  'nothing'
    # return render_template('suggested-jobs.html', tables=[df2.to_html(classes='job')], titles=['na', 'Job'])
    return df2.to_json()
