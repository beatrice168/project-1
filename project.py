import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime , timezone

def scrape_tennis_odds():
    url="https://sports.bwin.com/en/sports/tennis-5/betting"
    response=request.get(url)
    if response.status_code==200:
        soup = BeautifulSoup(response.content, 'html.parser')
        tournaments = []

        #fiinding all the tournament countainers
        tournament_containers = soup.find_all('div', class_='marketboard-component-wrapper')
        for container in tournament_containers:
            tournament_name = container.find('div', class_='marketboard-header').text.strip()
            matches = container.find_all('div', class_='marketboard-event-with-header')
            for match in matches:
                event_name = match.find('span', class_='multiple-bets-description').text.strip()
                date_time_str = match.find('span', class_='multiple-bets-time').text.strip()
                event_date = datetime.strptime(date_time_str, '%d.%m.%Y %H:%M').strftime('%Y-%m-%d %H:%M')

                # Omit in-play matches
                if 'live' in match['class']:
                    continue

                odds = match.find_all('span', class_='option-button-label')
                player1_odds = odds[0].text.strip()
                player2_odds = odds[1].text.strip()

                tournament_data = {
                    "tournament": tournament_name,
                    "eventName": event_name,
                    "player1": event_name.split(' vs ')[0],
                    "player2": event_name.split(' vs ')[1],
                    "player1_odds": player1_odds,
                    "player2_odds": player2_odds,
                    "eventDate": event_date,
                    "lastUpdate": datetime.utcnow().strftime('%Y-%m-%d %H:%M')
                }
                tournaments.append(tournament_data)

        return tournaments

    else:
        print("Failed to retrieve page:", response.status_code)

def save_to_json(data):
    with open('tennis_odds.json', 'w') as file:
        json.dump(data, file, indent=4)

if __name__ == "__main__":
    data = scrape_tennis_odds()
    if data:
        save_to_json(data)
        print("Data saved successfully.")
    else:
        print("No data scraped.")
