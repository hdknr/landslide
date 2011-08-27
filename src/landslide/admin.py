# -*- coding: utf-8 -*- 

from django.contrib import admin
from models import *

### Slide 
class SlideAdmin(admin.ModelAdmin):
    list_display=('creator','updater','dt_created','dt_updated','title','text','markup',)

admin.site.register(Slide,SlideAdmin)
