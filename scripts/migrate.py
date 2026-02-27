#!/usr/bin/env python3
"""
Migration script: GoatWantsBlog (Hashnode) + Hexo → Hugo (PaperMod)

Source 1 (primary): /Users/wanghsuanchung/Projects/GoatWantsBlog/posts/ (21 markdown files)
Source 2 (fallback): /Users/wanghsuanchung/Projects/GoatWang.github.io/ (Hexo HTML)

Output: content/posts/<YYYYMMDD>_<title_slug>.md in Hugo format
"""

import os
import re
import shutil
import urllib.request
import urllib.error
import yaml
from pathlib import Path
from datetime import datetime

# Paths
GOATWANTSBLOG_DIR = Path("/Users/wanghsuanchung/Projects/GoatWantsBlog/posts")
HEXO_DIR = Path("/Users/wanghsuanchung/Projects/GoatWang.github.io")
HUGO_DIR = Path("/Users/wanghsuanchung/Projects/GoatWangBlog")
CONTENT_DIR = HUGO_DIR / "content" / "posts"
STATIC_DIR = HUGO_DIR / "static" / "images" / "posts"

# Mapping: source filename -> (output_filename, title, category)
# Based on the plan's complete post manifest
POST_MANIFEST = {
    "ir1-information-retrieval-1.md": ("20170421_ir1_information_retrieval", "Information Retrieval"),
    "ir2.md": ("20170422_ir2_evaluation", "Information Retrieval"),
    "deploy-indri-on-window-10-using-visual-studio.md": ("20170517_deploy_indri_windows", "Information Retrieval"),
    "logloss-function.md": ("20170602_logloss_function", "Machine Learning"),
    "train-wiki-corpus-by-gensim-word2vec.md": ("20170606_train_wiki_word2vec", "Information Retrieval"),
    "backup-mlab-mongodb-to-local-peroidically-by-c.md": ("20170624_backup_mongodb", "Tools & DevOps"),
    "use-facebook-api-to-login-aspnet-identity.md": ("20170625_facebook_api_aspnet", "Web Development"),
    "python.md": ("20170729_python_web_scraping_beginners", "Web Scraping"),
    "5asa5z36kgm57es5pct6ywn6z2e5zcm5q2l5oqa6kgt57ay6acb54is5yw.md": ("20170729_async_web_scraping", "Web Scraping"),
    "6z2e5zcm5q2l55qe57ay6acb54is5yw5oqa6kgt.md": ("20170822_multithread_async_scraping", "Web Scraping"),
    "2017-e8b387e69699e58886e69e90e5b8abe79a84e7b7b4e68890e4b98be8b7af-b6f8d222b301.md": ("20180306_data_analyst_journey_2017", "Career & Life"),
    "e99d9ee69cace7a791e7b3bbe8bd89e881b7e8bb9fe9ab94e5b7a5e7a88be5b8abe68c87e58d97-9c7783190178.md": ("20190929_career_change_software_engineer", "Career & Life"),
    "linebot-2-0-with-django-complete-tutorial-echo-bot-saving-userprofile-two-page-richmenu-ca15d9f8ae4c.md": ("20200212_linebot_django_tutorial", "Web Development"),
    "e4bc81e6a5ade5b08ee585a5aie58588e69c9fe5b088e6a188e68c87e58d97-e4b880-e69c6be970bc.md": ("20200309_enterprise_ai_guide", "AI & LLM"),
    "yolov4e4bdbfe794a8e68a80e8a193e88488e7b5a1e5bd99e695b4-backbone-4408869015c2.md": ("20210210_yolov4_backbone", "Computer Vision"),
    "trongispy-gise7b6b2e6a0bce8b387e69699e89995e79086e5b7a5e585b7-42815036b353.md": ("20210724_trongispy_gis_tool", "Tools & DevOps"),
    "bi-tempered-loss-e89995e79086e98cafe8aaa4e6a899e8a898e8b387e69699e79a84e6908de5a4b1e587bde695b8-7c3d561a2c6f.md": ("20210921_bi_tempered_loss", "Machine Learning"),
    "pinhole-camera-modele79086e8ab96e88887e5afa6e58b99-7c331ed79fdb.md": ("20220502_pinhole_camera_model", "Computer Vision"),
    "2023e5b9b4e8bd89e881b7e8b387e69699e7a791e5adb8e5aeb6e4b88de5868de59083e9a699-4f3a37101c0d.md": ("20240423_data_scientist_career_2023", "Career & Life"),
    "e696b0e58aa0e59da1e5b7a5e4bd9ce4b880e5b9b4e79a84e5bf83e5be97-017a8b9647f1.md": ("20241211_singapore_one_year", "Career & Life"),
    "redbullmcpai.md": ("20250415_redbull_mcp_ai", "AI & LLM"),
}

