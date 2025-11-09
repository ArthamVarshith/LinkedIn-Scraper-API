from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

@app.route('/scrape', methods=['POST'])
def scrape():
    try:
        # Force JSON parsing even if headers are off
        data = request.get_json(force=True)
        print("✅ Received data:", data)
    except Exception as e:
        print("❌ Error reading JSON:", e)
        return jsonify({"error": "Failed to parse JSON"}), 400

    # Extract keyword and API key from the JSON body
    keyword = data.get("keyword")
    api_key = data.get("api_key")

    # Validate inputs
    if not keyword or not api_key:
        print("⚠️ Missing required fields")
        return jsonify({
            "error": "Missing keyword or SerpAPI key",
            "received_data": data
        }), 400

    print(f"🔍 Searching LinkedIn for: {keyword}")

    # Define search parameters
    params = {
        "engine": "google",
        "q": f"{keyword} site:linkedin.com/in/",
        "num": 50,
        "api_key": api_key
    }

    try:
        # Send the request to SerpAPI
        response = requests.get("https://serpapi.com/search", params=params)
        response.raise_for_status()
        results = response.json()
    except Exception as e:
        print("❌ SerpAPI error:", e)
        return jsonify({"error": f"SerpAPI request failed: {str(e)}"}), 500

    profiles = []
    for item in results.get("organic_results", []):
        title = item.get("title", "")
        link = item.get("link", "")
        if "linkedin.com/in/" in link:
            profiles.append({
                "name": title.replace(" | LinkedIn", "").strip(),
                "url": link
            })

    print(f"✅ Found {len(profiles)} profiles")

    return jsonify(profiles[:50])

if __name__ == '__main__':
    # Start the Flask server on port 10000
    print("🚀 Flask server running on http://127.0.0.1:10000/scrape")
    app.run(host="0.0.0.0", port=10000)
