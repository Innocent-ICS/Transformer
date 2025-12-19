
import requests
import re
import sys
import json
import websocket
import time
import ssl
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

BASE_URL = "https://compute.ashesi.edu.gh/jupyterhub_103"
LOGIN_URL = f"{BASE_URL}/hub/login"
SPAWN_URL = f"{BASE_URL}/hub/spawn"
USER = "ptinibu"
PASS = "ptinibuics2025"
KEY = "ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAILcosJkYIAhdAFzyQ4S8Y1tTIBsDr+/TkKDy6H47MYHr innocentchikwanda@Innocents-MacBook-Air.local"

s = requests.Session()
s.headers.update({'User-Agent': 'Mozilla/5.0'})
s.verify = False

# 1. Login
print("Logging in...")
r = s.get(LOGIN_URL)
match = re.search(r'name="_xsrf" value="([^"]+)"', r.text)
xsrf = match.group(1) if match else ""
r = s.post(LOGIN_URL, data={"username": USER, "password": PASS, "_xsrf": xsrf})
if "login" in r.url:
    print(f"Login failed: {r.url}")
    sys.exit(1)
print(f"Logged in. URL: {r.url}")

# Handle spawn
if "/hub/spawn" in r.url:
    print("Spawning...")
    match = re.search(r'name="_xsrf" value="([^"]+)"', r.text)
    spawn_xsrf = match.group(1) if match else xsrf
    r = s.post(SPAWN_URL, data={"_xsrf": spawn_xsrf})
    print(f"Spawned. URL: {r.url}")
    # Wait for redirect?
    while "/hub/spawn-pending" in r.url:
        print("Waiting for spawn...")
        time.sleep(2)
        r = s.get(r.url)

NOTEBOOK_BASE = f"{BASE_URL}/user/{USER}"
API_URL = f"{NOTEBOOK_BASE}/api/contents"

# Prime cookies
print("Priming cookies...")
r = s.get(f"{NOTEBOOK_BASE}/tree")
# xsrf_cookie = s.cookies.get("_xsrf", path=f"/jupyterhub_103/user/{USER}/")
# match = re.search(r'"xsrf_token":\s*"([^"]+)"', r.text)
# xsrf_token = match.group(1) if match else xsrf_cookie

# Try to find xsrf in cookies or page

print("Cookies in session:")
for c in s.cookies:
    print(f"{c.name}: {c.value} (Path: {c.path}, Domain: {c.domain})")

# Best match logic
xsrf_token = None
# Prioritize user path
for c in s.cookies:
    if c.name == "_xsrf" and USER in c.path:
        xsrf_token = c.value
        break
# Fallback
if not xsrf_token:
    for c in s.cookies:
        if c.name == "_xsrf":
            xsrf_token = c.value
            break

if not xsrf_token:
    match = re.search(r'"xsrf_token":\s*"([^"]+)"', r.text)
    if match:
        xsrf_token = match.group(1)


if xsrf_token:
    print(f"Selected XSRF Token: {xsrf_token}")
    s.headers.update({"X-XSRFToken": xsrf_token})
    qs = f"?_xsrf={xsrf_token}"
    qs = f"?_xsrf={xsrf_token}"
else:
    qs = ""




if len(sys.argv) < 2:
    print("Usage: python run_remote.py <file_to_upload> [command_to_run]")
    sys.exit(1)

SCRIPT_FILE = sys.argv[1]
SCRIPT_NAME = SCRIPT_FILE.split("/")[-1]

import base64

# ...

# 2. Upload script
print(f"Uploading {SCRIPT_NAME}...")

# Detect binary ext or just try utf-8
is_binary = SCRIPT_NAME.endswith(".zip") or SCRIPT_NAME.endswith(".tar.gz")

if is_binary:
    try:
        with open(SCRIPT_FILE, "rb") as f:
            file_content = base64.b64encode(f.read()).decode("utf-8")
        file_format = "base64"
    except Exception as e:
        print(f"Error reading local file: {e}")
        sys.exit(1)
