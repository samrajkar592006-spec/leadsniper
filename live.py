from flask import Flask, request, jsonify, send_file, render_template_string
from flask_cors import CORS
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import pandas as pd
import time
import uuid
import os

app = Flask(__name__)
CORS(app)

# --- THE UPGRADED 3D UI ---
HTML_CODE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>LeadSniper Enterprise</title>
    <link href="https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;800&family=Space+Grotesk:wght@700&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    
    <style>
        :root {
            --primary: #3b82f6;
            --accent: #8b5cf6;
            --dark: #020617;
            --glass: rgba(255, 255, 255, 0.05);
            --border: rgba(255, 255, 255, 0.1);
        }

        * { box-sizing: border-box; margin: 0; padding: 0; }

        body {
            background-color: var(--dark);
            color: white;
            font-family: 'Outfit', sans-serif;
            overflow-x: hidden;
            min-height: 100vh;
            background-image: 
                radial-gradient(circle at 15% 50%, rgba(59, 130, 246, 0.15), transparent 25%),
                radial-gradient(circle at 85% 30%, rgba(139, 92, 246, 0.15), transparent 25%);
            display: flex;
            flex-direction: column;
        }

        /* 3D Background Grid */
        .grid-bg {
            position: fixed;
            top: 0; left: 0; width: 100vw; height: 100vh;
            background-image: linear-gradient(var(--border) 1px, transparent 1px),
            linear-gradient(90deg, var(--border) 1px, transparent 1px);
            background-size: 50px 50px;
            opacity: 0.05;
            z-index: -1;
            transform: perspective(500px) rotateX(60deg) translateY(-100px) scale(2);
            pointer-events: none;
        }

        nav {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 20px 50px;
            backdrop-filter: blur(10px);
            border-bottom: 1px solid var(--border);
            position: sticky;
            top: 0;
            z-index: 100;
        }

        .logo {
            font-family: 'Space Grotesk', sans-serif;
            font-size: 24px;
            font-weight: 700;
            background: linear-gradient(to right, #60a5fa, #c084fc);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            letter-spacing: -1px;
            display: flex;
            align-items: center;
            gap: 10px;
        }

        .hero {
            flex-grow: 1;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            text-align: center;
            padding: 40px 20px;
            perspective: 1000px; /* Enables 3D space */
        }

        h1 {
            font-size: 64px;
            font-weight: 800;
            line-height: 1.1;
            margin-bottom: 20px;
            text-shadow: 0 0 40px rgba(59, 130, 246, 0.3);
        }
        
        h1 span { color: var(--primary); }

        .subtitle {
            font-size: 18px;
            color: #94a3b8;
            max-width: 600px;
            margin-bottom: 50px;
        }

        /* The 3D Card */
        .search-card {
            background: var(--glass);
            border: 1px solid var(--border);
            padding: 10px;
            border-radius: 20px;
            display: flex;
            gap: 10px;
            width: 100%;
            max-width: 700px;
            box-shadow: 
                0 25px 50px -12px rgba(0, 0, 0, 0.5),
                0 0 0 1px rgba(255, 255, 255, 0.1) inset;
            backdrop-filter: blur(20px);
            transition: transform 0.1s; /* Smooth movement */
            transform-style: preserve-3d;
        }

        input {
            background: transparent;
            border: none;
            color: white;
            font-size: 18px;
            padding: 20px;
            width: 100%;
            outline: none;
        }

        /* 3D Button */
        button {
            background: linear-gradient(135deg, var(--primary), var(--accent));
            color: white;
            border: none;
            padding: 20px 40px;
            border-radius: 14px;
            font-weight: 600;
            font-size: 16px;
            cursor: pointer;
            transition: all 0.2s;
            box-shadow: 
                0 10px 15px -3px rgba(59, 130, 246, 0.4),
                0 4px 0 #1e40af; /* 3D Edge */
            position: relative;
            overflow: hidden;
            display: flex;
            align-items: center;
            gap: 10px;
        }

        button:active {
            transform: translateY(4px); /* Pushes down */
            box-shadow: 0 0 0 #1e40af; /* Removes edge shadow */
        }

        button:disabled {
            opacity: 0.7;
            cursor: wait;
            transform: translateY(4px);
            box-shadow: none;
        }

        /* Status & Results */
        #status {
            margin-top: 50px;
            width: 100%;
            max-width: 700px;
            min-height: 60px;
        }

        .success-card {
            background: linear-gradient(145deg, #064e3b, #065f46);
            border: 1px solid #34d399;
            padding: 25px;
            border-radius: 16px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            animation: popIn 0.5s cubic-bezier(0.175, 0.885, 0.32, 1.275);
            box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.3);
        }

        .download-btn {
            background: white;
            color: #064e3b;
            padding: 12px 24px;
            border-radius: 8px;
            text-decoration: none;
            font-weight: 700;
            display: flex;
            align-items: center;
            gap: 8px;
            transition: transform 0.2s;
        }

        .download-btn:hover { transform: scale(1.05); }

        @keyframes popIn {
            from { opacity: 0; transform: scale(0.8) translateY(20px); }
            to { opacity: 1; transform: scale(1) translateY(0); }
        }
        
        @keyframes spin { 100% { transform: rotate(360deg); } }
    </style>
