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
            font-family: Arial;
            background: #f5f7fa;
            text-align: center;
        }
        .box {
            width: 80%;
            margin: auto;
            margin-top: 40px;
            background: white;
            padding: 20px;
            border-radius: 10px;
        }
        input {
            width: 60%;
            padding: 10px;
        }
        button {
            padding: 10px;
            background: #4CAF50;
            color: white;
            border: none;
        }
        table {
            width: 100%;
            margin-top: 20px;
        }
        th {
            background: #4CAF50;
            color: white;
        }
    </style>
</head>
<body>

<div class="box">
<h2>TF-IDF 분석기</h2>

<form method="post">
    <input name="url" placeholder="기사 링크 입력">
    <button type="submit">분석</button>
</form>

{% if error %}
<p style="color:red;">{{error}}</p>
{% endif %}

{% if table %}
<h3>단어사전</h3>
<p>U = { {{words}} }</p>

<table border="1">
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

<h3>Top 5</h3>
<ul>
{% for word, value in top5 %}
<li>Top{{loop.index}}. {{word}} ({{"%.6f"|format(value)}})</li>
{% endfor %}
</ul>
{% endif %}

</div>

</body>
</html>
"""

@app.route("/", methods=["GET", "POST"])
def index():
    table = None
    top5 = None
    words_str = ""
    error = None

    if request.method == "POST":
        try:
            url = request.form.get("url")

            response = requests.get(url)
            soup = BeautifulSoup(response.text, "html.parser")
            text = soup.get_text()

            words = re.findall(r'[가-힣]{2,}', text)

            stopwords = [
                '것','수','등','이','그','저','및','더','때',
                '중','의','를','에','에서','으로','하다','있다',
                '광고','추천','배너','기사','뉴스','오늘','구독','더보기','열기','전체',
                '노컷','노컷뉴스','댓글','바로가기'
            ]

            filtered = [w for w in words if w not in stopwords]

            count = Counter(filtered)
            top_words = count.most_common(15)

            words_str = ", ".join([w for w, _ in top_words])

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

    return render_template_string(HTML, table=table, top5=top5, words=words_str, error=error)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))