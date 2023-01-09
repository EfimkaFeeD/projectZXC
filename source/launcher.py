import sys
import os
import subprocess
import webbrowser
import psutil
from PyQt5.QtCore import QTimer, QSize, QRect, Qt
from PyQt5.QtGui import QImage, QBrush, QPalette, QFont
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QScrollArea, QPushButton, QVBoxLayout, QWidget, QDialog
from bin.system.Highly_Usable_Interface import Ui_MainWindow


# Класс главного окна (НЕОБХОДИМ .exe ИГРЫ ДЛЯ РАБОТЫ)
class MyWidget(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.setWindowTitle('launcher')
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setFixedSize(640, 480)
        self.start_button.clicked.connect(self.run)
        self.start_button.setStyleSheet("border-radius:20;background-color: rgb(77, 50, 145);color: white")
        self.quit_button.setStyleSheet("border-radius:20;background-color: rgb(77, 50, 145);color: white")
        self.bug_button.setStyleSheet("border-radius:20;background-color: rgb(77, 50, 145);color: white")
        self.git_button.setStyleSheet("border-radius:20;background-color: rgb(77, 50, 145);color: white")
        self.help_button.setStyleSheet("border-radius:20;background-color: rgb(77, 50, 145);color: white")
        self.git_button.clicked.connect(self.open_github)
        self.quit_button.clicked.connect(lambda: sys.exit())
        self.bug_button.clicked.connect(self.open_logs)
        self.help_button.clicked.connect(self.open_help)
        self.game_running = False
        self.game_name = open('bin//system//__name__.txt').read()
        self.repo = 'https://github.com/EfimkaFeeD/pygameProject'
        self.timer = QTimer()
        self.timer.setInterval(1000)
        self.timer.timeout.connect(self.update_state)
        self.timer.start()
        self.log_window = None
        self.project_label.setStyleSheet('color: rgb(255, 255, 255)')
        self.launcher_label.setStyleSheet('color: rgb(255, 255, 255)')
        self.zxc_label.setStyleSheet('color: rgb(255, 255, 255)')
        image = QImage('bin//materials//redactor_default.jpg').scaled(QSize(self.width(), self.height()))
        palette = QPalette()
        palette.setBrush(QPalette.Window, QBrush(image))
        self.setPalette(palette)
        self.picture = QLabel(self)

    # Открытие GitHub
    def open_github(self):
        webbrowser.open(self.repo)

    # Открытие инструкции
    @staticmethod
    def open_help():
        os.system(f'notepad.exe bin//system//instructions.txt')

    # Открытие окна с логами
    def open_logs(self):
        self.log_window = BugReportsWindow()
        self.log_window.show()

    # Открытие и закрытие игры
    def run(self):
        if not self.game_running:
            subprocess.Popen([f'bin//{self.game_name}'])
        else:
            subprocess.Popen(f'taskkill /im {self.game_name} /f')

    # Проверка на работу игры
    def update_state(self):
        for process in psutil.process_iter():
            if process.name() == self.game_name:
                self.start_button.setText('stop')
                self.game_running = True
                return
        self.game_running = False
        self.start_button.setText('run')

    # Выход из лаунчера при нажатии Escape
    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape:
            sys.exit()


# Класс репорта ошибок
class BugReportsWindow(QDialog):
    def __init__(self):
        super().__init__()
        self.resize(400, 320)
        self.setWindowTitle('logs')
        self.issue_button = QPushButton('send issue', self)
        self.issue_button.setGeometry(300, 290, 70, 30)
        self.issue_button.clicked.connect(lambda: webbrowser.open(
            "https://github.com/EfimkaFeeD/pygameProject/issues/new"))
        self.scrollArea = QScrollArea(self)
        self.scrollArea.setGeometry(QRect(10, 30, 341, 251))
        self.scrollArea.setWidgetResizable(True)
        self.label = QLabel('Bug reports for all time:', self)
        self.label.setGeometry(QRect(30, 0, 251, 31))
        font = QFont()
        font.setPointSize(12)
        self.label.setFont(font)
        logs = [arg[2] for arg in os.walk('bin//system//logs')][0]
        self.logs_layout = QVBoxLayout()
        for i, log in enumerate(logs[::-1]):
            button = QPushButton(log[:-4], self)
            button.resize(300, 30)
            button.clicked.connect(self.open_log)
            self.logs_layout.addWidget(button, i)
        widget = QWidget()
        widget.setLayout(self.logs_layout)
        self.scrollArea.setWidget(widget)

    # Открытие окна логов
    def open_log(self):
        log = self.sender().text()
        try:
            os.startfile(f'bin\\system\\logs\\{log}.log')
        except Exception as e:
            print(e)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MyWidget()
    ex.show()
    sys.exit(app.exec_())
