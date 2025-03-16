from bs4 import BeautifulSoup
from urllib.request import urlopen, Request
import re


def scrape_ma():
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

            # Get the acceptance rate
            acceptance_rate_tag = card.select_one('ul.list-inline.text-sm.mb-3.text-muted li.h6')
            print(acceptance_rate_tag)

            if name_tag and tuition_tag and acceptance_rate_tag:
                full_name = name_tag.get_text(strip=True)
                name = full_name.split('Private')[
                    0].strip() if 'Private' in full_name else full_name  # Extract university name
                tuition = int(re.sub(r'[^0-9]', '', tuition_tag.get_text(strip=True)))  # Convert tuition to int
                acceptance_rate = re.search(r'\d+%', acceptance_rate_tag.get_text(strip=True))

                if acceptance_rate:
                    acceptance_rate = acceptance_rate.group()
                else:
                    acceptance_rate = 'N/A'

                data[name] = {"tuition": tuition, "acceptance_rate": acceptance_rate}
    return data


def main():
    university_data = scrape_ma()
    print(university_data)


if __name__ == "__main__":
    main()
