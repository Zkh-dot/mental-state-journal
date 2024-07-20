from datetime import datetime
from django.db import models

class users(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=255)
    
    def __str__(self) -> str:
        return self.name
    
    @classmethod
    def user_exists(cls, user_id: int) -> bool:
        return cls.objects.filter(id=user_id).count() != 0
    
    @classmethod
    def add_user(cls, user_id: int, user_name=''):
        if not cls.user_exists(user_id):
            print('creating!')
            cls(id=user_id, name=user_name).save()
            return True
        return False
    
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

class journal(models.Model):
    author = models.ForeignKey(users, on_delete=models.CASCADE)
    line_type = models.CharField(max_length=255)
    mark = models.IntegerField(default=0)
    line_datetime = models.DateTimeField(default=datetime.now())
    
    def __str__(self):
        return self.author
