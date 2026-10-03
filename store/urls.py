
from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),

    path('register/', views.register, name='register'),
    path('login/', views.login, name='login'),
    path('logout/', views.logout, name='logout'),

    path('add-product/', views.add_product, name='add_product'),

    path(
        'product/<str:product_id>/',
        views.product_detail,
        name='product_detail'
    ),

    path(
        'product-image/<str:product_id>/',
        views.product_image,
        name='product_image'
    ),

    path(
        'edit-product/<str:product_id>/',
        views.edit_product,
        name='edit_product'
    ),

    path(
        'delete-product/<str:product_id>/',
        views.delete_product,
        name='delete_product'
    ),

    path(
        'add-to-cart/<str:product_id>/',
        views.add_to_cart,
        name='add_to_cart'
    ),

    path('cart/', views.view_cart, name='view_cart'),

    path(
        'increase-quantity/<str:product_id>/',
        views.increase_quantity,
        name='increase_quantity'
    ),

    path(
        'decrease-quantity/<str:product_id>/',
        views.decrease_quantity,
        name='decrease_quantity'
    ),

    path(
        'remove-from-cart/<str:product_id>/',
        views.remove_from_cart,
        name='remove_from_cart'
    ),

    path('checkout/', views.checkout, name='checkout'),

    path('my-orders/', views.my_orders, name='my_orders'),

    # Admin Product Management
    path(
        'admin-products/',
        views.admin_products,
        name='admin_products'
    ),

    path(
        'admin-delete-product/<str:product_id>/',
        views.admin_delete_product,
        name='admin_delete_product'
    ),

    path(
        'admin-edit-product/<str:product_id>/',
        views.admin_edit_product,
        name='admin_edit_product'
    ),
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
    


    # Admin Order Management
    path('admin-orders/', views.admin_orders, name='admin_orders'),

    path(
        'update-order-status/<str:order_id>/',
        views.update_order_status,
        name='update_order_status'
    ),
]