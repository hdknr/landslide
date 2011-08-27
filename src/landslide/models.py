# -*- coding: utf-8 -*-

from django.db.models import AutoField,Sum,Max ,Q
from django.db import models
from django.contrib.auth.models import User
from django.contrib.auth import authenticate

from datetime import datetime,timedelta
import re
import uuid 

# Create your models here.

__all__ = ['Slide',]

class Slide(models.Model):
    ''' Slide
        
    '''
    creator =  models.ForeignKey(User, verbose_name=u'Creator', related_name =u"%(class)s_creator",null=True,blank=True,default=None ) 
    ''' Slide Creator '''

    updater=  models.ForeignKey(User, verbose_name=u'Updater', related_name =u"%(class)s_updater",null=True,blank=True,default=None ) 
    ''' Slide Updater'''

    dt_created = models.DateTimeField(u'Created DateTime', default=datetime.now )
    ''' Created DateTime '''

    dt_updated = models.DateTimeField(u'Updated DateTime', default=datetime.now )
    ''' Updated DateTime '''

    title = models.CharField(u'Slide Title',max_length=200, )
    ''' Slide Title '''

    text  = models.TextField(u'Slide Text' )     
    ''' Slide Text '''

    markup = models.CharField(u'Markup Type', max_length=10, choices=(('.md','Markdown'),('.rst','reStructuredText')) )
    ''' Markup Type '''

    class Meta:
        verbose_name =u'Slide'
        verbose_name_plural =u'Slides'
        
