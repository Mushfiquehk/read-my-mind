"""Main views"""

from datetime import datetime
from flask import Blueprint, render_template, request, current_app, redirect, url_for
from bson import ObjectId

from .spotify import read_spotify_profile, get_top_artists, get_top_songs, get_on_repeats

main = Blueprint("main", __name__)


@main.route("/", methods=["GET"])
def home():
    """Home page

    Displays a spotify style page with a profile image at the top right corner
    in a circle border with shadows. It has the brand name next to it with the words MK.

    The main content is set within a centered container. The container is divided into sections.
    Each section has a Spotify  style heading and square tabs like spotify has.

    The first section is for top_artists then one for top_tracks and one for lastly on_repeats.
    I want the project set up in a way that I can change this setup to where I have
    a filter button above the slicers which I can click to show either top tracks or
    top artists or on_repeats in that section
    """

    # get acces_token to request my profile info
    profile = read_spotify_profile()
    spotify_profile_image = profile["images"][0]["url"]

    projects = [
        {
            "title": "This Website",
            "description": "Things I do and things I am into",
            "url": "https://github.com/Mushfiquehk/read-my-mind",
        },
        {
            "title": "E-Commerce",
            "description": "Online retail storefront with item and order function",
            "url": "https://github.com/Mushfiquehk/Stork-Distribution.git",
        },
        {
            "title": "Stay Tuned",
            "description": "More coming soon...",
            "url": ""
        }
    ]

    # Fetch articles from MongoDB, sorted by date descending
    articles_collection = current_app.config["ARTICLES_COLLECTION"]
    articles = list(articles_collection.find().sort("date", -1).limit(10))

    return render_template(
        "pages/index.html",
        spotify_profile_image=spotify_profile_image,
        projects=projects,
        articles=articles
    )


@main.route("/article/<article_id>", methods=["GET"])
def view_article(article_id):
    """View a single article"""
    articles_collection = current_app.config["ARTICLES_COLLECTION"]
    article = articles_collection.find_one({"_id": ObjectId(article_id)})
    
    if not article:
        return "Article not found", 404
    
    return render_template("pages/article.html", article=article)


@main.route("/edit-article", methods=["GET"])
def edit_article():
    """List all articles for editing"""
    articles_collection = current_app.config["ARTICLES_COLLECTION"]
    articles = list(articles_collection.find().sort("date", -1))
    return render_template("pages/edit_articles_list.html", articles=articles)


@main.route("/edit-article/<article_id>", methods=["GET", "POST"])
def edit_article_form(article_id):
    """Edit an existing article"""
    articles_collection = current_app.config["ARTICLES_COLLECTION"]
    article = articles_collection.find_one({"_id": ObjectId(article_id)})

    if not article:
        return "Article not found", 404

    if request.method == "POST":
        title = request.form.get("title")
        date_str = request.form.get("date")
        content = request.form.get("content")

        articles_collection.update_one(
            {"_id": ObjectId(article_id)},
            {"$set": {
                "title": title,
                "date": date_str,
                "content": content
            }}
        )
        return redirect(url_for("main.view_article", article_id=article_id))

    return render_template("pages/edit_article.html", article=article, article_id=article_id)


@main.route("/post-article", methods=["GET", "POST"])
def post_article():
    """Post a new article - simple form, no auth required"""
    success = None
    today = datetime.now().strftime("%Y-%m-%d")
    
    if request.method == "POST":
        title = request.form.get("title")
        date_str = request.form.get("date", today)
        content = request.form.get("content")
        
        article = {
            "title": title,
            "date": date_str,
            "content": content,
            "created_at": datetime.utcnow()
        }
        
        articles_collection = current_app.config["ARTICLES_COLLECTION"]
        articles_collection.insert_one(article)
        success = title
    
    return render_template("pages/post_article.html", today=today, success=success)
