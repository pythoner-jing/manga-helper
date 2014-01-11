#!/usr/bin/env python
#coding:utf-8

from sgmllib import SGMLParser
import urllib2, re

reg_name = re.compile(r"g_comic_name\s=\s\"([^\"]+)\"")

url_test = "http://manhua.dmzj.com/cm100/"

url_root = "http://manhua.dmzj.com"


def read_url(url):
	socket = urllib2.urlopen(url)
	content = socket.read()
	socket.close()

	return content

class Parser(SGMLParser):
	def reset(self):
		SGMLParser.reset(self)

		self.name = ""
		self.chapter = []
		self.url = []
		self.chapter_url = None

		self.test_ul = 0
		self.test_li = 0
		self.test_a = 0
		self.test_div = 0

	def start_div(self, attrs):
		for k, v in attrs:
			if k == "class" and v == "cartoon_online_border":
				self.test_div = 1

			if k == "class" and v == "clearfix" and self.test_div == 1:
				self.test_div = 2

	def start_ul(self, attrs):
		if self.test_div == 1:
			self.test_ul = 1

	def start_li(self, attrs):
		if self.test_ul == 1:
			self.test_li = 1

	def start_a(self, attrs):
		if self.test_li == 1:
			for k, v in attrs:
				if k != "title" and k != "href":
					return
				
				if k == "href":
					self.url.append(url_root + v)
					
				self.test_a = 1

	def end_a(self):
		if self.test_li == 1:
			self.test_a = 0

	def end_li(self):
		if self.test_ul == 1:
			self.test_li = 0

	def end_ul(self):
		if self.test_div == 1:
			self.test_ul = 0

	def end_div(self):
		if self.test_div:
			self.test_div -= 1

	def handle_data(self, data):
		if self.test_a:
			self.chapter.append(data)

	def get_chapter_url(self):
		self.chapter_url = zip(self.chapter, self.url)
		return self.chapter_url

	def get_name(self, content):
		return reg_name.findall(content)[0]

def test():
	parser = Parser()
	content = read_url(url_test) 
	parser.feed(content)
	chapter_url = parser.get_chapter_url()
	name = parser.get_name(content) 
	with open("fetch_chapter_output.txt", "w") as f:
		f.write(name + "\n")
		for c, u in chapter_url:
			f.write(c + " " + u + "\n")

if __name__ == "__main__":
	test()
