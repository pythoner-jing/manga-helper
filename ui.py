#!/usr/bin/env python
#coding:utf-8

import wx
from fetch_chapter import *

UIFactory = {}

class PanelInfo(wx.Panel):
	def __init__(self, parent, id = -1, pos = wx.DefaultPosition, size = wx.DefaultSize):
		wx.Panel.__init__(self, parent, id, pos, size)

		self.parent = parent

		self.text_name = wx.StaticText(self, -1, "")
		self.checkbox_all = wx.CheckBox(self, -1, "全选")
		self.checkbox_reverse = wx.CheckBox(self, -1, "反选")
		self.button_download = wx.Button(self, -1, "下载")
		self.sizer = wx.FlexGridSizer(rows = 1, cols = 4, hgap = 10, vgap = 0)
		self.sizer.Add(self.text_name, 0, 0)
		self.sizer.Add(self.checkbox_all, 0, 0)
		self.sizer.Add(self.checkbox_reverse, 0, 0)
		self.sizer.Add(self.button_download, 0, 0)
		self.sizer.AddGrowableCol(0, 1)
		self.SetSizer(self.sizer)

		self.checkbox_all.Bind(wx.EVT_CHECKBOX, self.OnSelectAll)
		self.checkbox_reverse.Bind(wx.EVT_CHECKBOX, self.OnSelectReverse)
		self.button_download.Bind(wx.EVT_BUTTON, self.OnDownload)

		self.name = ""

	def OnDownload(self, evt):
		if len(self.name) and len(UIFactory["ScrollChapter"].get_selected()):
			UIFactory["ListBoxTask"].add_task(self.name + "\t\t\t0%")
			print UIFactory["ScrollChapter"].get_selected()

	def set_name(self, name):
		self.name = name
		self.text_name.SetLabel(name)

	def get_name(self):
		return self.name

	def OnSelectAll(self, evt):
		UIFactory["ScrollChapter"].select_all(self.checkbox_all.GetValue())

	def OnSelectReverse(self, evt):
		UIFactory["ScrollChapter"].select_reverse()

class PanelLink(wx.Panel):
	def __init__(self, parent, id = -1, pos = wx.DefaultPosition, size = wx.DefaultSize):
		wx.Panel.__init__(self, parent, id, pos, size)

		self.parent = parent 

		sizer = wx.FlexGridSizer(rows = 1, cols = 2, hgap = 10, vgap = 5)

		self.button_link = wx.Button(self, -1, "链接")
		self.text_url = wx.TextCtrl(self, -1)

		sizer.Add(self.text_url, 0, wx.EXPAND)
		sizer.Add(self.button_link, 0, wx.EXPAND)

		sizer.AddGrowableCol(0, 1)

		self.SetSizer(sizer)

		self.button_link.Bind(wx.EVT_BUTTON, self.OnLink)

	def OnLink(self, evt):
		UIFactory["ScrollChapter"].link(self.text_url.GetValue())

class ListBoxTask(wx.ListBox):
	def __init__(self, parent, id = -1, pos = wx.DefaultPosition, size = wx.DefaultSize):
		wx.ListBox.__init__(self, parent, id, pos, size, [], wx.LB_SINGLE)

		self.task_list = []

		self.SetMinSize((200, 400))

	def add_task(self, name):
		self.task_list.append(name)
		self.SetItems(self.task_list)

class PanelDisplay(wx.Panel):
	def __init__(self, parent, id = -1, pos = wx.DefaultPosition, size = wx.DefaultSize):
		wx.Panel.__init__(self, parent, id, pos, size)

		self.scroll_chapter = ScrollChapter(self)
		UIFactory["ScrollChapter"] = self.scroll_chapter

		self.listbox_task = ListBoxTask(self)
		UIFactory["ListBoxTask"] = self.listbox_task

		self.sizer = wx.FlexGridSizer(rows = 1, cols = 2, hgap = 10, vgap = 0)
		self.sizer.Add(self.scroll_chapter, 0, wx.EXPAND)
		self.sizer.Add(self.listbox_task, 0, wx.EXPAND)
		self.sizer.AddGrowableCol(0, 4)
		self.sizer.AddGrowableCol(1, 1)
		self.sizer.AddGrowableRow(0, 1)
		self.SetSizer(self.sizer)

