import time
import uuid
import os
import pandas as pd
from flask import Flask, jsonify, request, send_file, render_template_string
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager

app = Flask(__name__)

# --- 1. THE FRONTEND (Netflix Style 3D) ---
# We store the HTML inside this variable instead of a separate file
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>LeadSniper Enterprise</title>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;600;800&display=swap" rel="stylesheet">
    
    <style>
        body {
            margin: 0;
            overflow: hidden;
            font-family: 'Inter', sans-serif;
            color: white;
            display: flex;
            justify-content: center;
            align-items: center;
            height: 100vh;
            background: #000;
        }
        #vanta-canvas {
            position: absolute;
            width: 100%;
            height: 100%;
            z-index: -1;
        }
        .container {
            text-align: center;
            background: rgba(0, 0, 0, 0.6);
            padding: 50px;
            border-radius: 20px;
            border: 1px solid rgba(255, 255, 255, 0.1);
            backdrop-filter: blur(10px);
            box-shadow: 0 0 50px rgba(0, 150, 255, 0.2);
            max-width: 600px;
            width: 90%;
        }
        h1 {
            font-size: 3.5rem;
            margin: 0 0 10px 0;
            background: linear-gradient(to right, #4facfe 0%, #00f2fe 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            font-weight: 800;
            letter-spacing: -2px;
        }
        p { color: #aaa; font-size: 1.1rem; margin-bottom: 30px; }
        
        input {
            width: 80%;
            padding: 15px;
            border-radius: 30px;
            border: 1px solid rgba(255,255,255,0.2);
            background: rgba(0, 0, 0, 0.5);
            color: white;
            font-size: 1.2rem;
            outline: none;
            margin-bottom: 25px;
            text-align: center;
            transition: 0.3s;
        }
        input:focus {
            border-color: #4facfe;
            box-shadow: 0 0 20px rgba(79, 172, 254, 0.3);
        }
        button {
            padding: 15px 50px;
            border-radius: 30px;
            border: none;
            background: #4facfe;
            color: white;
            font-weight: bold;
            font-size: 1.2rem;
            cursor: pointer;
            transition: all 0.3s ease;
            text-transform: uppercase;
            letter-spacing: 1px;
        }
        button:hover {
            transform: scale(1.05);
            box-shadow: 0 0 30px #4facfe;
        }
        button:disabled { background: #333; cursor: not-allowed; }
        #status { margin-top: 25px; font-size: 0.9rem; min-height: 20px; }
    </style>
</head>
<body>
    <div id="vanta-canvas"></div>
    
    <div class="container">
        <h1>LEAD SNIPER</h1>
        <p>Global Geospatial Extraction System</p>
        
        <input type="text" id="query" placeholder="e.g. Dentists in London">
        <br>
        <button id="btn" onclick="startScraping()">INITIATE SCAN</button>
        
        <p id="status"></p>
    </div>

    <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r134/three.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/vanta@latest/dist/vanta.net.min.js"></script>
    <script>
        // 3D Background Effect
        VANTA.NET({
          el: "#vanta-canvas",
          mouseControls: true,
          touchControls: true,
          gyroControls: false,
          minHeight: 200.00,
          minWidth: 200.00,
          scale: 1.00,
          scaleMobile: 1.00,
          color: 0x4facfe,
          backgroundColor: 0x050505,
          points: 12.00,
          maxDistance: 22.00,
          spacing: 16.00
        })

        async function startScraping() {
            const query = document.getElementById('query').value;
            const status = document.getElementById('status');
            const btn = document.getElementById('btn');
            
            if (!query) { status.innerText = "Please enter a search term."; return; }

            // UI Update
            status.innerText = "Connecting to Satellite... Extracting Data...";
            status.style.color = "#4facfe";
            btn.disabled = true;
            btn.innerText = "SCANNING...";

            try {
                const response = await fetch('/api/scrape', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({query: query})
                });
                
                const data = await response.json();
                
                if (data.download_url) {
                    status.innerText = "Extraction Complete. Downloading File.";
                    status.style.color = "#00ff00";
                    window.location.href = data.download_url;
                } else {
                    status.innerText = "Error: " + (data.error || "Unknown issue");
                    status.style.color = "red";
                }
            } catch (e) {
                status.innerText = "System Error. Check logs.";
                status.style.color = "red";
            }
            
            // Reset UI
            btn.disabled = false;
            btn.innerText = "INITIATE SCAN";
        }
    </script>
</body>
</html>
"""

# --- 2. THE BACKEND LOGIC (With Scrolling) ---

def run_scraper(search_query):
    # Setup Chrome options for Render/Docker
    chrome_options = Options()
    chrome_options.add_argument("--headless") 
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--window-size=1920,1080")
    
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    leads = []
    
    try:
        # Construct URL
        url = f"https://www.google.com/maps/search/{search_query.replace(' ', '+')}"
        driver.get(url)
        time.sleep(4)  # Initial load

        # --- SCROLLING LOGIC FOR 100+ LEADS ---
        print("Starting scroll sequence...")
        try:
            # We look for the "feed" div where results live
            # Note: Selectors change often, but 'div[role="feed"]' is common for the sidebar
            scrollable_div = driver.find_element(By.CSS_SELECTOR, 'div[role="feed"]')
            
            # Scroll loop (20 times should get 80-120 results)
            for _ in range(20):
                driver.execute_script("arguments[0].scrollTop = arguments[0].scrollHeight", scrollable_div)
                time.sleep(2) # Give it time to load new boxes
                
                # Optional: Check if we have enough yet to speed things up
                count = len(driver.find_elements(By.CLASS_NAME, "Nv2PK"))
                if count >= 120:
                    break
        except Exception as e:
            print(f"Scroll Warning: {e}")

        # --- SCRAPING LOGIC ---
        items = driver.find_elements(By.CLASS_NAME, "Nv2PK") # The class for business cards
        print(f"Found {len(items)} items. Extracting text...")
        
        for item in items:
            try:
                # Get all text and split by lines
                data = item.text.split('\n')
                if not data: continue
                
                name = data[0]
                
                # Basic filter to remove Ads
                if "Ad" in name or "." in name[:2]: 
                    continue
                    
                leads.append({
                    "Business Name": name,
                    "Raw Details": " | ".join(data[1:]) # Joins address, rating, etc.
                })
            except:
                continue
                
    except Exception as e:
        print(f"Critical Error: {e}")
        return None
    finally:
        driver.quit()

    # Save to CSV
    if not leads:
        return None
        
    filename = f"leads_{uuid.uuid4()}.csv"
    df = pd.DataFrame(leads)
    df.to_csv(filename, index=False)
    return filename

# --- 3. FLASK ROUTES ---

@app.route('/')
def home():
    # Renders the HTML string we defined at the top
    return render_template_string(HTML_TEMPLATE)

@app.route('/api/scrape', methods=['POST'])
def scrape_endpoint():
    data = request.json
    query = data.get('query')
    
    if not query:
        return jsonify({"error": "No query provided"}), 400

    print(f"Received Request: {query}")
    file_path = run_scraper(query)
    
    if file_path:
        return jsonify({
            "message": "Success", 
            "download_url": f"/download/{file_path}"
        })
    else:
        return jsonify({"error": "Failed to extract data or no results found."}), 500

@app.route('/download/<filename>')
def download_file(filename):
    try:
        return send_file(filename, as_attachment=True)
    except Exception as e:
        return str(e), 404

if __name__ == '__main__':
    # Get PORT from Render, default to 5000
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)

