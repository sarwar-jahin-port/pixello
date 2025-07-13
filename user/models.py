from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings

# Create your models here.

class User(AbstractUser):
    phone = models.CharField(max_length=15, blank=True)
    location = models.CharField(max_length=100, blank=True)
    premium = models.BooleanField(default=False)
    connections = models.ManyToManyField('self', symmetrical=True, blank=True)

    def __str__(self):
        return self.username
    
class FriendRequest(models.Model):
    PENDING  = 'P'
    ACCEPTED = 'A'
    REJECTED = 'R'

    STATUS_CHOICES = [
        (PENDING,  'Pending'),
        (ACCEPTED, 'Accepted'),
        (REJECTED, 'Rejected'),
    ]

    from_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='sent_requests',
        on_delete=models.CASCADE
    )
    to_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='received_requests',
        on_delete=models.CASCADE
    )
    status  = models.CharField(max_length=1, choices=STATUS_CHOICES, default=PENDING)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('from_user', 'to_user')

    def accept(self):
        self.status = self.ACCEPTED
        self.save()
        # add each other as friends
        self.from_user.connections.add(self.to_user)

    def reject(self):
        self.status = self.REJECTED
        self.save()

    def delete(self, *args, **kwargs):
        if self.status == self.ACCEPTED:
            self.from_user.connections.remove(self.to_user)
        super().delete(*args, **kwargs)