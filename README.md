sublime-fb-flo
==============
Sublime plugin for fb-flo.
Runs a server that communicates with fb-flo's chrome extension. Enables live-editing.

![Alt text](pics/livecode.gif)


##Installation
Search [Package Control](https://sublime.wbond.net/) for "Fb-Flo"


##Commands

- ###Start/Stop server
    Starts/stops the fb-flo server.

    ![Alt text](pics/start.png)

- ###Watch/Unwatch current file
    Start/stop watching the active file for changes.    

    ![Alt text](pics/watch.png)

##Settings

- ###livereload
    If false, updates will be pushed when files are saved, rather than instantly.
    - default: true

- ###timeout 
    Timeout before broadcasting update (seconds).
    - default: 0.3
