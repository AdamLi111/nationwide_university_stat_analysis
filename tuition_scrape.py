from bs4 import BeautifulSoup
from urllib.request import urlopen, Request
import re
from geopy.geocoders import Nominatim
import time
from radar_chart import draw_radar_chart
import json

def scrape_NE():
    '''
    scrapes the tuition data of all universities in New England area
    :return: a dictionary with the name of the university be the key and tuition be the value
    '''
    data = {}
    ma_pages = 5
    for page in range(0, ma_pages + 1):
        MA_LINK = (
            f"https://www.collegesimply.com/colleges/search?sort=&place=&fr=&fm=tuition-in-state&lm="
            f"&years=4&type=private&gpa=&sat=&act=&admit=comp&field=&major=&radius=300&zip="
            f"&state=new-england&size=&tuition-fees=&net-price=&page={page}&pp=/colleges/search")
        req = Request(MA_LINK, headers={'User-Agent': 'Mozilla/5.0'})
        html = urlopen(req)
        bs = BeautifulSoup(html.read(), "html.parser")

        # Use CSS selector to find all college cards
        cards = bs.select('div.col-sm-6.col-xl-4.mb-5.hover-animate')

        for card in cards:
            # Get the university name from the <h3> tag
            name_tag = card.find('h3', class_='h6 card-title')
            # Get the tuition from the <span> tag within an <h4> tag
            h4_tag = card.find('h4')
            tuition_tag = h4_tag.find('span', class_='text-primary') if h4_tag else None

            if name_tag and tuition_tag:
                full_name = name_tag.get_text(strip=True)
                name = full_name.split('Private')[0].strip() if 'Private' in full_name else full_name  # Extract university name
                tuition = int(re.sub(r'[^0-9]', '', tuition_tag.get_text(strip=True)))  # Convert tuition to int
                data[name] = tuition
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
    parse the uni_ratings.json file and return it in a dictionary
    :return: a dictionary that contains all ratings data
    '''
    with open('uni_ratings.json', 'r') as infile:
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
                    new_ratings.append(None)
            else:
                # If the rating is "NA" or another value, handle accordingly
                new_ratings.append(None)
        cleaned_ratings[university] = new_ratings
    return cleaned_ratings

def try_drawing(dct: dict):
    '''
    test run that draws the first couple of universities' radar chart
    :param dct: uni_ratings dictionary
    :return: radar charts
    '''
    values = list(dct.items())
    print(values)
    for (k, v) in values[:5]:
        draw_radar_chart(k, v)

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

def main():

    ###########################################################################
    # the following code will do the web scraping job, which takes a long time.
    # Since we've already scraped some data, which have been stored in json files
    # only run the following code when you actually want to scrape for more data.

    #tuition_data = scrape_NE()
    #print(tuition_data)
    #get_states(tuition_data)
    #print(local_states)
    #print(get_rating(local_states))
    ###########################################################################

    uni_ratings = parse_ratings()
    try_drawing(uni_ratings)


if __name__ == "__main__":
    main()
