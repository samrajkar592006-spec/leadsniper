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
import re

app = Flask(__name__)
CORS(app)

# --- THE "BILLION DOLLAR" UI (Clean, Modern, Trustworthy) ---
HTML_CODE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>LeadSniper Enterprise</title>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;800&display=swap" rel="stylesheet">
    <style>
        :root {
            --primary: #2563EB; /* Enterprise Blue */
            --dark: #0F172A;    /* Slate Black */
            --gray: #64748B;    /* Cool Gray */
            --bg: #F8FAFC;      /* Off White */
        }

        * { box-sizing: border-box; margin: 0; padding: 0; font-family: 'Inter', sans-serif; }
        
        body { background-color: var(--bg); color: var(--dark); }

        /* Navigation */
        nav {
            display: flex; justify-content: space-between; align-items: center;
            padding: 20px 60px; background: white; border-bottom: 1px solid #E2E8F0;
        }
        .logo { font-weight: 800; font-size: 20px; letter-spacing: -0.5px; color: var(--dark); display: flex; align-items: center; gap: 10px;}
        .logo span { background: var(--primary); color: white; padding: 2px 8px; border-radius: 6px; font-size: 14px;}
        .nav-links { display: flex; gap: 30px; font-size: 14px; font-weight: 500; color: var(--gray); }
        .nav-btn { background: var(--dark); color: white; padding: 10px 20px; border-radius: 8px; font-weight: 600; border: none; cursor: pointer;}

        /* Hero Section */
        .hero {
            max-width: 800px; margin: 100px auto; text-align: center; padding: 0 20px;
        }
        
        .badge {
            background: #EFF6FF; color: var(--primary); padding: 6px 16px; border-radius: 50px;
            font-size: 13px; font-weight: 600; display: inline-block; margin-bottom: 24px;
            border: 1px solid #BFDBFE;
        }

        h1 {
            font-size: 56px; line-height: 1.1; font-weight: 800; letter-spacing: -2px; margin-bottom: 20px; color: var(--dark);
        }

        p { color: var(--gray); font-size: 18px; line-height: 1.6; margin-bottom: 40px; }

        /* The Input Component */
        .search-container {
            background: white;
            padding: 8px;
            border-radius: 16px;
            box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04);
            display: flex;
            align-items: center;
            border: 1px solid #E2E8F0;
            transition: 0.3s;
        }

        .search-container:focus-within {
            border-color: var(--primary);
            box-shadow: 0 0 0 4px rgba(37, 99, 235, 0.1);
        }

        input {
            flex-grow: 1; border: none; outline: none; padding: 15px 20px; font-size: 16px; color: var(--dark); border-radius: 12px;
        }
        input::placeholder { color: #94A3B8; }

        button#scrapeBtn {
            background: var(--primary); color: white; border: none;
            padding: 16px 32px; border-radius: 10px; font-weight: 600; font-size: 16px;
            cursor: pointer; transition: 0.2s;
        }
        button#scrapeBtn:hover { background: #1D4ED8; transform: translateY(-1px); }
        button:disabled { opacity: 0.7; cursor: not-allowed; }

        /* Results Area */
        #status { margin-top: 40px; }
        
        .success-card {
            background: white; border: 1px solid #E2E8F0; padding: 30px; border-radius: 12px;
            display: inline-block; text-align: center; box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
        }
        
        .download-btn {
            display: inline-block; background: #10B981; color: white; padding: 12px 24px;
            border-radius: 8px; text-decoration: none; font-weight: 600; margin-top: 15px;
            box-shadow: 0 4px 14px 0 rgba(16, 185, 129, 0.39);
        }

        .loader {
            width: 24px; height: 24px; border: 3px solid #E2E8F0; border-bottom-color: var(--primary);
            border-radius: 50%; display: inline-block; animation: rotation 1s linear infinite;
        }
        @keyframes rotation { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }
        
        .trust-metrics {
            margin-top: 60px; display: flex; justify-content: center; gap: 40px; color: #94A3B8; font-size: 14px; font-weight: 500;
        }

    </style>
