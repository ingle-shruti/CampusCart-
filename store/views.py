
from bson import ObjectId

from django.shortcuts import render, redirect
from django.contrib.auth.hashers import make_password, check_password
from django.http import HttpResponse

from .mongodb import (
    products_collection,
    users_collection,
    orders_collection,
    save_order
)


# Check whether the logged-in account is active
def is_account_active(username):
    user = users_collection.find_one({"username": username})

    # Existing accounts without is_active are treated as active
    return user is not None and user.get("is_active", True) is True


# Home
def home(request):
    search_query = request.GET.get("search", "")
    selected_category = request.GET.get("category", "")

    query = {}

    if search_query:
        query["name"] = {"$regex": search_query, "$options": "i"}

    if selected_category:
        query["category"] = {
            "$regex": f"^{selected_category}$",
            "$options": "i"
        }

    products = list(products_collection.find(query))

    for product in products:
        product["id"] = str(product["_id"])
        product["image_url"] = (
            f"/product-image/{product['id']}/"
            if product.get("image") else None
        )

    return render(request, "store/home.html", {
        "products": products,
        "search_query": search_query,
        "selected_category": selected_category
    })


# Student Registration
def register(request):
    if request.method == "POST":
        full_name = request.POST.get("full_name", "").strip()
        email = request.POST.get("email", "").strip()
        username = request.POST.get("username", "").strip()
        password = request.POST.get("password", "")
        confirm_password = request.POST.get("confirm_password", "")

        if not all([full_name, email, username, password]):
            return render(request, "store/register.html", {
                "error": "Please fill in all fields!"
            })

        if password != confirm_password:
            return render(request, "store/register.html", {
                "error": "Passwords do not match!"
            })

        if users_collection.find_one({
            "$or": [{"username": username}, {"email": email}]
        }):
            return render(request, "store/register.html", {
                "error": "Username or email already exists!"
            })

        users_collection.insert_one({
            "full_name": full_name,
            "email": email,
            "username": username,
            "password": make_password(password),
            "is_active": True
        })

        return redirect("login")

    return render(request, "store/register.html")


# Student Login
def login(request):
    if request.method == "POST":
        username = request.POST.get("username", "").strip()
        password = request.POST.get("password", "")

        user = users_collection.find_one({"username": username})

        if user and not user.get("is_active", True):
            return render(request, "store/login.html", {
                "error": "Your account is deactivated. Please reactivate your account first."
            })

        if user and check_password(password, user["password"]):
            request.session["username"] = username
            return redirect("home")

        return render(request, "store/login.html", {
            "error": "Invalid username or password!"
        })

    return render(request, "store/login.html")


# Student Logout
def logout(request):
    request.session.flush()
    return redirect("home")


# Deactivate Account
def deactivate_account(request):
    if not request.session.get("username"):
        return redirect("login")

    if request.method != "POST":
        return redirect("home")

    username = request.session.get("username")

    users_collection.update_one(
        {"username": username},
        {"$set": {"is_active": False}}
    )

    request.session.flush()

    return redirect("home")


# Reactivate Account
def reactivate_account(request):
    if request.method == "POST":
        username = request.POST.get("username", "").strip()
        password = request.POST.get("password", "")

        user = users_collection.find_one({"username": username})

        if (
            user
            and user.get("is_active", True) is False
            and check_password(password, user["password"])
        ):
            users_collection.update_one(
                {"username": username},
                {"$set": {"is_active": True}}
            )

            return redirect("login")

        return render(request, "store/reactivate_account.html", {
            "error": "Invalid username or password, or account is already active!"
        })

    return render(request, "store/reactivate_account.html")


# Add Product
def add_product(request):
    if not request.session.get("username") or not is_account_active(
        request.session.get("username")
    ):
        request.session.flush()
        return redirect("login")

    if request.method == "POST":
        try:
            price = float(request.POST.get("price"))

            if price <= 0:
                raise ValueError

        except (TypeError, ValueError):
            return render(request, "store/add_product.html", {
                "error": "Please enter a valid price!"
            })

        image = request.FILES.get("image")

        if not image:
            return render(request, "store/add_product.html", {
                "error": "Please select a product photo!"
            })

        if image.size > 5 * 1024 * 1024:
            return render(request, "store/add_product.html", {
                "error": "Image size must be less than 5 MB!"
            })

        if image.content_type not in [
            "image/jpeg", "image/png", "image/webp"
        ]:
            return render(request, "store/add_product.html", {
                "error": "Please upload a JPG, PNG or WEBP image!"
            })

        product = {
            "name": request.POST.get("name"),
            "description": request.POST.get("description"),
            "price": price,
            "category": request.POST.get("category"),
            "condition": request.POST.get("condition"),
            "seller": request.session.get("username"),
            "image": image.read(),
            "image_content_type": image.content_type
        }

        products_collection.insert_one(product)
        return redirect("home")

    return render(request, "store/add_product.html")


