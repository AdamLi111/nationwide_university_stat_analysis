from bs4 import BeautifulSoup
from urllib.request import urlopen, Request
from urllib.parse import quote
import re
from geopy.geocoders import Nominatim
import time

def scrape_NE():
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
    ratings = []
    uni_ratings = {}
    missing_universities = []  # Track universities that return 404 errors

    for name, state in university_states.items():
        name_cleaned = ("-".join(name.split(" "))).lower()
        state_cleaned = ("-".join(state.split(" "))).lower()
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


def get_admission(university_states):
    missing_universities = []  # Track universities that return 404 errors

    for name, state in university_states.items():
        name_cleaned = ("-".join(name.split(" "))).lower()
        state_cleaned = ("-".join(state.split(" "))).lower()
        link = f"https://www.collegesimply.com/colleges/{state_cleaned}/{name_cleaned}/admission/"

        req = Request(link, headers={'User-Agent': 'Mozilla/5.0'})
        try:
            html = urlopen(req)
            bs = BeautifulSoup(html.read(), "html.parser")

            # ✅ Find all admission spans
            admission_element = bs.select_one("td.text-right.pr-0.font-weight-bold")

            # ✅ Extract ratings, or return "NA" if not found
            admission = admission_element.text.strip() if admission_element else ["NA"]

            print(f"✅ Admission Standards for {name}: {admission}")  # Debugging output

        except Exception as e:
            print(f"⚠️ Error fetching admission standard for {name}: {e}")
            admission = ["NA"]  # Mark as NA if there's an error
            missing_universities.append((name, link))  # Track universities with failed URLs

        time.sleep(1)  # Prevent rate-limiting

        # Debug: Print universities that failed due to 404 errors
        if missing_universities:
            print("\n🚨 WARNING: The following universities returned 404 errors:")
            for uni, url in missing_universities:
                print(f"- {uni} → {url}")
    return admission

def main():
    tuition_data = scrape_NE()
    print(tuition_data)
    university_states = {}
    # for university in tuition_data.keys():
    #     state = get_state(university)
    #     if state:
    #         university_states[university] = state
    #     time.sleep(1)  # Pause to prevent API rate limits

    local_states = {'Harvard University': 'Massachusetts', 'Boston University': 'Massachusetts', 'Yale University': 'Connecticut', 'Boston College': 'Massachusetts', 'Brown University': 'Rhode Island', 'Massachusetts Institute of Technology': 'Massachusetts', 'Northeastern University': 'Massachusetts', 'Dartmouth College': 'New Hampshire', 'Quinnipiac University': 'Connecticut', 'Tufts University': 'Massachusetts', 'Rhode Island School of Design': 'Rhode Island', 'Emerson College': 'Massachusetts', 'Babson College': 'Massachusetts', 'Amherst College': 'Massachusetts', 'Bentley University': 'Massachusetts', 'Brandeis University': 'Massachusetts', 'Williams College': 'Massachusetts', 'Providence College': 'Rhode Island', 'Dean College': 'Massachusetts', 'Wesleyan University': 'Connecticut', 'Fairfield University': 'Connecticut', 'Colby College': 'Maine', 'Sacred Heart University': 'Connecticut', 'Wellesley College': 'Massachusetts', 'Middlebury College': 'Vermont', 'Endicott College': 'Massachusetts', 'Bryant University': 'Rhode Island', 'Berklee College of Music': 'Massachusetts', 'University of New Haven': 'Connecticut', 'Merrimack College': 'Massachusetts', 'Assumption College': 'Massachusetts', 'Salve Regina University': 'Rhode Island', 'Suffolk University': 'Massachusetts', 'Curry College': 'Massachusetts', 'Worcester Polytechnic Institute': 'Massachusetts', 'Trinity College': 'Connecticut', 'University of Hartford': 'Connecticut', 'Norwich University': 'Vermont', 'Stonehill College': 'Massachusetts', 'Wentworth Institute of Technology': 'Massachusetts', 'Bowdoin College': 'Maine', 'Clark University': 'Massachusetts', 'Roger Williams University': 'Rhode Island', 'Simmons University': 'Massachusetts', 'Smith College': 'Massachusetts', 'Springfield College': 'Massachusetts', 'Emmanuel College': 'Massachusetts', 'Olin College of Engineering': 'Massachusetts', 'Western New England University': 'Massachusetts', 'American International College': 'Massachusetts', 'Mount Holyoke College': 'Massachusetts', 'Nichols College': 'Massachusetts', 'Mitchell College': 'Connecticut', 'College of the Holy Cross': 'Massachusetts', 'Champlain College': 'Vermont', 'Saint Anselm College': 'New Hampshire', 'Bates College': 'Maine', 'Wheaton College': 'Massachusetts', 'Fisher College': 'Massachusetts', 'Southern New Hampshire University': 'New Hampshire', 'University of New England': 'Maine', 'Lesley University': 'Massachusetts', 'University of Bridgeport': 'Connecticut', 'New England College': 'New Hampshire', 'Husson University': 'Maine', 'Becker College': 'Hamilton County', 'Lasell College': 'Massachusetts', 'Regis College': 'Massachusetts', 'Connecticut College': 'Connecticut', 'Gordon College': 'Massachusetts', 'Cambridge College': 'Massachusetts', 'Albertus Magnus College': 'Connecticut', "Saint Michael's College": 'Vermont', 'Anna Maria College': 'Massachusetts', 'Colby Sawyer College': 'New Hampshire', "Bard College at Simon's Rock": 'Massachusetts', 'Hampshire College': 'Massachusetts', 'Eastern Nazarene College': 'Massachusetts', 'Bennington College': 'Vermont', 'Benjamin Franklin Institute of Technology': 'Suffolk County', 'University of Saint Joseph': 'Connecticut', 'Boston Architectural College': 'Massachusetts', 'Franklin Pierce University': 'New Hampshire', 'New England Institute of Technology': 'Rhode Island', 'Green Mountain College': 'Vermont', 'College of Our Lady of the Elms': 'Massachusetts'}
    print(local_states)
    print(get_admission(local_states))
    #print(get_rating(local_states))


if __name__ == "__main__":
    main()
