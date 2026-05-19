# read-my-mind
Personal website at [mhkbd.me](https://mhkbd.me), built with Jekyll and hosted on GitHub Pages.

## Structure

- `_layouts/` — Page layouts (`default.html`, `post.html`)
- `_includes/` — Reusable partials (header, footer)
- `_posts/` — Blog posts in Markdown (`YYYY-MM-DD-title.md`)
- `assets/css/` — Stylesheets
- `app/static/` — Images and legacy static assets

## Writing Posts

Create a file in `_posts/` following the naming convention:

```
_posts/YYYY-MM-DD-your-title.md
```

With front matter:

```yaml
---
title: "Your Post Title"
date: YYYY-MM-DD
---

Your content here (Markdown).
```

## Local Development

```bash
bundle install
bundle exec jekyll serve
```

## Deployment

Pushed to `main` → GitHub Pages builds and deploys automatically.