</head>
<body>

    <div class="grid-bg"></div>

    <nav>
        <div class="logo"><i class="fa-solid fa-crosshairs"></i> LeadSniper</div>
        <div style="font-size: 14px; opacity: 0.7;">ENTERPRISE V3.0</div>
    </nav>

    <div class="hero">
        <h1>Extract Leads <br> with <span>Precision</span></h1>
        <p class="subtitle">AI-powered extraction engine for Google Maps. Get verified B2B contacts instantly.</p>

        <div class="search-card" id="tiltCard">
            <input type="text" id="keyword" placeholder="e.g. Real Estate Agents in Dubai">
            <button id="scrapeBtn" onclick="startScrape()">
                <i class="fa-solid fa-bolt"></i> Start
            </button>
        </div>

        <div id="status"></div>
    </div>

    <script>
        // --- 3D TILT EFFECT SCRIPT ---
        const card = document.getElementById('tiltCard');
        document.addEventListener('mousemove', (e) => {
            const xAxis = (window.innerWidth / 2 - e.pageX) / 25;
            const yAxis = (window.innerHeight / 2 - e.pageY) / 25;
            card.style.transform = `rotateY(${xAxis}deg) rotateX(${yAxis}deg)`;
        });

        async function startScrape() {
            const query = document.getElementById('keyword').value;
            const statusDiv = document.getElementById('status');
            const btn = document.getElementById('scrapeBtn');
            
            if(!query) { alert("Please enter a keyword."); return; }
            
            // Loading State
            btn.innerHTML = '<i class="fa-solid fa-circle-notch fa-spin"></i> Working';
            btn.disabled = true;
            statusDiv.innerHTML = '<div style="color: #94a3b8; font-size: 14px; margin-top: 20px;">Initializing Neural Engine...</div>';
            
            try {
                const response = await fetch('/api/scrape', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ query: query })
                });
                const data = await response.json();
                
                if (data.download_url) {
                    statusDiv.innerHTML = `
                        <div class="success-card">
                            <div>
                                <h3 style="font-size: 18px; margin-bottom: 5px;"><i class="fa-solid fa-check-circle"></i> Extraction Complete</h3>
                                <p style="font-size: 14px; opacity: 0.9;">Successfully scraped ${data.count} leads</p>
                            </div>
                            <a href="${data.download_url}" class="download-btn"><i class="fa-solid fa-download"></i> Download CSV</a>
                        </div>`;
                } else { 
                    statusDiv.innerHTML = `<div style="color: #ef4444; margin-top: 20px;"><i class="fa-solid fa-triangle-exclamation"></i> Error: ${data.error}</div>`; 
                }
            } catch (e) { 
                statusDiv.innerHTML = `<div style="color: #ef4444; margin-top: 20px;">Server connection failed.</div>`; 
            }
            
            btn.innerHTML = '<i class="fa-solid fa-bolt"></i> Start'; 
            btn.disabled = false;
        }
    </script>
</body>
</html>
"""

@app.route('/')
def home():
    return render_template_string(HTML_CODE)

@app.route('/api/scrape', methods=['POST'])
def scrape_endpoint():
    data = request.json
    query = data.get('query')
    print(f"🚀 Processing: {query}")
    
    leads = []
    driver = None
    
    try:
        # --- DOCKER COMPATIBLE OPTIONS ---
        chrome_options = Options()
        chrome_options.add_argument("--headless") 
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
        
        # --- STANDARD SEARCH URL (More reliable) ---
        url = f"https://www.google.com/maps/search/{query.replace(' ', '+')}"
        driver.get(url)
        time.sleep(3) 
        
        cards = driver.find_elements(By.CLASS_NAME, "Nv2PK")
        for card in cards:
            try:
                text_all = card.text
                lines = text_all.split('\n')
                leads.append({"Business Name": lines[0], "Full Data": text_all.replace("\n", ", ")})
            except: continue
                
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"error": str(e)}), 500
    finally:
        if driver: driver.quit()

    filename = f"leads_{uuid.uuid4()}.csv"
    df = pd.DataFrame(leads)
    df.to_csv(filename, index=False)
    
    return jsonify({"message": "Success", "download_url": f"/download/{filename}", "count": len(leads)})

@app.route('/download/<filename>')
def download_file(filename):
    return send_file(filename, as_attachment=True)

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
