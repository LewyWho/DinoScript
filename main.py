import sys
import pyautogui
from PIL import ImageGrab
import time
import threading
import keyboard
from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QMenuBar, QHBoxLayout
from PySide6.QtCore import Qt, QTimer, QPropertyAnimation, QSequentialAnimationGroup, Property
from PySide6.QtGui import QIcon, QPixmap, QDesktopServices, QColor, QAction
from PySide6.QtCore import QUrl

bbox = (841, 471, 881, 509)
running = False
script_thread = None
jump_counter = 0


def detect_and_jump():
    global running, jump_counter
    jump_cooldown = 0.5
    last_jump_time = 0

    while running:
        current_time = time.time()
        if current_time - last_jump_time >= jump_cooldown:
            screen = ImageGrab.grab(bbox=bbox)
            grayscale_image = screen.convert('L')
            threshold = 100
            binary_image = grayscale_image.point(lambda p: p > threshold and 255)

            cactus_detected = False
            for x in range(binary_image.width):
                for y in range(binary_image.height):
                    if binary_image.getpixel((x, y)) == 0:
                        cactus_detected = True
                        break
                if cactus_detected:
                    break

            if cactus_detected:
                pyautogui.press("space")
                last_jump_time = current_time
                jump_counter += 1
        time.sleep(0.05)


def open_developer_link():
    QDesktopServices.openUrl(QUrl('https://t.me/TREX_DINO_SCRIPT'))


class AnimatedLabel(QLabel):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._color = QColor(0, 0, 0)

    def get_color(self):
        return self._color

    def set_color(self, color):
        self._color = color
        self.setStyleSheet(f"color: {color.name()};")

    color = Property(QColor, get_color, set_color)


class DinoApp(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Dino Script | tg: @aqsky")
        self.setGeometry(100, 100, 325, 125)
        self.setWindowIcon(QIcon("ico.ico"))
        self.setWindowIcon(QPixmap("ico.ico"))

        self.setFixedSize(345, 125)

        self.layout = QVBoxLayout()

        self.status_label = QLabel("Скрипт выключен", self)
        self.status_label.setStyleSheet("color: red; font-size: 16px;")
        self.status_label.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(self.status_label)

        self.info_label = QLabel("Для включения/отключения скрипта нажмите F8", self)
        self.info_label.setStyleSheet("font-size: 14px;")
        self.info_label.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(self.info_label)

        keyboard.add_hotkey('F8', self.toggle_script)

        menubar = QMenuBar(self)
        developer_menu = menubar.addMenu("Разработчик")

        self.top_layout = QHBoxLayout()
        self.jump_label = AnimatedLabel("Прыжки: 0", self)
        self.jump_label.setStyleSheet("font-size: 14px; margin-right: 2px;")
        self.jump_label.setAlignment(Qt.AlignRight | Qt.AlignTop)
        self.top_layout.addWidget(self.jump_label)
        self.top_layout.setAlignment(Qt.AlignTop)

        self.layout.addLayout(self.top_layout)

        jump_action = QAction("Прыжки", self)
        jump_action.setEnabled(False)
        jump_action.setText(f"Прыжки: {jump_counter}")
        developer_menu.addAction(jump_action)

        developer_menu.aboutToShow.connect(open_developer_link)

        self.layout.setMenuBar(menubar)
        self.setLayout(self.layout)

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_jump_label)
        self.timer.start(100)

        self.start_color_animation()

    def start_color_animation(self):
        self.color_animation = QSequentialAnimationGroup()

        colors = [
            QColor(255, 0, 0), QColor(255, 127, 0), QColor(255, 255, 0),
            QColor(0, 255, 0), QColor(0, 0, 255), QColor(75, 0, 130), QColor(143, 0, 255)
        ]

        for i in range(len(colors)):
            start_color = colors[i]
            end_color = colors[(i + 1) % len(colors)]
            animation = QPropertyAnimation(self.jump_label, b"color")
            animation.setDuration(1000)
            animation.setStartValue(start_color)
            animation.setEndValue(end_color)
            self.color_animation.addAnimation(animation)

        self.color_animation.setLoopCount(-1)
        self.color_animation.start()

    def toggle_script(self):
        global running, script_thread

        if not running:
            running = True
            self.status_label.setText("Скрипт включен")
            self.status_label.setStyleSheet("color: green; font-size: 16px;")
            script_thread = threading.Thread(target=self.run_script)
            script_thread.start()
        else:
            running = False
            self.status_label.setText("Скрипт выключен")
            self.status_label.setStyleSheet("color: red; font-size: 16px;")
            if script_thread:
                script_thread.join()

    def run_script(self):
        detect_and_jump()

    def update_jump_label(self):
        self.jump_label.setText(f"Прыжки: {jump_counter}")

    def closeEvent(self, event):
        global running
        running = False
        if script_thread:
            script_thread.join()
        keyboard.unhook_all_hotkeys()
        event.accept()


def main():
    app = QApplication(sys.argv)
    dino_app = DinoApp()
    dino_app.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
