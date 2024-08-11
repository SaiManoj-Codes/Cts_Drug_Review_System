# from flask import Flask, request, jsonify
# from pymongo import MongoClient
# import bcrypt

# app = Flask(__name__)
# client = MongoClient("mongodb+srv://vedesh:Vedeshsb003%40@user.8fwgqcw.mongodb.net/?retryWrites=true&w=majority&appName=user")
# db = client.get_database('CTS_Hackathon')
# users_collection = db.get_collection('User_Info')

# # User registration route
# # @app.route('/register', methods=['POST'])
# def register():
#     username = "vedesh"
#     password = "vedesh"
#     client.admin.command("ping")
#     if users_collection.find_one({'username': username}):
#         return jsonify({"error": "User already exists"}), 400

#     users_collection.insert_one({'username': username, 'password': password})

#     return jsonify({"message": "User registered successfully"}), 201

# # User login route
# # @app.route('/login', methods=['POST'])
# def login():
#     username = "vedesh"
#     password = "vedesh"

#     user = users_collection.find_one({'username': username})
#     if not user or not user["password"]==password:
#         return jsonify({"error": "Invalid username or password"}), 401
#     print("Logged in")

#     return jsonify({"message": "Login successful"}), 200

# if __name__ == '__main__':
#     login()




import os
print(os.getenv('USERNAME'))

from transformers import AutoTokenizer, AutoModelForSequenceClassification, pipeline

# Initialize sentiment analysis model
model_name = "nlptown/bert-base-multilingual-uncased-sentiment"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForSequenceClassification.from_pretrained(model_name)
sentiment_analyzer = pipeline('sentiment-analysis', model=model, tokenizer=tokenizer)

text=[['For me its very good for pain and headache works in  30 minutes with every thing getting better'], ['Paracetamol is a very fine medicine.'], ['I had a headache and it didn’t help me one tiny bit just made my headache 100x worse'], ['Helps lower my blood sugar. I take 500 mg a day I live in the UK.'], ['paracetamol is the best and safe drug. its really amazing'], ["It is the ABSOLUTE WORST PAINKILLER to take when you have period pain. It does did not ease my period pain at all. I would not recommend it to anyone . DON'T TOUCH IT. I am very lucky now that I do not take Paracetamol anymore."], ["Paracetamol The only thing that works for me without any side effects, takes about 20 minutes to kick in, fantastic for muscle pain and anxiety attacks and insomnia, I take two 500mg tablets every 4 hours (four times a day), for two days then I'm okay."], ['Paracetamol has no pain- relief effect on me, whatsoever.'], ["I rate it 5. I've had a very high fever, and after taking Paracetamol, it only made it worse. That is why they suggested me to take Paracetamol every 4 hours. As a result, my fever is now gone, but my stomach is suffering. I currently have stomach/intestinal disturbances due to Paracetamol. This medicine is 50:50."], ['Does not work. Made me more ill than I am'], ['Administered an IV bolus of 600mg of Paracetamol to a patient in severe to moderate pain and patient suddenly started sleeping off but that was not expected so I checked and found the pulse unrecordable and BP not measurable. Quickly gave and IV bolus of saline and restored vitals and subsequently monitored patient for the next six hours. I think the effect of rapid administration IV should be hammered on.'], ["It's for fever and muscle pain. It's the best if you have a muscle pain after training or the next day. 30 minutes after taking the pill you will be just fine."], ['I have found Tylenol and other equivalents to be relatively ineffective in reducing pain associated with my Degenerative Disk Disease (Neck Pain, Severe Headaches, Lower Back Pain).  I have had some success with tramadol coupled with muscle relaxants, Tylenol with codeine and Vicodin (5 and 7.5 mg).  I also had good results with Aleve, until I started to have stomach problems.']]

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

senti_counts = {'positive': 0, 'neutral': 0, 'negative': 0}
for i in text:
    s=''
    for j in i:
        s+=j
    c=t_ex(s)
    #print(c)
    a1=sentiment_analyze(c)
    print(a1)
    if a1 =='1 star' or a1 == '2 stars':
        senti_counts['negative']+=1
    elif a1 == '3 stars':
        senti_counts['neutral']+=1
    elif a1 == '4 stars' or a1 == '5 stars':
        senti_counts['positive']+=1
print(senti_counts)