# Posts to skip
SKIP_POSTS = set()  # All 21 GoatWantsBlog posts are in the manifest


def parse_hashnode_frontmatter(content):
    """Parse YAML front matter from Hashnode markdown."""
    if not content.startswith("---"):
        return {}, content
    end = content.index("---", 3)
    fm_text = content[3:end].strip()
    body = content[end + 3:].strip()
    fm = yaml.safe_load(fm_text)
    return fm, body


def download_image(url, dest_path):
    """Download an image from URL to local path."""
    dest_path = Path(dest_path)
    if dest_path.exists():
        print(f"  [skip] Already exists: {dest_path.name}")
        return True
    dest_path.parent.mkdir(parents=True, exist_ok=True)
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=30) as resp:
            with open(dest_path, "wb") as f:
                f.write(resp.read())
        print(f"  [ok] Downloaded: {dest_path.name}")
        return True
    except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError) as e:
        print(f"  [FAIL] {url}: {e}")
        return False


def process_cdn_images(body, slug):
    """Find all cdn.hashnode.com images, download them, replace URLs."""
    img_dir = STATIC_DIR / slug
    # Pattern: matches both markdown images and raw URLs
    cdn_pattern = re.compile(
        r'(https://cdn\.hashnode\.com/res/hashnode/image/upload/[^\s\)"]+)'
    )
    urls_found = set()
    for match in cdn_pattern.finditer(body):
        urls_found.add(match.group(1))

    for url in urls_found:
        # Extract filename from URL
        filename = url.split("/")[-1]
        # Some URLs may have query params
        if "?" in filename:
            filename = filename.split("?")[0]
        local_path = img_dir / filename
        download_image(url, local_path)
        # Replace in body
        local_url = f"/images/posts/{slug}/{filename}"
        body = body.replace(url, local_url)

    return body


def process_cover_image(cover_url, slug):
    """Download cover image and return local path."""
    if not cover_url:
        return None
    filename = cover_url.split("/")[-1]
    if "?" in filename:
        filename = filename.split("?")[0]
    local_path = STATIC_DIR / slug / filename
    if download_image(cover_url, local_path):
        return f"/images/posts/{slug}/{filename}"
    return cover_url  # fallback to CDN URL if download fails


def strip_align_attrs(body):
    """Remove Hashnode align="..." from image markdown syntax."""
    # Pattern: ![...](url align="...") -> ![...](url)
    return re.sub(r' align="[^"]*"', '', body)


def convert_youtube_embeds(body):
    """Convert Hashnode %[youtube] and HTML iframe to Hugo shortcode."""
    # Hashnode format: %[https://youtu.be/ID] or %[https://www.youtube.com/watch?v=ID]
    def replace_hashnode_yt(m):
        url = m.group(1)
        vid_id = extract_youtube_id(url)
        if vid_id:
            return '{{< youtube ' + vid_id + ' >}}'
        return m.group(0)

    body = re.sub(r'%\[(https://(?:youtu\.be|www\.youtube\.com)[^\]]+)\]', replace_hashnode_yt, body)

    # HTML iframe: <iframe src="https://www.youtube.com/embed/ID"...></iframe>
    def replace_iframe_yt(m):
        url = m.group(1)
        vid_id = extract_youtube_id(url)
        if vid_id:
            return '{{< youtube ' + vid_id + ' >}}'
        return m.group(0)

    body = re.sub(
        r'<iframe\s+src="(https://www\.youtube\.com/embed/[^"]+)"[^>]*></iframe>',
        replace_iframe_yt, body
    )

    return body


