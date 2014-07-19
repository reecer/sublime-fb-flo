import json, threading

import tornado.process
import tornado.ioloop;
import tornado.web;
import tornado.websocket;
import tornado.httpserver;

class EventHook(object):
    def __init__(self):
        self.__handlers = []

    def __iadd__(self, handler):
        self.__handlers.append(handler)
        return self

    def __isub__(self, handler):
        self.__handlers.remove(handler)
        return self

    def fire(self, *args, **keywargs):
        for handler in self.__handlers:
            handler(*args, **keywargs)
            

class WSHandler(tornado.websocket.WebSocketHandler):
    onOpen = EventHook()
    onClose = EventHook()
    def open(self, *args): WSHandler.onOpen.fire(self)
    def on_close(self, *args): WSHandler.onClose.fire(self)
    def on_message(self, message):
        j = json.loads(message)
        print('fb flo message', j)
                 
class Server:
    def __init__(self, port=8888):
        self.views = []
        self.clients = []
        self.connected = False
        self.port = port
        self.thread = None

        WSHandler.onOpen += self.client_opened
        WSHandler.onClose += self.client_closed
        print('Fb-flo initialized')

    def start(self):
        application = tornado.web.Application([ (r'/(.*)', WSHandler), ])
        
        self.http_server = tornado.httpserver.HTTPServer(application)
        self.http_server.listen(self.port)
        
        self.thread = threading.Thread(target=tornado.ioloop.IOLoop.instance().start).start()
        self.connected = True
        print('Fb-flo server on port', self.port)

    def stop(self):
        if not self.connected: return
        
        self.views = []
        self.clients = []
        self.connected = False

        WSHandler.onOpen -= self.client_opened
        WSHandler.onClose -= self.client_closed

        # stop thread
        self.http_server.stop()
        tornado.ioloop.IOLoop.instance().stop()
        self.thread.join()
        print('Fb-flo server stopped')

    def add(self, view):
        self.views.append(view.id())
        print('Fb-flo now watching', view.file_name())

    def rm(self, view):
        if self.has(view):
            self.views.remove(view.id())
            print('Fb-flo stopped watching view.file_name()')

    def has(self, view):
        return view.id() in self.views


    def broadcast(self, msg):
        for ws in self.clients:
            ws.write_message(json.dumps(msg))

    def client_opened(self, ws):
        self.clients.append(ws)
        print('Client opened')

    def client_closed(self, ws):
        if ws in self.clients:
            self.clients.remove(ws)
            print('Client closed')

