

import os
import getpass
import gradio as gr
from google import genai
from google.genai import types

# Enter API key privately
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "").strip()

if not GEMINI_API_KEY:
    GEMINI_API_KEY = getpass.getpass(
        "Paste your Gemini API key (input stays hidden): "
    ).strip()

MODEL_NAME  = "gemini-3.1-flash-lite"  # Keep your currently selected model

# Create the API client once, instead of recreating it for every question.
client = genai.Client(api_key=GEMINI_API_KEY) if GEMINI_API_KEY else None

FAQS = [
    ("What is artificial intelligence?",
     "Artificial Intelligence (AI) is technology that enables computers to perform tasks such as learning, reasoning, recognizing patterns, and solving problems."),

    ("What is prompt engineering?",
     "Prompt engineering is the process of writing clear instructions to help an AI model produce more useful and accurate responses."),

    ("What is a large language model?",
     "A Large Language Model (LLM) is an AI model trained on large amounts of text to understand and generate language."),

    ("What is summarization?",
     "Summarization turns long text into a shorter version containing the main ideas."),

    ("What is text classification?",
     "Text classification assigns text to categories, such as positive/negative sentiment or spam/not spam."),

    ("What is a chatbot?",
     "A chatbot is software that communicates with people through text or voice."),
]


def local_faq(question):
    q = (question or "").lower().strip().rstrip("?!. ")

    for known_q, answer in FAQS:
        if q == known_q.lower().rstrip("?!. "):
            return answer

    words = set(q.replace("?", "").split())
    scored = []

    for known_q, answer in FAQS:
        score = len(
            words & set(known_q.lower().replace("?", "").split())
        )
        if score:
            scored.append((score, answer))

    if scored:
        return max(scored, key=lambda item: item[0])[1]

    return (
        "I couldn't find that in the built-in FAQ. "
        "Try asking about AI, prompt engineering, LLMs, "
        "summarization, classification, or chatbots."
    )


def run_assistant(mode, message):
    message = (message or "").strip()

    if not message:
        return "⚠️ Please type a question or paste text first."

    if mode == "FAQ":
        return local_faq(message)

    if not GEMINI_API_KEY:
        return (
            "🔑 Gemini API key was not provided. "
            "Restart this cell and enter a valid key when prompted."
        )

    instructions = {
        "Q&A": (
            "Answer accurately in simple, friendly language. "
            "Use examples when useful."
        ),
        "Summarization": (
            "Summarize the provided text in simple language. "
            "Give a short paragraph and key bullet points."
        ),
        "Classification": (
            "Classify the provided text and briefly explain the category. "
            "For sentiment, use positive, neutral, or negative."
        ),
        "Prompt Engineering": (
            "Improve the user's prompt. Show the improved prompt "
            "and briefly explain why it is better."
        )
    }

    try:
        # Shorter instructions + lower thinking/output limits can reduce latency.
        prompt = (
            instructions.get(mode, instructions["Q&A"])
            + " Reply concisely in simple language. Avoid unnecessary detail."
            + "\n\nUser input:\n"
            + message
        )

        response = client.models.generate_content(
            model=MODEL_NAME,
            contents=prompt,
            config=types.GenerateContentConfig(
                max_output_tokens=256,
                thinking_config=types.ThinkingConfig(
                    thinking_level="minimal"
                )
            )
        )

        answer = getattr(response, "text", None)

        return (
            answer if answer
            else "⚠️ Gemini returned an empty answer. Please try again."
        )

    except Exception as exc:
        details = str(exc)
        low = details.lower()

        if "429" in details or "quota" in low or "resource_exhausted" in low:
            return (
                "⚠️ **Gemini API quota limit reached.** "
                "Wait until your quota resets or use a Gemini API "
                "project with available quota. The FAQ mode still works.\n\n"
                "Technical details: " + details[:350]
            )

        if (
            "api key not valid" in low
            or "invalid api key" in low
            or "401" in details
            or "403" in details
        ):
            return (
                "🔑 **API key problem.** Check that you copied the "
                "correct key from Google AI Studio and that it is enabled. "
                "Do not share the key publicly.\n\n"
                "Technical details: " + details[:350]
            )

        if "model" in low and (
            "not found" in low or "not supported" in low
        ):
            return (
                "⚠️ **Model access problem.** Your API project may not "
                "have access to this model. Check available models "
                "in Google AI Studio.\nTechnical details: "
                + details[:350]
            )

        return (
            "⚠️ **Gemini request failed.** Check your internet connection, "
            "API key, model access, and quota.\n\nTechnical details: "
            + details[:350]
        )


