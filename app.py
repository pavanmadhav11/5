from flask import Flask, render_template, request
from converter import python_to_mermaid

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def index():
    code = ""
    mermaid_code = ""
    if request.method == "POST":
        code = request.form["code"]
        mermaid_code = python_to_mermaid(code)
    return render_template("index.html", code=code, mermaid_code=mermaid_code)

if __name__ == "__main__":
    app.run(debug=True)
