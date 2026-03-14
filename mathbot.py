import importlib
import subprocess
import sys
import string, secrets
import json

def install_and_import(package, import_name=None):
    try:
        importlib.import_module(import_name or package)
    except ImportError:
        print(f"Installing {package}...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])
install_and_import("Pillow", "PIL")
install_and_import("requests")
install_and_import("beautifulsoup4", "bs4")
install_and_import("colorama")
from PIL import Image
import requests
from bs4 import BeautifulSoup as bs
import re, time, random
from colorama import Fore, Style
import os

print("All modules are ready!")

s = requests.Session()

def extract_url(raw_script_html):
    match = re.search(r"\.load\(['\"](.+?)['\"]\);", raw_script_html, re.DOTALL)
    return {"extracted_url": match.group(1)} if match else []

def image_to_text():
    img = Image.open("mathbot.png")
    width, height = img.size
    cropped_img = img.crop((0, 0, width, int(height * 0.8)))

    cropped_img.save("cropped_image.png")

    url = "https://znippe-fastapi-my-ocr.hf.space/predict"

    with open("cropped_image.png", "rb") as f:
        files = {"file": f}
        response = requests.post(url, files=files)
    data = response.json()
    result = "".join(filter(str.isdigit, data["full_text"]))
    return result

def purple(text):
    os.system("")
    faded = ""
    down = False

    for line in text.splitlines():
        red = 40
        for character in line:
            if down:
                red -= 3
            else:
                red += 3
            if red > 254:
                red = 255
                down = True
            elif red < 1:
                red = 30
                down = False
            faded += (f"\033[38;2;{red};0;220m{character}\033[0m")
    return faded

def mask_name(name):
    def mask_word(word):
        length = len(word)

        # Convert to list of *
        masked = ['*'] * length

        if length == 3:
            masked[0] = word[0]

        elif length == 4:
            masked[0] = word[0]
            masked[-1] = word[-1]

        elif length in (5, 6):
            masked[0] = word[0]
            masked[1] = word[1]
            masked[-1] = word[-1]

        elif length >= 7:
            masked[0] = word[0]        # 1st
            masked[1] = word[1]        # 2nd
            
            # Even positions (1-based index)
            for i in range(3, length - 1):
                if (i + 1) % 2 == 0:   # convert to 1-based check
                    masked[i] = word[i]

            masked[-1] = word[-1]      # last

        else:  # length 1 or 2
            masked[0] = word[0]

        return ''.join(masked)

    return ' '.join(mask_word(w) for w in name.split())

def hex_to_rgb(hex_color):
    return tuple(int(hex_color[i:i+2], 16) for i in (1, 3, 5))

def rgb_to_ansi(r, g, b):
    return f"\033[38;2;{r};{g};{b}m"

def interpolate_colors(color1, color2, steps):
    r1, g1, b1 = hex_to_rgb(color1)
    r2, g2, b2 = hex_to_rgb(color2)
    
    step_r = (r2 - r1) / steps
    step_g = (g2 - g1) / steps
    step_b = (b2 - b1) / steps
    
    colors = []
    for i in range(steps):
        r = int(r1 + step_r * i)
        g = int(g1 + step_g * i)
        b = int(b1 + step_b * i)
        colors.append(rgb_to_ansi(r, g, b))
    
    return colors

def print_gradient_text(text):
    color1 = "#4158D0"
    color2 = "#C850C0"
    color3 = "#FFCC70"
    
    steps = len(text)

    gradient1 = interpolate_colors(color1, color2, steps // 2)
    gradient2 = interpolate_colors(color2, color3, steps - len(gradient1))

    full_gradient = gradient1 + gradient2
    
    for i, char in enumerate(text):
        print(f"{full_gradient[i]}{char}", end="", flush=True)
    
    print("\033[0m")

def generate_random_string(length=32):
    characters = string.ascii_letters + string.digits
    return ''.join(secrets.choice(characters) for _ in range(length))

def login(username: str, password: str) -> str:
    while True:
        try:
            session = s.get("https://math-bot.com/login")
            cookies = s.headers.get("Set-Cookie")
            headers = {
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
            "Accept-Language": "en-US,en;q=0.9",
            "Cache-Control": "max-age=0",
            "Content-Type": "application/x-www-form-urlencoded",
            "Cookie": cookies,
            "Origin": "https://math-bot.com",
            "Priority": "u=0, i",
            "Referer": "https://math-bot.com/login",
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "same-origin",
            "Sec-Fetch-User": "?1",
            "Upgrade-Insecure-Requests": "1",
            "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 18_5 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.5 Mobile/15E148 Safari/604.1"
            }
            s.post(
                "https://math-bot.com/login",
                data={"username": username, "password": password, "submit": ""},
                headers=headers,
                allow_redirects=True
            )

            return cookies
        except Exception as e:
            print(f"Login failed: {e}")
        time.sleep(random.uniform(5, 15))

def start_bot(username, password):
    right = 0
    wrong = 0
    total = 0
    while True:
        cookie = login(username, password)
        time.sleep(random.uniform(5, 15))
        while 1:
            try:
                response = s.get("https://math-bot.com/dashboard")
                response_data = bs(response.text, "html.parser")
                user_data = [h3.get_text(strip=True) for h3 in response_data.find("div", {"class": "page-wrapper"}).find_all("h3")]
                user = user_data[0]
                balance = user_data[6]
                print(f"Logged in as: {mask_name(user)} | {balance}")
            except Exception as e:
                print(f"Error fetching dashboard!")
                print("Logging in again...")
                break
            try:
                captchasolving = s.get("https://math-bot.com/mathbot-typingnumbers")
                captcha_data = bs(captchasolving.text, "html.parser")
                captcha_data = captcha_data.select("script")[22].string
                captcha_data = re.search(r"\.load\('(.*?)'\);", captcha_data).group(1)
            except Exception as e:
                print(f"Error fetching captcha solving page!")
                print("Logging in again...")
                break
            try:
                while True:
                    math_call = s.get(f"https://math-bot.com/{captcha_data}", headers={"X-Requested-With": "XMLHttpRequest"})
                    math_call_data = bs(math_call.text, "html.parser")
                    math_call_data = math_call_data.select_one('script[type="text/javascript"]:nth-of-type(1)').string
                    extracted_url = extract_url(math_call_data)['extracted_url']
                    myloading = s.get(f"https://math-bot.com/{extracted_url}", headers={"X-Requested-With": "XMLHttpRequest"})
                    myloading_data = bs(myloading.text, "html.parser").select_one("#myloading2")
                    img = myloading_data.find("img")["src"]
                    input_text = myloading_data.select_one("input[type='text']")["id"]
                    hidden_values = [input["value"] for input in myloading_data.select("input[type='hidden']")]
                    hidden_ids = [input["id"] for input in myloading_data.select("input[type='hidden']")]
                    problem = s.get(f"https://math-bot.com/{img}")
                    with open("mathbot.png", "wb") as f:
                        f.write(problem.content)
                    solution = image_to_text()
                    if len(solution) == 10:
                        print(f"~ Captcha solution: {solution}")
                        break
            except Exception as e:
                print(f"Error fetching problem image!")
                print("Logging in again...")
                break
            try:
                url = f"https://math-bot.com/{extracted_url.replace('problem','success')}"
                alert = f"https://math-bot.com/{extracted_url.replace('problem','alert')}"
                data = {
                    hidden_ids[0]: hidden_values[0],
                    hidden_ids[1]: hidden_values[1],
                    input_text: solution
                }
                success = s.post(url, headers={"X-Requested-With": "XMLHttpRequest"}, data=data)
                if success.status_code == 200:
                    print("~ Successfully submitted solution!")
                    if "rantoken" in success.text:
                        print("~ " + Fore.GREEN + "Correct solution!" + Style.RESET_ALL)
                        alert_response = s.get(alert, headers={"X-Requested-With": "XMLHttpRequest"})
                        right += 1
                        total += 1
                    elif "limit" in success.text:
                        print("~ " + Fore.YELLOW + "Limit hit, waiting 1hr..." + Style.RESET_ALL)
                        time.sleep(3600)
                    else:
                        print("~ " + Fore.RED + "Incorrect solution!" + Style.RESET_ALL)
                        wrong += 1
                        total += 1
                else:
                    print(f"Failed to submit solution! Status code: {success.status_code}")
                print(f"~ Stats: {Fore.GREEN}Correct: {right}{Style.RESET_ALL} | {Fore.RED}Wrong: {wrong}{Style.RESET_ALL} | {Fore.BLUE}Total: {total}{Style.RESET_ALL}")
                print_gradient_text('[============================================]')
            except Exception as e:
                print(f"Error constructing success URL!")
                print("Logging in again...")
                break
            time.sleep(random.uniform(2, 5))

os.system('cls' if os.name == 'nt' else 'clear')
print_gradient_text("""
[============================================]
        ▖  ▖▄▖▄▖▖▖▄ ▄▖▄▖  ▄▖▄▖▄▖▄▖▄▖▄▖
        ▛▖▞▌▌▌▐ ▙▌▙▘▌▌▐   ▚ ▌ ▙▘▐ ▙▌▐ 
        ▌▝ ▌▛▌▐ ▌▌▙▘▙▌▐   ▄▌▙▖▌▌▟▖▌ ▐ 
[============================================]
|This bot will assist you in tastk solving on|
|              mathbot.com                   |
| by automating the captcha solving process. |
[============================================]""")
username = input(purple("Enter username: ")+ "\033[38;2;148;0;230m")
password = input(purple("Enter password: ")+ "\033[38;2;148;0;230m")
print_gradient_text('[============================================]')
if __name__ == "__main__":
    data_file = "datamb.json"
    secret = None

    if os.path.exists(data_file):
        with open(data_file, "r") as f:
            try:
                data = json.load(f)
            except Exception:
                data = {}
    else:
        data = {}

    secret = data.get(username)
    if not secret:
        secret = generate_random_string()
        data[username] = secret
        with open(data_file, "w") as f:
            json.dump(data, f)
    payload = {
        "username": username,
        "id": secret
    }
    print(purple(f"Using token: {secret}"))
    activate = requests.post("https://ecnl-taskassistant-backend.onrender.com/activate-mathbot", json=payload)
    if activate.status_code != 200:
        print(Fore.RED + activate.json()['error'] + Style.RESET_ALL)
        sys.exit(1)
    if activate.json()['message'] == "User already activated":
        print(purple("User already activated. Continuing..."))
        print_gradient_text('[============================================]')
        start_bot(username, password)
    else:
        print(Fore.RED + f"{activate.json()['message']}" + Style.RESET_ALL)
        sys.exit(1)