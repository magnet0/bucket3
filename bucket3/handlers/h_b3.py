from bucket3.bucket import bucket

import markdown
import codecs
import sys,os
import yaml
from datetime import datetime
import time
import shutil

from django.template import Template, Context, loader

class h_b3(bucket):
	@classmethod
	def types(cls):
		return ('.b3',)

	def toHTML(self, content):
		# asking the user to enter "@site" in from of image URLs, etc is not the most
		# elegant solution... Ex. <img src="@site/photo.jpg" />
		# any suggestion is welcome!
		if self.page['type']=='page':
			isPage = True
		else:
			isPage = False
		return markdown.markdown(content.replace('@site',self.itemURL(self.file, self.date(), isPage)))

	def __init__(self, conf, file):
		bucket.__init__(self, conf)
		self.file = file
		self.index_file = "%s/%s" % (file, 'index.markdown')
		self.page = {}
	def parse(self):
		data = codecs.open(self.index_file, mode='r', encoding='utf8').read()
		if data[0:3] == '---' :
			dummy, frontMatter, text = data.split('---', 2)
			self.frontmatter = yaml.load(frontMatter)
		else:
			return false
		if 'date' in self.frontmatter:
			self.page['cre_dat'] = datetime.strptime(self.frontmatter['date'], '%Y-%m-%d %H:%M')
			# self.page['cre_dat'] = self.frontmatter['date']
		else:
			self.page['cre_dat'] = datetime.today()
		if 'title' in self.frontmatter:
			self.page['title'] = self.frontmatter['title']
		else: 
			self.page['title'] = self.file
		if 'type' in self.frontmatter:
			self.page['type'] = self.frontmatter['type']
		else:
			self.page['type'] = 'post'
		if 'tags' in self.frontmatter and self.frontmatter['tags']:
			self.page['tags'] = self.frontmatter['tags'].split(',')
		else:
			self.page['tags'] = ()

		# .toHTML must be called last, as it may use data calculated above.
		self.page['body'] = self.toHTML(text)
		return self

	def title(self):
		return self.page['title']
	def url(self):
		if self.page['type']=='page':
			isPage = True
		else:
			isPage = False
		return self.itemURL(file=self.file, cre_dat=self.page['cre_dat'], isPage=isPage )
	def body(self):
		return self.page['body']
	def date(self):
		return self.page['cre_dat']
	def type(self):
		return self.page['type']
	def tags(self):
		return self.page['tags']
	def frontmatter(self):
		return self.frontmatter


	def render(self):
		if self.page['type']=='page':
			isPage = True
		else:
			isPage = False
		t = loader.get_template('post.html') 
		c = Context({'blog':self.conf, 
			'frontmatter':self.frontmatter,
			'page':self.page
			})
		html = t.render(c).encode('utf-8')
		post_dir = self.osItemDir(file=self.file, cre_dat=self.date(), isPage=isPage)
		if not os.path.exists(post_dir):
			os.makedirs(post_dir)
		out_filename = self.osItem(file=self.file, cre_dat=self.date(), isPage=isPage)
		out_file = open(out_filename,'w')
		out_file.write(html)
		out_file.close()
		base, dirs, files = os.walk(self.file).next() 
		for f in files:
			if f != 'index.markdown':
				ff = '%s/%s' % (self.file, f)
				shutil.copy(ff, post_dir)
		for f in dirs:
				ff = '%s/%s' % (self.file, f)
				shutil.copytree(ff, post_dir)

