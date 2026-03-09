You are a senior technical blog editor. The blog post content is provided below (or attached).

**Important**: The blog post has been annotated with paragraph IDs in the format `<!-- ¶N -->` (e.g., `<!-- ¶1 -->`, `<!-- ¶3:heading -->`). When referencing specific paragraphs or sections, always use these ¶ IDs.

## Task: Title Optimization

Generate **10 candidate titles** for this blog post, covering at least 4 of the following 5 style types:

### Style Types

1. **Authority Quote** — Lead with a named person/org and a quotable claim
   - e.g. "OpenAI's Researcher: 'We've Been Doing Encoding Detection Wrong for 30 Years'"
2. **Counter-Intuitive** — Challenge what readers think they know, use markers like "actually", "turns out", "not X — Y"
   - e.g. "The Python Library Everyone Trusts for Encoding Detection Is Almost Always Wrong"
3. **Data Shock** — Use specific numbers or contrasts to create impact
   - e.g. "From 12% to 97% Accuracy: How a Clean Room Rewrite Beat 20 Years of Heuristics"
4. **Suspense / Insider** — Create an information gap that compels the click
   - e.g. "The Encoding Bug That Silently Corrupts Millions of Files — And Nobody Talks About It"
5. **Practical / How-To** — Promise a concrete takeaway or lesson
   - e.g. "How I Rebuilt chardet From Scratch Using Only the Spec (And What I Learned)"

### Scoring Dimensions (rate each candidate 1-10)

| Dimension | Weight | What to evaluate |
|-----------|--------|-----------------|
| **Psychological trigger** | 0.30 | Curiosity gap, surprise, stakes, emotional hook |
| **Click appeal** | 0.30 | First-impression impact, rhythm, shareability, length (8-15 words ideal) |
| **Content accuracy** | 0.25 | Does the title honestly represent the post? No misleading hype |
| **Novelty** | 0.15 | Would the reader think "I haven't seen this angle before"? Avoid clichés |

### Self-Checks (each title must pass)

**Novelty**:
- Does the reader learn something new or see a familiar topic from an unexpected angle?
- Would a knowledgeable reader still think "that's interesting" rather than "I already knew that"?

**Readability**:
- Can a general developer understand the title in 3 seconds?
- No unexplained jargon, acronyms, or obscure references?
- Is the cause-effect or promise clear and concrete?

### Banned Patterns (overused, skip these)

- "X Is Dead" / "The Death of X"
- "X, Pair Programming, and the Future of Y"
- "Everything You Know About X Is Wrong"
- "I Tried X So You Don't Have To"

## Output Format

Present a ranked table of all 10 candidates:

| Rank | Title | Style | Psych | Click | Accuracy | Novelty | Weighted |
|------|-------|-------|-------|-------|----------|---------|----------|

Then recommend the **top 2** with a short rationale for each.

## Structured JSON Output

After your markdown analysis above, output a fenced JSON block with structured annotations. This enables an interactive viewer.

Include one annotation per title candidate.

```json
{
  "annotations": [
    {
      "paragraph_ids": ["¶1"],
      "dimension": "title",
      "action": "minor",
      "score": 8.2,
      "issue": "Counter-Intuitive style: 'The Python Library Everyone Trusts Is Almost Always Wrong' — strong curiosity gap, challenges assumptions"
    }
  ]
}
```

Field details:
- `paragraph_ids`: Always `["¶1"]` (title affects the opening)
- `dimension`: `"title"`
- `action`: `"minor"`
- `score`: The weighted ranking score from the scoring table
- `issue`: The title candidate text with its style type and brief rationale

**Language**: Match the post's language. If the post is in Traditional Chinese, write titles in Traditional Chinese.
