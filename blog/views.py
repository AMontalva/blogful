from flask import render_template

from blog import app
from .database import session, Entry

from flask import request, redirect, url_for

PAGINATE_BY = 10

@app.route("/")
@app.route("/page/<int:page>")
def entries(page=1):
    # Zero-indexed page
    page_index = page - 1

    count = session.query(Entry).count()

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

@app.route("/entry/add", methods=["GET"])
def add_entry_get():
    return render_template("add_entry.html")
    

@app.route("/entry/add", methods=["POST"])
def add_entry_post():
    entry = Entry(
        title=request.form["title"],
        content=request.form["content"],
    )
    session.add(entry)
    session.commit()
    return redirect(url_for("entries"))
    
@app.route("/entry/<id>")
def entry(id):
    entry_data = session.query(Entry).get(id)
    return render_template("entry.html", entry_data=entry_data)

@app.route("/edit/<id>/edit", methods=["GET"])
def edit_entry(id):
    entry_data = session.query(Entry).get(id)
    return render_template("edit.html", entry_data=entry_data)
    
@app.route("/edit/<id>/edit", methods=["POST"])
def edit_entry_post(id):
    entry_data = session.query(Entry).get(id)
    entry_data.title = request.form["title"]
    entry_data.content = request.form["content"]
    session.commit()
    return redirect(url_for("entries"))

@app.route("/delete/<id>/delete", methods=["GET"])
def delete_entry(id):
    entry_data = session.query(Entry).get(id)
    return render_template("delete.html", entry_data=entry_data)
    
@app.route("/delete/<id>/delete", methods=["POST"])
def delete_entry_post(id):
    choice = request.form["delete_button"]

    if(choice == "Yes"):
        entry_data = session.query(Entry).get(id)
        session.delete(entry_data)
        session.commit()
        return redirect(url_for("entries"))
    else:
        return redirect(url_for("entries"))
        