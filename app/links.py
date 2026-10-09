import re
import secrets
import string
from collections import Counter
from datetime import timedelta
from urllib.parse import urlparse

from flask import Blueprint, abort, flash, jsonify, redirect, render_template, request, url_for
from flask_login import current_user, login_required
from sqlalchemy import func
from sqlalchemy.exc import IntegrityError

from .extensions import db
from .models import Click, Link, utcnow

bp = Blueprint("links", __name__)

ALPHABET = string.ascii_letters + string.digits
ALIAS_RE = re.compile(r"^[A-Za-z0-9_-]{3,32}$")
RESERVED = {"login", "logout", "register", "dashboard", "static", "links", "health", "api", "admin"}
CHART_DAYS = 14


def normalize_url(raw: str) -> str | None:
    """Return a clean http(s) URL or None if it is not acceptable."""
    raw = (raw or "").strip()
    if not raw or len(raw) > 2048:
        return None
    if "://" not in raw:
        raw = "https://" + raw
    parsed = urlparse(raw)
    if parsed.scheme not in ("http", "https") or not parsed.hostname:
        return None
    if "." not in parsed.hostname and parsed.hostname != "localhost":
        return None
    return raw


def generate_code(length: int = 6) -> str:
    for _ in range(10):
        code = "".join(secrets.choice(ALPHABET) for _ in range(length))
        if not Link.query.filter_by(code=code).first():
            return code
    return generate_code(length + 1)


@bp.route("/")
def home():
    return render_template("index.html")


@bp.route("/health")
def health():
    return jsonify(status="ok")


@bp.route("/dashboard", methods=["GET", "POST"])
@login_required
def dashboard():
    if request.method == "POST":
        target = normalize_url(request.form.get("url"))
        alias = request.form.get("alias", "").strip()
        if not target:
            flash("Enter a valid web address, like https://example.com.", "error")
        elif urlparse(target).hostname == request.host.split(":")[0]:
            flash("You can't shorten a link to this site.", "error")
        elif alias and (not ALIAS_RE.match(alias) or alias.lower() in RESERVED):
            flash("Custom name must be 3-32 letters, numbers, - or _ (and not a reserved word).", "error")
        else:
            code = alias or generate_code()
            link = Link(user_id=current_user.id, code=code, target_url=target)
            db.session.add(link)
            try:
                db.session.commit()
            except IntegrityError:
                db.session.rollback()
                flash("That custom name is taken. Try another.", "error")
            else:
                flash("Short link created.", "ok")
                return redirect(url_for("links.dashboard"))

    rows = (
        db.session.query(Link, func.count(Click.id))
        .outerjoin(Click, Click.link_id == Link.id)
        .filter(Link.user_id == current_user.id)
        .group_by(Link.id)
        .order_by(Link.created_at.desc())
        .all()
    )
    total_clicks = sum(count for _, count in rows)
    return render_template("dashboard.html", rows=rows, total_clicks=total_clicks)


def _owned_link_or_404(link_id: int) -> Link:
    link = db.session.get(Link, link_id)
    if link is None or link.user_id != current_user.id:
        abort(404)
    return link


@bp.route("/links/<int:link_id>")
@login_required
def stats(link_id: int):
    link = _owned_link_or_404(link_id)
    today = utcnow().date()
    start = today - timedelta(days=CHART_DAYS - 1)
    clicks = link.clicks.filter(Click.clicked_at >= start).all()
    per_day = Counter(c.clicked_at.date() for c in clicks)
    series = [(start + timedelta(days=i), per_day.get(start + timedelta(days=i), 0)) for i in range(CHART_DAYS)]
    peak = max((n for _, n in series), default=0) or 1
    referrers = Counter((c.referrer or "Direct") for c in clicks).most_common(5)
    return render_template(
        "stats.html",
        link=link,
        series=series,
        peak=peak,
        referrers=referrers,
        total=link.clicks.count(),
        recent=sum(n for _, n in series),
    )


@bp.route("/links/<int:link_id>/delete", methods=["POST"])
@login_required
def delete(link_id: int):
    link = _owned_link_or_404(link_id)
    db.session.delete(link)
    db.session.commit()
    flash("Link deleted.", "ok")
    return redirect(url_for("links.dashboard"))


@bp.route("/<code>")
def follow(code: str):
    link = Link.query.filter_by(code=code).first()
    if link is None:
        abort(404)
    ref = request.referrer
    host = urlparse(ref).hostname if ref else None
    db.session.add(
        Click(
            link_id=link.id,
            referrer=(host or None),
            user_agent=(request.user_agent.string or "")[:255] or None,
        )
    )
    db.session.commit()
    return redirect(link.target_url, code=302)


@bp.app_errorhandler(404)
def not_found(_e):
    return render_template("error.html", code=404, message="That page doesn't exist."), 404


@bp.app_errorhandler(400)
def bad_request(e):
    return render_template("error.html", code=400, message=getattr(e, "description", "Bad request.")), 400