class ScrollChapter(wx.ScrolledWindow):
	def __init__(self, parent, id = -1, pos = wx.DefaultPosition, size = wx.DefaultSize):
		wx.ScrolledWindow.__init__(self, parent, id, pos, size, wx.RAISED_BORDER)

		self.parent = parent 
		self.sizer = None
		self.chapter_url = []
		self.selected = []
		self.name = ""
		self.checkbox = []

		self.sizer = wx.FlexGridSizer(rows = 500, cols = 4, hgap = 10, vgap = 10)
		self.sizer.AddGrowableCol(0, 1)
		self.sizer.AddGrowableCol(1, 1)
		self.sizer.AddGrowableCol(2, 1)
		self.sizer.AddGrowableCol(3, 1)
		self.SetSizer(self.sizer)

		self.SetMinSize((500, 400))

	def get_selected(self):
		self.selected = []
		for i, v in enumerate(self.checkbox):
			if v.GetValue():
				self.selected.append(self.chapter_url[i])

		return self.selected

	def select_all(self, value):
		if len(self.checkbox):
			map(lambda x : x.SetValue(value), self.checkbox)

	def select_reverse(self):
		if len(self.checkbox):
			map(lambda x : x.SetValue(not x.GetValue()), self.checkbox)

	def link(self, url):
		if len(url) == 0:
			return

		if self.sizer:
			self.sizer.Clear(True)

		parser = Parser()
		content = read_url(url)
		parser.feed(content)
		self.chapter_url = parser.get_chapter_url()
		self.checkbox = []
		self.name = parser.get_name(content)
		UIFactory["PanelInfo"].set_name(self.name)

		rows = 0
		if (len(self.chapter_url) % 4 == 0):
			rows = len(self.chapter_url) / 4
		else:
			rows = len(self.chapter_url) / 4 + 1

		self.SetScrollbars(1, 1, 400, rows * 24 + (rows - 1) * 10)

		p = 0
		for row in xrange(rows):
			for col in xrange(4):
				if p >= len(self.chapter_url):
					return
				checkbox = wx.CheckBox(self, -1, self.chapter_url[p][0])
				self.checkbox.append(checkbox)
				self.sizer.Add(checkbox, 0, 0)
				self.sizer.Layout()
				p += 1

		self.SetSizer(self.sizer)

class FrameMain(wx.Frame):
	def __init__(self, parent, id, title):
		wx.Frame.__init__(self, parent, id, title)

		self.SetClientSize(wx.DefaultSize)
		self.Show()
		self.Center()
		self.client_size = self.GetClientSize()

		self.panel_link = PanelLink(self)
		self.panel_info = PanelInfo(self)
		self.panel_display = PanelDisplay(self)

		self.sizer = wx.FlexGridSizer(rows = 3, cols = 1, hgap = 10, vgap = 5)
		self.sizer.Add(self.panel_link, 0, wx.EXPAND)
		self.sizer.Add(self.panel_info, 0, wx.EXPAND)
		self.sizer.Add(self.panel_display, 0, wx.EXPAND)

		self.sizer.AddGrowableCol(0, 1)
		self.sizer.AddGrowableRow(2, 1)

		self.SetSizer(self.sizer)

		self.SetMinSize((700, 500))
		self.Fit()

		UIFactory["PanelLink"] = self.panel_link
		UIFactory["PanelInfo"] = self.panel_info
		UIFactory["PanelDisplay"] = self.panel_display

class App(wx.App):
	def __init__(self, redirect = False):
		wx.App.__init__(self, redirect)
		frame_main = FrameMain(None, -1, "manga-helper")

	def OnInit(self):
		return True

if __name__ == "__main__":
	app = App()	
	app.MainLoop()
