
import sublime, sublime_plugin, sys, os

BASE_PATH = os.path.abspath(os.path.dirname(__file__))
for p in [BASE_PATH, os.path.join(BASE_PATH, 'flo')]:
	if p not in sys.path:
		sys.path.append(p)

from flo import Server
ctrl = Server()
print('Fb-flo loaded', ctrl)

def plugin_unloaded():
	global ctrl
	ctrl.stop()


class FbFloListener(sublime_plugin.EventListener):
	def on_modified(self, view):
		global ctrl
		if ctrl.has(view):
			ctrl.broadcast({
				"resourceURL": view.file_name().split('/')[-1],
				"contents": view.substr(sublime.Region(0, view.size())),
				"match": "indexOf"
				})
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
		return ctrl.connected and ctrl.has(self.view)
	def run(self, edit):
		global ctrl
		ctrl.rm(view)