</head>
<body>

    <nav>
        <div class="logo">LeadSniper <span>PRO</span></div>
        <div class="nav-links">
            <span>Products</span>
            <span>Enterprise</span>
            <span>Pricing</span>
        </div>
        <button class="nav-btn">Sign In</button>
    </nav>

    <div class="hero">
        <div class="badge">v2.0 Algorithm Now Live</div>
        <h1>Unlock B2B Growth with <br> <span style="color: var(--primary)">Precision Data</span></h1>
        <p>Instantly extract verified business contacts from Google Maps.<br>Trusted by 10,000+ growth agencies worldwide.</p>
        
        <div class="search-container">
            <input type="text" id="keyword" placeholder="e.g. Interior Designers in New York">
            <button id="scrapeBtn" onclick="startScrape()">Start Extraction</button>
        </div>

        <div id="status"></div>

        <div class="trust-metrics">
            <span>🔒 SOC2 Compliant</span>
            <span>⚡ 99.9% Uptime</span>
            <span>🌍 Global Coverage</span>
        </div>
    </div>

    <script>
        async function startScrape() {
            const query = document.getElementById('keyword').value;
            const statusDiv = document.getElementById('status');
            const btn = document.getElementById('scrapeBtn');
            
            if(!query) { alert("Please enter a target industry."); return; }

            // UI Loading State
            btn.innerHTML = '<span class="loader"></span> Processing...';
            btn.disabled = true;
            statusDiv.innerHTML = "<p style='font-size:14px; color: var(--gray)'>Initializing Headless Browser & Scanning Maps...</p>";
            
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
                            <h3 style="margin-bottom:10px; color:var(--dark)">Extraction Complete</h3>
                            <p style="margin-bottom:0px; font-size:14px;">Found ${data.count} Verified Business Leads</p>
                            <a href="${data.download_url}" class="download-btn">Download CSV Report</a>
                        </div>
                    `;
                } else {
                    statusDiv.innerHTML = `<span style='color:red'>Error: ${data.error}</span>`;
                }
            } catch (e) {
                console.error(e);
                statusDiv.innerHTML = "<span style='color:red'>Server Connection Failed.</span>";
            }
            
            // Reset Button
            btn.innerHTML = 'Start Extraction';
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
        chrome_options = Options()
        chrome_options.add_argument("--start-maximized")
        # chrome_options.add_argument("--headless") # Uncomment for invisible mode
        
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
        
        url = f"https://www.google.com/maps/search/{query.replace(' ', '+')}"
        driver.get(url)
        time.sleep(4) 
        
        # Quick Scroll
        try:
            sidebar = driver.find_element(By.XPATH, "//div[@role='feed']")
            for _ in range(3):
                driver.execute_script("arguments[0].scrollTop = arguments[0].scrollHeight", sidebar)
                time.sleep(1.5)
        except:
            pass

        cards = driver.find_elements(By.CLASS_NAME, "Nv2PK")
        
        for card in cards:
            try:
                text_all = card.text
                lines = text_all.split('\n')
                name = lines[0]
                
                phone = "N/A"
                match = re.search(r'((\+91|0\d{2,4})?[ -]?)?\d{5}[ -]?\d{5}', text_all)
                if match:
                    phone = match.group(0)
                
                leads.append({
                    "Business Name": name,
                    "Phone": phone,
                    "Full Data": text_all.replace("\n", ", ")
                })
            except:
                continue
                
    except Exception as e:
        print(f"❌ Error: {e}")
        return jsonify({"error": str(e)}), 500
    finally:
        if driver:
            driver.quit()

    filename = f"leads_{uuid.uuid4()}.csv"
    df = pd.DataFrame(leads)
    df.to_csv(filename, index=False)
    
    return jsonify({
        "message": "Success", 
        "download_url": f"/download/{filename}",
        "count": len(leads)
    })

@app.route('/download/<filename>')
def download_file(filename):
    return send_file(filename, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True, port=5000)