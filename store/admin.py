import mimetypes

from django.contrib import admin
from .models import Product
from .mongodb import products_collection


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):

    list_display = ("name", "price", "category", "condition")

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)

        product_data = {
            "name": obj.name,
            "description": obj.description,
            "price": float(obj.price),
            "category": obj.category,
            "condition": obj.condition,
            "seller": "Admin",
            "admin_product_id": obj.id,
        }

        if obj.image:
            with obj.image.open("rb") as image_file:
                product_data["image"] = image_file.read()

            content_type, _ = mimetypes.guess_type(obj.image.name)

            product_data["image_content_type"] = (
                content_type or "image/jpeg"
            )

        products_collection.update_one(
            {"admin_product_id": obj.id},
            {"$set": product_data},
            upsert=True
        )

    def delete_model(self, request, obj):
        products_collection.delete_one(
            {"admin_product_id": obj.id}
        )
        super().delete_model(request, obj)