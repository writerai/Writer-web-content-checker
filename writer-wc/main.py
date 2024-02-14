import requests
from bs4 import BeautifulSoup
import csv
import io
import streamsync as ss
import pandas as pd
import nltk
from nltk.tokenize import sent_tokenize

nltk.download("punkt")

MAX_PAYLOAD_SIZE = 15000

def crawl(state):
    urls = state["urls"]
    visited = set(state["visited"])
    url = urls.pop(0)
    if url in visited:
        return crawl(state)

    print(f"Crawling: {url}")
    try:
        response = requests.get(url)
        if response.status_code != 200:
            print('status code:', response.status_code)
            crawl(state)
            return
        if not response.headers.get("content-type").startswith("text/html"):
            print('not html')
            crawl(state)
            return
        soup = BeautifulSoup(response.content, "html.parser")
        for link in soup.find_all("a", href=True):
            if link['href'].startswith("http") and link['href'] not in visited:
                urls.append(link['href'])
        visited.add(url)
        state["urls"] = urls
        state["visited"] = list(visited)
        state['counter'] = state['counter'] + 1
        text = soup.get_text()
        sents = sent_tokenize(text)
        req = ''
        for sent in sents:
            if len(req) + len(sent) < MAX_PAYLOAD_SIZE:
                req += sent
                continue
            _check_text(state, req, url)
            req = sent
        _check_text(state, req, url)
    except Exception as e:
        stop(state)
        print(e)
        state['message'] = (f"-Failed to crawl {url}: {e}")


def _check_text(state, text, url):
    results = state["results"]
    response = _send_text_to_api(state, text)
    print(response)
    if 'issues' in response:
        for issue in response['issues']:
            exp = {}
            exp['url'] = url
            exp['text'] = text[issue['from']:issue['until']]
            exp['url'] = url
            exp['service'] = issue['service']
            exp['suggestions'] = issue['suggestions']
            exp['description'] = issue['description']
            exp['meta'] = issue['meta']
            results.append(exp)
        state['results'] = results
        state['df'] = df = pd.DataFrame(data=results)

def _send_text_to_api(state, text):
    organization_id = state["organization_id"]
    team_id = state["team_id"]
    api_key = state["api_key"]
    list_of_settings = state["settings"]
    settings = {}
    for setting in list_of_settings:
        settings[setting] = True

    url = "https://enterprise-api.writer.com/content/organization/{organization_id}/team/{team_id}/check".format(
        organization_id=organization_id, team_id=team_id
    )
    headers = {
        'accept': 'application/json',
        'content-type': 'application/json',
        'Authorization': 'Bearer {api_key}'.format(api_key=api_key)
    }
    data = {
        "settings": settings,
        "content": text
    }
    response = requests.post(url, json=data, headers=headers)
    print(response.status_code)
    return response.json()

def start(state):
    start_url = state["start_url"]
    state["info"] = ""
    if start_url.strip() == "":
        print("Please set a Website URL")
        state["info"] = "!Please set a Website URL"
        return
    state["urls"] = [start_url]
    state["active"] = 'yes'
    state["status"] = "#00ff00"

def stop(state):
    state["status"] = "#ff0000"
    state["active"] = 'no'

def set_options(state, payload):
    print(payload)

initial_state = ss.init_state({
    "organization_id": "",
    "team_id": "",
    "api_key": "",
    "start_url": "",
    "urls": [],
    "visited": [],
    "results": [],
    "status": "#0000ff",
    "active": False,
    "df": pd.DataFrame(columns=['from', 'until', 'service', 'suggestions', 'description', 'meta', 'url'], data=[]),
    "counter": 0,
    "message": "",
    "info": "",
    "settings_description": {
        "passivevoice": "Passive voice",
        "wordiness": "Wordiness",
        "unclearreference": "Unclear reference",
        "genderinclusivepronouns": "Gender-inclusive pronouns",
        "genderinclusivenouns": "Gender-inclusive nouns",
        "ageandfamilystatus": "Age and family status",
        "disability": "Disability",
        "genderidentitysensitivity": "Gender identity sensitivity",
        "raceethnicitynationalitysensitivity": "Race, ethnicity and nationality sensitivity",
        "sexualorientationsensitivity": "Sexual orientation sensitivity",
        "substanceusesensitivity": "Substance use sensitivity",
        "confidence": "Confidence",
        "healthycommunication": "Healthy communication",
        "grammar": "Grammar",
        "spelling": "Spelling",
        "contentSafeguards": "Content Safeguards"
    },
    "settings": ["passivevoice", "wordiness"],
})

