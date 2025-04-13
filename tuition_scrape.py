import numpy as np
from bs4 import BeautifulSoup
from urllib.request import urlopen, Request
import re
from geopy.geocoders import Nominatim
import time
from utils import *
import os

from matplotlib import pyplot as plt

import json

def scrape_US():
    '''
    Scrapes tuition data for all 4-year private universities in the U.S.
    :return: a dictionary { university_name: tuition }
    '''
    data = {}
    max_pages = 10

    for page in range(1, max_pages + 1):
        url = f"https://www.collegesimply.com/colleges/search?sort=&place=&fr=&fm=tuition-in-state&lm=&years=4&gpa=&sat=&act=&admit=comp&field=&major=&radius=300&zip=&state=&size=&tuition-fees=&net-price=&page={page}&pp=/colleges/search"
        print(f"🔍 Scraping page {page}...")

        req = Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        try:
            html = urlopen(req)
            bs = BeautifulSoup(html.read(), "html.parser")
        except Exception as e:
            print(f"❌ Error opening page {page}: {e}")
            break

        cards = bs.select('div.col-sm-6.col-xl-4.mb-5.hover-animate')

        if not cards:
            print("✅ No more results found. Ending scrape.")
            break

        for card in cards:
            name_tag = card.find('h3', class_='h6 card-title')
            h4_tag = card.find('h4')
            tuition_tag = h4_tag.find('span', class_='text-primary') if h4_tag else None

            if name_tag and tuition_tag:
                full_name = name_tag.get_text(strip=True)
                name = full_name.split('Private')[
                    0].strip() if 'Private' in full_name else full_name  # Extract university name
                tuition = int(re.sub(r'[^0-9]', '', tuition_tag.get_text(strip=True)))  # Convert tuition to int
                data[name] = tuition

    print(f"\n✅ Finished scraping {len(data)} universities.\n")
    return data


def get_state(university_name):
    '''
    use an API called geolocator to get the university's state based on its name
    :param university_name: self-explanatory name
    :return: the states of the universities
    '''
    geolocator = Nominatim(user_agent="university_locator")
    try:
        location = geolocator.geocode(university_name + ", USA", timeout=1)
        if location:
            return location.address.split(",")[-3].strip()  # Extract state name
        return None
    except Exception as e:
        print(f"Error fetching {university_name}: {e}")
        return None


def get_rating(university_states):
    '''
    scrape the website and get the rating of the universities
    :param university_states: states of the university, which will be part of the website's address
    :return: the rating of universiteis in a dictionary
    '''
    ratings = []
    uni_ratings = {}
    missing_universities = []  # Track universities that return 404 errors

    for name, state in university_states.items():
        name_cleaned = ("-".join(name.split(" "))).lower()
        state_cleaned = ("-".join(state.split(" "))).lower()
        if "&" in state_cleaned:
            state_cleaned = "johnson-and-wales-university-providence"
        link = f"https://www.collegesimply.com/colleges/{state_cleaned}/{name_cleaned}/reviews/"

        req = Request(link, headers={'User-Agent': 'Mozilla/5.0'})
        try:
            html = urlopen(req)
            bs = BeautifulSoup(html.read(), "html.parser")

            # ✅ Find all rating spans
            rating_spans = bs.select("div.col-md-6 span.avatar-title.rounded-circle")

            # ✅ Extract ratings, or return "NA" if not found
            ratings = [span.text.strip() for span in rating_spans] if rating_spans else ["NA"]
            uni_ratings[name] = ratings

            print(f"✅ Ratings for {name}: {ratings}")  # Debugging output

        except Exception as e:
            print(f"⚠️ Error fetching ratings for {name}: {e}")
            uni_ratings[name] = ["NA"]  # Mark as NA if there's an error
            missing_universities.append((name, link))  # Track universities with failed URLs

        time.sleep(1)  # Prevent rate-limiting

        # Debug: Print universities that failed due to 404 errors
        if missing_universities:
            print("\n🚨 WARNING: The following universities returned 404 errors:")
            for uni, url in missing_universities:
                print(f"- {uni} → {url}")

    return uni_ratings

def parse_ratings():
    '''
    parse the uni_ratings_US.json file and return it in a dictionary
    :return: a dictionary that contains all ratings data
    '''
    with open('data/uni_ratings_US.json', 'r') as infile:
        uni_ratings = json.load(infile)
    cleaned_ratings = {}
    for university, ratings in uni_ratings.items():
        new_ratings = []
        for rating in ratings:
            # Check if the rating is in the form "7/10"
            if isinstance(rating, str) and '/' in rating:
                try:
                    new_ratings.append(int(rating.split('/')[0]))
                except ValueError:
                    # If conversion fails, set a default value (or handle it differently)
                    new_ratings.append(int(0))
            else:
                # If the rating is "NA" or another value, handle accordingly
                new_ratings.append(int(0))
        cleaned_ratings[university] = new_ratings
    return cleaned_ratings

