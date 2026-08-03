import PySide6.QtCore as qtc
import PySide6.QtGui as qtg
import PySide6.QtWidgets as qtw

# noinspection unused-imports
import resources_rc

class HelpDialog(qtw.QDialog):
	def __init__(self, x, y, text=""):
		super().__init__()
		icon = qtg.QIcon(":/icon.png")

		self.setWindowTitle("Sharp Custom Dialog")
		self.setWindowIcon(icon)
		self.setFixedSize(x, y)

		icon_label = qtw.QLabel()
		pixmap = icon.pixmap(qtc.QSize(100, 100))
		icon_label.setPixmap(pixmap)

		text_label = qtw.QLabel()
		text_label.setText(text)
		text_label.setAlignment(qtg.Qt.AlignmentFlag.AlignTop | qtg.Qt.AlignmentFlag.AlignLeft)
		text_label.setWordWrap(True)
		text_label.setSizePolicy(qtw.QSizePolicy.Policy.Expanding, qtw.QSizePolicy.Policy.Expanding)

		layout_1 = qtw.QVBoxLayout()
		layout_1.addWidget(icon_label)
		layout_1.setAlignment(icon_label, qtg.Qt.AlignmentFlag.AlignTop)

		layout_2 = qtw.QHBoxLayout()
		layout_2.addLayout(layout_1)
		layout_2.addWidget(text_label)

		main_layout = qtw.QHBoxLayout()
		main_layout.addLayout(layout_2)

		self.setLayout(main_layout)


class HowToUseDialog(qtw.QDialog):
	def __init__(self, parent=None):
		super().__init__(parent)

		icon_label = qtw.QLabel()
		icon = qtg.QIcon(":/icon.png")
		pixmap = icon.pixmap(qtc.QSize(100, 100))
		icon_label.setPixmap(pixmap)

		md_file = qtc.QFile(":/README.md")
		if md_file.open(qtc.QIODevice.OpenModeFlag.ReadOnly):
			text = str(md_file.readAll(), encoding="utf-8")
			md_file.close()
		else:
			print(f"Qt Error: {md_file.errorString()}")
			return

		self.setWindowIcon(qtg.QIcon(":/icon.png"))

		screen_resolution = qtg.QGuiApplication.primaryScreen().size()
		self.setFixedSize(screen_resolution.width() - 400, screen_resolution.height() - 400)

		md_text_browser = qtw.QTextBrowser()
		md_text_browser.setOpenExternalLinks(True)
		md_text_browser.setFont(qtg.QFont("Segoe UI", 11))
		md_text_browser.setStyleSheet("""
		    QTextEdit {
		        background-color: transparent;
		        border: none;
		    }
		""")
		md_text_browser.setOpenExternalLinks(True)
		md_text_browser.setMarkdown(text)

		layout = qtw.QVBoxLayout()
		layout.addWidget(icon_label)
		layout.setAlignment(icon_label, qtc.Qt.AlignmentFlag.AlignTop)
		layout.setContentsMargins(10, 10, 10, 10)

		main_layout = qtw.QHBoxLayout()
		main_layout.addLayout(layout)
		main_layout.addWidget(md_text_browser)

		self.setLayout(main_layout)
		self.setWindowTitle("How to Use?")


class PLogoDocDialog(qtw.QDialog):
	def __init__(self):
		super().__init__()

		md_file = qtc.QFile(":/PLogo.md")

		text = str("")
		if md_file.open(qtc.QIODevice.OpenModeFlag.ReadOnly | qtc.QIODevice.OpenModeFlag.Text):
			text = str(md_file.readAll(), encoding="utf-8")
			md_file.close()
		else:
			print(f"Qt Error: {md_file.errorString()}")

		self.setWindowIcon(qtg.QIcon(":/icon.png"))
		screen_resolution = qtg.QGuiApplication.primaryScreen().size()
		self.setFixedSize(screen_resolution.width()-100, screen_resolution.height()-100)

		md_text_browser = qtw.QTextBrowser()
		md_text_browser.setOpenExternalLinks(True)
		md_text_browser.setFont(qtg.QFont("Segoe UI", 14))
		md_text_browser.setStyleSheet("""
		    QTextEdit {
		        background-color: transparent;
		        border: none;
		    }
		""")
		md_text_browser.setMarkdown(text)

		layout = qtw.QVBoxLayout()
		layout.addWidget(md_text_browser)
		self.setLayout(layout)
		self.setWindowTitle("PLogo Documentation")

class AboutDialog(HelpDialog):
	def __init__(self):
		x, y = 650, 150
		text = '''
        <h1>About</h1>
        <p style="font-size: 15px;">Made by <b><i>Solar Stacer</i></b>, in Python using:
        <ul>
        <li>PySide6, the official Python bindings for the native GUI C++ development framework, Qt, by The Qt Company</li>
        <li>Lark, a Python library for parsing context-free grammars,</li>
        <li>rich, a Python library for rich text and beautiful formatting in the terminal,</li>
        </ul>
        </p>
        '''
		super().__init__(x, y, text)
		self.setWindowTitle("About")


if __name__ == '__main__':
	app = qtw.QApplication([])
	h = HowToUseDialog()
	h.show()
	a = AboutDialog()
	a.show()
	p = PLogoDocDialog()
	p.show()
	app.exec()
