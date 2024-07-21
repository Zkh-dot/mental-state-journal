from datetime import datetime
from django.db import models
from django.contrib.auth.models import AbstractBaseUser

class users(AbstractBaseUser):
    id = models.IntegerField(primary_key=True)
    password = models.BinaryField()
    name = models.CharField(max_length=255)
    
    def __str__(self) -> str:
        return self.name
    
    @classmethod
    def user_exists(cls, user_id: int) -> bool:
        return cls.objects.filter(id=user_id).count() != 0
    
    @classmethod
    def add_user(cls, user_id: int, user_password: bytes, user_name=''):
        if cls.user_exists(user_id):
            return False
        cls(id=user_id, password=user_password, name=user_name).save()
        return True
    
    @classmethod
    def set_user_name(cls, user_id: int, user_name: str):
        if not cls.user_exists(user_id):
            return False
        line = cls.objects.get(id=user_id)
        line.name = user_name
        line.save()
        return True
    
    @classmethod
    def get_user_name(cls, user_id: int) -> str:
        if not cls.user_exists(user_id):
            return ""
        return cls.objects.get(id=user_id).name
    
    @classmethod
    def auth_user(cls, user_id: int, password: str):
        if not cls.user_exists(user_id):
            return None
        if cls.objects.get(id=user_id).password == password:
            return cls.objects.get(id=user_id)
        return None
    
class users_salt(models.Model):
    id = models.OneToOneField(users, primary_key=True, on_delete=models.CASCADE)
    salt = models.BinaryField()
    
    @classmethod
    def salt_exists(cls, user_id: int):
        return cls.objects.filter(id=users.objects.get(id=user_id)).count() != 0
    
    @classmethod
    def add_salt(cls, user_id: int, user_salt: bytes):
        if cls.salt_exists(user_id):
            return False
        cls(id=users.objects.get(id=user_id), salt=user_salt).save()
        return True
        
    @classmethod
    def get_salt(cls, user_id: int) -> bytes:
        if not cls.salt_exists(user_id):
            return False
        return cls.objects.get(id=users.objects.get(id=user_id)).salt

class journal(models.Model):
    author = models.ForeignKey(users, on_delete=models.CASCADE)
    line_type = models.CharField(max_length=255)
    mark = models.IntegerField(default=0)
    line_datetime = models.DateTimeField(default=datetime.now())
    
    def __str__(self):
        return self.author
    
    @classmethod
    def add_post(self, user_id: int):
        pass