def extract_youtube_id(url):
    """Extract YouTube video ID from various URL formats."""
    patterns = [
        r'youtu\.be/([a-zA-Z0-9_-]+)',
        r'youtube\.com/watch\?v=([a-zA-Z0-9_-]+)',
        r'youtube\.com/embed/([a-zA-Z0-9_-]+)',
    ]
    for pat in patterns:
        m = re.search(pat, url)
        if m:
            # Strip query params from ID
            vid_id = m.group(1).split("?")[0]
            return vid_id
    return None


def build_hugo_frontmatter(fm, category, slug, body):
    """Build Hugo-compatible front matter dict."""
    hugo_fm = {}
    hugo_fm["title"] = fm.get("title", "Untitled")

    # Parse date
    date_str = fm.get("date", "")
    if date_str:
        try:
            dt = datetime.fromisoformat(date_str.replace("Z", "+00:00"))
            hugo_fm["date"] = dt.strftime("%Y-%m-%dT%H:%M:%S+00:00")
        except (ValueError, TypeError):
            hugo_fm["date"] = date_str

    hugo_fm["draft"] = False
    hugo_fm["categories"] = [category]

    # Tags
    tags = fm.get("tags", [])
    if tags:
        hugo_fm["tags"] = tags

    # Summary from brief (first 200 chars, strip markdown)
    brief = fm.get("brief", "")
    if brief:
        # Clean up brief for summary
        summary = brief.replace("\n", " ").strip()
        if len(summary) > 200:
            summary = summary[:200] + "..."
        hugo_fm["summary"] = summary

    # Math detection
    if "$$" in body:
        hugo_fm["math"] = True

    # Cover image (will be set after download)
    cover_url = fm.get("cover", "")
    if cover_url:
        local_cover = process_cover_image(cover_url, slug)
        if local_cover:
            hugo_fm["cover"] = {"image": local_cover}

    return hugo_fm


def frontmatter_to_yaml(fm):
    """Convert front matter dict to YAML string."""
    return yaml.dump(fm, allow_unicode=True, default_flow_style=False, sort_keys=False).strip()


def migrate_goatwantsblog_post(src_file, output_name, category):
    """Migrate a single GoatWantsBlog post to Hugo format."""
    print(f"\n{'='*60}")
    print(f"Processing: {src_file.name} -> {output_name}.md")

    content = src_file.read_text(encoding="utf-8")
    fm, body = parse_hashnode_frontmatter(content)

    slug = output_name  # Use output name as slug

    # Process body transformations
    body = process_cdn_images(body, slug)
    body = strip_align_attrs(body)
    body = convert_youtube_embeds(body)

    # Build Hugo front matter
    hugo_fm = build_hugo_frontmatter(fm, category, slug, body)

    # Write output
    output_path = CONTENT_DIR / f"{output_name}.md"
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, "w", encoding="utf-8") as f:
        f.write("---\n")
        f.write(frontmatter_to_yaml(hugo_fm))
        f.write("\n---\n\n")
        f.write(body)
        f.write("\n")

    print(f"  -> Written: {output_path.name}")
    return True


