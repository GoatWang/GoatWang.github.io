Write a newsletter summary for a blog post, saved to the newsletters/ folder.

Usage: /write_launch_newsletter [post_slug]

If no post_slug is provided, automatically detect the most recent post by sorting files in content/posts/ by filename (descending) and using the first one.

Steps:
1. If post_slug is not provided, run: `ls content/posts/*.md | sort -r | head -1` to find the most recent post
2. Read the post file at content/posts/<post_slug>.md
3. Extract from frontmatter: title
4. Extract all top-level headings (## headings; if none, use ### headings)
5. Read the full post content to understand the key takeaways
6. If newsletters/<post_slug>.md already exists:
   - Show the existing content to the user
   - Ask the user to confirm if they want to overwrite it
   - If they say no, stop
7. Write a newsletter summary in the same language as the post that:
   - Opens with 1-2 sentences that hook the reader and explain what they'll learn
   - Lists or rewrites ALL top-level headings as key topics covered in the post
   - Keeps it concise (aim for 5-10 lines)
   - Tone: informative, direct, makes the reader want to click through
8. Save the summary to newsletters/<post_slug>.md
9. Show the user the summary and ask if they want to edit anything

IMPORTANT: The goal is to let the audience know what they will learn from the post. Every top-level heading should be represented in the summary.