# Display Product Image
def product_image(request, product_id):
    try:
        product = products_collection.find_one({
            "_id": ObjectId(product_id)
        })
    except Exception:
        return HttpResponse(status=404)

    if not product or not product.get("image"):
        return HttpResponse(status=404)

    return HttpResponse(
        product["image"],
        content_type=product.get("image_content_type", "image/jpeg")
    )


# Product Details
def product_detail(request, product_id):
    try:
        product = products_collection.find_one({
            "_id": ObjectId(product_id)
        })
    except Exception:
        return redirect("home")

    if not product:
        return redirect("home")

    product["id"] = str(product["_id"])

    return render(request, "store/product_detail.html", {
        "product": product
    })


# Student Edit Product
def edit_product(request, product_id):
    if not request.session.get("username") or not is_account_active(
        request.session.get("username")
    ):
        request.session.flush()
        return redirect("login")

    try:
        product = products_collection.find_one({
            "_id": ObjectId(product_id)
        })
    except Exception:
        return redirect("home")

    if not product:
        return redirect("home")

    if product.get("seller") != request.session.get("username"):
        return redirect("home")

    if request.method == "POST":
        try:
            price = float(request.POST.get("price"))

            if price <= 0:
                raise ValueError

        except (TypeError, ValueError):
            product["id"] = str(product["_id"])

            return render(request, "store/edit_product.html", {
                "product": product,
                "error": "Please enter a valid price!"
            })

        updated_product = {
            "name": request.POST.get("name"),
            "description": request.POST.get("description"),
            "price": price,
            "category": request.POST.get("category"),
            "condition": request.POST.get("condition")
        }

        image = request.FILES.get("image")

        if image:
            if image.size > 5 * 1024 * 1024:
                product["id"] = str(product["_id"])

                return render(request, "store/edit_product.html", {
                    "product": product,
                    "error": "Image size must be less than 5 MB!"
                })

            if image.content_type not in [
                "image/jpeg", "image/png", "image/webp"
            ]:
                product["id"] = str(product["_id"])

                return render(request, "store/edit_product.html", {
                    "product": product,
                    "error": "Please upload JPG, PNG or WEBP image!"
                })

            updated_product["image"] = image.read()
            updated_product["image_content_type"] = image.content_type

        products_collection.update_one(
            {"_id": ObjectId(product_id)},
            {"$set": updated_product}
        )

        return redirect("product_detail", product_id=product_id)

    product["id"] = str(product["_id"])

    return render(request, "store/edit_product.html", {
        "product": product
    })


# Student Delete Product
def delete_product(request, product_id):
    if not request.session.get("username") or not is_account_active(
        request.session.get("username")
    ):
        request.session.flush()
        return redirect("login")

    if request.method != "POST":
        return redirect("home")

    try:
        product = products_collection.find_one({
            "_id": ObjectId(product_id)
        })
    except Exception:
        return redirect("home")

    if not product:
        return redirect("home")

    if product.get("seller") != request.session.get("username"):
        return redirect("home")

    products_collection.delete_one({
        "_id": ObjectId(product_id)
    })

    cart = request.session.get("cart", {})
    cart.pop(product_id, None)
    request.session["cart"] = cart

    return redirect("home")


# Add Product to Cart
def add_to_cart(request, product_id):
    if not request.session.get("username") or not is_account_active(
        request.session.get("username")
    ):
        request.session.flush()
        return redirect("login")

    if request.method != "POST":
        return redirect("home")

    try:
        product = products_collection.find_one({
            "_id": ObjectId(product_id)
        })
    except Exception:
        return redirect("home")

    if not product:
        return redirect("home")

    if product.get("seller") == request.session.get("username"):
        return redirect("home")

    cart = request.session.get("cart", {})
    product_id = str(product_id)

    cart[product_id] = int(cart.get(product_id, 0)) + 1

    request.session["cart"] = cart
    request.session.modified = True

    return redirect("view_cart")


# View Cart
def view_cart(request):
    if not request.session.get("username") or not is_account_active(
        request.session.get("username")
    ):
        request.session.flush()
        return redirect("login")

    cart = request.session.get("cart", {})
    cart_items = []
    total = 0

    for product_id, quantity in cart.items():
        try:
            product = products_collection.find_one({
                "_id": ObjectId(product_id)
            })
        except Exception:
            continue

        if product:
            product["id"] = product_id
            product["quantity"] = quantity
            product["subtotal"] = product["price"] * quantity

            total += product["subtotal"]
            cart_items.append(product)

    return render(request, "store/cart.html", {
        "cart_items": cart_items,
        "total": total
    })


