from django.core.management.base import BaseCommand
from django.conf import settings
from products.models import Product
import cloudinary.uploader
import os


class Command(BaseCommand):
    help = "Migrate local product images to Cloudinary"

    def handle(self, *args, **kwargs):
        migrated_count = 0

        # BASE_DIR points to backend/
        BASE_DIR = settings.BASE_DIR

        for product in Product.objects.all():
            for field_name in ["image", "image2", "image3"]:
                field = getattr(product, field_name)

                if not field:
                    continue

                # Skip already migrated images
                if str(field).startswith("http"):
                    continue

                # 🔥 Correct absolute path (THIS IS THE FIX)
                local_path = os.path.join(BASE_DIR, "media", field.name)

                if not os.path.exists(local_path):
                    self.stdout.write(
                        self.style.WARNING(f"❌ File not found: {local_path}")
                    )
                    continue

                result = cloudinary.uploader.upload(local_path, folder="products")

                setattr(product, field_name, result["secure_url"])
                product.save(update_fields=[field_name])

                migrated_count += 1
                self.stdout.write(self.style.SUCCESS(f"✅ Uploaded: {local_path}"))

        self.stdout.write(
            self.style.SUCCESS(
                f"\n🎉 Migration complete. Total images uploaded: {migrated_count}"
            )
        )
