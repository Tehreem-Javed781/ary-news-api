"""REST API: GET /get?keyword=... on port 7000."""
import os

from flask import Flask, jsonify, request

from scraper import fetch_news
from summarizer import summarize

REGISTRATION = os.environ.get("REGISTRATION", "FA23-BDS-041")
NEWS_SOURCE = "ARY News Pakistan"

app = Flask(__name__)


@app.route("/")
def home():
    return f"""<!doctype html>
<html><head><title>Lab 4 - {REGISTRATION}</title></head>
<body style="font-family:sans-serif;max-width:720px;margin:40px auto">
  <h1>Selenium News Summarizer API</h1>
  <p><b>Registration:</b> {REGISTRATION}</p>
  <p><b>News source:</b> {NEWS_SOURCE}</p>
  <form action="/get" method="get">
    <input name="keyword" placeholder="Enter keyword" required>
    <button type="submit">Search</button>
  </form>
  <p>Usage: <code>/get?keyword=cricket</code></p>
</body></html>"""


@app.route("/get", methods=["GET"])
def get_news():
    keyword = (request.args.get("keyword") or "").strip()
    result = {
        "registration": REGISTRATION,
        "newssource": NEWS_SOURCE,
        "keyword": keyword,
        "url": "",
        "summary": "",
    }
    if not keyword:
        result["summary"] = "Please provide a keyword, e.g. /get?keyword=cricket"
        return jsonify(result), 400
    try:
        url, title, text = fetch_news(keyword)
        if not url:
            result["summary"] = "No article found for this keyword."
            return jsonify(result), 200
        result["url"] = url
        result["summary"] = summarize(text, 3) if text else title
    except Exception as e:
        result["summary"] = f"Error while scraping: {e}"
        return jsonify(result), 500
    return jsonify(result), 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=7000)
