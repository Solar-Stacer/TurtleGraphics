from math import sin, cos, pi

from PySide6 import QtCore as qtc
from PySide6 import QtGui as qtg
from PySide6 import QtWidgets as qtw


# noinspection unused-imports
import resources_rc

class Turtle(qtw.QGraphicsObject):
	TurtleDrawInCanvasRequest = qtc.Signal()

	def __init__(self, x: float | int, y: float | int):
		super().__init__()
		self.new_x = None
		self.new_y = None
		self.center_x = x
		self.center_y = y
		self.prev_x = self.x
		self.prev_y = self.y
		self.angle = 0
		self.setPos(self.center_x, self.center_y)

	def move(self, pixels: float | int):
		self.prev_x = self.scenePos().x()
		self.prev_y = self.scenePos().y()
		self.new_x = self.prev_x + pixels * cos((self.rotation() - 90) * pi / 180)
		self.new_y = self.prev_y + pixels * sin((self.rotation() - 90) * pi / 180)
		self.setPos(self.new_x, self.new_y)
		self.TurtleDrawInCanvasRequest.emit()

	def forward(self, pixels: float | int):
		self.move(pixels)

	def backward(self, pixels: float | int):
		self.move(-pixels)

	def turn(self, angle: float | int):
		self.angle += angle
		self.setRotation(self.angle)

	def right(self, angle: float | int):
		self.angle += angle
		self.setRotation(self.angle)

	def left(self, angle: float | int):
		self.angle -= angle
		self.setRotation(self.angle)

	def home(self):
		self.prev_x = self.scenePos().x()
		self.prev_y = self.scenePos().y()
		self.angle = 0
		self.setPos(self.center_x, self.center_y)
		self.setRotation(self.angle)

	def setxy(self, x: float | int, y: float | int):
		self.setPos(x + self.center_x, -y + self.center_y)

	def hideTurtle(self):
		self.hide()

	def showTurtle(self):
		self.show()

	def boundingRect(self):
		return qtc.QRectF(-15, -20, 30, 30)

	def paint(self, painter: qtg.QPainter, option: qtw.QStyleOptionGraphicsItem, widget: qtw.QWidget = None):
		painter.setRenderHint(qtg.QPainter.RenderHint.Antialiasing, True)
		painter.setPen(qtg.QPen(qtc.Qt.GlobalColor.red, 2))
		painter.setBrush(qtg.QBrush(qtc.Qt.GlobalColor.red))
		painter.drawPolygon([qtc.QPoint(-10, 0), qtc.QPoint(10, 0), qtc.QPoint(0, -10)])


class TurtleCanvas(qtw.QGraphicsObject):
	colors = ["red", "green", "blue", "orange", "yellow", "cyan", "violet", "magenta", "white", "gray", "black"]

	def __init__(self, max_size: qtc.QSize):
		super().__init__()
		self.size = max_size
		self.image = qtg.QImage(self.size, qtg.QImage.Format.Format_ARGB32_Premultiplied)
		self.image.fill(qtg.QColor('black'))
		self.disable_pen = False
		self.angle = -90
		self.color = qtg.QColor('red')
		self.thick = 2

		self.turtle = Turtle(self.size.width() / 2, self.size.height() / 2)
		self.turtle.setParentItem(self)
		self.turtle.TurtleDrawInCanvasRequest.connect(self.drawCanvas)

	@qtc.Slot()
	def drawCanvas(self):
		if not self.disable_pen:
			painter = qtg.QPainter(self.image)
			painter.setPen(qtg.QPen(self.color, self.thick))
			painter.setRenderHints(qtg.QPainter.RenderHint.Antialiasing)
			painter.drawLine(self.turtle.prev_x, self.turtle.prev_y, self.turtle.scenePos().x(),
			                 self.turtle.scenePos().y())
			painter.end()
		self.update()

	def setColor(self, color: str):
		for item in TurtleCanvas.colors:
			if color == item:
				self.color = qtg.QColor(item)
		self.update()

	def setFill(self, color: str):
		self.color = color
		self.image.fill(qtg.QColor(color))
		self.update()

	def setWidth(self, number: int | float):
		self.thick = number

	def setPenUp(self):
		self.disable_pen = True

	def setPenDown(self):
		self.disable_pen = False

	def clearCanvas(self):
		self.turtle.setPos(self.size.width() / 2, self.size.height() / 2)
		self.image.fill(qtg.QColor('black'))
		self.update()

	def resetCanvas(self):
		self.clearCanvas()
		self.turtle.home()
		self.turtle.showTurtle()
		self.disable_pen = False
		self.angle = -90
		self.color = qtg.QColor('red')
		self.thick = 2

	def boundingRect(self):
		return qtc.QRectF(0, 0, self.size.width(), self.size.height())

	def paint(self, painter: qtg.QPainter, option: qtw.QStyleOptionGraphicsItem, widget: qtw.QWidget = None):
		painter.setRenderHints(qtg.QPainter.RenderHint.Antialiasing, True)
		painter.drawImage(0, 0, self.image)
