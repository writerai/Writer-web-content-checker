import requests
from bs4 import BeautifulSoup
import csv

def crawl_website(start_url):
    """
    Crawls a website from a given start URL and returns a list of URLs.
    This is a very basic crawler; depending on the website structure, you might need a more sophisticated approach.
    """
    urls = [start_url]
    visited = set()

    for url in urls:
        if url in visited:
            continue
        print(f"Crawling: {url}")
        try:
            response = requests.get(url)
            soup = BeautifulSoup(response.content, "html.parser")
            for link in soup.find_all("a", href=True):
                if link['href'].startswith("http") and link['href'] not in visited:
                    urls.append(link['href'])
            visited.add(url)
        except Exception as e:
            print(f"Failed to crawl {url}: {e}")
    
    return list(visited)

def extract_text(url):
    """
    Extracts text from a given URL.
    """
    try:
        response = requests.get(url)
        soup = BeautifulSoup(response.content, "html.parser")
        return soup.get_text()
    except Exception as e:
        print(f"Failed to extract text from {url}: {e}")
        return ""

def send_text_to_api(text):
    """
    Sends extracted text to the REST API and returns the response.
    """
    url = "https://enterprise-api.writer.com/content/organization/organizationId/team/teamId/check"
    headers = {
        'accept': 'application/json',
        'content-type': 'application/json'
    }
    data = {
        "settings": {
            "passiveVoice": True,
            "wordiness": True,
            # Include all other settings as needed
        },
        "document": {
            "text": text
        }
    }
    response = requests.post(url, json=data, headers=headers)
    return response.json()

def save_results_to_csv(results, filename="results.csv"):
    """
    Saves parsed JSON responses into a CSV file.
    """
    keys = results[0].keys() if results else ["No data"]
    with open(filename, "w", newline='') as output_file:
        dict_writer = csv.DictWriter(output_file, keys)
        dict_writer.writeheader()
        dict_writer.writerows(results)

def main(start_url):
    urls = crawl_website(start_url)
    all_results = []

    for url in urls:
        text = extract_text(url)
        if text:
            response = send_text_to_api(text)
            # Assuming the API response is directly in the desired format for CSV saving
            all_results.append(response)

    save_results_to_csv(all_results)

if __name__ == "__main__":
    start_url = "http://example.com"  # Change this to the website you want to crawl
    main(start_url)
