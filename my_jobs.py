import pandas as pd
import re
from ftfy import fix_text
from nltk.corpus import stopwords
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.neighbors import NearestNeighbors

from db import job_collection, user_collection

stopw = set(stopwords.words('english'))

allJobs = job_collection.find({})
df = []

for job in allJobs:
    job['owner'] = user_collection.find_one({
        '_id': job['owner']
    })

    job['_id'] = str(job['_id'])

    del job['owner']['password']

    df.append(job)

df = pd.DataFrame(df)

df['test'] = df['description'].apply(lambda x: ' '.join(
    [word for word in str(x).split() if len(word) > 2 and word not in (stopw)]))


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
    string = string.title()
    # normalise case - capital at start of each word
    # get rid of multiple spaces and replace with a single
    string = re.sub(' +', ' ', string).strip()
    string = ' ' + string + ' '
    # pad names for ngrams...
    string = re.sub(r'[,-./]|\sBD', r'', string)
    ngrams = zip(*[string[i:] for i in range(n)])

    return [''.join(ngram) for ngram in ngrams]


def my_jobs(org_name_clean, description=""):
    print(df['test'])

    vectorizer = TfidfVectorizer(min_df=1, analyzer=ngrams, lowercase=False)
    tfidf = vectorizer.fit_transform(org_name_clean)

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
    df2 = df1[['title', 'owner', 'location', 'salary', 'type', "_id"]].head(
        10).reset_index()

    return df2.to_json()
