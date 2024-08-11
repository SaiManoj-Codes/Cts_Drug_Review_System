from flask import Flask, request, render_template, jsonify

import threading
from pymongo import MongoClient
import requests
from bs4 import BeautifulSoup
from transformers import AutoTokenizer, AutoModelForSequenceClassification, pipeline
from transformers import BartForConditionalGeneration, BartTokenizer
import string
from flask import Flask, render_template, request, redirect, url_for, session
import os
import google.generativeai as gemini
from viz import create_sentiment_bar_chart


client = MongoClient("mongodb+srv://vedesh:Vedeshsb003%40@user.8fwgqcw.mongodb.net/?retryWrites=true&w=majority&appName=user")
db = client.get_database('CTS_Hackathon')
users_collection = db.get_collection('User_Info')

app = Flask(__name__)

app.secret_key = os.getenv('SECRET_KEY', 'your_secret_key')




# Initialize sentiment analysis model
l=[]
model_name = "nlptown/bert-base-multilingual-uncased-sentiment"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForSequenceClassification.from_pretrained(model_name)
sentiment_analyzer = pipeline('sentiment-analysis', model=model, tokenizer=tokenizer)


def genai(initial,a):
    gemini.configure(api_key='AIzaSyAamNc1vBJWyGIibImjN23KLxg9Wr6Zns0')
    model = gemini.GenerativeModel('gemini-1.5-pro-latest')
    try:
        chat = model.start_chat(history=[])
        response = chat.send_message(initial)
        q=response.text
        return q
    except:
        prompt=f"""Instructions:
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




"""def summarize_text(text, max_length=1000, min_length=100, length_penalty=2.0, num_beams=4):
        inputs = tokenizer.encode("summarize only about all side effects: "+text, return_tensors="pt", max_length=1024, truncation=True)
        summary_ids = model.generate(inputs, max_length=max_length, min_length=min_length, length_penalty=length_penalty, num_beams=num_beams)
        summary = tokenizer.decode(summary_ids[0], skip_special_tokens=True)
        return summary
"""


def filter_word(n):
    print(n, 'input')
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



"""def t_ex(text):
    text2 = []
    s = ''
    for i in text:
        if i != '.':
            s += i
        elif i == '.':
            text2.append(s)
            s = ''
    return text2"""



def review(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    c = soup.find_all('div', class_="ddc-sidebox ddc-sidebox-rating")
    for i in c:
        a = (i.find('a')['href'])
    url = "https://www.drugs.com" + a+"?search=&sort_reviews=time_on_medication#reviews"
    print(url)
    review_response = requests.get(url)
    review_soup = BeautifulSoup(review_response.content, 'html.parser')
    cont = review_soup.find_all('div', class_='ddc-comment ddc-box ddc-mgb-2')
    v = []
    po = []
    for i in cont:
        v.append(i.find('p').text)
    for i in range(len(v)):
        result = v[i].split('"')[1::2]
        po.append(result)
    return po

def sentiment_analyze(c):
    for text1 in c:
        result = sentiment_analyzer(text1)[0]
    return result['label']


"""def senti(a):
    
    senti_counts = {'positive': 0, 'neutral': 0, 'negative': 0}
    for i in a:
        s=''
        for j in i:
            s+=j
        c=t_ex(s)
        print("hi")
        a1=sentiment_analyze(c)
        if a1 =='1 star' or a1 == '2 stars':
            senti_counts['negative']+=1
        elif a1 == '3 stars':
            senti_counts['neutral']+=1
        elif a1 == '4 stars' or a1 == '5 stars':
            senti_counts['positive']+=1
    print(senti_counts)
    return senti_counts"""




def webdata(s):
    s = filter_word(s)
    a = s[0]
    p = "https://www.drugs.com/sfx/" + a + "-side-effects.html"
    print(p)

    def fetch_data(url):
        response = requests.get(url)
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            l.append(s)
            return soup.get_text()
        else:
            print(f"Failed to retrieve the webpage. Status code: {response.status_code}")
            return ""

    # Thread to fetch data concurrently
    def fetch_data_thread(url,a):
        result = fetch_data(url)
        #initial = "give only side effect details in bulletin points from data: " + result
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
        gen=genai(prompt,a)
        return gen

    # Thread to process reviews concurrently
    def process_reviews_thread(url,a):
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
            for text1 in a:
                result = sentiment_analyzer(text1)[0]
            return result['label']

        #senti_counts = {'positive': 0, 'neutral': 0, 'negative': 0}
        senti_counts=[0,0,0]
        for i in d:
            s=''
            for j in i:
                s+=j
            c=t_ex(s)
            #print(c)
            a1=sentiment_analyze(c)
            if a1 =='1 star' or a1 == '2 stars':
                #senti_counts['negative']+=1
                senti_counts[0]+=1
            elif a1 == '3 stars':
                #senti_counts['neutral']+=1
                senti_counts[1]+=1
            elif a1 == '4 stars' or a1 == '5 stars':
                #senti_counts['positive']+=1
                senti_counts[2]+=1
        print(senti_counts)

        tex = ''
        for i in d:
            for j in i:
                tex += j

        prompt = f"""Instructions:
