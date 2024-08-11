

def create_sentiment_bar_chart(sentiment):
#     # visualization.py
#     import matplotlib.pyplot as plt
#     import io
#     import base64
#     labels = ['Positive', 'Neutral', 'Negative']
#     values = [list[0],list[1],list[2]]

#     ax = plt.subplots()
#     ax.bar(labels, values, color=['green', 'gray', 'red'])
#     ax.set_xlabel('Sentiment')
#     ax.set_ylabel('Count')
#     ax.set_title('Sentiment Distribution')

#     # Save the plot to a PNG image in memory
#     img = io.BytesIO()
#     plt.savefig(img, format='png')
#     img.seek(0)

#     # Encode the image as a base64 string
#     plot_url = base64.b64encode(img.getvalue()).decode('utf8')

#     return plot_url


    import pandas as pd
    import matplotlib.pyplot as plt

    values = [sentiment[0],sentiment[1],sentiment[2]]
    labels=['pos','neu','negative']
    fig,ax = plt.subplots()
    ax.bar(labels,values)
    fig.savefig('static/my_plot.png')