def migrate_hexo_ithome_post():
    """Migrate the ithome ironman post from Hexo HTML."""
    from bs4 import BeautifulSoup
    import markdownify

    print(f"\n{'='*60}")
    print("Processing: Hexo ithome ironman post")

    src_html = HEXO_DIR / "2018/04/13/玩轉資料與機器學習-以自然語言處理為例（ithome鐵人競賽）/index.html"
    if not src_html.exists():
        print(f"  [FAIL] Source not found: {src_html}")
        return False

    html = src_html.read_text(encoding="utf-8")
    soup = BeautifulSoup(html, "html.parser")

    # Extract post body
    post_body = soup.find("div", class_="post-body")
    if not post_body:
        print("  [FAIL] Could not find post-body div")
        return False

    # Convert HTML to markdown
    body_md = markdownify.markdownify(str(post_body), heading_style="ATX")

    # Clean up the markdown
    # Remove excessive blank lines
    body_md = re.sub(r'\n{3,}', '\n\n', body_md)

    # Fix image path: /2018/04/13/.../encourage.JPG -> /images/posts/ithome_ironman/encourage.JPG
    body_md = body_md.replace(
        "/2018/04/13/玩轉資料與機器學習-以自然語言處理為例（ithome鐵人競賽）/encourage.JPG",
        "/images/posts/20180413_ithome_ironman_nlp_ml/encourage.JPG"
    )

    # Remove <a id="more"></a> or similar
    body_md = re.sub(r'<a id="more"></a>', '', body_md)

    # Copy encourage.JPG
    slug = "20180413_ithome_ironman_nlp_ml"
    img_src = HEXO_DIR / "2018/04/13/玩轉資料與機器學習-以自然語言處理為例（ithome鐵人競賽）/encourage.JPG"
    img_dest = STATIC_DIR / slug / "encourage.JPG"
    img_dest.parent.mkdir(parents=True, exist_ok=True)
    if img_src.exists():
        shutil.copy2(img_src, img_dest)
        print(f"  [ok] Copied: encourage.JPG")

    # Build front matter
    hugo_fm = {
        "title": "玩轉資料與機器學習-以自然語言處理為例（ithome鐵人競賽）",
        "date": "2018-04-13T00:00:00+00:00",
        "draft": False,
        "categories": ["Machine Learning"],
        "tags": ["machine-learning", "nlp", "ithome", "ironman"],
        "summary": "2017 ithome鐵人競賽：包含網路爬蟲、Pandas、自然語言處理、資訊檢索、機器學習等主題的30天文章索引。",
    }

    # Write output
    output_name = f"{slug}"
    output_path = CONTENT_DIR / f"{output_name}.md"

    with open(output_path, "w", encoding="utf-8") as f:
        f.write("---\n")
        f.write(frontmatter_to_yaml(hugo_fm))
        f.write("\n---\n\n")
        f.write(body_md.strip())
        f.write("\n")

    print(f"  -> Written: {output_path.name}")
    return True


def main():
    print("Hugo Blog Migration Script")
    print("=" * 60)

    # Ensure output directories exist
    CONTENT_DIR.mkdir(parents=True, exist_ok=True)
    STATIC_DIR.mkdir(parents=True, exist_ok=True)

    success_count = 0
    fail_count = 0

    # 1. Migrate GoatWantsBlog posts
    for src_filename, (output_name, category) in POST_MANIFEST.items():
        src_file = GOATWANTSBLOG_DIR / src_filename
        if not src_file.exists():
            print(f"\n[SKIP] Source not found: {src_filename}")
            fail_count += 1
            continue
        if migrate_goatwantsblog_post(src_file, output_name, category):
            success_count += 1
        else:
            fail_count += 1

    # 2. Migrate Hexo-only post (ithome ironman)
    if migrate_hexo_ithome_post():
        success_count += 1
    else:
        fail_count += 1

    print(f"\n{'='*60}")
    print(f"Migration complete!")
    print(f"  Success: {success_count}")
    print(f"  Failed:  {fail_count}")
    print(f"  Posts:   {CONTENT_DIR}")
    print(f"  Images:  {STATIC_DIR}")

    # Summary of images downloaded
    total_images = 0
    for dirpath, dirnames, filenames in os.walk(STATIC_DIR):
        total_images += len(filenames)
    print(f"  Total images: {total_images}")


if __name__ == "__main__":
    main()
