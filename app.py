<!DOCTYPE html>
<html lang="si">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Binance Signals VIP</title>
  <style>
    body {
      font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
      margin: 0;
      padding: 0;
      background-color: #12161c;
      color: #ffffff;
    }
    .container {
      padding: 20px;
      max-width: 500px;
      margin: auto;
    }
    /* Lock Screen Style */
    #lock-screen {
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      height: 90vh;
      text-align: center;
    }
    .lock-card {
      background: #1e2329;
      padding: 30px;
      border-radius: 12px;
      box-shadow: 0 4px 15px rgba(0,0,0,0.5);
      width: 100%;
      box-sizing: border-box;
    }
    input {
      padding: 14px;
      font-size: 16px;
      margin: 15px 0;
      border-radius: 8px;
      border: 1px solid #474d57;
      background: #2b313a;
      color: #fff;
      width: 100%;
      box-sizing: border-box;
      text-align: center;
    }
    button {
      padding: 14px;
      font-size: 16px;
      background: #f0b90b;
      color: #000;
      border: none;
      border-radius: 8px;
      cursor: pointer;
      font-weight: bold;
      width: 100%;
    }
    button:hover {
      background: #d9a307;
    }
    
    /* Main App Content Style */
    #app-content {
      display: none; /* Unlock වන තෙක් සඟවා ඇත */
    }
    .signal-card {
      background: #1e2329;
      padding: 15px 20px;
      border-radius: 10px;
      margin-top: 15px;
      border-left: 5px solid #f0b90b;
    }
    .green-text { color: #0ecb81; }
    .red-text { color: #f6465d; }
  </style>
</head>
<body>

  <!-- 1. Lock Screen (පළමු පාර විතරක් පෙනෙන කොටස) -->
  <div id="lock-screen" class="container">
    <div class="lock-card">
      <h2>🔒 VIP Access Required</h2>
      <p>Signals App එක Unlock කරගන්න ඔබට ලැබුණු Secret Key එක ඇතුළත් කරන්න:</p>
      
      <input type="password" id="secretKeyInput" placeholder="Enter Access Key Here">
      <button onclick="unlockApp()">UNLOCK APP</button>
      
      <p id="error-msg" style="color: #f6465d; display: none; margin-top: 15px; font-size: 14px;">
        ❌ වැරදි Access Key එකක්! නිවැරදි Key එක ඇතුළත් කරන්න.
      </p>
    </div>
  </div>

  <!-- 2. Main App Content (Unlock වූ පසු හැමදාම පෙනෙන කොටස) -->
  <div id="app-content" class="container">
    <h1 style="color: #f0b90b;">🚀 Binance Signals VIP</h1>
    <p>Welcome back! මෙන්න අද දවසේ Live Trading Signals:</p>

    <!-- Signal Card 01 -->
    <div class="signal-card">
      <h3>BTC / USDT (<span class="green-text">LONG</span>)</h3>
      <p><b>Entry Zone:</b> $62,500 - $63,000</p>
      <p><b>Take Profit 1:</b> $64,500</p>
      <p><b>Take Profit 2:</b> $66,000</p>
      <p><b>Stop Loss:</b> <span class="red-text">$61,200</span></p>
    </div>

    <!-- Signal Card 02 -->
    <div class="signal-card">
      <h3>ETH / USDT (<span class="green-text">LONG</span>)</h3>
      <p><b>Entry Zone:</b> $3,400 - $3,420</p>
      <p><b>Take Profit 1:</b> $3,550</p>
      <p><b>Stop Loss:</b> <span class="red-text">$3,320</span></p>
    </div>
    
    <!-- තවත් Signals මෙතැනට එකතු කරන්න -->
  </div>

  <script>
    // 🔑 ඔයා සල්ලි ගෙවන අයට දෙන Password / Secret Key එක මෙතැනට දාන්න:
    const MY_SECRET_KEY = "BINANCE2026"; 

    // Page එක ඕපන් වෙද්දීම කලින් එක පාරක් Unlock කරලද බලනවා
    window.onload = function() {
      if (localStorage.getItem("isAppUnlocked") === "true") {
        showMainApp();
      }
    };

    function unlockApp() {
      const userEnteredKey = document.getElementById("secretKeyInput").value;
      
      if (userEnteredKey === MY_SECRET_KEY) {
        // Phone එකේ Storage එකේ Permanently Save කරනවා "Unlocked" කියලා
        localStorage.setItem("isAppUnlocked", "true");
        showMainApp();
      } else {
        document.getElementById("error-msg").style.display = "block";
      }
    }

    function showMainApp() {
      document.getElementById("lock-screen").style.display = "none";
      document.getElementById("app-content").style.display = "block";
    }
  </script>
</body>
</html>
