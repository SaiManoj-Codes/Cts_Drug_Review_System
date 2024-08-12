from flask import Flask, request, render_template, jsonify, redirect, url_for, session
import threading
from pymongo import MongoClient
import requests
from bs4 import BeautifulSoup
from transformers import pipeline, AutoTokenizer, AutoModelForSequenceClassification
import google.generativeai as gemini
import pandas as pd
import os
import string

client = MongoClient("mongodb+srv://Nithosh:Vidhya18@user.8fwgqcw.mongodb.net/?retryWrites=true&w=majority&appName=user")
db = client.get_database('CTS_Hackathon')
users_collection = db.get_collection('User_Info')

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'your_secret_key')

# Initialize sentiment analysis model only when needed
def get_sentiment_analyzer():
    model_name = "nlptown/bert-base-multilingual-uncased-sentiment"
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForSequenceClassification.from_pretrained(model_name)
    return pipeline('sentiment-analysis', model=model, tokenizer=tokenizer)

def genai(initial, a):
    gemini.configure(api_key='AIzaSyAamNc1vBJWyGIibImjN23KLxg9Wr6Zns0')
    model = gemini.GenerativeModel('gemini-1.5-pro-latest')
    try:
        chat = model.start_chat(history=[])
        response = chat.send_message(initial)
        return response.text
    except:
        prompt = f"""Instructions:
                    1. List all the known side effects associated with the given medicine.
                    2. Provide the side effects in a simple, clear format without any additional explanations or unrelated information.
                    3. Ensure the list is comprehensive, including both common and rare side effects.
                    4. Do not include any repeated words, similar words, or words with similar synonyms in the response. Each side effect should be unique.

                    ### Medicine:
                    {a}

                    ### Side Effects:"""

        chat = model.start_chat(history=[])
        response = chat.send_message(prompt)
        return response.text

def filter_word(n):
    res = []
    for i in [n]:
        t, st = [], ''
        for j in i:
            if j in string.punctuation or j.isspace():
                if not st.strip().isspace():
                    t.append(st.strip())
                st = ''
            else:
                st += j
        t.append(st.strip())
        res.append('-'.join(list(filter(lambda x: x != '', t))))
    return res

