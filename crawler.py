import json
from datetime import datetime, timedelta
from pytz import UTC
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup

def scrape_bwin_tennis_odds():
    options = Options()
    options.headless = True
    driver = webdriver.Chrome(options=options)

    url = "https://sports.bwin.com/en/sports/tennis-5/betting"

    try:
        driver.get(url)

        WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.CLASS_NAME, "ng-star-inserted"))
        )

        html = driver.page_source
        soup = BeautifulSoup(html, "html.parser")

        grid_events = soup.find_all("div", class_="grid-event-wrapper")
        scraped_data = []

        event_groups = soup.find_all("ms-event-group")

        for event_group in event_groups:
            title = event_group.find("ms-league-header").find("div", class_="title").text.strip()

            for event in event_group.find_all("ms-event"):
                event_info_elem = event.find("ms-prematch-timer")
                if event_info_elem:
                    event_info = event_info_elem.text.strip()
                else:
                    event_info = "N/A"  # Or any default value you want to set

                if not event_info.startswith(('Today', 'Tomorrow')):
                    continue

                player_names = event.find_all("div", class_="participant")
                player1_name = player_names[0].text.strip()
                player2_name = player_names[1].text.strip()

                # event_datetime_str = event_info.split('/')[1].strip()
                event_info_parts = event_info.split('/')
                day_indicator = event_info_parts[0].strip()
                # Get today's date
                today_date =    datetime.now().date()
                if day_indicator == 'Today':
                    event_date = today_date
                elif day_indicator == 'Tomorrow':
                    event_date = today_date + timedelta(days=1)
                else:
                    # Handle other cases if needed
                    event_date = None

                # Parse the time part and create a datetime object
                event_time_str = event_info_parts[1].strip()
                event_time = datetime.strptime(event_time_str, "%I:%M %p").time()

                # Combine date and time into a datetime object
                event_datetime = datetime.combine(event_date, event_time)

                # Convert to UTC timezone
                event_datetime_utc = UTC.localize(event_datetime)    

                

                odds_elements = event.find_all("ms-font-resizer")
                if len(odds_elements) >= 2:
                    odds = [option.text.strip() for option in odds_elements]
                else:
                    odds = ["N/A", "N/A"]

                # Get current time when constructing the data dictionary
                last_update = datetime.now().strftime("%Y-%m-%d %H:%M")

                data = {
                    "tournament": title,
                    "eventName": f"{player1_name} vs {player2_name}",
                    "player1": player1_name,
                    "player2": player2_name,
                    "player1_odds": odds[0],
                    "player2_odds": odds[1],
                    "eventDate": event_datetime_utc.strftime("%Y-%m-%d %H:%M"),
                    "lastUpdate": last_update
                }
                scraped_data.append(data)

        return scraped_data

    finally:
        driver.quit()

def save_to_json(data):
    with open("tennis_odds.json", "w") as json_file:
        json.dump(data, json_file, indent=2)

if __name__ == "__main__":
    data = scrape_bwin_tennis_odds()
    save_to_json(data)
