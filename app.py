import time
import requests
from flask import Flask, render_template, url_for, request, redirect
from serpapi import GoogleSearch
from bs4 import BeautifulSoup as soup
import textstat as test

app = Flask(__name__)

class Result:
    def __init__(self, title, url, difficulty, numScore):
        self.title = title
        self.url = url
        self.difficulty = difficulty
        self.numScore = numScore

@app.route('/', methods=['POST', 'GET'])
def index():
    if(request.method == 'POST'):
        searchQ = request.form['query']
        return redirect(url_for("searchq", query=searchQ))
    else:
        return render_template('index.html')

@app.route('/search/<query>')
def searchq(query=""):

    if(query == ""):
        return redirect(url_for("index"))

    results = []

    # Search Google for the top 8 results
    search = GoogleSearch({
        "engine": "google",
        "q": query,
        "location_requested": "United States",
        "location_used": "United States",
        "google_domain": "google.com",
        "hl": "en",
        "gl": "us",
        "safe": "active",
        "num": "8",
        "device": "desktop",
        "api_key": "857f08b5fbc7db9200955480a1742e5acdd6427938db5f88707d85e2cdf0c5aa"
    })

    SearchResult = search.get_dict()

    for dictionary in SearchResult.get('organic_results', []):
        link = dictionary.get('link')
        title = dictionary.get('title')

        try:
            headers = {'User-Agent': 'Mozilla/5.0'}
            response = requests.get(link, headers=headers, timeout=10)
            response.raise_for_status()
            webpage = response.text

            page_soup = soup(webpage, "html.parser")
            for script in page_soup(["script", "style"]):
                script.extract()

            text = page_soup.get_text()

            if len(text.split()) >= 200:
                grade, score = diffGrader(text)
                result = Result(title, link, grade, score)
                results.append(result)

            time.sleep(1)  # polite delay to avoid getting blocked

        except Exception as e:
            print(f"Error fetching {link}: {e}")
            continue

    results = sorted(results, key=lambda x: x.numScore)

    return render_template('search.html', query=query, results=results)

def diffGrader(text):
    r = test.dale_chall_readability_score(text) - 2

    if r <= 4.9:
        grade = "4th Grade or Below"
    elif 5 <= r <= 5.4:
        grade = "5th Grade"
    elif 5.5 <= r <= 5.9:
        grade = "6th Grade"
    elif 6.0 <= r <= 6.4:
        grade = "7th Grade"
    elif 6.5 <= r <= 6.9:
        grade = "8th Grade"
    elif 7.0 <= r <= 7.4:
        grade = "9th Grade"
    elif 7.5 <= r <= 7.9:
        grade = "10th Grade"
    elif 8.0 <= r <= 8.4:
        grade = "11th Grade"
    elif 8.5 <= r <= 8.9:
        grade = "12th Grade"
    elif 9.0 <= r <= 9.2:
        grade = "College Freshman"
    elif 9.3 <= r <= 9.6:
        grade = "College Sophomore"
    elif 9.7 <= r <= 9.9:
        grade = "College Junior"
    else:
        grade = "College Grad. and above"

    return [grade, r]

if __name__ == "__main__":
    app.run(debug=True)
