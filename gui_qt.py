import sys
from PySide6.QtWidgets import QApplication
from widgets.main_window import MainWindow

def gui_qt_main(url="", dest=None, lang=None):
    app = QApplication(sys.argv)
    app.setStyle("windowsvista") # Force native OS style
    window = MainWindow(url=url, dest=dest, lang=lang)
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    gui_qt_main()
