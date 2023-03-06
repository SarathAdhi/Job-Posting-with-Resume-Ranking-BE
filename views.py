import json
import os
from pyresparser import ResumeParser
from flask import render_template, redirect, request, jsonify
from bson import json_util
from bson.objectid import ObjectId
import jsonpickle

from db import user_collection, job_collection
from application import app
from job_similarity import get_similarity
from my_jobs import my_jobs


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


@app.route("/auth/register", methods=['POST'])
def register_user():
    if request.method == 'POST':

        user = request.get_json()

        print(user)

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


@app.route("/upload/resume", methods=['POST'])
def upload_resume():
    if request.method == 'POST':

        resume = request.files['resume']
        prev_filepath = request.form['prev_filepath']

        print(prev_filepath)

        if os.path.isfile(prev_filepath):
            os.remove(prev_filepath)

        filePath = os.path.join("./UPLOADED_RESUME/", resume.filename)

        resume.save(filePath)

        user_uuid = request.form['uuid']

        myquery = {'uuid': user_uuid}
        newvalues = {
            "$set": {"resume": "./UPLOADED_RESUME/" + resume.filename}}

        try:
            user_collection.update_one(myquery, newvalues, upsert=False)
            return jsonify({'message': "Resume uploaded Successfully"})
        except:
            return jsonify({'error': "Something went wrong"}), 404


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


@app.route("/profile/update", methods=['POST'])
def profile_update():
    user = request.get_json()
    user_id = user['_id']

    del user["_id"]
    del user["uuid"]
    del user["email"]

    myquery = {'_id': ObjectId(user_id)}
    newvalues = {"$set": user}

    try:
        user_collection.update_one(myquery, newvalues, upsert=False)
        return jsonify({'message': "Updated Profile"})

    except:
        return jsonify({'error': "Something went wrong"}), 400


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

        all_candidates = []

        for candidate in job['candidates']:
            cand_id = str(candidate)
            all_candidates.append(cand_id)

        job["candidates"] = all_candidates

        del job['owner']['password']

        job = parse_json(job)

        return job
    except:
        return jsonify({'error': "Something went wrong"}), 400


@app.route("/jobs/analytics/<job_id>")
def get_job_analytics(job_id):

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

        all_candidates = []

        for candidate in job['candidates']:
            candidate_details = user_collection.find_one({
                '_id': candidate
            })
            candidate_details['_id'] = str(candidate_details['_id'])

            result = get_similarity(
                candidate_details["resume"], job['description'], "number")

            candidate_details['score'] = result

            del candidate_details['password']
            all_candidates.append(candidate_details)

        job["candidates"] = all_candidates

        job = parse_json(job)

        return job
    except:
        return jsonify({'error': "Something went wrong here"}), 400


@app.route("/company/jobs/<company_id>")
def get_company_jobs(company_id):

    print(company_id)
    allJobs = []

    try:
        jobs = job_collection.find({'companyId': str(company_id)})
        for job in jobs:
            job['_id'] = str(job['_id'])
            allJobs.append(job)

        return jsonpickle.encode(allJobs)
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


@app.route("/job/apply/<job_id>", methods=['POST'])
def apply_job(job_id):

    user = request.get_json()
    user_id = user['_id']

    print(user_id)

    myquery = {'_id': ObjectId(job_id)}
    newvalues = {
        "$push": {"candidates": ObjectId(user_id)}}

    job = job_collection.find_one(
        {'_id': ObjectId(job_id), 'candidates': {'$in': [ObjectId(user_id)]}})

    if job is not None:
        return jsonify({'error': "Already Applied to the job"}), 401

    try:
        job_collection.update_one(myquery, newvalues, upsert=False)
        return jsonify({'message': "Applied Successfully"})

    except:
        return jsonify({'error': "Something went wrong"}), 400


@app.route("/job/similarity", methods=['POST'])
def job_similarity():
    if request.method == 'POST':
        res = request.get_json()

        job = job_collection.find_one({'_id': ObjectId(res["job_id"])})
        job_description = job["description"]

        result = get_similarity(res["resume"], job_description)

        return jsonify({'data': result})


@app.route('/job/suggestions')
def submit_data():

    token = ""

    if 'Authorization' in request.headers:
        token = request.headers['Authorization']
        token = token.split(" ")[1]
        print(token)

    user = user_collection.find_one({'uuid': token})

    filePath = os.path.join(user["resume"])
    data = ResumeParser(filePath).get_extracted_data()

    resume = data['skills']

    skills = []
    skills.append(' '.join(word for word in resume))
    org_name_clean = skills

    df2 = my_jobs(org_name_clean)

    return df2