else:
    try:
        with open(SCRIPT_FILE, "r") as f:
            file_content = f.read()
        file_format = "text"
    except UnicodeDecodeError:
        # Fallback to binary
        print("Detected binary content, switching to base64")
        with open(SCRIPT_FILE, "rb") as f:
            file_content = base64.b64encode(f.read()).decode("utf-8")
        file_format = "base64"
    except Exception as e:
        print(f"Error reading local file: {e}")
        sys.exit(1)

payload = {
    "content": file_content,
    "format": file_format,
    "type": "file"
}
r = s.put(f"{API_URL}/{SCRIPT_NAME}{qs}", json=payload)
print(f"Uploaded {SCRIPT_NAME} ({file_format}): {r.status_code}")

if r.status_code not in [200, 201]:
    print(r.text)

# 3. Spawning Terminal
print("Spawning terminal...")
r = s.post(f"{NOTEBOOK_BASE}/api/terminals{qs}")
if r.status_code != 200:
    print(f"Failed to spawn terminal: {r.status_code} {r.text}")
    sys.exit(1)
term_name = r.json()["name"]
print(f"Terminal spawned: {term_name}")

# 3. Spawning Terminal (only if it's a script we want to run, but for zip we might want to unzip using a command)
# We can allow passing a command to run?
# Currently run_remote.py runs "python3 <script>".
# If I upload a zip, I probably want to run "unzip ml.zip".
# So run_remote.py should accept an optional "command" argument or infer it?
# Or I can upload the zip, then upload a small "unzip.py" script and run that.
# Or just upload a script `setup_project.py` that uploads the zip (embedded?) no that's too big.

# Better: upload the zip, then run a python command to unzip it.
# The `run_remote.py` is designed to run the file it uploaded.
# If I upload `ml.zip`, `python3 ml.zip` works IF it has `__main__.py` inside.
# But `unzip` is better.

# Let's Modify run_remote.py to accept TWO arguments:
# python run_remote.py <file_to_upload> <command_to_run>
# If 2nd arg missing, default to "python3 <file>"

if len(sys.argv) < 3:
    if SCRIPT_NAME.endswith(".py"):
        CMD = f"/home/compute.ashesi.lan/ptinibu/python-env/bin/python {SCRIPT_NAME}\r"
    elif SCRIPT_NAME.endswith(".zip"):
        CMD = f"unzip -o {SCRIPT_NAME}\r"
    else:
        CMD = f"./{SCRIPT_NAME}\r"
else:
    CMD = sys.argv[2] + "\r"


print(f"Command to run: {CMD.strip()}")

# Connect
ws_url = f"wss://compute.ashesi.edu.gh/jupyterhub_103/user/{USER}/terminals/websocket/{term_name}"
print(f"Connecting to WS: {ws_url}")
# cookie_str = "; ".join([f"{c.name}={c.value}" for c in s.cookies]) # Defined earlier? No.
cookie_str = "; ".join([f"{c.name}={c.value}" for c in s.cookies])

ws = websocket.create_connection(ws_url, cookie=cookie_str, sslopt={"cert_reqs": ssl.CERT_NONE})
time.sleep(1)

# Send command
# cmd = f"python3 {SCRIPT_NAME}\r" # No, use CMD
ws.send(json.dumps(["stdin", CMD]))

# Read output
start_time = time.time()

params_output = []
while time.time() - start_time < 600: # Increase timeout
    try:
        res = ws.recv()
        data = json.loads(res)
        if data[0] == "stdout":
            content = data[1]
            print(content, end="")
            # Check for python prompt or exit?
            # We rely on script finishing.
            # But the terminal stays open.
            # We can detect if the script prints "DONE" or just wait.
    except Exception as e:
        print(f"Error reading: {e}")
        break

ws.close()
