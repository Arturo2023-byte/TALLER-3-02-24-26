from flask import Flask, render_template, request, redirect, url_for, session, flash
import requests
import os
from datetime import datetime

app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY", "clave-por-defecto-cambiar")

API_URL = os.getenv("API_URL", "http://api:8000")


def api_request(endpoint, method="GET", data=None, headers=None):
    url = f"{API_URL}{endpoint}"
    headers = headers or {"Content-Type": "application/json"}

    try:
        if method == "GET":
            r = requests.get(url, headers=headers, timeout=8)
        elif method == "POST":
            r = requests.post(url, json=data, headers=headers, timeout=8)
        elif method == "PUT":
            r = requests.put(url, json=data, headers=headers, timeout=8)
        elif method == "DELETE":
            r = requests.delete(url, headers=headers, timeout=8)
        else:
            raise ValueError("Método HTTP no soportado")

        if r.headers.get("content-type", "").startswith("application/json"):
            return r.status_code, r.json()
        return r.status_code, r.text
    except Exception as e:
        return 500, {"error": str(e)}


def is_logged_in():
    return session.get("user_id") is not None


@app.route("/")
def index():
    status, products = api_request("/api/v1/products/", "GET")
    if status != 200:
        products = []
        flash("No se pudieron cargar los productos.", "error")
    return render_template("index.html", products=products, now=datetime.now(), logged_in=is_logged_in())


@app.route("/products")
def products():
    status, products_list = api_request("/api/v1/products/", "GET")
    if status != 200:
        products_list = []
        flash("No se pudieron cargar los productos.", "error")
    return render_template("products.html", products=products_list, now=datetime.now(), logged_in=is_logged_in())


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "").strip()

        if not email or not password:
            flash("Email y contraseña son obligatorios.", "error")
            return redirect(url_for("login"))

        status, resp = api_request("/api/v1/users/login", "POST", {"email": email, "password": password})
        if status == 200 and isinstance(resp, dict) and resp.get("user_id"):
            session["user_id"] = resp["user_id"]
            flash("Login exitoso.", "success")
            return redirect(url_for("index"))

        flash("Credenciales inválidas.", "error")
        return redirect(url_for("login"))

    return render_template("login.html", now=datetime.now(), logged_in=is_logged_in())


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "").strip()

        if not username or not email or not password:
            flash("Todos los campos son obligatorios.", "error")
            return redirect(url_for("register"))

        status, resp = api_request(
            "/api/v1/users/register",
            "POST",
            {"username": username, "email": email, "password": password},
        )

        if status in (200, 201):
            flash("Registro exitoso. Ahora puedes iniciar sesión.", "success")
            return redirect(url_for("login"))

        detail = resp.get("detail") if isinstance(resp, dict) else None
        flash(detail or "No se pudo registrar el usuario.", "error")
        return redirect(url_for("register"))

    return render_template("register.html", now=datetime.now(), logged_in=is_logged_in())


@app.route("/cart")
def cart():
    if not is_logged_in():
        flash("Debes iniciar sesión para ver tu carrito.", "error")
        return redirect(url_for("login"))

    user_id = session["user_id"]
    status, cart_data = api_request(f"/api/v1/carts/?user_id={user_id}", "GET")
    if status != 200:
        cart_data = {"items": []}
        flash("No se pudo cargar el carrito.", "error")

    products_status, products_list = api_request("/api/v1/products/", "GET")
    product_map = {p["id"]: p for p in products_list} if products_status == 200 else {}

    items = cart_data.get("items", [])
    for item in items:
        prod = product_map.get(item.get("product_id"))
        if prod:
            item["product"] = prod

    return render_template(
        "cart.html",
        cart=cart_data,
        items=items,
        now=datetime.now(),
        logged_in=is_logged_in(),
    )


@app.route("/add-to-cart/<product_id>", methods=["POST"])
def add_to_cart(product_id):
    if not is_logged_in():
        flash("Debes iniciar sesión para agregar al carrito.", "error")
        return redirect(url_for("login"))

    qty = int(request.form.get("quantity", "1") or 1)
    user_id = session["user_id"]

    status, resp = api_request(
        "/api/v1/carts/items",
        "POST",
        {"user_id": user_id, "product_id": product_id, "quantity": qty},
    )

    if status in (200, 201):
        flash("Producto agregado al carrito.", "success")
    else:
        detail = resp.get("detail") if isinstance(resp, dict) else None
        flash(detail or "No se pudo agregar al carrito.", "error")

    return redirect(url_for("products"))


@app.route("/logout")
def logout():
    session.clear()
    flash("Sesión cerrada.", "success")
    return redirect(url_for("index"))


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
