from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtWebEngineWidgets import *
from PyQt5.QtNetwork import *

import os
import sys
import qdarkstyle
from weather_api import check_weather


class ProxyDialog(QDialog):
    def __init__(self, *args, **kwargs):
        super(ProxyDialog, self).__init__(*args, **kwargs)

        layout = QVBoxLayout()

        label = QLabel("Enter your username and password")
        username = QLineEdit()
        password = QLineEdit()
        btn = QPushButton("Ok")

        self.setLayout(layout)

        layout.addWidget(label)
        layout.addWidget(username)
        layout.addWidget(password)
        layout.addWidget(btn)


class BookmarkToolBar(QToolBar):
    bookmarkClicked = pyqtSignal(QUrl, str)

    def __init__(self, parent=None):
        super(BookmarkToolBar, self).__init__(parent)
        self.actionTriggered.connect(self.onActionTriggered)
        self.bookmark_list = []

    def setBookmarks(self, bookmarks):
        for bookmark in bookmarks:
            self.addBookmarkAction(bookmark['title'], bookmark['url'])

    def addBookmarkAction(self, title, url):
        bookmark = {'title': title, 'url': url}
        fm = QFontMetrics(self.font())
        if bookmark not in self.bookmark_list:
            text = fm.elidedText(title, Qt.ElideRight, 150)
            action = self.addAction(text)
            action.setData(bookmark)
            self.bookmark_list.append(bookmark)

    @pyqtSlot(QAction)
    def onActionTriggered(self, action):
        bookmark = action.data()
        self.bookmarkClicked.emit(bookmark["url"], bookmark["title"])


class WeatherDialog(QDialog):
    def __init__(self, *args, **kwargs):
        super(WeatherDialog, self).__init__(*args, **kwargs)

        layout = QVBoxLayout()

        title = QLabel("Check The Weather")
        font = title.font()
        font.setPointSize(20)
        title.setFont(font)

        layout.addWidget(title)

        logo = QLabel()
        logo.setPixmap(QPixmap(os.path.join('images', 'weather_icon.png')))
        layout.addWidget(logo)

        self.button_get = QPushButton("Check Weather")
        self.button_get.clicked.connect(self.get_text)
        layout.addWidget(self.button_get)

        self.setLayout(layout)

    def get_text(self):
        text, ok = QInputDialog.getText(self, 'Text Input Dialog', 'Enter your City:')
        if text == '':  # Checks if there is an input if not - do nothing
            return
        if text.isdigit():
            print('The entered text is an Int type, needed Str type.')
            return
        try:
            if ok:
                current_temp, current_cond = check_weather(text)

                self.button_get.setText("The current temperature is %s°C, and the weather is: %s" % (current_temp,
                                                                                                     current_cond))
        except:
            print("Crashed - Unknown error")


class AboutDialog(QDialog):
    def __init__(self, *args, **kwargs):
        super(AboutDialog, self).__init__(*args, **kwargs)

        QBtn = QDialogButtonBox.Ok  # No cancel
        self.buttonBox = QDialogButtonBox(QBtn)
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)

        layout = QVBoxLayout()

        title = QLabel("Tempo")
        font = title.font()
        font.setPointSize(20)
        title.setFont(font)

        layout.addWidget(title)

        logo = QLabel()
        logo.setPixmap(QPixmap(os.path.join('images', 'logo_b.png')))
        layout.addWidget(logo)

        layout.addWidget(QLabel("Version 2.0"))
        layout.addWidget(QLabel("Copyright @ Rokas La"))

        for i in range(0, layout.count()):
            layout.itemAt(i).setAlignment(Qt.AlignHCenter)

        layout.addWidget(self.buttonBox)

        self.setLayout(layout)


