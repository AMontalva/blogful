from flask import render_template

from blog import app
from .database import session, Entry

from flask import request, redirect, url_for

from flask import flash
from flask.ext.login import login_user
from werkzeug.security import check_password_hash
from .database import User

from flask.ext.login import login_required

from flask.ext.login import current_user

from flask.ext.login import logout_user

@app.route("/", methods=["GET"])
@app.route("/page/<int:page>", methods=["GET"])
def entries(page=1):
    PAGINATE_BY = 10
    count = session.query(Entry).count()

    limit = request.args.get("limit", "10")
    # try:
    limit = int(limit)
    
    if(limit >= 1 << 63):
        PAGINATE_BY = 10
    else:
        PAGINATE_BY = limit

    # Zero-indexed page
    page_index = page - 1

    start = page_index * PAGINATE_BY
    end = start + PAGINATE_BY

    total_pages = (count - 1) / PAGINATE_BY + 1
    has_next = page_index < total_pages - 1
    has_prev = page_index > 0

    entries = session.query(Entry)
    entries = entries.order_by(Entry.datetime.desc())
    entries = entries[start:end]

    return render_template("entries.html",
        entries=entries,
        has_next=has_next,
        has_prev=has_prev,
        page=page,
        total_pages=total_pages
    )
    
@app.route("/", methods=["POST"])
@app.route("/page/<int:page>", methods=["POST"])
def entries_post(page=1):
    limit=request.form["limit"]
    return redirect(request.base_url + "?limit=" + limit)

@app.route("/entry/add", methods=["GET"])
@login_required
def add_entry_get():
    return render_template("add_entry.html")
    

@app.route("/entry/add", methods=["POST"])
@login_required
def add_entry_post():
    entry = Entry(
        title=request.form["title"],
        content=request.form["content"],
        author=current_user
    )
    session.add(entry)
    session.commit()
    return redirect(url_for("entries"))
    
@app.route("/entry/<id>")
def entry(id):
    entry_data = session.query(Entry).get(id)
    return render_template("entry.html", entry_data=entry_data)

@app.route("/entry/<id>/edit", methods=["GET"])
@login_required
def edit_entry(id):
    entry_data = session.query(Entry).get(id)
    return render_template("edit.html", entry_data=entry_data)
    
@app.route("/entry/<id>/edit", methods=["POST"])
@login_required
def edit_entry_post(id):
    entry_data = session.query(Entry).get(id)
    entry_data.title = request.form["title"]
    entry_data.content = request.form["content"]
    session.commit()
    return redirect(url_for("entries"))

@app.route("/entry/<id>/delete", methods=["GET"])
@login_required
def delete_entry(id):
    entry_data = session.query(Entry).get(id)
    return render_template("delete.html", entry_data=entry_data)
    
@app.route("/entry/<id>/delete", methods=["POST"])
@login_required
def delete_entry_post(id):
    choice = request.form["delete_button"]

    if(choice == "Yes"):
        entry_data = session.query(Entry).get(id)
        session.delete(entry_data)
        session.commit()
        return redirect(url_for("entries"))
    else:
        return redirect(url_for("entries"))

@app.route("/test")
def test():
    # i = request.args.get("var")
    return request.url
    
@app.route("/login", methods=["GET"])
def login_get():
    return render_template("login.html")
    
@app.route("/login", methods=["POST"])
def login_post():
    email = request.form["email"]
    password = request.form["password"]
    user = session.query(User).filter_by(email=email).first()
    if not user or not check_password_hash(user.password, password):
        flash("Incorrect username or password", "danger")
        return redirect(url_for("login_get"))

    login_user(user)
    return redirect(request.args.get('next') or url_for("entries"))

@app.route("/logout", methods=["GET"])
def logout():
    logout_user()
    return redirect(url_for("entries"))