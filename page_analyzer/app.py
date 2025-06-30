"""
page_analyzer application
"""

import os
from urllib.parse import urlparse

from flask import (
    Flask,
    flash,
    get_flashed_messages,
    redirect,
    render_template,
    request,
    url_for,
)

from page_analyzer.repository import SitesRepository
from page_analyzer.validator import validate

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
repo = SitesRepository()


def normalize_url(url):
    """
    URL normalize
    """
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
    """
    Handler for site registration
    """
    name = request.form.to_dict()["url"]
    valres = validate(name)
    if valres is not True:
        flash(valres, "error")
        return redirect(url_for("index"), 302)
    name = normalize_url(name)
    site = repo.find(name)
    if site:
        flash("Site already exists", "warning")
    else:
        site = {"name": name}
        repo.save_site(site)
        flash("Site added", "success")
    return redirect(url_for("show_url", url_id=site["id"]))


@app.get('/urls')
def urls_list():
    """
    Handler for URL list page
    """
    sites = repo.list_sites()
    return render_template("sites.html", sites=sites)


@app.get('/urls/<int:url_id>')
def show_url(url_id):
    """
    Handler for site details page
    """
    messages = get_flashed_messages(with_categories=True)
    site = repo.get_by_id(url_id)
    if not site:
        return "Page not found", 404
    checks = repo.list_checks(url_id)
    return render_template("site.html", messages=messages, site=site,
                           checks=checks)


@app.post('/urls/<int:url_id>/checks')
def run_check(url_id):
    """
    Handler for site check run
    """
    check = {'url_id': url_id, 'status_code': 666}
    repo.save_check(check)
    return redirect(url_for("show_url", url_id=url_id))
    

