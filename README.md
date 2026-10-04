# CampusCart 🛒

**CampusCart** is a student marketplace web application that allows college students to buy and sell used books, electronics, stationery, and other essential products.

🌐 **Live Demo:** https://campuscart-40pk.onrender.com/

## ✨ Features

* Student Registration, Login and Logout
* Add, Edit and Delete Products
* Search Products and Filter by Category
* Product Images and Detailed Information
* Shopping Cart with Quantity Management
* Checkout and Order Placement
* My Orders and Order Status Tracking
* Admin Dashboard
* Admin Product and Order Management

## 🛠️ Technologies Used

**Frontend**

* HTML5
* CSS3
* JavaScript
* Bootstrap

**Backend**

* Python
* Django

**Database**

* MongoDB
* SQLite (for Django built-in admin features)

**Deployment**

* Render
* GitHub

## 🚀 How to Run Locally

1. Clone the repository:

   ```bash
   git clone https://github.com/ingle-shruti/CampusCart-.git
   ```

2. Open the project folder:

   ```bash
   cd CampusCart-
   ```

3. Create and activate a virtual environment:

   ```bash
   python -m venv venv
   ```

   Windows PowerShell:

   ```powershell
   .\venv\Scripts\Activate.ps1
   ```

4. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

5. Configure your MongoDB connection using the `MONGO_URI` environment variable. Set `DJANGO_SECRET_KEY` as well.

6. Run database migrations:

   ```bash
   python manage.py migrate
   ```

7. Start the development server:

   ```bash
   python manage.py runserver
   ```

8. Open in your browser:

   `http://127.0.0.1:8000/`

## 👩‍💻 Developer

**Shruti Ingle**
Full Stack Development Intern

## 📌 Project Purpose

CampusCart aims to make buying and selling useful academic products easier and more convenient for college students.