# ============================================================
# THEME CSS
# Original Avengers theme and pure-white answer text preserved
# ============================================================

css = r"""
.gradio-container {
  background: radial-gradient(ellipse at 50% 0%, rgba(130,8,8,.34), transparent 43%),
              linear-gradient(145deg,#070707,#170707 54%,#050505) !important;
  color: #f8eeee !important;
}

footer {
  display: none !important;
}

#avengers-header {
  border: 1px solid #8f2525;
  border-radius: 22px;
  padding: 22px;
  background: linear-gradient(135deg,rgba(40,8,8,.98),rgba(8,8,8,.98) 68%);
  box-shadow: 0 0 30px rgba(255,20,20,.13), inset 0 0 22px rgba(150,0,0,.08);
  margin-bottom: 12px;
}

.hud {
  display: flex;
  justify-content: space-between;
  gap: 10px;
  flex-wrap: wrap;
  font: 700 11px Arial,sans-serif;
  letter-spacing: 2px;
  color: #d9b778;
}

.online {
  color: #ff5959;
}

.hero-layout {
  display: grid;
  grid-template-columns: 150px 1fr;
  gap: 22px;
  align-items: center;
  margin: 24px 0 16px;
}

.reactor {
  width: 132px;
  height: 132px;
  border-radius: 50%;
  margin: auto;
  display: flex;
  align-items: center;
  justify-content: center;
  background: radial-gradient(circle,#4d0808 0%,#160606 52%,#080808 72%);
  border: 2px solid #c79a4c;
  box-shadow: 0 0 28px #d7191944,inset 0 0 22px #ff303033;
}

.ring {
  width: 91px;
  height: 91px;
  border: 5px double #f04444;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  transform: rotate(-18deg);
}

.core {
  width: 42px;
  height: 42px;
  border-radius: 50%;
  background: radial-gradient(circle at 35% 30%,#ffe0bd,#ff3434 45%,#790000 80%);
  box-shadow: 0 0 26px #ff2727;
}

.hero-title {
  font: 900 clamp(25px,4vw,42px)/1.05 Arial,sans-serif;
  letter-spacing: 3px;
  color: #ff4040;
  text-shadow: 0 0 15px #a40000;
  margin: 0;
}

.hero-sub {
  color: #e4c17c;
  font: 700 12px Arial,sans-serif;
  letter-spacing: 3px;
  margin-top: 10px;
}

.hero-desc {
  color: #c8b5b5;
  font-size: 13px;
  line-height: 1.6;
  margin-top: 10px;
}

.team {
  display: grid;
  grid-template-columns: repeat(5,minmax(0,1fr));
  gap: 8px;
  margin-top: 18px;
}

.hero-card {
  text-align: center;
  border: 1px solid #4b2020;
  border-radius: 12px;
  background: linear-gradient(180deg,#230b0b,#0b0909);
  padding: 12px 4px;
}

.hero-icon {
  font-size: 25px;
  line-height: 1.4;
}

.hero-name {
  font-size: 10px;
  font-weight: 800;
  letter-spacing: .5px;
  color: #f3d9d9;
}

.hero-role {
  font-size: 9px;
  color: #d4ad71;
  margin-top: 4px;
}

button.primary {
  background: linear-gradient(90deg,#8e1111,#d82020) !important;
  border: 1px solid #e14b4b !important;
  color: white !important;
}

textarea {
  border-color: #572525 !important;
}

/* ===== ONLY CHANGE: MAKE ANSWERS PURE WHITE ===== */
.gradio-container .prose,
.gradio-container .prose p,
.gradio-container .prose li,
.gradio-container .prose strong,
.gradio-container .prose em,
.gradio-container .prose ul,
.gradio-container .prose ol,
.gradio-container .prose h1,
.gradio-container .prose h2,
.gradio-container .prose h3,
.gradio-container .prose h4 {
    color: #FFFFFF !important;
    opacity: 1 !important;
}
/* ===== END OF ANSWER COLOUR CHANGE ===== */

@media(max-width:650px) {
  .hero-layout {
    grid-template-columns: 1fr;
    text-align: center;
  }
  .team {
    grid-template-columns: repeat(3,minmax(0,1fr));
  }
  .reactor {
    width: 112px;
    height: 112px;
  }
}
"""


