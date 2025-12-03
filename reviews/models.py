from django.db import models

from houses.models import House


# Create your models here.
class Review(models.Model):
    house = models.ForeignKey(House, on_delete=models.CASCADE, related_name='reviews')

    # No user account needed
    name = models.CharField(max_length=60)
    email = models.EmailField()

    rating = models.PositiveIntegerField(choices=[(i, f"{i} Star{'s' if i > 1 else ''}") for i in range(1,6)])
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} - {self.rating} - {self.house.title}"

    class Meta:
        verbose_name = "Review"
        verbose_name_plural = "Reviews"
        ordering = ['-created_at']
