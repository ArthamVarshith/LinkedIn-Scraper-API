from flask import Flask, request, jsonify
import requests
import os
import time

app = Flask(__name__)

@app.route('/scrape', methods=['POST'])
def scrape():
    try:
        data = request.get_json(force=True)
        print("✅ Received data:", data)
    except Exception as e:
        print("❌ Error reading JSON:", e)
        return jsonify({"error": "Failed to parse JSON"}), 400

    keyword = data.get("keyword")
    api_key = data.get("api_key")

    if not keyword or not api_key:
        print("⚠️ Missing required fields")
        return jsonify({
            "error": "Missing keyword or SerpAPI key",
            "received_data": data
        }), 400

    print(f"🔍 Searching LinkedIn profiles on Google for: {keyword}")

    all_profiles = []
    seen = set()
    pages_scraped = 0
    max_pages = 10  # scrape up to 10 pages

    # Loop dynamically up to 10 pages
    for page in range(max_pages):
        start = page * 20  # Google pagination: 0, 20, 40, ...

        params = {
            "engine": "google",
            "q": f"{keyword} site:linkedin.com/in/",
            "num": 20,       # up to 20 results per page
            "start": start,
            "api_key": api_key
        }

        print(f"🌐 Fetching Google page {page+1} (start={start})...")
        try:
            response = requests.get("https://serpapi.com/search", params=params)
            response.raise_for_status()
            results = response.json()
        except Exception as e:
            print(f"⚠️ SerpAPI error on page {page+1}: {e}")
            continue

        organic_results = results.get("organic_results", [])
        if not organic_results:
            print(f"⚠️ No more results found after page {page+1}. Stopping early to save searches.")
            break  # stop making further API calls

        for item in organic_results:
            title = item.get("title", "")
            link = item.get("link", "")
            if "linkedin.com/in/" in link and link not in seen:
                all_profiles.append({
                    "name": title.replace(" | LinkedIn", "").strip(),
                    "url": link
                })
                seen.add(link)

        pages_scraped += 1
        time.sleep(1.5)  # prevent rate limit

    print(f"✅ Completed: {pages_scraped} pages scraped, {len(all_profiles)} profiles found.")

    return jsonify({
        "keyword": keyword,
        "pages_scraped": pages_scraped,
        "profiles_found": len(all_profiles),
        "profiles": all_profiles
    })


if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    print(f"🚀 Flask server running on http://0.0.0.0:{port}/scrape")
    app.run(host="0.0.0.0", port=port)
