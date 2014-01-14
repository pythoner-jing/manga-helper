#!/usr/bin/env python
#coding:utf-8

import urllib, urllib2, re, os, Queue, threading, time, wx
from spidermonkey import *
from sgmllib import SGMLParser

root_url_img = "http://imgfast.dmzj.com/"
url_test = "http://manhua.dmzj.com/qytlsndyghrj/26148.shtml"
url_root = "http://manhua.dmzj.com"

reg_name = re.compile(r"g_comic_name\s=\s\"([^\"]+)\"")
reg_img_list = re.compile(r"eval(.+)")
reg_img_type = re.compile(r"(\w+)")

rt = Runtime()
cx = rt.new_context()

mutex = threading.Lock()

def read_url(url):
	content = ""
	try:
		socket = urllib2.urlopen(url)
		content = socket.read()
		socket.close()
	except Exception, e:
		print "exception at read_url"

	return content

def get_comic_name(content):
	if not reg_name.findall(content):
		return -1
	return reg_name.findall(content)[0]

class ParserChapter(SGMLParser):
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

class Thread(threading.Thread):
	def __init__(self, queue, thread_no, handler):
		threading.Thread.__init__(self, name = thread_no)
		self.queue = queue
		self.thread_no = thread_no
		self.handler = handler

	def run(self):
		time.sleep(1)
		while self.queue.qsize() > 0:
			self.handler(self.queue.get())

class Thread2(Thread):
	def run(self):
		time.sleep(1)
		while True:
			self.handler(self.queue.get())

class Download:
	def __init__(self, name, chapter_url, text_ctrl_task, task_no):
		self.name = name
		self.chapter_url = chapter_url
		self.url_img = []	
		self.thread_pool_download = []
		self.queue_task = Queue.Queue(0)
		self.num_thread = 20
		self.size_comic = 0
		self.num_downloaded = 0
		self.text_ctrl_task = text_ctrl_task 
		self.task_no = task_no

	def run_task(self):
		print "开始下载 " + self.name
		if os.path.isdir(self.name) or os.path.isfile(self.name):
			return

		path_cur = os.path.abspath(".")
		path_comic = os.path.join(path_cur, self.name)
		os.mkdir(path_comic)
		for v in self.chapter_url:
			path_chapter = os.path.join(path_comic, v[0])
			os.mkdir(path_chapter)
			try:
				for i, v in enumerate(self.fetch_img_url(v[1])):
					filepath = os.path.join(path_chapter, str(i + 1) + "." + reg_img_type.findall(v)[-1])
					self.queue_task.put((v, filepath))
			except Exception, e:
				print "exception at run_task"

		self.size_comic = self.queue_task.qsize() 
		map(lambda x : self.thread_pool_download.append(Thread(self.queue_task, x, self.handler_download)), xrange(self.num_thread))
		map(lambda x : x.setDaemon(True), self.thread_pool_download)
		map(lambda x : x.start(), self.thread_pool_download)
		map(lambda x : x.join(), self.thread_pool_download)

	def handler_download(self, task):
		try:
			urllib.urlretrieve(task[0], task[1])
		except Exception, e:
			print "exception at hanler_download"
			
		self.num_downloaded += 1.0
		info = self.name + " " + ("%.1f" % (self.num_downloaded / self.size_comic * 100)) + "%"
		wx.CallAfter(self.text_ctrl_task.set_info, self.task_no, info)

	def fetch_img_url(self, url):
		socket = urllib2.urlopen(url)
		content = socket.read()
		socket.close()
		js = "eval" + reg_img_list.findall(content)[0] + ";eval(pages)"
		url_img = []
		for v in list(cx.eval_script(js)):
			url_img.append(root_url_img + v)
	
		return url_img
