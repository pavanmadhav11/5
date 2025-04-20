import os
from flask import Flask, render_template, request
import google.generativeai as genai
from flask_cors import CORS
from converter import python_to_mermaid

app = Flask(__name__)
CORS(app)

try:
    genai.configure(api_key=os.getenv('GOOGLE_API_KEY'))
    model = genai.GenerativeModel('gemini-1.5-flash')
    print("Gemini configured successfully")
except Exception as e:
    print(f"Gemini config failed: {str(e)}")
    model = None

@app.route("/", methods=["GET", "POST"])
def index():
    code = mermaid_code = explanation = ""
    
    if request.method == "POST":
        code = request.form.get("code", "")
        mermaid_code = python_to_mermaid(code)
        
        if model and code.strip():
            try:
                prompt = f"""Analyze this Python code and provide a structured explanation:

                {code}

                Format your response EXACTLY as follows:

                **Code Name**

                **Code Purpose**
                
                <1-2 sentence description>

                **Key Components**
                
                1. • <component 1> - <description>
                
                2. • <component 2> - <description>
                
                3. • <component 3> - <description>

                **Execution Flow**
                
                1. <step 1 description>
                
                2. <step 2 description>
                
                3. <step 3 description>

                **Example Usage**
                
                • Input: <sample input>
                
                • Output: <expected output>

                Requirements:
                - Use **double asterisks** for section headings
                - Number all bullet points sequentially
                - Keep descriptions concise but clear
                - Provide a practical input/output pair"""
                
                response = model.generate_content(prompt)
                explanation = response.text
                
            except Exception as e:
                explanation = f"""**Error**
                Could not generate explanation.

                **Details**
                {str(e)}"""

    return render_template("index.html",
        code=code,
        mermaid_code=mermaid_code,
        explanation=explanation
    )

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv('PORT', 10000)))