# Increase Cart Quantity
def increase_quantity(request, product_id):
    if not request.session.get("username") or not is_account_active(
        request.session.get("username")
    ):
        request.session.flush()
        return redirect("login")

    if request.method != "POST":
        return redirect("view_cart")

    cart = request.session.get("cart", {})

    if product_id in cart:
        cart[product_id] = int(cart[product_id]) + 1

    request.session["cart"] = cart
    request.session.modified = True

    return redirect("view_cart")


# Decrease Cart Quantity
def decrease_quantity(request, product_id):
    if not request.session.get("username") or not is_account_active(
        request.session.get("username")
    ):
        request.session.flush()
        return redirect("login")

    if request.method != "POST":
        return redirect("view_cart")

    cart = request.session.get("cart", {})

    if product_id in cart:
        if int(cart[product_id]) > 1:
            cart[product_id] = int(cart[product_id]) - 1
        else:
            del cart[product_id]

    request.session["cart"] = cart
    request.session.modified = True

    return redirect("view_cart")


# Remove Product from Cart
def remove_from_cart(request, product_id):
    if not request.session.get("username") or not is_account_active(
        request.session.get("username")
    ):
        request.session.flush()
        return redirect("login")

    if request.method != "POST":
        return redirect("view_cart")

    cart = request.session.get("cart", {})
    cart.pop(product_id, None)

    request.session["cart"] = cart
    request.session.modified = True

    return redirect("view_cart")


# Checkout Page
def checkout(request):
    if not request.session.get("username") or not is_account_active(
        request.session.get("username")
    ):
        request.session.flush()
        return redirect("login")

    cart = request.session.get("cart", {})
    cart_items = []
    total = 0

    for product_id, quantity in cart.items():
        try:
            product = products_collection.find_one({
                "_id": ObjectId(product_id)
            })
        except Exception:
            continue

        if product:
            subtotal = product["price"] * quantity

            cart_items.append({
                "product_id": product_id,
                "name": product["name"],
                "price": product["price"],
                "quantity": quantity,
                "subtotal": subtotal
            })

            total += subtotal

    if not cart_items:
        return redirect("view_cart")

    if request.method == "POST":
        customer_name = request.POST.get("customer_name", "").strip()
        phone = request.POST.get("phone", "").strip()
        address = request.POST.get("address", "").strip()

        if not customer_name or not phone or not address:
            return render(request, "store/checkout.html", {
                "cart_items": cart_items,
                "total": total,
                "error": "Please fill in all delivery details!"
            })

        order = {
            "username": request.session.get("username"),
            "customer_name": customer_name,
            "phone": phone,
            "address": address,
            "items": cart_items,
            "total": total,
            "status": "Placed"
        }

        order_id = save_order(order)

        request.session["cart"] = {}
        request.session.modified = True

        return render(request, "store/order_success.html", {
            "order_id": str(order_id),
            "total": total
        })

    return render(request, "store/checkout.html", {
        "cart_items": cart_items,
        "total": total
    })


# My Orders
def my_orders(request):
    if not request.session.get("username") or not is_account_active(
        request.session.get("username")
    ):
        request.session.flush()
        return redirect("login")

    username = request.session.get("username")

    orders = list(
        orders_collection.find({"username": username}).sort("_id", -1)
    )

    for order in orders:
        order["id"] = str(order["_id"])

    return render(request, "store/my_orders.html", {
        "orders": orders
    })


# Admin Product Management
def admin_products(request):
    if not request.user.is_authenticated or not request.user.is_superuser:
        return redirect("admin:login")

    products = list(products_collection.find().sort("_id", -1))

    for product in products:
        product["id"] = str(product["_id"])

    return render(request, "store/admin_products.html", {
        "products": products
    })


# Admin Delete Product
def admin_delete_product(request, product_id):
    if not request.user.is_authenticated or not request.user.is_superuser:
        return redirect("admin:login")

    if request.method == "POST":
        try:
            products_collection.delete_one({
                "_id": ObjectId(product_id)
            })
        except Exception as e:
            print("Delete error:", e)

    return redirect("admin_products")


