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

# --- 1. THE FRONTEND (No changes needed, kept your UI) ---
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>LeadSniper Enterprise</title>
    <link href="https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700;900&family=Inter:wght@300;600&display=swap" rel="stylesheet">
    
    <style>
        body { margin: 0; overflow: hidden; font-family: 'Inter', sans-serif; color: white; background: #000; }
        #vanta-canvas { position: absolute; width: 100%; height: 100%; z-index: -1; }
        
        #intro-overlay {
            position: fixed; top: 0; left: 0; width: 100%; height: 100%;
            background: #000; z-index: 9999; display: flex;
            justify-content: center; align-items: center; flex-direction: column;
            cursor: pointer; transition: opacity 1s ease;
        }
        #intro-text { font-family: 'Orbitron', sans-serif; font-size: 2rem; color: #4facfe; animation: pulse 1.5s infinite; }
        
        .container {
            position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%);
            text-align: center; background: rgba(10, 20, 40, 0.7); padding: 50px;
            border-radius: 20px; border: 1px solid rgba(79, 172, 254, 0.3);
            backdrop-filter: blur(15px); box-shadow: 0 0 80px rgba(0, 150, 255, 0.2);
            max-width: 600px; width: 90%; opacity: 0; transition: opacity 1s ease;
        }

        h1 {
            font-family: 'Orbitron', sans-serif; font-size: 3.5rem; margin: 0 0 10px 0;
            background: linear-gradient(to right, #4facfe 0%, #00f2fe 100%);
            -webkit-background-clip: text; -webkit-text-fill-color: transparent;
            font-weight: 900; text-transform: uppercase; letter-spacing: 2px;
        }
        
        p { color: #88c0d0; font-size: 1.1rem; margin-bottom: 30px; }
        
        input {
            width: 80%; padding: 15px; border-radius: 5px; border: 1px solid #4facfe;
            background: rgba(0, 20, 40, 0.8); color: #00f2fe; font-family: 'Orbitron', sans-serif;
            font-size: 1.2rem; outline: none; margin-bottom: 25px; text-align: center;
            box-shadow: 0 0 15px rgba(79, 172, 254, 0.2);
        }
        
        button {
            padding: 15px 50px; border-radius: 5px; border: none; background: #4facfe;
            color: #000; font-family: 'Orbitron', sans-serif; font-weight: 900;
            font-size: 1.2rem; cursor: pointer; transition: all 0.3s ease;
            text-transform: uppercase; letter-spacing: 1px;
            box-shadow: 0 0 20px rgba(79, 172, 254, 0.5);
        }
        button:hover { transform: scale(1.05); background: #fff; box-shadow: 0 0 40px #fff; }
        
        @keyframes pulse { 0% { opacity: 0.5; } 50% { opacity: 1; } 100% { opacity: 0.5; } }
    </style>
</head>
<body>

    <div id="intro-overlay" onclick="enterSystem()">
        <div id="intro-text">CLICK TO INITIALIZE SYSTEM</div>
    </div>

    <div id="vanta-canvas"></div>
    
    <div class="container" id="main-interface">
        <h1>LEAD SNIPER</h1>
        <p>Target. Extract. Dominate.</p>
        
        <input type="text" id="query" placeholder="ENTER TARGET SECTOR (e.g. Gyms NY)">
        <br>
        <button id="btn" onclick="startScraping()">INITIATE SCAN</button>
        
        <p id="status"></p>
    </div>

    <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r134/three.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/vanta@latest/dist/vanta.globe.min.js"></script>
    
    <script>
        function speak(text) {
            const synth = window.speechSynthesis;
            const utterance = new SpeechSynthesisUtterance(text);
            utterance.pitch = 0.8; 
            utterance.rate = 0.9;
            utterance.volume = 1;
            synth.speak(utterance);
        }

        function enterSystem() {
            document.getElementById('intro-overlay').style.opacity = '0';
            setTimeout(() => {
                document.getElementById('intro-overlay').style.display = 'none';
                document.getElementById('main-interface').style.opacity = '1';
            }, 1000);

            speak("Welcome to Lead Sniper. System Online.");

            VANTA.GLOBE({
              el: "#vanta-canvas",
              mouseControls: true,
              touchControls: true,
              gyroControls: false,
              minHeight: 200.00,
              minWidth: 200.00,
              scale: 1.00,
              scaleMobile: 1.00,
              color: 0x4facfe,
              backgroundColor: 0x000000
            });
        }

        async function startScraping() {
            const query = document.getElementById('query').value;
            const status = document.getElementById('status');
            const btn = document.getElementById('btn');
            
            if (!query) { 
                speak("Error. No target specified.");
                status.innerText = "Please enter a search term."; 
                return; 
            }

            status.innerText = "Accessing Satellite Feed... Extracting Max 100 Leads...";
            status.style.color = "#4facfe";
            btn.disabled = true;
            btn.innerText = "SCANNING...";
            
            speak("Initiating scan. Please wait while we extract data.");

            try {
                const response = await fetch('/api/scrape', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({query: query})
                });
                
                const data = await response.json();
                
                if (data.download_url) {
                    speak("Extraction complete. Downloading file.");
                    status.innerText = "Extraction Complete. Downloading File.";
                    status.style.color = "#00ff00";
                    window.location.href = data.download_url;
                } else {
                    status.innerText = "Error: " + (data.error || "Timeout or Invalid Query");
                    status.style.color = "red";
                    speak("System Error. Extraction failed.");
                }
            } catch (e) {
                status.innerText = "System Timeout (Limit exceeded for Free Plan).";
                status.style.color = "red";
                speak("Connection timed out.");
            }
            
            btn.disabled = false;
            btn.innerText = "INITIATE SCAN";
        }
    </script>
</body>
</html>
"""

# --- 2. OPTIMIZED BACKEND ---

def run_scraper(search_query):
    chrome_options = Options()
    chrome_options.add_argument("--headless") 
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    # FIX: Added User Agent and Window Size so Google doesn't block us immediately
    chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36")
    chrome_options.add_argument("--window-size=1920,1080")
    
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    leads = []
    
    try:
        # FIX: Corrected the Google Maps URL
        url = f"https://www.google.com/maps/search/{search_query.replace(' ', '+')}"
        driver.get(url)
        time.sleep(4) # Wait for page to load

        # Find Scroll Container
        try:
            scrollable_div = driver.find_element(By.CSS_SELECTOR, 'div[role="feed"]')
            
            # --- OPTIMIZED SCROLL LOOP ---
            for _ in range(15): 
                driver.execute_script("arguments[0].scrollTop = arguments[0].scrollHeight", scrollable_div)
                time.sleep(2) 
                
                # Check current count
                current_items = driver.find_elements(By.CLASS_NAME, "Nv2PK")
                if len(current_items) >= 100:
                    print(f"Reached limit. Found {len(current_items)}")
                    break
        except Exception as e:
            print(f"Scroll Error: {e}")
            # If scroll fails, we just continue and scrape what is visible

        # --- EXTRACT DATA ---
        items = driver.find_elements(By.CLASS_NAME, "Nv2PK")
        
        count = 0
        for item in items:
            if count >= 100: 
                break
                
            try:
                # Basic extraction strategy - grabbing all text
                data = item.text.split('\n')
                if not data: continue
                name = data[0]
                
                if "Ad" not in name: 
                    # Cleaning up the details slightly
                    details_text = " | ".join(data[1:])
                    leads.append({
                        "Business Name": name,
                        "Details": details_text
                    })
                    count += 1
            except:
                continue
                
    except Exception as e:
        print(f"Major Error: {e}")
    finally:
        driver.quit()

    if not leads: return None
        
    filename = f"leads_{uuid.uuid4()}.csv"
    df = pd.DataFrame(leads)
    df.to_csv(filename, index=False)
    return filename

# --- 3. FLASK ROUTES ---

@app.route('/')
def home():
    return render_template_string(HTML_TEMPLATE)

@app.route('/api/scrape', methods=['POST'])
def scrape_endpoint():
    data = request.json
    file_path = run_scraper(data.get('query'))
    
    if file_path:
        return jsonify({"message": "Success", "download_url": f"/download/{file_path}"})
    else:
        return jsonify({"error": "Failed to find leads."}), 500

@app.route('/download/<filename>')
def download_file(filename):
    return send_file(filename, as_attachment=True)

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)


