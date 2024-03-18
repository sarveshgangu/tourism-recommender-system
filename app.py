import streamlit as st
import pickle
import requests

from sklearn.feature_extraction.text import CountVectorizer

from sklearn.metrics.pairwise import cosine_similarity
import pandas as pd
import nltk
from nltk.stem.porter import PorterStemmer

import googlemaps
import wikipedia





st.set_page_config(
    page_title="Hi TRS",
    page_icon="👋",
)


def search_images(query):
    # You need to provide your Custom Search Engine (CX) ID and API key
    cx = 'c567825322ab0463f'
    api_key = 'AIzaSyAAIfKsDhAXtL74w-oOnTm7OpJZM4twC5c'
    url = f"https://www.googleapis.com/customsearch/v1?q={query}&cx={cx}&imgSize=large&num=5&searchType=image&key={api_key}"
    response = requests.get(url)
    search_results = response.json()
    images = [item['link'] for item in search_results.get('items', [])]
    return images

# Initialize the Google Maps client with your API key
gmaps = googlemaps.Client(key='AIzaSyDPY3arhqaU-G9V7fIeDB0kdcsT6p7hvVA')




ps = PorterStemmer()

def stem(text):
    y = []

    for i in text.split():
        y.append(ps.stem(i))

    return " ".join(y)



def recommend(desc, num):
    txt = desc.lower()
    txt = stem(txt)
    txt_vector = cv.transform([txt]).toarray()

    similarity_array = cosine_similarity(txt_vector, vectors)

    rec_places = pd.DataFrame(places['place'], columns=['place'])
    rec_places['similarity'] = similarity_array[0]
    rec_places['popularity'] = places['popularity']
    rec_places['recommend_rating'] = rec_places['similarity'] * (1 + (rec_places['popularity'] / 2))

    # Selecting desired columns from places DataFrame
    selected_places = places[['place', 'city', 'timeofyear', 'popularity']]

    # Renaming the 'timeofyear' column to 'best-time-to-visit'
    selected_places.rename(columns={'timeofyear': 'best-time-to-visit'}, inplace=True)

    top_indices = rec_places.nlargest(num, 'recommend_rating').index

    # Extract the corresponding rows from the places DataFrame
    top_recommendations = selected_places.iloc[top_indices]

    top_recommendations.reset_index(drop=True, inplace=True)

    # Display the top recommendations
    st.write(top_recommendations)

    st.markdown("<h4 style='color:green; font-weight:bold;'>TOP 5 RECOMMENDED-PLACES</h4>", unsafe_allow_html=True)

    for index, row in top_recommendations.iterrows():
        place_name = row['place']

        # Search for the place
        place_result = gmaps.places(query=place_name)

        # Extract relevant information from the place result
        if place_result['status'] == 'OK':
            place_info = place_result['results'][0]
            place_name = place_info['name']
            location = place_info['geometry']['location']
            address = place_info.get('formatted_address', 'Address not available')
            rating = place_info.get('rating', 'Rating not available')

            try:
                wikipedia_page = wikipedia.page(place_name)
                description = wikipedia_page.summary
            except wikipedia.exceptions.PageError:
                description = "Description not available"

            images = search_images(place_name)

            # Print or use the information as needed
            st.write("Place:", place_name)
            st.write("Location:", location)
            st.write("Address:", address)
            st.write("Rating:", rating)
            st.write("Description:", description)
            st.write("Best-time-to-visit:", row['best-time-to-visit'])
            if len(images) >= 2:
                st.image([images[0], images[1]], caption=['Image 1', 'Image 2'], width=350)
            else:
                st.write("Images not available")
        else:
            st.write("Place search failed:", place_result['status'])






def text_based_recommendation():
    st.write("Enter the free-text: ")
    free_text = st.text_area( "Write anything...",
        value="", placeholder="'snow winter nature trekking' ... 'lake boating waterfall tiger' ...",
    )

    recommendations_count = st.number_input("How many recommendations do you want?", min_value=0, step=1)
    col1, col2 = st.columns([1, 3], gap="small")

    recommend_button = col1.button("Recommend")

    if recommend_button:
        recommend(free_text, recommendations_count)



def destination_based_recommendation():
    st.write("Text-based recommendation functionality is under development.")



vectors = pickle.load(open('vector.pkl', 'rb'))
cv = pickle.load(open('cv.pkl', 'rb'))

place = pickle.load(open('places.pkl', 'rb'))
places = pd.DataFrame(place)


st.title('Tourism Recommender System')

st.divider()

col1, col2 = st.columns(2)

with col1:
    st.markdown("<h4>Top Places to Visit in India</h4>", unsafe_allow_html=True)
    places1 = ['Taj Mahal', 'Amber Fort', 'Gateway of India', 'Qutub Minar', 'Agra fort']

    # Display places with indexing
    for index, place in enumerate(places1, start=1):
        st.write(f"{index}. {place}")


with col2:
    st.markdown("<h4>Top Cities with Most destinations</h4>", unsafe_allow_html=True)
    cities = ['Mumbai', 'New Delhi', 'Chennai', 'Bengaluru', 'Hyderabad']

    # Display places with indexing
    for index, city in enumerate(cities, start=1):
        st.write(f"{index}. {city}")


option = st.selectbox(
    'Which type of recommendation system do you prefer?',
    ('Recommendation based on free-text based query', 'Recommendations similar to previously visited destination'),
    index=None,
    placeholder="Select contact method...",
)

if option == 'Recommendation based on free-text based query':
    st.write('You selected:', option)
    text_based_recommendation()
elif option == 'Recommendations similar to previously visited destination':
    st.write('You selected:', option)
    destination_based_recommendation()






