import json, threading, os, sys

# Sublime path settings....
BASE_PATH = os.path.abspath(os.path.dirname(__file__))
for p in [BASE_PATH, os.path.join(BASE_PATH, 'tornado')]:
    if p not in sys.path:
        sys.path.append(p)
        
import tornado.process
import tornado.ioloop
import tornado.web
import tornado.websocket
import tornado.httpserver

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
        '''Fb-flo server implementation'''
        self.views = []
        self.clients = []
        self.connected = False
        self.port = port
        self.thread = None
        print('Fb-flo initialized')

    def start(self):
        '''Start the server'''
        application = tornado.web.Application([ (r'/(.*)', WSHandler), ])
        
        self.http_server = tornado.httpserver.HTTPServer(application)
        self.http_server.listen(self.port)
        
        self.thread = threading.Thread(target=tornado.ioloop.IOLoop.instance().start)
        self.thread.start()

        self.connected = True
        WSHandler.onOpen += self.client_opened
        WSHandler.onClose += self.client_closed
        print('Fb-flo server on port', self.port, self.thread)

    def stop(self):
        '''Stop the server'''
        if not self.connected: return
        # stop thread
        self.http_server.stop()
        tornado.ioloop.IOLoop.instance().stop()
        self.thread.join()
        
        # Close clients
        for client in self.clients: 
            print('closing client', client)
            client.close()

        # reset vars
        self.views = []
        self.clients = []
        self.connected = False

        WSHandler.onOpen -= self.client_opened
        WSHandler.onClose -= self.client_closed
        print('Fb-flo server stopped')

    def add(self, view):
        '''Start watching file view `view`'''
        self.views.append(view.id())
        print('Fb-flo now watching', view.file_name())

    def rm(self, view):
        '''Stop watching file view `view`'''
        if self.has(view):
            self.views.remove(view.id())
            print('Fb-flo stopped watching view.file_name()')

    def has(self, view):
        '''Returns True if this view is being watched'''
        return view.id() in self.views


    def broadcast(self, msg):
        '''Broadcast to all clients'''
        for ws in self.clients:
            ws.write_message(json.dumps(msg))

    def client_opened(self, ws):
        '''Client connected callback'''
        self.clients.append(ws)
        print('Client opened')

    def client_closed(self, ws):
        '''Client disconnected callback'''
        if ws in self.clients:
            self.clients.remove(ws)
            print('Client closed')

