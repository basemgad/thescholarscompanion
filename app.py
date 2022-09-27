from flask import Flask, render_template, url_for, request, redirect
from urllib.request import Request, urlopen
from googlesearch import search
from bs4 import BeautifulSoup as soup
import textstat as test
#imports done

app = Flask(__name__)

class Result:
    def __init__(self, title, url, difficulty):
        self.title = title
        self.url = url
        self.difficulty = difficulty

@app.route('/', methods=['POST', 'GET'])
def index():
    if(request.method == 'POST'):
        searchQ = request.form['query']
        return redirect(url_for("searchq", query = searchQ))

    else:
        return render_template('index.html')

@app.route('/search/<query>')
def searchq(query = ""):

    if(query == ""):
        return redirect(url_for("index"))

    results = []
    #search google for the top 10 results of query search
    list = search(query, 10)
    for i in list :
        req = Request(i , headers={'User-Agent': 'Mozilla/5.0'})
        webpage = urlopen(req).read()
        page_soup = soup(webpage, "html.parser")
        for script in page_soup(["script", "style"]):
            script.extract()  
        text = page_soup.get_text()
        title = page_soup.find("title")
        title = title.string
        if(len(text.split()) >= 100):
            score = diffGrader(text)
            result = Result(title,i,score)
            results.append(result)

    results = sorted(results, key=lambda x: x.difficulty)

    return render_template('search.html', query=query, results=results) 

def diffGrader(text):
    r = test.dale_chall_readability_score(text)
    if(r <= 4.9):
        return "4th Grade or Below"
    elif(5 <= r <= 5.4):
        return "5th Grade"
    elif(5.5 <= r <= 5.9):
        return "6th Grade"
    elif(6.0 <= r <= 6.4):
        return "7th Grade"
    elif(6.5 <= r <= 6.9):
        return "8th Grade"
    elif(7.0 <= r <= 7.4):
        return "9th Grade"
    elif(7.5 <= r <= 7.9):
        return "10th Grade"
    elif(8.0 <= r <= 8.4):
        return "11th Grade"
    elif(8.5 <= r <= 8.9):
        return "12th Grade"
    elif(9.0 <= r <= 9.2):
        return "College Freshman"
    elif(9.3 <= r <= 9.6):
        return "College Sophomore"
    elif(9.7 <= r <= 9.9):
        return "College Junior"
    else:
        return "College Grad. and above"
    


if __name__ == "__main__":
    app.run(debug=True)