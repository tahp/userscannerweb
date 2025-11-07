from flask import Flask, render_template, request, jsonify
import importlib
import pkgutil
from concurrent.futures import ThreadPoolExecutor, as_completed

from user_scanner import dev, social, creator, community, gaming

app = Flask(__name__)

def load_modules(package):
    modules = []
    for _, name, _ in pkgutil.iter_modules(package.__path__, package.__name__ + "."):
        try:
            module = importlib.import_module(name)
            modules.append(module)
        except Exception as e:
            print(f"Failed to import {name}: {e}")
    return modules

def get_site_url(site_name, username):
    urls = {
        "Github": f"https://github.com/{username}",
        "Gitlab": f"https://gitlab.com/{username}",
        "Codeberg": f"https://codeberg.org/{username}",
        "Cratesio": f"https://crates.io/users/{username}",
        "Dockerhub": f"https://hub.docker.com/u/{username}",
        "Launchpad": f"https://launchpad.net/~{username}",
        "Npmjs": f"https://www.npmjs.com/~{username}",
        "Replit": f"https://replit.com/@{username}",
        "Bluesky": f"https://bsky.app/profile/{username}",
        "Instagram": f"https://www.instagram.com/{username}",
        "Mastodon": f"https://mastodon.social/@{username}",
        "Pinterest": f"https://www.pinterest.com/{username}",
        "Reddit": f"https://www.reddit.com/user/{username}",
        "Snapchat": f"https://www.snapchat.com/add/{username}",
        "Threads": f"https://www.threads.net/@{username}",
        "X": f"https://x.com/{username}",
        "Youtube": f"https://www.youtube.com/@{username}",
        "Devto": f"https://dev.to/{username}",
        "Hashnode": f"https://hashnode.com/@{username}",
        "Kaggle": f"https://www.kaggle.com/{username}",
        "Medium": f"https://medium.com/@{username}",
        "Patreon": f"https://www.patreon.com/user?u={username}",
        "Coderlegion": f"https://www.coderlegion.com/users/{username}",
        "Chess_com": f"https://www.chess.com/member/{username}",
    }
    return urls.get(site_name, "#")

@app.route("/")
def index():
    return render_template("index.html")

def _scan_site(module, username, get_site_url_func, cat_name):
    func = next((getattr(module, f) for f in dir(module) if f.startswith("validate_") and callable(getattr(module, f))), None)
    if not func:
        return cat_name, None

    site_name = module.__name__.split('.')[-1].capitalize()
    
    try:
        result = func(username)
        status = "Error"
        if result == 1:
            status = "Available"
        elif result == 0:
            status = "Taken"
        
        return cat_name, {
            "site": site_name,
            "status": status,
            "url": get_site_url_func(site_name, username)
        }
    except Exception as e:
        return cat_name, {
            "site": site_name,
            "status": "Error",
            "url": get_site_url_func(site_name, username)
        }

@app.route("/scan", methods=["POST"])
def scan_username():
    username = request.json.get("username")
    if not username:
        return jsonify({"error": "Username not provided"}), 400

    results = {}
    categories = [
        ("DEV", dev),
        ("SOCIAL", social),
        ("CREATOR", creator),
        ("COMMUNITY", community),
        ("GAMING", gaming)
    ]

    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = []
        for cat_name, package in categories:
            try:
                modules = load_modules(package)
            except ModuleNotFoundError:
                continue

            for module in modules:
                futures.append(executor.submit(_scan_site, module, username, get_site_url, cat_name))
        
        for future in as_completed(futures):
            cat_name, site_result = future.result()
            if site_result:
                if cat_name not in results:
                    results[cat_name] = []
                results[cat_name].append(site_result)

    return jsonify(results)

if __name__ == "__main__":
    app.run(debug=True)
