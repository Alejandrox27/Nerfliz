from PyQt5 import QtWidgets, QtCore, QtGui
from GUI.messageBox_confirmation import Ui_Dialog

class MessageBox_confirmation(QtWidgets.QDialog):
    def __init__(self,
                 message = 'message',
                 icon = ''
                 ):
        super().__init__()
        
        self.setWindowFlags(QtCore.Qt.WindowType.FramelessWindowHint)
        self.setAttribute(QtCore.Qt.WidgetAttribute.WA_TranslucentBackground)
        
        self.drag_position = None
        self.confirmation = False
        self.message = message
        self.icon = icon
        
        self.inicializateMessage()
        
    def inicializateMessage(self):
        self.ui = Ui_Dialog()
        self.ui.setupUi(self)
        
        self.ui.messageLbl.setText(self.message)
        self.ui.label.setPixmap(QtGui.QPixmap(self.icon))
        self.ui.label.setFixedSize(50,50)
        
        self.ui.noBtn.clicked.connect(self.closeAnimation)
        self.ui.yesBtn.clicked.connect(self.closeAnimation)
        self.ui.closeMessageBtn.clicked.connect(self.closeAnimation)
        
    def mousePressEvent(self, event):
        if not self.isMaximized():
            if event.buttons() == QtCore.Qt.LeftButton:
                self.drag_position = event.globalPos() - self.frameGeometry().topLeft()
                event.accept()

    def mouseMoveEvent(self, event):
        if not self.isMaximized():
            if self.drag_position:
                self.move(event.globalPos() - self.drag_position)
                event.accept()

    def mouseReleaseEvent(self, event):
        if not self.isMaximized():
            self.drag_position = None
        
    def showEvent(self, event):
        super().showEvent(event)

        self.animation = QtCore.QPropertyAnimation(self, b'windowOpacity')
        self.animation.setDuration(200)
        self.animation.setStartValue(0.0)
        self.animation.setEndValue(1.0)
        self.animation.start()
        
    def closeAnimation(self):
        button = self.sender()
        
        if button.text() == 'Yes':
            self.confirmation = True
        else:
            self.confirmation = False
            
        self.fade_out_animation = QtCore.QPropertyAnimation(self, b'windowOpacity')
        self.fade_out_animation.setDuration(80)
        self.fade_out_animation.setStartValue(1.0)
        self.fade_out_animation.setEndValue(0.0)
        self.fade_out_animation.finished.connect(self.close)
        self.fade_out_animation.start()