header = """
<div id="avengers-header">
  <div class="hud">
    <span>AVENGERS // AI INITIATIVE</span>
    <span class="online">● COMMAND SYSTEM READY</span>
  </div>

  <div class="hero-layout">
    <div class="reactor">
      <div class="ring">
        <div class="core"></div>
      </div>
    </div>

    <div>
      <h1 class="hero-title">AVENGERS<br>AI COMMAND</h1>
      <div class="hero-sub">
        INTELLIGENCE • ANALYSIS • KNOWLEDGE
      </div>
      <div class="hero-desc">
        Your AI learning station: ask questions, summarize notes,
        classify text, improve prompts, or search the built-in FAQ.
      </div>
    </div>
  </div>

  <div class="team">
    <div class="hero-card">
      <div class="hero-icon">🦾</div>
      <div class="hero-name">IRON CORE</div>
      <div class="hero-role">Q&amp;A</div>
    </div>

    <div class="hero-card">
      <div class="hero-icon">🛡️</div>
      <div class="hero-name">SHIELD</div>
      <div class="hero-role">SUMMARIZE</div>
    </div>

    <div class="hero-card">
      <div class="hero-icon">⚡</div>
      <div class="hero-name">THUNDER</div>
      <div class="hero-role">CLASSIFY</div>
    </div>

    <div class="hero-card">
      <div class="hero-icon">💥</div>
      <div class="hero-name">SMASH LAB</div>
      <div class="hero-role">PROMPTS</div>
    </div>

    <div class="hero-card">
      <div class="hero-icon">🧠</div>
      <div class="hero-name">KNOWLEDGE</div>
      <div class="hero-role">FAQ</div>
    </div>
  </div>
</div>
"""


with gr.Blocks(
    theme=gr.themes.Base(),
    css=css,
    title="Avengers AI Command Center"
) as demo:

    gr.HTML(header)

    gr.Markdown("### 🟥 Mission Console")

    mode = gr.Dropdown(
        choices=[
            "Q&A",
            "Summarization",
            "Classification",
            "Prompt Engineering",
            "FAQ"
        ],
        value="Q&A",
        label="Select Mission"
    )

    message = gr.Textbox(
        label="Your message / text",
        placeholder="Ask a question or paste text here...",
        lines=5
    )

    with gr.Row():
        run_btn = gr.Button(
            "⚡ RUN MISSION",
            variant="primary"
        )
        clear_btn = gr.Button("Clear Console")

    answer = gr.Markdown()

    gr.Markdown(
        "**FAQ works without a Gemini API key. Other modes use the "
        "key entered privately when this cell starts.**"
    )

    run_btn.click(
        fn=run_assistant,
        inputs=[mode, message],
        outputs=answer
    )

    message.submit(
        fn=run_assistant,
        inputs=[mode, message],
        outputs=answer
    )

    clear_btn.click(
        fn=lambda: ("", ""),
        inputs=None,
        outputs=[message, answer]
    )


print("Avengers AI Command Center ready. Launching app...")
demo.launch(share=True)
