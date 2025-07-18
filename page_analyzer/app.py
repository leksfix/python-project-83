"""
page_analyzer application
"""

import os

from flask import (
    Flask,
    flash,
    redirect,
    render_template,
    request,
    url_for,
)

from page_analyzer.repository import SitesRepository
from page_analyzer.utils import get_site_data, normalize_url
from page_analyzer.validator import validate

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
repo = SitesRepository()


@app.get('/')
def index():
    """
    Root route handler
    """
    return render_template('index.html')


@app.post('/check_url')
def check_url():
    """
    Handler for site registration
    """
    url = request.form.to_dict()["url"]

    is_valid, err_msg = validate(url)
    if not is_valid:
        flash(err_msg, "error")
        return redirect(url_for("urls_list"), 302)

    url = normalize_url(url)
    site = repo.find(url)
    if site:
        flash("Страница уже существует", "warning")
    else:
        site = repo.add_site(url)
        flash("Страница успешно добавлена", "success")

    return redirect(url_for("show_url", url_id=site["id"]))


@app.get('/urls')
def urls_list():
    """
    Handler for URL list page
    """
    return render_template("sites.html", sites=repo.get_sites())


@app.get('/urls/<int:url_id>')
def show_url(url_id):
    """
    Handler for site details page
    """
    site = repo.get_by_id(url_id)
    if not site:
        return "Page not found", 404

    checks = repo.get_checks(url_id)
    return render_template(
        "site.html",
        site=site,
        checks=checks,
    )


@app.post('/urls/<int:url_id>/checks')
def run_check(url_id):
    """
    Handler for site check run
    """
    site = repo.get_by_id(url_id)
    res = get_site_data(site['name'])
    if not res:
        flash("Произошла ошибка при проверке", "error")
    else:
        repo.add_check(
            url_id,
            res["status_code"],
            res["h1"],
            res["title"],
            res["description"]
        )
        flash("Страница успешно проверена", "success")
    return redirect(url_for("show_url", url_id=url_id))
