# portfolio-news
AI news summaries for your stock portfolio.
This is a webapp that summarizes recent news for each stock in your portfolio. This way, you don't have to google company specific news, 
read the news provided by your brokerage service, waste your time on ads, scroll through unrelated news, read useless noise and low quality financial slop, and the best part is that all the news are automatically delivered to
you, summarized. I also got sick of the quality of financial news slop such as Zacks Investment Research which is 
objectively garbage. I made sure that such misleading, harmful and useless news sources are completely filtered out
and only important news with substance are kept. I also want to proudly highlight that I am doing my best to eliminate any analyst rating and recommendation from the news sources used, which do more harm than good. This is to make sure that investment decisions are made based on the investor's personal judgement rather than the opinions of some analyst who has 'revolutionary ideas' on a daily basis. Note that this a personal project, not commercial in any way.
Note that this platform, for now, only serves to report the latest news in a pleasant and concise way to
shareholders of equities. This is not an investing, data analysis or full scale analysis software by any means.
If the goal is intelligent and educated stock picking, I highly recommend the following resources:
Value Line, S&P Capital IQ, Value Investors Club, SEC Edgar, Mergent Atlas, magicformulainvesting.com, Investor Relations pages and
news sites for very high level insight gathering. This project aims at conveying news in a pleasant format that filters out
terrible news sources and unnecessary noise, producing a report for each stock in your portfolio which combines all the recent news.
I think this should be useful for retail investors to effectively read news, never miss a detail and save time by focusing on 
news that really matter. The medium term goal is to build a somewhat agentic value investing framework that integrates this project.

## Technical Requirements

To run this project locally, you will need:
- **Python 3.8+**
- **Node.js 16+**
- **Ollama** (for local LLM inference)
- **Llama 3 Model** (`llama3:8b`)

## Getting Started

### 1. Clone the Repository
```bash
git clone https://github.com/DevRobi/portfolio-news.git
cd portfolio-news
```

### 2. Backend Setup
Create a virtual environment and install dependencies:
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Frontend Setup
Install Node.js dependencies:
```bash
cd ../frontend
npm install
```

### 4. LLM Setup
Install [Ollama](https://ollama.com/) and pull the Llama 3 model:
```bash
ollama pull llama3:8b
ollama serve
```

### 5. Running the Application
Start the backend (in one terminal):
```bash
# In /backend
source venv/bin/activate
uvicorn main:app --reload
```

Start the frontend (in another terminal):
```bash
# In /frontend
npm run dev
```

Open your browser and navigate to `http://localhost:5173`.
