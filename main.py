from fastapi import FastAPI, Form
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from rag_engine import ask_question

app = FastAPI(
    title="Arabic Legal AI Assistant 🇸🇦",
    description="استشارة قانونية ومالية وإدارية ذكية مبنية على القانون السعودي.",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Show form on homepage
@app.get("/", response_class=HTMLResponse)
def form_page():
    return """
    <html>
        <head>
            <meta charset="UTF-8">
            <title>المساعد القانوني الذكي</title>
            <style>
                body {
                    direction: rtl;
                    font-family: 'Tahoma', sans-serif;
                    background-color: #f0f0f0;
                    padding: 2em;
                }
                textarea {
                    width: 100%%;
                    height: 150px;
                    font-size: 16px;
                    padding: 1em;
                    direction: rtl;
                }
                .submit {
                    padding: 10px 20px;
                    font-size: 16px;
                }
            </style>
        </head>
        <body>
            <h2>📋 اكتب سؤالك القانوني هنا</h2>
            <form action="/ask/html" method="post">
                <textarea name="query" required></textarea><br><br>
                <button type="submit" class="submit">🔍 أرسل السؤال</button>
            </form>
        </body>
    </html>
    """

# Handle HTML form submission
@app.post("/ask/html", response_class=HTMLResponse)
def ask_html(query: str = Form(...)):
    try:
        answer = ask_question(query)
        html = f"""
        <html>
            <head>
                <meta charset="UTF-8">
                <style>
                    body {{
                        direction: rtl;
                        font-family: 'Tahoma', sans-serif;
                        background-color: #f0f0f0;
                        padding: 2em;
                    }}
                    .box {{
                        background: white;
                        padding: 2em;
                        border-radius: 12px;
                        box-shadow: 0 0 10px rgba(0,0,0,0.1);
                    }}
                </style>
            </head>
            <body>
                <div class="box">
                    <h3>🧠 السؤال:</h3>
                    <p>{query}</p>
                    <hr>
                    <h3>✅ الرد:</h3>
                    <p>{answer}</p>
                    <br><a href="/">🔙 العودة للسؤال</a>
                </div>
            </body>
        </html>
        """
        return HTMLResponse(content=html)

    except Exception as e:
        return HTMLResponse(
            content=f"<p style='color:red;'>❌ حصل خطأ: {str(e)}</p>",
            status_code=500
        )