class MainWindow(QMainWindow):
    """ Class to create a main window of the web browser """
    def __init__(self, parent=None, *args, **kwargs):
        super(MainWindow, self).__init__(parent, Qt.FramelessWindowHint, *args, **kwargs)

        self.defaultUrl = QUrl()
        self.proxy = QNetworkProxy(QNetworkProxy.Socks5Proxy, '', 1080)

        self.tabs = QTabWidget()
        self.tabs.setDocumentMode(True)
        self.tabs.setTabsClosable(True)
        self.tabs.currentChanged.connect(self.current_tab_changed)
        self.tabs.tabCloseRequested.connect(self.close_current_tab)
        self.tabs.tabBarDoubleClicked.connect(self.tab_open_doubleclick)
        self.tabs.setTabShape(1)

        self.setCentralWidget(self.tabs)

        self.status = QStatusBar()
        self.setStatusBar(self.status)

        main_func_bar = QToolBar('Main Tools')
        main_func_bar.setIconSize(QSize(20, 20))
        main_func_bar.setMovable(False)
        self.addToolBar(main_func_bar)
        self.addToolBarBreak()

        navigation_bar = QToolBar('Navigation')
        navigation_bar.setIconSize(QSize(18, 18))
        navigation_bar.setMovable(False)
        self.addToolBar(navigation_bar)
        self.addToolBarBreak()

        self.bookmark_bar = BookmarkToolBar('Bookmark Bar')
        self.bookmark_bar.bookmarkClicked.connect(self.add_new_tab)
        self.bookmark_bar.setMovable(False)
        self.addToolBar(self.bookmark_bar)

        about_action = QAction(QIcon(os.path.join('images', 'question.png')), "About Tempo", self)
        about_action.setStatusTip('Find more about Tempo')
        about_action.triggered.connect(self.about)
        main_func_bar.addAction(about_action)

        change_theme = QPushButton(QIcon(os.path.join('images', 'logo_b')), '', self)
        change_theme.setCheckable(True)
        change_theme.clicked[bool].connect(self.change_theme)
        main_func_bar.addWidget(change_theme)

        weather_action = QAction(QIcon(os.path.join('images', 'weather_icon')), "What's the weather", self)
        weather_action.setStatusTip('Find the temperature and weather conditions in a city')
        weather_action.triggered.connect(self.weather)
        main_func_bar.addAction(weather_action)

        proxy_btn = QPushButton(QIcon(os.path.join('images', '')), '', self)
        proxy_btn.setCheckable(True)
        proxy_btn.setStatusTip("Connect to a Proxy")

        # proxy_btn.clicked[bool].connect(self.connect_to_proxy) Still in Development.

        main_func_bar.addWidget(proxy_btn)

        spacer = QWidget()
        spacer.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        main_func_bar.addWidget(spacer)

        back_button = QAction(QIcon(os.path.join('images', 'back_icon.PNG')), 'Back', self)
        back_button.setStatusTip('Go back to previous page')
        back_button.triggered.connect(lambda: self.tabs.currentWidget().back())
        navigation_bar.addAction(back_button)

        forward_button = QAction(QIcon(os.path.join('images', 'forward_icon.PNG')), 'Forward', self)
        forward_button.setStatusTip('Go to the forward page')
        forward_button.triggered.connect(lambda: self.tabs.currentWidget().forward())
        navigation_bar.addAction(forward_button)

        reload_button = QAction(QIcon(os.path.join('images', 'reload_icon.PNG')), 'Reload', self)
        reload_button.setStatusTip('Reload page')
        reload_button.triggered.connect(lambda: self.tabs.currentWidget().reload())
        navigation_bar.addAction(reload_button)

        home_button = QAction(QIcon(os.path.join('images', 'home_icon.PNG')), 'Home', self)
        home_button.setStatusTip('Go to home page')
        home_button.triggered.connect(self.navigate_home)
        navigation_bar.addAction(home_button)

        navigation_bar.addSeparator()

        self.httpsicon = QLabel()

        self.https_icon = QPixmap()
        self.https_icon.load(os.path.join('images', 'https_icon.PNG'))
        self.https_icon = self.https_icon.scaledToWidth(20)
        self.https_icon = self.https_icon.scaledToHeight(20)

        self.http_icon = QPixmap()
        self.http_icon.load(os.path.join('images', 'http_icon.PNG'))
        self.http_icon = self.http_icon.scaledToWidth(20)
        self.http_icon = self.http_icon.scaledToHeight(20)

        self.httpsicon.setPixmap(self.https_icon)
        navigation_bar.addWidget(self.httpsicon)

        self.urlbar = QLineEdit()
        self.urlbar.returnPressed.connect(self.onReturnPressed)
        navigation_bar.addWidget(self.urlbar)

        self.bookmark_btn = QToolButton()
        self.bookmark_btn.setIcon(QIcon(os.path.join('images', 'star_icon.PNG')))
        self.bookmark_btn.clicked.connect(self.addFavoriteClicked)
        navigation_bar.addWidget(self.bookmark_btn)

        stop_button = QAction(QIcon(os.path.join('images', 'stop_icon.PNG')), 'Stop', self)
        stop_button.setStatusTip('Stop Loading The Web Page')
        stop_button.triggered.connect(lambda: self.tabs.currentWidget().stop())
        navigation_bar.addAction(stop_button)

        settings_button = QAction(QIcon(os.path.join('images', 'menu_icon.PNG')), 'Settings', self)
        settings_button.setStatusTip('Settings')
        settings_button.triggered.connect(self.settings)
        navigation_bar.addAction(settings_button)

        minimize_button = QAction(QIcon(os.path.join('images', 'minimize-window.PNG')), 'Minimize', self)
        minimize_button.setStatusTip('Minimize Window')
        minimize_button.triggered.connect(lambda: self.window().showMinimized())
        main_func_bar.addAction(minimize_button)

        maximise_button = QAction(QIcon(os.path.join('images', 'maximised_window.PNG')), 'Maximize', self)
        maximise_button.setStatusTip('Maximize Window')
        maximise_button.triggered.connect(self.maximize_window)
        main_func_bar.addAction(maximise_button)

        close_button = QAction(QIcon(os.path.join('images', 'close_button.PNG')), 'Exit', self)
        close_button.setStatusTip('Close Web Browser')
        close_button.triggered.connect(lambda: self.window().close())
        main_func_bar.addAction(close_button)

        self.readSettings()

        self.show()
        self.setWindowTitle('Tempo')

    def onReturnPressed(self):
        self.tabs.currentWidget().setUrl(QUrl.fromUserInput(self.urlbar.text()))

    def addFavoriteClicked(self):
        loop = QEventLoop()

        def callback(resp):
            setattr(self, "title", resp)
            loop.quit()

        web_browser = self.tabs.currentWidget()
        web_browser.page().runJavaScript("(function() { return document.title;})();", callback)
        url = web_browser.url()
        loop.exec_()
        self.bookmark_bar.addBookmarkAction(getattr(self, "title"), url)

    def add_new_tab(self, qurl=None, label='Blank'):
        if qurl is None:
            qurl = QUrl('')

        web_browser = QWebEngineView()
        web_browser.setUrl(qurl)
        web_browser.adjustSize()

        index = self.tabs.addTab(web_browser, label)

        web_browser.urlChanged.connect(lambda qurl, web_browser=web_browser:
                                       self.update_urlbar(qurl, web_browser))

        web_browser.loadFinished.connect(lambda _, i=index, web_browser=web_browser:
                                         self.tabs.setTabText(i, web_browser.page().title()))

        self.tabs.setCurrentIndex(index)

        self.urlbar.setText(qurl.toDisplayString())

    def readSettings(self):
        setting = QSettings()
        self.defaultUrl = setting.value("defaultUrl", QUrl('http://www.google.com'))
        self.add_new_tab(self.defaultUrl, 'Home Page')
        self.bookmark_bar.setBookmarks(setting.value("bookmarks", []))

    def saveSettins(self):
        settings = QSettings()
        settings.setValue("defaultUrl", self.defaultUrl)
        settings.setValue("bookmarks", self.bookmark_bar.bookmark_list)

    def tab_open_doubleclick(self, index):
        try:
            if index == -1:
                self.add_new_tab()
        except:
            print('wtf')
            pass

    def current_tab_changed(self, index):
        qurl = self.tabs.currentWidget().url()
        self.update_urlbar(qurl, self.tabs.currentWidget())
        self.update_title(self.tabs.currentWidget())

    def close_current_tab(self, index):
        """ Close the TAB, as PyQT does not close the page widget you need to close it too. """

        if self.tabs.count() < 2:
            return

        if index == 0:
            return

        web_browser = self.tabs.currentWidget()
        web_browser.deleteLater()
        self.tabs.removeTab(index)

    def update_title(self, web_browser):
        """ Update the TAB title, by pulling out web page title """
        if web_browser != self.tabs.currentWidget():
            return

        title = self.tabs.currentWidget().page().title()
        self.setWindowTitle("%s - Tempo" % title)

    def navigate_home(self):
        """ Go back to the Home Page """
        self.tabs.currentWidget().setUrl(QUrl("http://www.google.com"))

    def update_urlbar(self, q, web_browser=None):
        """ Update url bar, by the web page """
        if web_browser != self.tabs.currentWidget():
            return

        if q.scheme() == 'https':
            # Secure padlock icon
            self.httpsicon.setPixmap(self.https_icon)

        else:
            # Insecure padlock icon
            self.httpsicon.setPixmap(self.http_icon)

        self.urlbar.setText(q.toDisplayString())
        self.urlbar.setCursorPosition(0)

    def about(self):
        dlg = AboutDialog()
        dlg.exec_()

    def weather(self):
        weath_dlg = WeatherDialog()
        weath_dlg.exec_()

    def maximize_window(self):
        if self.isMaximized():
            self.showNormal()
        else:
            self.showMaximized()

    def change_theme(self, pressed):
        if pressed:
            app.setStyleSheet("")
        else:
            app.setStyleSheet(qdarkstyle.load_stylesheet_pyqt5())

    def settings(self):
        try:
            print('Pressed on settings button')  # For now does nothing
        except:
            pass

    def connect_to_proxy(self, pressed):
        proxy_dial = ProxyDialog()
        proxy_dial.exec_()

    def contextMenuEvent(self, event):
        menu = QMenu(self)
        quitAction = menu.addAction('Quit')
        add_tab_Action = menu.addAction('New Tab')
        action = menu.exec_(self.mapToGlobal(event.pos()))
        if action == quitAction:
            qApp.quit()
        elif action == add_tab_Action:
            self.add_new_tab(QUrl(''), 'Blank')

    def mousePressEvent(self, event):
        """" Over write the original function to monitor the mouse press"""
        self.oldPos = event.globalPos()

    def mouseMoveEvent(self, event):
        """" Over write the original function to monitor the mouse position """
        delta = QPoint(event.globalPos() - self.oldPos)
        self.move(self.x() + delta.x(), self.y() + delta.y())
        self.oldPos = event.globalPos()

    def closeEvent(self, event):
        self.saveSettins()
        super(MainWindow, self).closeEvent(event)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setApplicationName("Tempo")
    app.setOrganizationName("R.L")
    app.setOrganizationDomain("https://www.linkedin.com/in/rokasla/")
    app.setWindowIcon(QIcon(os.path.join('images', 'logo_b')))
    app.setStyleSheet(qdarkstyle.load_stylesheet_pyqt5())

    window = MainWindow()
    window.setWindowIcon(QIcon(os.path.join('images', 'logo_b')))

    sys.exit(app.exec_())

# @TODO: Fix Close Tab, closes the next tab.
# @TODO: New Tab In Google does not work.
