Send a new post notification email to ALL subscribers.

Usage: /send_post_launch <post_slug>
Example: /send_post_launch 20260226_mac_mini_claude_code_server

If no post_slug is provided, automatically detect the most recent post by sorting files in content/posts/ by filename (descending) and using the first one.

Steps:
1. If post_slug is not provided, run: `ls content/posts/*.md | sort -r | head -1` to find the most recent post
2. Read the post file at content/posts/<post_slug>.md
3. Extract from frontmatter: title, cover.image
4. Build the post URL: https://goatwang.github.io/posts/<post_slug>/
5. Build the cover image URL: https://goatwang.github.io{cover.image}
6. Read summary from newsletters/<post_slug>.md — if the file doesn't exist, generate a 2-3 sentence summary (in the same language as the post), save it to newsletters/<post_slug>.md, and tell the user
7. Read the HTML template from templates/email_notification.html
8. Show the user a preview of the email (subject, from, cover image URL, summary, post URL) and ask for approval
9. On approval, send the email using the Resend API:
   - Read API key from config.local.json (resend.api_key)
   - Read audience ID from config.json (resend.audience_id)
   - From: "GoatWang's Blog <jeremy@voieech.com>"
   - To: the full audience using `"to": "audience:{audience_id}"`
   - Subject: "New Post: {title}"
   - HTML body: read from templates/email_notification.html, replace placeholders {title}, {cover_image_url}, {summary}, {url}
10. Report delivery status

Use curl to call the Resend API.

When inserting the summary into the HTML, convert newlines to `<br>` and use `•` instead of `-` for bullet points. Minify the HTML into a single line before sending (remove newlines and collapse whitespace).

IMPORTANT: Always show preview and get user approval before sending. The user may want to edit the summary.
