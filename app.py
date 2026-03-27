import requests
from flask import Flask, request, render_template_string
from bs4 import BeautifulSoup
from collections import Counter
import math
import os
import re

app = Flask(__name__)

HTML = """
<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<title>TF-IDF 분석기</title>

<style>
body {
    margin: 0;
    font-family: 'Segoe UI', sans-serif;
    background: linear-gradient(135deg, #667eea, #764ba2);
    color: #333;
}

.container {
    max-width: 900px;
    margin: 40px auto;
    padding: 20px;
}

.card {
    background: white;
    border-radius: 16px;
    padding: 25px;
    margin-bottom: 20px;
    box-shadow: 0 10px 30px rgba(0,0,0,0.1);
}

h1 {
    text-align: center;
    color: white;
}

input {
    width: 75%;
    padding: 12px;
    border-radius: 8px;
    border: 1px solid #ddd;
}

button {
    padding: 12px 18px;
    border: none;
    border-radius: 8px;
    background: #667eea;
    color: white;
    cursor: pointer;
    transition: 0.3s;
}

button:hover {
    background: #5a67d8;
}

.table-container {
    overflow-x: auto;
}

table {
    width: 100%;
    border-collapse: collapse;
}

th, td {
    padding: 10px;
    text-align: center;
}

th {
    background: #667eea;
    color: white;
}

tr:nth-child(even) {
    background: #f2f2f2;
}

.tag-box {
    margin-top: 10px;
}

.tag {
    display: inline-block;
    background: #667eea;
    color: white;
    padding: 6px 10px;
    border-radius: 8px;
    margin: 4px;
    font-size: 14px;
}

.top-box {
    display: flex;
    flex-wrap: wrap;
    gap: 10px;
}

.top-item {
    flex: 1;
    min-width: 120px;
    background: #f5f7fa;
    padding: 10px;
    border-radius: 10px;
    text-align: center;
    font-weight: bold;
}

.error {
    color: red;
    text-align: center;
}
</style>
</head>

<body>

<h1>TF-IDF 분석기</h1>

<div class="container">

<div class="card">
<form method="post">
    <input name="url" placeholder="뉴스 링크 입력">
    <button type="submit">분석</button>
</form>
</div>

{% if error %}
<p class="error">{{error}}</p>
{% endif %}

{% if table %}

<div class="card">
<h3>📚 단어 사전</h3>
<div class="tag-box">
{% for word in words %}
<span class="tag">{{word}}</span>
{% endfor %}
</div>
</div>

<div class="card">
<h3>📊 TF-IDF 분석</h3>
<div class="table-container">
<table>
<tr>
<th>단어</th><th>빈도</th><th>TF</th><th>IDF</th><th>TF-IDF</th>
</tr>
{% for row in table %}
<tr>
<td>{{row.word}}</td>
<td>{{row.count}}</td>
<td>{{"%.6f"|format(row.tf)}}</td>
<td>{{"%.6f"|format(row.idf)}}</td>
<td>{{"%.6f"|format(row.tfidf)}}</td>
</tr>
{% endfor %}
</table>
</div>
</div>

<div class="card">
<h3>🔥 중요 키워드 TOP 5</h3>
<div class="top-box">
{% for word, value in top5 %}
<div class="top-item">
Top{{loop.index}}<br>
{{word}}<br>
({{"%.6f"|format(value)}})
</div>
{% endfor %}
</div>
</div>

{% endif %}

</div>

</body>
</html>
"""

@app.route("/", methods=["GET", "POST"])
def index():
    table = None
    top5 = None
    words = []
    error = None

    if request.method == "POST":
        try:
            url = request.form.get("url")

            response = requests.get(url)
            soup = BeautifulSoup(response.text, "html.parser")
            text = soup.get_text()

            words_all = re.findall(r'[가-힣]{2,}', text)

            stopwords = [
                '것','수','등','이','그','저','및','더','때',
                '중','의','를','에','에서','으로','하다','있다',
                '광고','추천','배너','기사','뉴스','오늘','구독','더보기','열기','전체',
                '노컷','노컷뉴스','댓글','바로가기'
            ]

            filtered = [w for w in words_all if w not in stopwords]

            count = Counter(filtered)
            top_words = count.most_common(15)

            words = [w for w, _ in top_words]

            total = len(filtered) if len(filtered) > 0 else 1

            tf = {w: c / total for w, c in top_words}
            idf = {w: math.log(2) for w, _ in top_words}
            tfidf = {w: tf[w] * idf[w] for w in tf}

            sorted_tfidf = sorted(tfidf.items(), key=lambda x: x[1], reverse=True)[:5]

            table = []
            for w, c in top_words:
                table.append({
                    "word": w,
                    "count": c,
                    "tf": tf[w],
                    "idf": idf[w],
                    "tfidf": tfidf[w]
                })

            top5 = sorted_tfidf

        except Exception as e:
            error = str(e)

    return render_template_string(HTML, table=table, top5=top5, words=words, error=error)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))