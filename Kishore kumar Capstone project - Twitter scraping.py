# importing the necessary libraries
import snscrape.modules.twitter as sntwitter
import pandas as pd
import pymongo
import base64
from datetime import datetime, timedelta

#scrapping twitter data

def scrape_twitter_data(keyword, start_date, 
                        end_date, tweet_limit):

    # Createing empty list to store data
    scraped_data = []

    # Use snscrape to scrape the data
    for i, tweet in enumerate(sntwitter.TwitterSearchScraper
                              (f'{keyword} since:{start_date} until:{end_date}').get_items()):
        if i >= tweet_limit:
            break
        scraped_data.append([tweet.date, tweet.id, tweet.url, tweet.content, tweet.user.username,
                             tweet.replyCount, tweet.retweetCount, tweet.lang, tweet.source, tweet.likeCount])

    # Converting the scraped data to a pandas dataframe
    df = pd.DataFrame(scraped_data, columns=['date', 'id', 'url', 'tweet content', 'user', 'reply count', 'retweet count',
                                             'language', 'source', 'like count'])
    return df

# storing the data in mongodb
def store_in_mongodb(data, keyword):
    # Connecting to the MongoDB server
    client = pymongo.MongoClient('mongodb://localhost:27017/')

    # Creating a new database and collection
    db = client['twitter_data']
    collection = db[keyword]

    # Insert the scraped data into the collection
    collection.insert_many(data.to_dict('records'))

# creating gui

import streamlit as st

def create_gui():
    # Create the GUI layout
    st.title("Kishore's Twitter Data Scraper")
    keyword = st.text_input('Enter the keyword or hashtag to search:')
    start_date = st.date_input('Select the start date:')
    end_date = st.date_input('Select the end date:')
    tweet_limit = st.number_input('Enter the number of tweets to scrape:', value=100)
    submit_button = st.button('Scrape Twitter Data')

    # When the submit button is clicked, scrape the data and store it in MongoDB
    if submit_button:
        # Convert the start and end dates to the required format
        start_date_str = datetime.strftime(start_date, '%Y-%m-%d')
        end_date_str = datetime.strftime(end_date + timedelta(days=1), '%Y-%m-%d')

        # Scrape the data
        data = scrape_twitter_data(keyword, start_date_str, end_date_str, tweet_limit)

        # Store the data in MongoDB
        store_in_mongodb(data, keyword)

        # Display the scraped data
        st.write(data)

        # Add buttons to download the data in CSV and JSON formats
        csv_button = download_button(data.to_csv(index=False), 'Download as CSV', 'data.csv')
        json_button = download_button(data.to_json(indent=4), 'Download as JSON', 'data.json')

        # Display the download buttons
        st.write(csv_button)
        st.write(json_button)

# creating button function
def download_button(object_to_download, 
                    download_filename, button_text):

#Generates a link to download the given object_to_download.

    # Convert the object to bytes
    if isinstance(object_to_download, bytes):
        object_to_download = object_to_download.decode('utf-8')

    # Generate a download link using the object and the download filename
    href = f'<a href="data:file/csv;base64,{base64.b64encode(object_to_download.encode()).decode()}" download="{download_filename}">{button_text}</a>'

    # Create the download button using Streamlit's st.markdown function
    return st.markdown(href, unsafe_allow_html=True)

create_gui()
