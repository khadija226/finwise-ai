# FinWise AI 💰

**AI-Powered Personal Financial Analysis & Smart Budget Assistant**
*LangChain + Streamlit FinTech assignment — educational prototype only.*

## 🔗 Quick Links
| 🚀 Live App | 🎥 Demo Video |
|---|---|
| [Open FinWise AI](PASTE_STREAMLIT_APP_URL_HERE) | [Watch the demo](PASTE_DEMO_VIDEO_URL_HERE) |

> See [`DEPLOYMENT.md`](./DEPLOYMENT.md) for how these two links were produced,
> and how to update them once your app is live and your video is recorded.

> ⚠️ This app is for **education only**. It does not give guaranteed investment
> advice, does not execute real transactions, and is not connected to any real
> bank account. Always consult a qualified financial professional for real
> financial decisions.

## 🔑 About the API key
This app does **not** ship with a shared API key. Each visitor pastes their
**own** OpenAI API key into a password-style field in the sidebar before
running an analysis. It's kept only in that browser session (Streamlit
`session_state`) — never written to disk, logged, or sent anywhere except
directly to OpenAI to answer that person's own request.

---

## 1. What this app does

1. You enter your monthly income, ten expense categories, current savings, and a goal.
2. **Python** (`src/financial_calculator.py`) deterministically computes total
   expenses, remaining income, savings ratio, expense ratio, and a rule-based
   preliminary score (0–100).
3. Those numbers are inserted into **LangChain** prompts and sent to an OpenAI
   chat model.
4. The model returns **structured JSON** (financial summary, AI health score,
   spending analysis, risk level, priorities, budget/savings advice, and a
   next-month action plan).
5. Streamlit renders it all as a dashboard, and a second call **streams** a
   friendly written recommendation live into the UI.

## 2. Project structure

```
finwise_ai/
├── app.py                     # Streamlit UI — run this
├── requirements.txt
├── .env.example
├── README.md
├── src/
│   ├── __init__.py
│   ├── config.py               # settings + form options
│   ├── prompts.py               # PromptTemplate + ChatPromptTemplate + JSON schema
│   ├── financial_calculator.py  # deterministic maths — no AI
│   ├── chains.py                 # ChatOpenAI, LLMChain, streaming
│   ├── cache_manager.py          # in-memory + SQLite caching
│   └── utils.py                  # safe JSON parsing + helpers
└── docs/
    └── FinTech_AI_Assignment.pdf
```

## 3. Setup — step by step

### Step 1 — Create and activate a virtual environment
```bash
python -m venv venv

# Windows
venv\Scripts\activate

# macOS / Linux
source venv/bin/activate
```

### Step 2 — Install dependencies
You mentioned you already have most packages installed. Just make sure
**Streamlit** is added too (it is *not* in your original list):
```bash
pip install streamlit
```
Then install everything from the requirements file to be safe:
```bash
pip install -r requirements.txt
```

### Step 3 — Add your OpenAI API key (optional for local dev)
You have two options:

- **Easiest — just use the app:** run `streamlit run app.py` and paste your
  key straight into the sidebar's "Your OpenAI API Key" field. Nothing to
  configure.
- **Optional for local dev — use a `.env` file** so you don't have to
  retype the key every time:
  1. Go to https://platform.openai.com, sign in, and create an API key.
  2. Copy the example env file:
     ```bash
     # Windows
     copy .env.example .env
     # macOS / Linux
     cp .env.example .env
     ```
  3. Open `.env` and paste your key:
     ```
     OPENAI_API_KEY=sk-...
     ```
  4. `.env` should already be in `.gitignore` (add one if you don't have it)
     so the key is never pushed to GitHub. If both a `.env` key and a
     sidebar key are present, the sidebar key wins (so anyone using your
     deployed app always uses their own key).

### Step 4 — Run the app
```bash
streamlit run app.py
```
Streamlit will open `http://localhost:8501` in your browser.

### Step 5 — Use it
1. Fill in income, expenses (in the tabs), savings, and your goal.
2. Click **Analyze My Budget**.
3. Explore the **Financial Overview** metrics, then the **AI Financial
   Analysis** tabs (Overview / Spending Analysis / Action Plan / Rule-based vs AI).
4. In the Overview tab, click **Generate streaming recommendation** to watch
   the AI's advice type itself out live.
5. Use the sidebar to switch the cache backend or reset the session.

---

## 4. Python calculations vs. AI insights

| | Python (`financial_calculator.py`) | LangChain LLM (`chains.py`) |
|---|---|---|
| Total expenses, remaining income, ratios | ✅ computed deterministically | — |
| Preliminary 0-100 score | ✅ rule-based heuristic | — |
| Financial summary, risk level, priorities | — | ✅ generated as structured JSON |
| Budget recommendations, savings strategy, action plan | — | ✅ generated as structured JSON |
| Streamed narrative recommendation | — | ✅ generated live with `.stream()` |

The two are kept **strictly separate on purpose**: Python guarantees the same
numbers every time (auditable, no hallucination risk), while the LLM adds
qualitative reasoning and natural-language explanation on top of those
trusted numbers. The dashboard shows both scores side by side in the
**"Rule-based vs AI"** tab so you can compare them.

## 5. Caching explained

`set_llm_cache(...)` registers **one global cache** for all LangChain LLM
calls. Before making an API call, LangChain checks whether the exact same
prompt + model settings were already answered — if so, it returns the cached
answer instantly instead of calling OpenAI again (faster, and no extra cost).

| | In-Memory | SQLite |
|---|---|---|
| Where it lives | RAM | a `.finwise_cache.db` file on disk |
| Speed | fastest | fast, slightly slower |
| Survives an app restart? | ❌ No | ✅ Yes |
| Best for | a single working session | reusing answers across sessions/days |

Switch between them from the sidebar under **Caching**, or choose
"No caching" to force a fresh model call every time (useful when testing
prompt changes).

## 6. Testing scenarios

Try these five inputs (from the assignment brief) to sanity-check the app:

| # | Input | Expect |
|---|---|---|
| 1 | Income 8000, expenses ≈2000 | High score, LOW risk, growth-focused tips |
| 2 | Income 2000, expenses ≈2600 | Low score, HIGH risk, urgent cost-cutting |
| 3 | Income 5000, debt 2500 | MEDIUM/HIGH risk, debt-reduction priorities |
| 4 | Income 4000, savings 1200 | High score, LOW risk, reinforce good habits |
| 5 | Income 3000, expenses 3000 | MEDIUM/HIGH risk, "find room to save" |

## 7. Troubleshooting

| Problem | Fix |
|---|---|
| `ModuleNotFoundError: streamlit` | `pip install streamlit` |
| `ModuleNotFoundError: langchain_classic` | `pip install langchain-classic` |
| "No OPENAI_API_KEY found" warning | Make sure `.env` exists (not just `.env.example`) and has a real key, then restart `streamlit run app.py` |
| AI tab shows a generic fallback message | The model returned invalid JSON once — click **Analyze My Budget** again, or lower the temperature slider |
| Cache doesn't seem to speed things up | Make sure you selected a cache option and clicked **Apply cache setting**, then re-submit the *exact same* inputs |
| `sqlite3.OperationalError` on SQLite cache | Make sure the app has write permission in its folder; delete `.finwise_cache.db` and retry |

## 8. Bonus ideas (optional, not required)

CSV expense upload, expense charts, month-to-month comparison, PDF report
export, goal tracker, conversation history, dark/light mode, multi-currency
formatting, Docker deployment.

---

*Reminder: this project is for education only. It is not financial advice
and must not be used to make real investment or money decisions.*