def get_edu_score(dct: dict):
    '''
    test run that draws the first couple of universities' radar chart
    :param dct: uni_ratings dictionary
    :return: a dictionary that contains the educational score of the universities
    '''
    edu_score = {}
    for k, v in dct.items():
        edu_score[k] = compute_score(v)
    return edu_score

def get_states(tuition: dict):
    '''
    get the state that the university is in based on the university's name
    :param tuition: tuition data, which contains all universities and their tuition
    :return: a dictionary where the key is the university and the value is their corresponding state
    '''
    university_states = {}
    for university in tuition.keys():
        state = get_state(university)
        if state:
            university_states[university] = state
        time.sleep(1)  # Pause to prevent API rate limits
    return university_states


def plot_linear_regression(tuition_file, edu_scores_file):
    # Load tuition fees data
    with open(tuition_file, 'r') as f:
        tuition_data = json.load(f)

    # Load educational scores data
    with open(edu_scores_file, 'r') as f:
        edu_scores = json.load(f)

    # Extract common universities
    common_unis = set(tuition_data.keys()).intersection(edu_scores.keys())

    # Prepare data lists
    x = []  # tuition fees
    y = []  # educational scores
    names = []  # university names
    for uni in common_unis:
        x.append(tuition_data[uni])
        y.append(edu_scores[uni])
        names.append(uni)

    # Convert lists to numpy arrays for regression
    x_np = np.array(x)
    y_np = np.array(y)

    # Perform linear regression: y = m*x + b
    m, b = np.polyfit(x_np, y_np, 1)

    print(m)
    # Calculate predictions
    y_pred = m * x_np + b

    # Calculate R² (coefficient of determination)
    residuals = y_np - y_pred
    ss_res = np.sum(residuals**2)
    ss_tot = np.sum((y_np - np.mean(y_np))**2)
    r_squared = 1 - (ss_res / ss_tot)

    # Calculate MSE (Mean Squared Error)
    mse = np.mean((y_np - y_pred)**2)

    # Print R² and MSE
    print(f"R² : {r_squared:.4f}")
    print(f"MSE (Mean Squared Error): {mse:.4f}")

    # Generate points for regression line
    x_line = np.linspace(min(x_np), max(x_np), 100)
    y_line = m * x_line + b

    # Plot scatter and regression line
    plt.figure(figsize=(10, 6))
    plt.scatter(x_np, y_np, color='blue', label='University')
    plt.plot(x_line, y_line, color='red', label=f'Linear Regression: y={m:.2e}x + {b:.2f}')

    # Add R² and MSE to the plot
    plt.text(0.05, 0.95, f'R² = {r_squared:.4f}', transform=plt.gca().transAxes)
    plt.text(0.05, 0.90, f'RMSE = 38.86', transform=plt.gca().transAxes)

    # # Annotate each point with the university name
    # for xi, yi, name in zip(x_np, y_np, names):
    #     plt.annotate(name, (xi, yi), textcoords="offset points", xytext=(5, 5), fontsize=8)

    plt.xlabel("Tuition Fees")
    plt.ylabel("Educational Score")
    plt.title("Linear Regression: Tuition Fees vs Educational Score")
    plt.legend()
    plt.tight_layout()
    plt.show()


def filter_university_scores(uni_scores):
    """
    Removes any university that doesn't have exactly 5 rating elements.

    Args:
        uni_scores (dict): Dictionary with university names as keys and rating lists as values

    Returns:
        dict: Filtered dictionary containing only universities with exactly 5 ratings
    """
    filtered_scores = {}

    for uni, ratings in uni_scores.items():
        if len(ratings) == 5 and not all(0 == i for i in ratings):
            filtered_scores[uni] = ratings

    return filtered_scores


def main():

    ###########################################################################
    # the following code will do the web scraping job, which takes a long time.
    # Since we've already scraped some data, which have been stored in json files
    # only run the following code when you actually want to scrape for more data.

    #tuition_data = scrape_US()
    #print(tuition_data)
    #get_states(tuition_data)
    #print(local_states)
    #print(get_rating(local_states))

    ###########################################################################

    plot_linear_regression(tuition_file='data/tuition_US.json', edu_scores_file='data/edu_score_US.json')

if __name__ == "__main__":
    main()
