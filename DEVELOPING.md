# Developing

This page contains some hints to take into account when switching between laptop and raspberry.

## designer_main.py

On laptop, code needs 2 changes after a pyuic5:

    from PyQt5 import QtWebKitWidgets --> from PyQt5 import QtWebEngineWidgets
    self.webView = QtWebKitWidgets.QWebView(self.tab_trawls) --> self.webView = QtWebEngineWidgets.QWebEngineView(self.tab_trawls)

These are automatically patched on DDH in file ``run_ddh.sh``.


