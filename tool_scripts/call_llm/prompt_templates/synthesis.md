You are a senior editorial director. Below is a collection of review reports from multiple LLMs (Claude, Gemini, Grok) analyzing the same blog post across different dimensions: titles, tone rewrites, paragraph arrangement, and AI slop detection.

Your job is to synthesize these reports into a single, decision-ready summary that the author can act on immediately.

## Task: Cross-Model Synthesis

---

### 1. Title Recommendation (標題推薦)

All 3 models proposed title candidates. Your job:
- Identify **consensus picks** — titles or patterns that multiple models ranked highly
- Identify **unique gems** — strong titles only one model proposed
- Produce a **final top 3** with rationale, combining the best across all models
- If the models disagree significantly, explain the tradeoff (e.g., click-bait vs accuracy)

### 2. Tone Verdict (語氣判定)

Gemini and Grok each picked 2 tones and rewrote the full post. Your job:
- Which tones did each model pick? Do they overlap?
- Compare the rewrite quality: which model's rewrite is more engaging, more natural, more publishable?
- Identify the **single best rewrite** (or best sections from each) with specific paragraph references
- Note any sections where a tone rewrite significantly improved the original

### 3. Arrangement Verdict (結構判定)

Gemini proposed structural changes. Your job:
- Summarize the key structural moves proposed
- Evaluate: would these changes actually improve engagement, or are they rearranging for rearranging's sake?
- Give a clear **accept / reject / partially accept** verdict for each proposed change

### 4. AI Slop Report (AI 味評估)

Claude scored paragraphs on 9 AI-slop dimensions. Your job:
- Which paragraphs scored worst? List the top 3 with their scores
- Which dimensions are systemic across the whole post? (e.g., "hedging is consistently high")
- Are the AI slop findings consistent with what the tone/arrangement reviews flagged?

### 5. Final Action Plan (最終行動計畫)

Synthesize everything into a prioritized checklist:

| Priority | Action | Source | Expected Impact |
|----------|--------|--------|-----------------|
| 1 | ... | Which report(s) support this | High / Medium / Low |
| 2 | ... | ... | ... |
| ... | ... | ... | ... |

Keep it to **5-7 actions max**. The author should be able to read this table and start editing.

---

**Language**: If the original reports are in Traditional Chinese, write the synthesis in Traditional Chinese.
