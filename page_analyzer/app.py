"""
page_analyzer application
"""

from page_analyzer.repository import SitesRepository
from page_analyzer.validator import validate
from flask import (
    Flask, flash, get_flashed_messages,
    redirect, request, render_template,
    url_for
)
from urllib.parse import urlparse
import os



app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
repo = SitesRepository()


def normalize_url(url):
    if not url:
        return None
    res = urlparse(url)
    return f"{res.scheme}://{res.netloc}"


@app.get('/')
def index():
    """
    Root route handler
    """
    messages = get_flashed_messages(with_categories=True)
    return render_template('index.html', messages=messages)


@app.post('/check_url')
def check_url():
    name = request.form.to_dict()["url"]    
    valres = validate(name)
    if not valres == True:
        flash(valres, "error")
        return redirect(url_for("index"), 302)
    name = normalize_url(name)
    site = repo.find(name)
    if site:
        flash("Site already exists", "warning")
    else:
        site = {"name": name}
        repo.save(site)
        flash("Site added", "success")
    return redirect(url_for("show_url", id=site["id"]))


@app.get('/urls')
def urls_list():
    sites = repo.list_sites()
    return render_template("sites.html", sites=sites)


@app.get('/urls/<int:id>')
def show_url(id):
    messages = get_flashed_messages(with_categories=True)
    site = repo.get_by_id(id)
    if not site:
        return "Page not found", 404
    checks = repo.list_checks(id)
    return render_template("site.html", messages=messages, site=site, checks=checks)


@app.post('/run_check/<int:id>')
def run_check(id):
    pass
