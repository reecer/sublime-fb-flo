

import sublime, sublime_plugin, sys, os
from threading import Timer

# Sublime path settings....
BASE_PATH = os.path.abspath(os.path.dirname(__file__))
for p in [BASE_PATH, os.path.join(BASE_PATH)]:
	if p not in sys.path:
		sys.path.append(p)

from fbflo import Server
ctrl = Server()

def plugin_unloaded():
	global ctrl
	ctrl.stop()


def plugin_loaded():
	pass


class FbFloListener(sublime_plugin.EventListener):
	def __init__(self):
		super().__init__()
		self.timeout = None
		self.settings = None

	def on_load(self, view):
		self.settings = sublime.load_settings('sublime-fb-flo.sublime-settings')

	def delay(self): return self.settings.get('timeout')
	def livereload(self): return self.settings.get('livereload')


	def update(self, view):
		if self.timeout: self.timeout.cancel()
		def broadcast():
			print('Broadcasting update')
			global ctrl
			ctrl.broadcast({
				"resourceURL": view.file_name().split('/')[-1],
				"contents": view.substr(sublime.Region(0, view.size())),
				"match": "indexOf"
				})
			self.timeout = None

		print('Starting timeout')
		self.timeout = Timer(self.delay(), broadcast)
		self.timeout.start()
		

	def on_modified(self, view):
		global ctrl
		if not self.settings: self.on_load(None)
		if ctrl.has(view) and self.livereload():
			self.update(view)

	def on_post_save(self, view):
		global ctrl
		if ctrl.has(view) and not self.livereload():
			self.update(view)

	def on_close(self, view):
		global ctrl
		if ctrl.has(view):
			ctrl.rm(view)

class FbFloStartCommand(sublime_plugin.TextCommand):
	def is_enabled(self):
		global ctrl
		return not ctrl.connected
	def run(self, edit):
		global ctrl
		ctrl.start()

class FbFloStopCommand(sublime_plugin.TextCommand):
	def is_enabled(self):
		global ctrl
		return ctrl.connected
	def run(self, edit):
		global ctrl
		ctrl.stop()


class FbFloWatchCommand(sublime_plugin.TextCommand):
	def is_enabled(self):
		global ctrl
		return ctrl.connected and not ctrl.has(self.view)
	def run(self, edit):
		global ctrl
		ctrl.add(self.view)

class FbFloUnwatchCommand(sublime_plugin.TextCommand):
	def is_enabled(self):
		global ctrl
		return ctrl.has(self.view)
	def run(self, edit):
		global ctrl
		ctrl.rm(self.view)
