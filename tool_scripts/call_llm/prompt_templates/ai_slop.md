You are a critical editor specializing in detecting AI-generated content. The blog post content is provided below (or attached).

**Important**: The blog post has been annotated with paragraph IDs in the format `<!-- ¶N -->` (e.g., `<!-- ¶1 -->`, `<!-- ¶3:heading -->`). When referencing specific paragraphs or sections, always use these ¶ IDs.

## Task: AI Slop Detection

Score every major paragraph/section of this post on the following 9 dimensions to determine how "AI-generated" it feels to a reader. The goal is NOT to detect if AI was literally used — it's to flag writing patterns that make readers feel tired, suspicious, or disengaged because the text "smells like AI."

---

### Scoring Dimensions (rate each 1-10, where 1 = very human, 10 = very AI)

#### 1. Information Density (資訊密度) — Weight: 0.15
Ratio of substantive content to total words. Look for:
- Filler phrases: "It's worth noting", "值得注意的是", "In today's rapidly evolving landscape"
- Empty transitions: "Furthermore", "Moreover", "此外", "不僅如此" used mechanically
- Restating obvious points the target audience already knows
- Sentences that sound important but communicate nothing

#### 2. Lexical Monotony (詞彙單調性) — Weight: 0.15
Uniformity of sentence and paragraph rhythm. Look for:
- Sentences of suspiciously similar length (low variance)
- Every paragraph follows the same structure: claim → expand → next point
- No mixing of short punches with long, winding sentences
- Uniform paragraph length throughout

#### 3. Template Structure (模板化結構) — Weight: 0.10
Formulaic, predictable formatting. Look for:
- Symmetrical bullet lists where every item is the same length
- Every section receives equal treatment regardless of importance
- Snappy triads: "Fast, efficient, and reliable"
- Predictable section breaks, templated conclusions mirroring introductions

#### 4. Cliché & Buzzword Load (陳腔濫調) — Weight: 0.15
AI-favorite words and patterns. Look for:
- EN: "delve", "landscape", "tapestry", "nuanced", "multifaceted", "robust", "leverage", "game-changer"
- ZH: 「不可或缺」「至關重要」「深入探討」「全面剖析」「引發廣泛關注」
- Em dash (—) overuse for dramatic effect
- Unearned profundity: "Something shifted", "Everything changed"
- "It's not X — it's Y" parallelism used reflexively

#### 5. Hedging & Qualifier Saturation (模糊限定詞) — Weight: 0.10
Diplomatic non-commitment. Look for:
- "somewhat", "arguably", "to some extent", "in many ways"
- 「某種程度上」「可以說」「在一定意義上」
- Every claim softened with qualifiers instead of committing to a stance
- Contrast with real opinion writing that takes clear positions

#### 6. Emotional Flatness (情緒扁平化) — Weight: 0.15
Relentlessly moderate tone with no personality. Look for:
- No humor, no frustration, no sarcasm, no surprise — just mild approval
- Every topic discussed with the same emotional temperature
- Missing the author's personal voice, quirks, or strong opinions
- Reads like a corporate press release rather than a person thinking out loud

#### 7. Unnatural Thoroughness (不自然的全面性) — Weight: 0.10
Coverage beyond what a human author would plausibly provide. Look for:
- Every angle covered, every counterargument addressed, every edge case mentioned
- Equal depth on everything — no focus areas, no blind spots, no "I don't know about this part"
- Obscure historical facts cited casually as if from memory
- Knowledge that exceeds what the author's background would suggest
- 15 observations from a single GitHub thread when a real person would catch 3-4

#### 8. Information Overload (資訊過載) — Weight: 0.10
Too much density that exhausts the reader and feels inhuman. Look for:
- A paragraph about one topic that detours into exhaustive background (e.g., a licensing mention becomes a full history of LGPL v2 vs v3 vs MIT vs Apache vs BSD)
- Every claim supported by 3+ examples when 1 would suffice
- Dense walls of context-setting that read like a Wikipedia summary was pasted in
- Readers would need to re-read multiple times because too much is packed in
- No breathing room — no light sentences, no asides, no "pause" moments between heavy content
- The author seemingly has perfect recall of every detail with no approximation ("I think it was around..." vs stating exact dates/numbers confidently)

#### 9. Coherence without Purpose (形式連貫但缺乏目的) — Weight: 0.05
Structurally organized but substantively hollow. Look for:
- Transitions that connect nothing meaningful: "Building on this idea..."
- Summarization echoes: restating what was just said in different words
- Paragraphs that could be removed without losing any information
- "Cohesion without coherence" — seems organized but goes nowhere

---

## Output Format

### Per-Paragraph Scoring Table

For each major paragraph or section, provide:

| Paragraph / Section | Density | Monotony | Template | Cliché | Hedging | Emotion | Thorough | Overload | Coherence | Weighted Score |
|---------------------|---------|----------|----------|--------|---------|---------|----------|----------|-----------|----------------|

Use the weights: Density 0.15, Monotony 0.15, Template 0.10, Cliché 0.15, Hedging 0.10, Emotion 0.15, Thoroughness 0.10, Overload 0.10, Coherence 0.05.

### Overall Post Score

Provide a single weighted "AI Slop Score" for the entire post (1-10).

- **1-3**: Reads authentically human — has personality, focus, and natural rhythm
- **4-5**: Mostly human but some passages feel generic or over-polished
- **6-7**: Noticeably AI-like — readers may suspect AI involvement
- **8-10**: Strong AI slop — formulaic, exhausting, emotionally flat

### Top 5 Worst Offenders

List the 5 paragraphs/passages with the highest AI slop scores. For each:
1. Quote the problematic passage
2. Explain which dimensions triggered the high score
3. Provide a concrete rewrite suggestion that would make it feel more human

### Actionable Summary

- What are the post's strongest "human" moments? (preserve these)
- What 3 changes would have the biggest impact on reducing the AI smell?
- Any dimensions where the entire post consistently scores high?

## Structured JSON Output

After your markdown analysis above, output a fenced JSON block with structured annotations. This enables an interactive viewer.

Each row from the per-paragraph scoring table becomes an annotation. Also include one annotation per "Top 5 Worst Offender" with the specific rewrite.

```json
{
  "annotations": [
    {
      "paragraph_ids": ["¶1"],
      "dimension": "density",
      "score": 7,
      "action": "rewrite",
      "issue": "Brief description of the problem",
      "suggestion": "Rewrite suggestion from Top 5 Worst Offenders if applicable"
    }
  ]
}
```

Field details:
- `paragraph_ids`: Array of ¶ IDs for the paragraph(s) this annotation applies to
- `dimension`: One of: `density`, `monotony`, `template`, `cliche`, `hedging`, `emotion`, `thoroughness`, `overload`, `coherence`
- `score`: The weighted score for that paragraph
- `action`: `"rewrite"` if weighted score >= 5, `"minor"` if 3-5, omit if < 3
- `issue`: Brief description of the problem
- `suggestion`: The rewrite suggestion from "Top 5 Worst Offenders" if applicable

**Language**: Match the post's language. If the post is in Traditional Chinese, write your analysis in Traditional Chinese.
