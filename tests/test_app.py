from app.extensions import db
from app.models import Click, Link
from app.links import normalize_url
from app.security import is_safe_next
from tests.conftest import csrf


def make_link(client, url="https://example.com/page", alias=""):
    token = csrf(client, "/dashboard")
    return client.post("/dashboard", data={"url": url, "alias": alias, "csrf_token": token}, follow_redirects=True)


def test_health(client):
    assert client.get("/health").get_json() == {"status": "ok"}


def test_dashboard_requires_login(client):
    r = client.get("/dashboard")
    assert r.status_code == 302 and "/login" in r.headers["Location"]


def test_post_without_csrf_is_rejected(client):
    r = client.post("/register", data={"email": "a@example.com", "password": "password123"})
    assert r.status_code == 400


def test_register_and_login_flow(client):
    token = csrf(client, "/register")
    r = client.post("/register", data={"email": "New@Example.com", "password": "password123", "csrf_token": token})
    assert r.status_code == 302
    token = csrf(client, "/dashboard")
    client.post("/logout", data={"csrf_token": token})
    token = csrf(client)
    bad = client.post("/login", data={"email": "new@example.com", "password": "nope", "csrf_token": token})
    assert b"wrong" in bad.data
    ok = client.post("/login", data={"email": "new@example.com", "password": "password123", "csrf_token": token})
    assert ok.status_code == 302


def test_register_rejects_short_password_and_duplicates(client):
    token = csrf(client, "/register")
    r = client.post("/register", data={"email": "a@example.com", "password": "short", "csrf_token": token})
    assert b"at least 8" in r.data
    client.post("/register", data={"email": "a@example.com", "password": "password123", "csrf_token": token})
    token = csrf(client, "/dashboard")
    client.post("/logout", data={"csrf_token": token})
    token = csrf(client, "/register")
    dup = client.post("/register", data={"email": "a@example.com", "password": "password123", "csrf_token": token})
    assert b"already registered" in dup.data


def test_create_follow_and_count_click(logged_in, app):
    r = make_link(logged_in, alias="my-link")
    assert b"my-link" in r.data
    resp = logged_in.get("/my-link", headers={"Referer": "https://news.ycombinator.com/item?id=1"})
    assert resp.status_code == 302 and resp.headers["Location"] == "https://example.com/page"
    with app.app_context():
        click = Click.query.one()
        assert click.referrer == "news.ycombinator.com"


def test_duplicate_alias_and_reserved_alias(logged_in):
    make_link(logged_in, alias="taken")
    assert b"taken. Try another" in make_link(logged_in, url="https://example.org", alias="taken").data
    assert b"reserved" in make_link(logged_in, url="https://example.org", alias="login").data


def test_invalid_urls_rejected(logged_in):
    for bad in ["javascript:alert(1)", "ftp://example.com", "not a url", "http://nodot"]:
        assert b"valid web address" in make_link(logged_in, url=bad).data


def test_cannot_shorten_own_host(logged_in):
    assert b"this site" in make_link(logged_in, url="http://localhost/abc").data


def test_stats_page_and_ownership(logged_in, client, app):
    make_link(logged_in, alias="stat-me")
    logged_in.get("/stat-me")
    with app.app_context():
        link_id = Link.query.one().id
    page = logged_in.get(f"/links/{link_id}")
    assert page.status_code == 200 and b"Clicks per day" in page.data

    # Another user must not see it.
    other = app.test_client()
    token = csrf(other, "/register")
    other.post("/register", data={"email": "b@example.com", "password": "password123", "csrf_token": token})
    assert other.get(f"/links/{link_id}").status_code == 404
    token = csrf(other, "/dashboard")
    assert other.post(f"/links/{link_id}/delete", data={"csrf_token": token}).status_code == 404


def test_delete_removes_link_and_clicks(logged_in, app):
    make_link(logged_in, alias="bye-bye")
    logged_in.get("/bye-bye")
    with app.app_context():
        link_id = Link.query.one().id
    token = csrf(logged_in, "/dashboard")
    logged_in.post(f"/links/{link_id}/delete", data={"csrf_token": token})
    assert logged_in.get("/bye-bye").status_code == 404
    with app.app_context():
        assert Click.query.count() == 0


def test_unknown_code_is_404(client):
    assert client.get("/nope123").status_code == 404


def test_security_headers_present(client):
    assert client.get("/").headers["X-Frame-Options"] == "DENY"


def test_normalize_url_adds_scheme():
    assert normalize_url("example.com/a") == "https://example.com/a"
    assert normalize_url("") is None


def test_open_redirect_guard():
    assert is_safe_next("/dashboard")
    assert not is_safe_next("//evil.com")
    assert not is_safe_next("https://evil.com")
    assert not is_safe_next(None)