# Admin Edit Product
def admin_edit_product(request, product_id):
    if not request.user.is_authenticated or not request.user.is_superuser:
        return redirect("admin:login")

    try:
        product = products_collection.find_one({
            "_id": ObjectId(product_id)
        })
    except Exception:
        return redirect("admin_products")

    if not product:
        return redirect("admin_products")

    product["id"] = str(product["_id"])

    if request.method == "POST":
        try:
            price = float(request.POST.get("price"))

            if price <= 0:
                raise ValueError

        except (TypeError, ValueError):
            return render(request, "store/admin_edit_product.html", {
                "product": product,
                "error": "Please enter a valid price!"
            })

        updated_product = {
            "name": request.POST.get("name", "").strip(),
            "description": request.POST.get("description", "").strip(),
            "price": price,
            "category": request.POST.get("category", "").strip(),
            "condition": request.POST.get("condition", "").strip()
        }

        if not all([
            updated_product["name"],
            updated_product["description"],
            updated_product["category"],
            updated_product["condition"]
        ]):
            return render(request, "store/admin_edit_product.html", {
                "product": product,
                "error": "Please fill in all fields!"
            })

        image = request.FILES.get("image")

        if image:
            if image.size > 5 * 1024 * 1024:
                return render(request, "store/admin_edit_product.html", {
                    "product": product,
                    "error": "Image size must be less than 5 MB!"
                })

            if image.content_type not in [
                "image/jpeg", "image/png", "image/webp"
            ]:
                return render(request, "store/admin_edit_product.html", {
                    "product": product,
                    "error": "Please upload JPG, PNG or WEBP image!"
                })

            updated_product["image"] = image.read()
            updated_product["image_content_type"] = image.content_type

        products_collection.update_one(
            {"_id": ObjectId(product_id)},
            {"$set": updated_product}
        )

        return redirect("admin_products")

    return render(request, "store/admin_edit_product.html", {
        "product": product
    })


# Admin Order Management
def admin_orders(request):
    if not request.user.is_authenticated or not request.user.is_superuser:
        return redirect("admin:login")

    orders = list(orders_collection.find().sort("_id", -1))

    for order in orders:
        order["id"] = str(order["_id"])

    return render(request, "store/admin_orders.html", {
        "orders": orders
    })


# Update Order Status
def update_order_status(request, order_id):
    if not request.user.is_authenticated or not request.user.is_superuser:
        return redirect("admin:login")

    if request.method == "POST":
        status = request.POST.get("status")

        allowed_statuses = ["Placed", "Shipped", "Delivered"]

        if status not in allowed_statuses:
            return redirect("admin_orders")

        try:
            order = orders_collection.find_one({
                "_id": ObjectId(order_id)
            })

            if order:
                orders_collection.update_one(
                    {"_id": ObjectId(order_id)},
                    {"$set": {"status": status}}
                )

        except Exception as e:
            print("Update error:", e)

    return redirect("admin_orders")


# Admin Dashboard
def admin_dashboard(request):
    if not request.user.is_authenticated or not request.user.is_superuser:
        return redirect("admin:login")

    total_products = products_collection.count_documents({})
    total_orders = orders_collection.count_documents({})
    total_users = users_collection.count_documents({})

    total_revenue = sum(
        float(order.get("total", order.get("total_amount", 0)) or 0)
        for order in orders_collection.find()
    )

    recent_orders = list(
        orders_collection.find().sort("_id", -1).limit(5)
    )

    recent_products = list(
        products_collection.find().sort("_id", -1).limit(5)
    )

    for order in recent_orders:
        order["id"] = str(order["_id"])

    for product in recent_products:
        product["id"] = str(product["_id"])
        product["has_image"] = bool(product.get("image"))

        print(
            product.get("name"),
            "IMAGE EXISTS:",
            product["has_image"]
        )

    return render(request, "store/admin_dashboard.html", {
        "total_products": total_products,
        "total_orders": total_orders,
        "total_users": total_users,
        "total_revenue": total_revenue,
        "recent_orders": recent_orders,
        "recent_products": recent_products
    })
    # Admin User Management
def admin_users(request):
    if not request.user.is_authenticated or not request.user.is_superuser:
        return redirect("admin:login")

    users = list(users_collection.find().sort("_id", -1))

    for user in users:
        user["id"] = str(user["_id"])
        user.pop("password", None)

    return render(request, "store/admin_users.html", {
        "users": users
    })


# Admin Delete User Account
def admin_delete_user(request, user_id):
    if not request.user.is_authenticated or not request.user.is_superuser:
        return redirect("admin:login")

    if request.method == "POST":
        try:
            users_collection.delete_one({
                "_id": ObjectId(user_id)
            })
        except Exception as e:
            print("Delete user error:", e)

    return redirect("admin_users")