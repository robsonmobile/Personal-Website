#!/usr/bin/env python
#
# Copyright 2007 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
import webapp2
import logging
import jinja2
import json
import os
from google.appengine.ext.webapp import template
from google.appengine.ext import db

template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir), autoescape = True)

class Handler(webapp2.RequestHandler):
    def write(self, *a, **kw):
        self.response.out.write(*a, **kw)

    def render_str(self, template, **params):
        t = jinja_env.get_template(template)
        return t.render(params)

    def render(self, template, **kw):
        self.write(self.render_str(template, **kw))

    def render_json(self, d):
        json_text = json.dumps(d)
        self.response.headers['Content-Type'] = 'application/json; charset=UTF-8'
        self.write(json_text)

class MainHandler(Handler):
    def get(self):
        self.render("index.html")

class ProjectPage(Handler):
    def get(self, project=None):
        project = Project.by_name(project)

        if not project:
            self.error(404)
            return
        if self.format == 'html':
            self.render('project.html', project = project)
        else:
            self.render_json(project.as_dict())

    def initialize(self, *a, **kw):
        webapp2.RequestHandler.initialize(self, *a, **kw)
        if self.request.url.endswith('.json'):
            self.format = 'json'
        else:
            self.format = 'html'

class TestAddProject(Handler):
    def get(self):
        project = Project(name = "Depot", short_description = 'A CTA app', long_description = 'A CTA app for people in Chicago', play_store_link = 'http://www.google.com', github_link = 'http://www.github.com')
        project.put()


class Project(db.Model):
    name = db.StringProperty(required = True)
    short_description = db.TextProperty(required = True)
    long_description = db.TextProperty()
    play_store_link = db.LinkProperty()
    github_link = db.LinkProperty()
    screenshots = db.StringListProperty()

    @classmethod
    def by_name(cls, name):
        project = Project.all().filter('name =', name).get()
        return project

    def render(self):
        self._render_text = self.content.replace('\n', '<br>')
        return render_str("project.html", project = self)

    def as_dict(self):
        d = {'name': self.name,
             'short_description': self.short_description,
             'long_description': self.long_description,
             'play_store_link': self.play_store_link,
             'github_link': self.github_link,
             'screenshots': self.screenshots}
        return d

app = webapp2.WSGIApplication([('/', MainHandler),
                               webapp2.Route(r'/projects/<project>', handler = ProjectPage),
                               ('/testaddproject', TestAddProject),
                               ], 
                              debug=True)