def review(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    c = soup.find_all('div', class_="ddc-sidebox ddc-sidebox-rating")
    for i in c:
        a = (i.find('a')['href'])
    url = "https://www.drugs.com" + a + "?search=&sort_reviews=time_on_medication#reviews"
    review_response = requests.get(url)
    review_soup = BeautifulSoup(review_response.content, 'html.parser')
    cont = review_soup.find_all('div', class_='ddc-comment ddc-box ddc-mgb-2')
    po = []
    for i in cont:
        po.append(i.find('p').text)
    return po

def sentiment_analyze(texts):
    sentiment_analyzer = get_sentiment_analyzer()
    sentiments = [sentiment_analyzer(text)[0]['label'] for text in texts]
    return sentiments

def webdata(s):
    s = filter_word(s)
    a = s[0]
    p = "https://www.drugs.com/sfx/" + a + "-side-effects.html"

    def fetch_data(url):
        response = requests.get(url)
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            return soup.get_text()
        return ""

    def fetch_data_thread(url, a):
        result = fetch_data(url)
        prompt = f"""
        Instructions:
1. Extract and list only the side effects mentioned in the data provided.
2. Ensure that the response should be categorized and contains only the names of the category name, such as "pain", "urinary problem", "digestive problem", "skin" etc.
3. Do not include any other words, phrases, or explanations in the response.
4. Each side effect should be unique. Do not list any repeated words or phrases.
5. Exclude words that have the same or similar meanings (e.g., do not list both "fever" and "high temperature"—only include one).
6. Do not include other side effects in the response

##data


        ## Data:
        {result}

        ### effects:
        """
        return genai(prompt, a)

    def process_reviews_thread(url, a):
        d = review(url)

        def t_ex(text):
            text2 = []
            s = ''
            for i in text:
                if i != '.':
                    s += i
                elif i == '.':
                    text2.append(s)
                    s = ''
            if s:
                text2.append(s)
            return text2

        def sentiment_analyze(a):
            sentiment_analyzer = get_sentiment_analyzer()
            for text1 in a:
                result = sentiment_analyzer(text1)[0]
            return result['label']

        senti_counts = [0, 0, 0]  # positive, neutral, negative
        for i in d:
            s = ''.join(i)
            c = t_ex(s)
            a1 = sentiment_analyze(c)
            if a1 == '1 star' or a1 == '2 stars':
                senti_counts[2] += 1
            elif a1 == '3 stars':
                senti_counts[1] += 1
            elif a1 == '4 stars' or a1 == '5 stars':
                senti_counts[0] += 1

        tex = ''.join(''.join(i) for i in d)

        prompt = f"""Instructions:
1. Read the provided data carefully.
2. Summarize all the reviews to create an easy-to-understand overview of the medicine.
3. Highlight the overall sentiment, key strengths, weaknesses, and common experiences mentioned in the reviews.
4. Ensure the summary is clear, informative, and helps users understand the medicine's effects and user experiences.
5. Structure the response so that each highlighted word (such as strengths, weaknesses, etc.) is followed by the summary in the next line.
6. Underline each keyword (such as Overall Sentiment, Strengths, Weaknesses, and Common Experiences) to make them stand out like titles.

### Data:
{tex}

### Comprehensive Review Summary:

__**Overall Sentiment:**__  
[Summary of overall sentiment]

__**Strengths:**__  
[Summary of strengths]

__**Weaknesses:**__  
[Summary of weaknesses]

__**Common Experiences:**__  
[Summary of common experiences]
"""
        fir = genai(prompt, a)
        return senti_counts, fir

    urls = [p, p]

    threads = []
    results = [None, [None, None]]
    for i, url in enumerate(urls):
        if i % 2 == 0:
            t = threading.Thread(target=lambda idx, u=url: results.__setitem__(idx, fetch_data_thread(u, a)), args=(i,))
        else:
            t = threading.Thread(target=lambda idx, u=url: results.__setitem__(idx, process_reviews_thread(u, a)), args=(i,))
        threads.append(t)

    for t in threads:
        t.start()
    for t in threads:
        t.join()

    return results[0], results[1][0], results[1][1]

@app.route('/home')
def home_main():
    return render_template('index.html')

@app.route('/analyze', methods=['POST', 'GET'])
def analyze():
    drug_name = request.form.get("drug_name", "")
    side_effects, sentiment, review_summary = webdata(drug_name)
    results = {
        "side_effects": side_effects,
        "sentiment": create_sentiment_bar_chart(sentiment),
        "review_summary": review_summary
    }
    return render_template('analyise.html', results=results)

@app.route('/blogpage')
def blog():
    return render_template('blog.html')

@app.route('/', methods=['GET', 'POST'])
@app.route('/home', methods=['GET', 'POST'])
def login():
    msg = ''
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        username = request.form['username']
        password = request.form['password']
        user = users_collection.find_one({'username': username})
        if user and user['password'] == password:
            session['loggedin'] = True
            session['username'] = user['username']
            return render_template('index.html')
        else:
            msg = 'Incorrect username/password!'
    return render_template('login.html', msg=msg)

@app.route('/home')
def home():
    if 'loggedin' in session:
        return render_template('index.html', username=session['username'])
    return redirect(url_for('login'))

@app.route('/logout')
def logout():
    session.pop('loggedin', None)
    session.pop('username', None)
    return redirect(url_for('login'))

def create_sentiment_bar_chart(sentiment_counts):
    # Implement the bar chart creation here
    # You can use a library like Matplotlib, Plotly, etc.
    pass

if __name__ == "__main__":
    app.run(debug=True)