1. Read the provided data carefully.
2. Summarize all the reviews to create an easy-to-understand overview of the medicine.
3. Highlight the overall sentiment, key strengths, weaknesses, and common experiences mentioned in the reviews.
4. Ensure the summary is clear, informative, and helps users understand the medicine's effects and user experiences.
5. Structure the response so that each highlighted word (such as strengths, weaknesses, etc.) is followed by the summary in the next line.
6. Underline each key word (such as Overall Sentiment, Strengths, Weaknesses, and Common Experiences) to make them stand out like titles.

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
        fir=genai(prompt,a)
        r=[]
        r.append(senti_counts)
        r.append(fir)
        return r

    urls = [p, p]

    threads = []
    results = [None,[None,None]]
    for i, url in enumerate(urls):
        if i % 2 == 0:
            t = threading.Thread(target=lambda idx, u=url: results.__setitem__(idx, fetch_data_thread(u,a)), args=(i,))
        else:
            t = threading.Thread(target=lambda idx, u=url: results.__setitem__(idx, process_reviews_thread(u,a)), args=(i,))
        threads.append(t)

    for t in threads:
        t.start()
    for t in threads:
        t.join()
    #visual=create_sentiment_bar_chart(results[1][1])
    return results[0], results[1][0],results[1][1]



@app.route('/home')
def home_main():
    return render_template('index.html')

@app.route('/analyze', methods=['POST','GET'])
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
# @app.route('/to_home_from_blog')
# def to_home_from_blog():
#     return render_template('index.html')



@app.route('/', methods=['GET', 'POST'])

@app.route('/home', methods=['GET', 'POST'])
def login():
    msg = ''
    print(request.method)
    print(request.form)
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        print("hi")
        try:
            username = request.form['username']
            password = request.form['password']
            user = users_collection.find_one({'username': username})
            if user and user['password'] == password:
                session['loggedin'] = True
                session['username'] = user['username']
                print("hi")
                return render_template('index.html')    
            else:
                msg = 'Incorrect username/password!'
        except:
            msg = 'Incorrect username/password!'
    return render_template('login.html', msg=msg)

@app.route('/home')
def home():
    if 'loggedin' in session:
        return render_template('home.html')

@app.route('/logout')
def logout():
    session.pop('loggedin', None)
    session.pop('id', None)
    session.pop('username', None)
    return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    msg = ''
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form and 'email' in request.form:
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
        if users_collection.find_one({'username': username}) and users_collection.find_one({'password': password}):
            msg="User Already Exist!"
        else:
            users_collection.insert_one({'username': username, 'password': password,'email':email})
            msg = 'You have successfully registered!'

    elif request.method == 'POST':
        msg = 'Please fill out the form!'
    return render_template('login.html', msg=msg)


if __name__ == '__main__':
    app.run(debug=True)
