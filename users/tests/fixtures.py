from django.contrib.auth.models import User


def create_users():
    User.objects.create_user(username='user1', password='12345')
    User.objects.create_user(username='user2', password='12345')
    User.objects.create_user(username='user3', password='12345')
    User.objects.create_user(username='user4', password='12345')