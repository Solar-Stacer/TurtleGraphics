import functools
import sys

from DialogClasses import *
from PLogo import *
from TurtleUI import *


class TurtleException(Exception):
    pass


class CustomFieldGroupBox(qtw.QGroupBox):
    def __init__(self):
        super().__init__()
        self.text_edit = qtw.QTextEdit()
        self.text_edit.setParent(self)
        self.text_edit.setAcceptRichText(False)
        self.font = qtg.QFont("Consolas", 10)
        self.text_edit.setFont(self.font)
        tab_size_in_spaces = 4
        font_metrics = qtg.QFontMetricsF(self.font)
        space_width = font_metrics.horizontalAdvance(' ')
        tab_stop_distance = space_width * tab_size_in_spaces
        self.text_edit.setTabStopDistance(tab_stop_distance)

        self.layout = qtw.QVBoxLayout()
        self.layout.addWidget(self.text_edit)
        self.setLayout(self.layout)


class MainWindow(qtw.QMainWindow):
    queue = []
    clock = 500

    def __init__(self):
        super().__init__()
        self.Node = None
        self.setWindowTitle("Turtle Graphics")

        self.setWindowIcon(qtg.QIcon(":/icon.png"))
        self.setFixedSize(1300, 670)

        width, height = 800, 600
        self.canvas_size = qtc.QSize(width, height)
        self.canvas = TurtleCanvas(self.canvas_size)
        self.scene = qtw.QGraphicsScene()
        self.scene.addItem(self.canvas)
        self.scene.setSceneRect(0, 0, width, height)
        self.view = qtw.QGraphicsView()
        self.view.setScene(self.scene)
        self.view.setFixedSize(width + 10, height + 10)
        self.view.setHorizontalScrollBarPolicy(qtc.Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.view.setVerticalScrollBarPolicy(qtc.Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        self.clock = qtc.QTimer(self)
        self.clock.timeout.connect(self.start_clock)

        self.command_field = CustomFieldGroupBox()
        self.output_field = CustomFieldGroupBox()
        self.command_field.setTitle("Input")
        self.output_field.setTitle("Output")
        self.output_field.text_edit.setReadOnly(True)

        self.slider_label = qtw.QLabel()
        self.slider_label.setText(f"Execution Time (ms) per instruction: {MainWindow.clock}")

        self.slider = qtw.QSlider(qtc.Qt.Orientation.Horizontal)
        self.slider.setMinimum(0)
        self.slider.setMaximum(1000)
        self.slider.setValue(MainWindow.clock)
        self.slider.valueChanged.connect(self.set_slider)

        self.run_button = qtw.QPushButton("Run", self)
        self.run_button.clicked.connect(self.run)
        self.pause_play_button = qtw.QPushButton()
        self.pause_play_button.setText("Pause")
        self.pause_play_button.clicked.connect(self.pause_play)

        self.button_layout = qtw.QHBoxLayout()
        self.button_layout.addWidget(self.run_button)
        self.button_layout.addWidget(self.pause_play_button)

        self.right_layout = qtw.QVBoxLayout()
        self.right_layout.addWidget(self.slider_label)
        self.right_layout.addWidget(self.slider)
        self.right_layout.addWidget(self.command_field)
        self.right_layout.addWidget(self.output_field)
        self.right_layout.addLayout(self.button_layout)

        main_layout = qtw.QHBoxLayout()
        main_layout.addWidget(self.view)
        main_layout.addLayout(self.right_layout)

        self.menu = self.menuBar()
        self.file_menu = self.menu.addMenu("&File")
        self.open_action = qtg.QAction("&Open PLogo", self)
        self.save_action = qtg.QAction("&Save PLogo", self)
        self.export_action = qtg.QAction("&Export Canvas PNG", self)
        self.file_menu.addAction(self.open_action)
        self.file_menu.addAction(self.save_action)
        self.file_menu.addAction(self.export_action)
        self.open_action.triggered.connect(self.open_plogo)
        self.save_action.triggered.connect(self.save_plogo)
        self.export_action.triggered.connect(self.export_image)

        self.help_menu = self.menu.addMenu("&Help")
        self.how_use_action = qtg.QAction("&How to Use?", self)
        self.PLogoDoc_action = qtg.QAction("&PLogo Documentation", self)
        self.about_action = qtg.QAction("&About", self)
        self.help_menu.addAction(self.how_use_action)
        self.help_menu.addAction(self.PLogoDoc_action)
        self.help_menu.addAction(self.about_action)
        self.how_use_action.triggered.connect(self.showHowToUse)
        self.about_action.triggered.connect(self.showAbout)
        self.PLogoDoc_action.triggered.connect(self.showPLogoDoc)

        container = qtw.QWidget()
        container.setLayout(main_layout)
        self.setCentralWidget(container)

        self.show()
        self.centerWindow()

        self.PLogoExecute = PLogoObject()

    def set_slider(self, value):
        MainWindow.clock = value
        self.slider_label.setText(f"Execution Time (ms) per instruction: {MainWindow.clock}")

    def centerWindow(self):
        screen_geometry = qtg.QScreen.availableGeometry(qtw.QApplication.primaryScreen())
        screen_center = screen_geometry.center()
        window_frame = self.frameGeometry()
        window_frame.moveCenter(screen_center)
        self.move(window_frame.topLeft())

    @qtc.Slot()
    def showHowToUse(self):
        dialog = HowToUseDialog()
        dialog.exec()

    @qtc.Slot()
    def showAbout(self):
        dialog = AboutDialog()
        dialog.exec()

    @qtc.Slot()
    def showPLogoDoc(self):
        dialog = PLogoDocDialog()
        dialog.exec()

    def open_plogo(self):
        fileName = qtw.QFileDialog.getOpenFileName(self, "Open PLogo Code", "",
                                                   "PLogo Files (*.PLogo);; Text files (*.txt)")
        if fileName[0]:
            with open(fileName[0], "r") as fh:
                self.command_field.text_edit.setText(fh.read())

    def save_plogo(self):
        fileName = qtw.QFileDialog.getSaveFileName(self, "Save PLogo Code", "",
                                                   "PLogo Files (*.PLogo);; Text files (*.txt)")
        if fileName[0]:
            with open(fileName[0], "w", encoding="utf-8") as fh:
                fh.write(self.command_field.text_edit.toPlainText())

    def export_image(self):
        fileName = qtw.QFileDialog.getSaveFileName(self, "Save Image", "", "Image Files (*.png)")
        if fileName[0]:
            self.canvas.image.save(fileName[0])

    @qtc.Slot(str)
    def changeOutputField(self, string):
        self.output_field.text_edit.setTextColor(qtc.Qt.GlobalColor.red)
        self.output_field.text_edit.setText(f"{type(string).__name__}: {string}")

    def run(self):
        custom_global = {
            "fd": self.canvas.turtle.forward,
            "bd": self.canvas.turtle.backward,
            "tr": self.canvas.turtle.turn,
            "rt": self.canvas.turtle.right,
            "lt": self.canvas.turtle.left,
            "setxy": self.canvas.turtle.setxy,
            "home": self.canvas.turtle.home,
            "st": self.canvas.turtle.showTurtle,
            "ht": self.canvas.turtle.hideTurtle,

            "fl": self.canvas.setFill,
            "col": self.canvas.setColor,
            "wd": self.canvas.setWidth,
            "cc": self.canvas.clearCanvas,
            "pu": self.canvas.setPenUp,
            "pd": self.canvas.setPenDown,
            "rst": self.canvas.resetCanvas
        }

        self.clock.stop()
        MainWindow.queue.clear()
        self.canvas.resetCanvas()
        self.output_field.text_edit.setText(f"")
        try:
            if self.command_field.text_edit.toPlainText().isspace() or not self.command_field.text_edit.toPlainText():
                raise Exception("No command entered.")
            queue_tuple = self.PLogoExecute.executePLogo(self.command_field.text_edit.toPlainText().lower())
            for instruction in queue_tuple:
                _instruction_name = instruction[0]
                _arguments = instruction[1:]
                MainWindow.queue.append(functools.partial(custom_global[_instruction_name], *_arguments))
            self.clock.start(MainWindow.clock)
        except Exception as e:
            self.clock.stop()
            MainWindow.queue.clear()
            self.changeOutputField(e)
        if self.pause_play_button.text() == "Play":
            self.pause_play_button.setText("Pause")

    def pause_play(self):
        if self.pause_play_button.text() == "Pause":
            self.pause_play_button.setText("Play")
            self.clock.stop()
        elif self.pause_play_button.text() == "Play":
            self.pause_play_button.setText("Pause")
            self.clock.start(MainWindow.clock)

    def start_clock(self):
        if not MainWindow.queue:
            self.output_field.text_edit.setTextColor(qtc.Qt.GlobalColor.green)
            self.output_field.text_edit.setText(f"Success.")
            self.clock.stop()
            return
        self.clock.setInterval(MainWindow.clock)
        try:
            MainWindow.queue.pop(0)()
        except Exception as e:
            self.clock.stop()
            MainWindow.queue.clear()
            self.changeOutputField(e)
            return


if "__main__" == __name__:
    app = qtw.QApplication(sys.argv)
    w = MainWindow()

    sys.exit(app.exec())
