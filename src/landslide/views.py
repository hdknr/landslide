# -*- coding: utf-8 -*-

from datetime import datetime,timedelta
from django import template
from django.conf.urls.defaults import *
from django.contrib.auth import  login as auth_login , logout as auth_logout
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.core.urlresolvers import reverse
from django.core.exceptions import ValidationError
from django.db import transaction,models
from django.db.models import Q
from django.http import HttpResponse,HttpResponseRedirect
from django.shortcuts import render_to_response

from models import *
import csv
import re
import settings

from landslide import generator,main
from landslide.parser import Parser

class DjGenerator(generator.Generator):

    def __init__(self,*args,**kwargs):
        self.copy_theme = kwargs.get('copy_theme', False)
        self.debug = kwargs.get('debug', False)
        self.destination_file = kwargs.get('destination_file',
                                           'presentation.html')
        self.direct = kwargs.get('direct', False)
        self.embed = kwargs.get('embed', False)
        self.encoding = kwargs.get('encoding', 'utf8')
        self.extensions = kwargs.get('extensions', None)
        self.logger = kwargs.get('logger', None)
        self.relative = kwargs.get('relative', False)
        self.theme = kwargs.get('theme', 'default')
        self.verbose = kwargs.get('verbose', False)
        self.linenos = self.linenos_check(kwargs.get('linenos'))
        self.num_slides = 0
        self.__toc = []


        # macros registering
        self.macros = []
        self.register_macro(*self.default_macros)

        if self.direct:
            self.verbose = True

        self.theme_dir = ''

    def fetch_contents(self, source, markup='.md'):
        """ Recursively fetches Markdown contents from a single file or
            directory containing itself Markdown files.
        """
        slides = []

        if type(source) is list:
            for entry in source:
                slides.extend(self.fetch_contents(entry))
        else:
            try:
                parser = Parser( markup, self.encoding, self.extensions)
            except NotImplementedError,e:
                print type(e),e
                return slides

#            self.log(u"Adding   %s (%s)" % (source, parser.format))

            try:
                file_contents = source
            except UnicodeDecodeError,e:
                print type(e),e
#                self.log(u"Unable to decode source %s: skipping" % source, 'warning')
            else:
                parsed_contents = parser.parse(file_contents)
                inner_slides = re.split(r'<hr.+>', parsed_contents)
                for inner_slide in inner_slides:
                    slides.append(self.get_slide_vars(inner_slide, source))

        if not slides:
            self.log(u"Exiting  %s: no contents found" % source, 'notice')

        return slides


    def get_template_vars(self, slides):
        """ Computes template vars from slides html source code.
        """
        try:
            head_title = slides[0]['title']
        except (IndexError, TypeError):
            head_title = "Untitled Presentation"

        for slide_index, slide_vars in enumerate(slides):
            if not slide_vars:
                continue
            self.num_slides += 1
            slide_number = slide_vars['number'] = self.num_slides
            if slide_vars['level'] and slide_vars['level'] <= generator.TOC_MAX_LEVEL:
                self.add_toc_entry(slide_vars['title'], slide_vars['level'],
                                   slide_number)

        return {'head_title': head_title, 'num_slides': str(self.num_slides),
                'slides': slides, 'toc': self.toc, 'embed': self.embed,
                'css': self.get_css(), 'js': self.get_js(),
                'user_css': self.user_css, 'user_js': self.user_js}

    def add_toc_entry(self, title, level, slide_number):
        """ Adds a new entry to current presentation Table of Contents.
        """
        self.__toc.append({'title': title, 'number': slide_number,
                           'level': level})

    @property
    def toc(self):
        """ Smart getter for Table of Content list.
        """
        toc = []
        stack = [toc]
        for entry in self.__toc:
            entry['sub'] = []
            while entry['level'] < len(stack):
                stack.pop()
            while entry['level'] > len(stack):
                stack.append(stack[-1][-1]['sub'])
            stack[-1].append(entry)
        return toc


    def render(self,request,texts,markup='.md'):
        """ Returns generated html code.
        """
        slides = self.fetch_contents(texts,markup)
        context = self.get_template_vars(slides)
        
        for k in context:
            print k
        return render_to_response( "slide.html", context ,        
                    context_instance=template.RequestContext(request),)
    
from models import *
def render(request,id=None):
    ''' lender 

        :param request: WSGI request object
        :param id: model id
    '''
    opt , f= main._parse_options()
    return DjGenerator(** opt.__dict__).render(request,Slide.objects.get(id=id ).text)
