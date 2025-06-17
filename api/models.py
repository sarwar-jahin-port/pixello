from django.db import models
from django.conf import settings

class Payment(models.Model):
    user           = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    transaction_id = models.CharField(max_length=100, unique=True)
    status         = models.CharField(
                        max_length=20,
                        choices=[('pending','pending'),('success','success'),('failed','failed')]
                    )
    created_at     = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return f"{self.transaction_id} ({self.status})"