import requests
from bs4 import BeautifulSoup
from twilio.rest import Client

def get_score():
    url = 'https://www.cricbuzz.com/cricket-match/live-scores'
    res = requests.get(url)
    soup = BeautifulSoup(res.content, 'lxml')
    league_tab = soup.find('div', {'ng-show': "active_match_type == 'league-tab'"})
    if league_tab:
        match_id = league_tab.find('h3', {'class': 'cb-lv-scr-mtch-hdr'}
                            ).find('a')['href'].split('/')[2]
        cricbuzz_api = f'https://www.cricbuzz.com/api/cricket-match/commentary/{match_id}'
        res = requests.get(cricbuzz_api)
        commentary = res.json()['commentaryList']
        for comm in commentary:
            try:
                score = comm['overSeparator']['score']
                wickets = comm['overSeparator']['wickets']
                summary = comm['overSeparator']['o_summary']
                over = comm['overNumber']
                batteam = comm['batTeamName']
                break
            except:
                score = wickets = summary = over = batteam = None

        result = f'{batteam} {score}/{wickets} ({over})\nThis Over: {summary}'
        return result, over
    return

def send_message(message, over):
    if str(over)[-1] == '6':
        client = Client('ACff9de7df66412ff3ce720873c53679e5', '718d5f259973636c24927fbc774dedd3')
        client.messages.create(from_='whatsapp:+14155238886', to='whatsapp:+919677470417', body=message)

def main():
    result = get_score()
    if result:
        while True:
            message, over = result
            send_message(message, over)

main()