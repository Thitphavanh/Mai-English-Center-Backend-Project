import os
import requests
from django.core.management.base import BaseCommand
from django.core.files.base import ContentFile
from academics.models import Course

class Command(BaseCommand):
    help = 'Seed placeholder images for courses'

    def handle(self, *args, **options):
        courses = Course.objects.all()
        if not courses.exists():
            self.stdout.write(self.style.WARNING("No courses found to update."))
            return

        # List of placeholder images from Unsplash (Educational/Books related)
        image_urls = [
            "https://images.unsplash.com/photo-1503676260728-1c00da094a0b?q=80&w=800&auto=format&fit=crop",
            "https://images.unsplash.com/photo-1497633762265-9d179a990aa6?q=80&w=800&auto=format&fit=crop",
            "https://images.unsplash.com/photo-1546410531-bb4caa6b424d?q=80&w=800&auto=format&fit=crop",
            "https://images.unsplash.com/photo-1456513080510-7bf3a84b82f8?q=80&w=800&auto=format&fit=crop",
            "https://images.unsplash.com/photo-1516979187457-637abb4f9353?q=80&w=800&auto=format&fit=crop",
            "https://images.unsplash.com/photo-1580582932707-520aed937b7b?q=80&w=800&auto=format&fit=crop",
        ]

        count = 0
        for i, course in enumerate(courses):
            # Rotate through the images
            image_url = image_urls[i % len(image_urls)]
            
            try:
                self.stdout.write(f"Downloading image for {course.name}...")
                response = requests.get(image_url, timeout=10)
                if response.status_code == 200:
                    file_name = f"course_{course.id}.jpg"
                    course.thumbnail.save(file_name, ContentFile(response.content), save=True)
                    self.stdout.write(self.style.SUCCESS(f"Updated {course.name} with image."))
                    count += 1
                else:
                    self.stdout.write(self.style.ERROR(f"Failed to download image for {course.name}"))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"Error updating {course.name}: {str(e)}"))

        self.stdout.write(self.style.SUCCESS(f"Successfully updated {count} courses with placeholder images."))
