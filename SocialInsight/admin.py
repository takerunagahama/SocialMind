from django.contrib import admin
from .models import Session, QandA, Scores, Messages

admin.site.register(Session)
admin.site.register(QandA)
admin.site.register(Scores)
admin.site.register(Messages)