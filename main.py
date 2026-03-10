import sys
from PySide6.QtWidgets import QApplication
from ui.logs_window import LogsWindow
from video.video_worker import VideoWorker
from ui.controller_window import PlainVideoWindow
from ui.main_window import MainWindow
from PySide6.QtCore import QThread

if __name__ == "__main__":
    app = QApplication(sys.argv)

    with open("ui/theme.qss", "r") as f:
        app.setStyleSheet(f.read())

    # thread = QThread()

    # worker = VideoWorker(device_id=1)

    # # third window for technical logs
    # logs_win = LogsWindow()
    # logs_win.move(100, 100)
    # logs_win.show()

    # # first window controller
    # plain_win = PlainVideoWindow(worker)
    # plain_win.move(150, 150)
    # plain_win.show()

    # second window for AI inference feed
    ai_win = MainWindow()
    ai_win.move(200, 200)
    ai_win.show()

    print("[SYSTEM] K-10 Software System Started Successfully")

    sys.exit(app.exec())
