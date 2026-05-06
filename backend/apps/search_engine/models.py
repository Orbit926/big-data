from django.db import models


class Destination(models.Model):
    name = models.CharField(max_length=255)
    country = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    avg_cost_per_day = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    tags = models.JSONField(default=list, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return f"{self.name}, {self.country}"
