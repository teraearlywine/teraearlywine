# Tech Debt Backlog — teraearlywine.com
> Generated: 2026-03-10
> Codebase: Flask portfolio site (`core/`, deployed to GCP App Engine)
> Scoring: Priority = (Impact + Risk) × (6 − Effort) — higher = do sooner

---

## Priority Rankings

| # | Issue | Category | Priority Score | Labels |
|---|-------|----------|---------------|--------|
| 1 | [Hardcoded secret key in production](#issue-1) | Security | **45** | `security` `bug` |
| 2 | [Add Open Graph + canonical meta tags for SEO](#issue-2) | Documentation | **25** | `enhancement` `seo` |
| 3 | [Deprecated `User.query.get()` in SQLAlchemy 2.x](#issue-3) | Code debt | **25** | `bug` `dependency` |
| 4 | [Database never initialized — auth blueprint missing](#issue-4) | Architecture | **24** | `bug` `architecture` |
| 5 | [No environment-based config (dev/prod split)](#issue-5) | Architecture | **24** | `enhancement` `architecture` |
| 6 | [Flake8 config silences too many real errors](#issue-6) | Code debt | **20** | `code-quality` |
| 7 | [No custom error handlers (404, 500)](#issue-7) | Code debt | **20** | `enhancement` |
| 8 | [No tests — pytest configured but no test files exist](#issue-8) | Test debt | **16** | `testing` |
| 9 | [Duplicated SVG icons across hero and contact sections](#issue-9) | Code debt | **15** | `refactor` |
| 10 | [No CI/CD pipeline](#issue-10) | Infrastructure | **15** | `infrastructure` `enhancement` |
| 11 | [Empty `core/utils/` directory](#issue-11) | Code debt | **10** | `cleanup` |
| 12 | [Dead / commented-out code (TimestampMixin, app.run)](#issue-12) | Code debt | **10** | `cleanup` |

---

## Issues

---

### Issue 1
**Title:** `[Security] Replace hardcoded secret key with environment variable`
**Labels:** `security` `bug`
**Priority Score:** 45 (Impact: 4, Risk: 5, Effort: 1)

**Problem**

`core/__init__.py` line 32 sets `app.secret_key = 'dev_test'`. This value is shipped to production unchanged. Flask uses the secret key to sign session cookies — anyone who knows the value can forge session data and impersonate authenticated users.

**Location**

```
core/__init__.py:32
app.secret_key = 'dev_test'  # Can be anything;
```

**Remediation**

1. Add `SECRET_KEY` to `.env` with a cryptographically random value (e.g. `python -c "import secrets; print(secrets.token_hex(32))"`)
2. Load it in `create_app`: `app.secret_key = os.environ.get('SECRET_KEY')` (raise if missing in production)
3. Confirm `.env` remains in `.gitignore` (it currently is — keep it that way)

**Effort:** ~15 min
**Risk of not fixing:** Session forgery; immediate risk if this repo is ever public or the key leaks

---

### Issue 2
**Title:** `[SEO] Add Open Graph, Twitter Card, and canonical meta tags`
**Labels:** `enhancement` `seo`
**Priority Score:** 25 (Impact: 3, Risk: 2, Effort: 1)

**Problem**

`core/home/templates/home/includes/header.html` only has a basic `<meta name="description">` and title. When the portfolio URL is shared on LinkedIn, Twitter/X, Slack, or iMessage, it renders with no preview image, no formatted title, and no description — a missed opportunity for a professional first impression.

**Location**

```
core/home/templates/home/includes/header.html
```

**Remediation**

Add to `<head>`:
```html
<!-- Canonical -->
<link rel="canonical" href="https://www.teraearlywine.com/">

<!-- Open Graph -->
<meta property="og:type" content="website">
<meta property="og:url" content="https://www.teraearlywine.com/">
<meta property="og:title" content="Tera Earlywine — Senior Data Engineer">
<meta property="og:description" content="Building data systems that scale. Co-founder, consultant, and engineer.">
<meta property="og:image" content="https://www.teraearlywine.com/static/assets/images/og-preview.png">

<!-- Twitter Card -->
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="Tera Earlywine — Senior Data Engineer">
<meta name="twitter:image" content="https://www.teraearlywine.com/static/assets/images/og-preview.png">
```

**Effort:** ~30 min (including creating a 1200×630 OG preview image)
**Risk of not fixing:** Every social share looks bare; low-effort, high-visibility win

---

### Issue 3
**Title:** `[Bug] Replace deprecated User.query.get() with SQLAlchemy 2.x syntax`
**Labels:** `bug` `dependency`
**Priority Score:** 25 (Impact: 2, Risk: 3, Effort: 1)

**Problem**

`core/__init__.py` line 41 uses `User.query.get(int(user_id))`. This pattern (`session.query(Model).get()`) was deprecated in SQLAlchemy 1.4 and removed in 2.0. The project pins `SQLAlchemy==2.0.38` — this code will raise a warning today and may break silently or loudly depending on the Flask-SQLAlchemy wrapper version.

**Location**

```
core/__init__.py:41
return User.query.get(int(user_id))
```

**Remediation**

Replace with:
```python
return db.session.get(User, int(user_id))
```

**Effort:** 5 min
**Risk of not fixing:** Silent breakage when auth is wired up; already technically broken per SQLAlchemy 2.x docs

---

### Issue 4
**Title:** `[Bug] Database is imported but never initialized — auth infrastructure is non-functional`
**Labels:** `bug` `architecture`
**Priority Score:** 24 (Impact: 3, Risk: 3, Effort: 2)

**Problem**

`core/__init__.py` imports `db` and `User` from `core.models` and initializes `Flask-Login`, but:

1. `db.init_app(app)` is never called — SQLAlchemy is never bound to the Flask app
2. `login_manager.login_view = 'auth.login'` references an `auth` blueprint that does not exist (not registered, not implemented)
3. There is no `SQLALCHEMY_DATABASE_URI` set anywhere

The result is that all auth-related code is dead weight — it will raise errors if any auth route is ever hit.

**Options**

- **Option A (Remove):** Strip out `Flask-Login`, `db`, and `User` imports from `__init__.py` if auth is not planned
- **Option B (Stub):** Add `db.init_app(app)` and a database URI config so the structure is ready to extend
- **Option C (Implement):** Build out the auth blueprint properly if user login is a near-term goal

**Effort:** 30–60 min depending on chosen path
**Risk of not fixing:** Misleading codebase that looks like it has auth but does not; silent import-time side effects

---

### Issue 5
**Title:** `[Architecture] Add environment-based configuration (dev / prod)`
**Labels:** `enhancement` `architecture`
**Priority Score:** 24 (Impact: 3, Risk: 3, Effort: 2)

**Problem**

`create_app(env='')` accepts an `env` parameter but never uses it. There are no config classes and no environment-aware settings. Currently, debug logging (`logging.DEBUG`) runs in production, the secret key is hardcoded (see Issue 1), and there is no way to toggle behavior between local dev and Cloud Run.

**Remediation**

Create a `core/config.py` with `DevelopmentConfig`, `ProductionConfig` classes. Load via `FLASK_ENV` env var in `create_app`. At minimum control: `SECRET_KEY`, `DEBUG`, `SQLALCHEMY_DATABASE_URI`, `LOG_LEVEL`.

**Effort:** ~1 hour
**Risk of not fixing:** Debug output in production logs, no clean path to add env-specific settings as the app grows

---

### Issue 6
**Title:** `[Code Quality] Flake8 config silences too many real errors — tighten rules`
**Labels:** `code-quality`
**Priority Score:** 20 (Impact: 2, Risk: 2, Effort: 1)

**Problem**

`.flake8` suppresses `F401` (unused imports), `F841` (assigned-but-never-used variables), `E402` (module-level imports not at top), and sets `max-line-length = 180`. These are legitimate errors that should surface during development, not be ignored globally. Silencing `F401` in particular masks dead imports.

**Specific concerns**

- `F401` suppressed: Flask-Login and db are imported in `__init__.py` without being fully used
- `E402` suppressed: imports inside functions (like `register_blueprints`) are an intentional pattern here but should be called out explicitly, not globally silenced
- `max-line-length = 180`: effectively disables line-length enforcement

**Remediation**

Remove `F401`, `F841` from `extend-ignore`. Use `# noqa: F401` inline on intentional re-exports. Reduce `max-line-length` to 100 or 120.

**Effort:** ~30 min (fix suppression + clean up any newly surfaced errors)

---

### Issue 7
**Title:** `[Enhancement] Register custom 404 and 500 error handlers`
**Labels:** `enhancement`
**Priority Score:** 20 (Impact: 2, Risk: 2, Effort: 1)

**Problem**

The Flask app has no registered error handlers. A 404 returns Flask's default HTML error page, which is inconsistent with the portfolio's design and exposes the Flask version in the response.

**Remediation**

Add to `create_app` in `core/__init__.py`:
```python
@app.errorhandler(404)
def not_found(e):
    return render_template('home/404.html'), 404

@app.errorhandler(500)
def server_error(e):
    return render_template('home/500.html'), 500
```

Create minimal `404.html` and `500.html` templates in `core/home/templates/home/`.

**Effort:** ~30 min

---

### Issue 8
**Title:** `[Testing] Add test suite — pytest is configured but no tests exist`
**Labels:** `testing`
**Priority Score:** 16 (Impact: 4, Risk: 4, Effort: 4)

**Problem**

`pytest.ini` is committed and configured, and pytest is in `requirements.txt`, but there are zero test files anywhere in the project. The `tests` directory referenced in `.flake8` does not exist.

**Suggested starting point**

1. Create `tests/` directory with `conftest.py` + Flask test client fixture
2. Write smoke tests: does the app start, does `/` return 200, does a bad route return 404
3. Add route tests for `about-me` redirect behavior

**Effort:** 2–4 hours for meaningful coverage
**Risk of not fixing:** Regressions ship silently; no safety net as the app grows

---

### Issue 9
**Title:** `[Refactor] Extract duplicated SVG icons into a shared Jinja2 macro`
**Labels:** `refactor`
**Priority Score:** 15 (Impact: 2, Risk: 1, Effort: 1)

**Problem**

The GitHub and LinkedIn SVG paths are copy-pasted verbatim in two places:
- `core/home/templates/home/sections/hero.html` (lines 11–19)
- `core/home/templates/home/sections/contact.html` (lines 11–19)

If either icon path ever needs to change, it must be updated in two places.

**Remediation**

Create `core/home/templates/home/includes/icons/` with a Jinja2 macro file:
```jinja2
{% macro github_icon() %}
  <svg viewBox="0 0 24 24" ...>...</svg>
{% endmacro %}
```

Import and call the macro in both `hero.html` and `contact.html`.

**Effort:** ~20 min

---

### Issue 10
**Title:** `[Infrastructure] Add GitHub Actions CI/CD pipeline for lint and deploy`
**Labels:** `infrastructure` `enhancement`
**Priority Score:** 15 (Impact: 3, Risk: 2, Effort: 3)

**Problem**

Deployment to GCP App Engine is currently manual (`gcloud app deploy`). There is no CI pipeline to run linting or tests before deploy. A bad push goes straight to production with no gates.

**Remediation**

Add `.github/workflows/deploy.yml`:
1. On push to `main`: run `flake8` + `pytest`
2. On passing tests: run `gcloud app deploy` using a stored GCP service account secret

**Effort:** ~2 hours (includes GCP service account setup in GitHub Secrets)

---

### Issue 11
**Title:** `[Cleanup] Remove or populate empty core/utils/ directory`
**Labels:** `cleanup`
**Priority Score:** 10 (Impact: 1, Risk: 1, Effort: 1)

**Problem**

`core/utils/` exists as a directory but contains no files — not even an `__init__.py`. It shows up in directory listings and implies shared utility functions exist when they do not.

**Remediation**

Either delete the directory, or add `core/utils/__init__.py` with a placeholder comment if utility functions are planned.

**Effort:** 5 min

---

### Issue 12
**Title:** `[Cleanup] Remove commented-out dead code (TimestampMixin, app.run)`
**Labels:** `cleanup`
**Priority Score:** 10 (Impact: 1, Risk: 1, Effort: 1)

**Problem**

Several commented-out code blocks exist that are either incomplete or unnecessary:

- `# from .mixins import TimestampMixin` appears in both `core/models/__init__.py` and `core/models/user.py` — the mixin and file don't exist
- `# app.run(host="127.0.0.1", port=8080, debug=True)` in `core/app.py` — not needed since gunicorn handles this; the comment creates confusion about how to run locally

**Remediation**

- Delete TimestampMixin references or create the mixin if it's planned
- Replace the commented `app.run` with a proper `if __name__ == '__main__':` block or a note in the README about local development

**Effort:** 10 min

---

## Suggested Phasing

**Sprint 1 — Security & Correctness (do before next deploy)**
- Issue 1: Secret key (15 min)
- Issue 3: Deprecated SQLAlchemy call (5 min)
- Issue 4: Decide on auth strategy and clean up dead scaffolding (30–60 min)

**Sprint 2 — Code Health (1–2 sessions)**
- Issue 5: Environment config
- Issue 6: Tighten flake8
- Issue 7: Error handlers
- Issue 11: Clean up utils/
- Issue 12: Remove dead comments

**Sprint 3 — Visibility & Infrastructure (1–2 sessions)**
- Issue 2: Open Graph / SEO meta tags
- Issue 9: Extract SVG macros
- Issue 10: GitHub Actions CI/CD

**Ongoing**
- Issue 8: Tests — add incrementally as new routes or features are added
