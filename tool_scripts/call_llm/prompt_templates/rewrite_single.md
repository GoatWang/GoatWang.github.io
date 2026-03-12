You are rewriting a single paragraph of a blog post based on reviewer feedback and the author's instruction.

## Original paragraph
{content from stdin - the paragraph text}

The input will contain the following sections separated by `---`:
1. Original paragraph text
2. Reviewer feedback (dimension, issue, suggestion)
3. Author's comment/instruction

## Rules
- Follow the author's instruction as the primary guide
- Use the reviewer's suggestion as additional context
- Preserve the original language (if Chinese, write in Chinese)
- Preserve any markdown formatting, links, and emphasis
- Output ONLY the rewritten paragraph, nothing else
- Do not add explanations or commentary
