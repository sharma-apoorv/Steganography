# Import PySide classes
import sys
from PySide.QtCore import *
from PySide.QtGui import *
from scipy.misc import imread
from scipy.misc import imsave

from SteganographyGUI import *
import Steganography

class Displays(QGraphicsView):
    newpic = Signal(str)
    def __init_(self, title, parent):
        super(Displays, self).__init__(title, parent)

        #Enable for images to be dropped
        self.setAcceptDrops(True)

        self.imgArr = None
        self.name = None

    def dropEvent(self, event):
        ext = event.mimeData().text()[-5:-2]
        if ext == "png" or ext == "jpg" or ext == "PEG":
            scene = QtGui.QGraphicsScene()
            pixMap = QtGui.QPixmap(event.mimeData().text()[7:-2])
            PixItem = scene.addPixmap(pixMap)
            self.setScene(scene)
            self.fitInView(PixItem, Qt.KeepAspectRatio)
            self.show()

            self.name = event.mimeData().text()[7:-2]
            self.imgArr = imread(self.name)
            self.newpic.emit('signal')

    def dragMoveEvent(self, event):
        event.accept()

    def dragEnterEvent(self, event):
        if event.mimeData().hasFormat('text/plain'):
            event.accept()
        else:
            event.ignore()

class SteganographyConsumer(QMainWindow, Ui_MainWindow):

    def __init__(self, parent=None):
        super(SteganographyConsumer, self).__init__(parent)
        self.setupUi(self)

        # Current status of GUI boxes
        self.applyCompressVal = self.chkApplyCompression.isChecked()
        self.compressionLevelVal = -1
        self.payloadSizeVal = 0
        self.payload1InPlace = False
        self.pay1Img = None
        self.payload1 = None

        self.applyOverrideVal = self.chkOverride.isChecked()
        self.carrierSizeVal = 0
        self.existsPayload = False
        self.carrier1InPlace = False
        self.car1Img = None
        self.carrier1 = None

        self.extractPay = False
        self.cleanCar = False
        self.existsPayload2 = False
        self.carrier2InPlace = False
        self.car2Img = None
        self.carrier2 = None

        # Functions for sliders and check boxes
        self.chkApplyCompression.stateChanged.connect(self.compressChk)
        self.slideCompression.valueChanged.connect(self.updateCompressVal)
        self.slideCompression.setTickInterval(0)

        self.chkOverride.stateChanged.connect(self.overrideChk)
        self.btnSave.clicked.connect(self.startSaveProcess)

        self.btnExtract.clicked.connect(self.startExtractProcess)
        self.btnClean.clicked.connect(self.startCleanProcess)

        # Embed payload --> Payload
        self.viewPayload1 = Displays(self.grpPayload1, self)
        self.viewPayload1.setGeometry(QtCore.QRect(10, 40, 361, 281))
        self.viewPayload1.setObjectName("viewPayload1")
        self.viewPayload1.newpic.connect(self.newpayload1)

        # Embed Payload --> Carrier
        self.viewCarrier1 = Displays(self.grpCarrier1, self)
        self.viewCarrier1.setGeometry(QtCore.QRect(10, 40, 361, 281))
        self.viewCarrier1.setObjectName("viewCarrier1")
        self.viewCarrier1.newpic.connect(self.newCarrier1)

        # Extract Payload --> Carrier
        self.viewCarrier2 = Displays(self.grpCarrier2, self)
        self.viewCarrier2.setGeometry(QtCore.QRect(10, 40, 361, 281))
        self.viewCarrier2.setObjectName("viewCarrier2")
        self.viewCarrier2.newpic.connect(self.newCarrier2)

    def newpayload1(self):
        print("Payload 1")
        self.payload1InPlace = True
        self.chkApplyCompression.setChecked(False)
        self.slideCompression.setEnabled(False)
        self.compressionLevelVal = -1
        self.txtCompression.setText('0')
        self.slideCompression.setSliderPosition(0)

        self.pay1Img = self.viewPayload1.imgArr
        self.updateCompressionTextBox()

    def updateCompressionTextBox(self):
        self.payload1 = Steganography.Payload(img=self.pay1Img, compressionLevel=self.compressionLevelVal)
        self.payloadSizeVal = len(self.payload1.content)
        self.txtPayloadSize.setText(str(self.payloadSizeVal))

        self.checkSaveBtnConds()

    def compressChk(self):
        print("Compression state has changed")
        self.applyCompressVal = self.chkApplyCompression.isChecked()

        # Check if the compression check box was checked or not
        if self.applyCompressVal == True:
            self.slideCompression.setEnabled(True)
            self.txtCompression.setEnabled(True)
            self.lblLevel.setEnabled(True)
            self.compressionLevelVal = int(self.txtCompression.text())
        else:
            self.slideCompression.setEnabled(False)
            self.txtCompression.setEnabled(False)
            self.lblLevel.setEnabled(False)
            self.compressionLevelVal = -1

        self.updateCompressionTextBox()

    def updateCompressVal(self):
        print("Slider value changed")

        # Update the value of the slider in the text box
        self.compressionLevelVal = self.slideCompression.value()
        self.txtCompression.setText(str(self.compressionLevelVal))

        # New compression value is available --> Update size of compression size
        self.updateCompressionTextBox()

    def newCarrier1(self):
        print("Carrier1")
        self.carrier1InPlace = True

        self.car1Img = self.viewCarrier1.imgArr
        self.carrier1 = Steganography.Carrier(img=self.car1Img)

        self.existsPayload = self.carrier1.payloadExists()

        if self.existsPayload:
            self.chkOverride.setEnabled(True)
            self.lblPayloadFound.setText(">>>> Payload Found <<<<")
        else:
            self.chkOverride.setEnabled(False)
            self.lblPayloadFound.setText("")

        if len(self.carrier1.img.shape) == 3:
            self.carrierSizeVal = self.carrier1.img.shape[0] * self.carrier1.img.shape[1]
        else:
            self.carrierSizeVal = self.carrier1.img.size

        self.txtCarrierSize.setText(str(self.carrierSizeVal))

        self.checkSaveBtnConds()

    def overrideChk(self):
        print("Override state has changed")
        self.applyOverrideVal = self.chkOverride.isChecked()

        self.checkSaveBtnConds()

    def checkSaveBtnConds(self):
        if self.carrier1InPlace and self.payload1InPlace:
            print("Both in place")
            if self.carrierSizeVal >= self.payloadSizeVal:
                print(self.carrierSizeVal, self.payloadSizeVal)
                if (self.existsPayload == False) or (self.existsPayload == True and self.applyOverrideVal == True):
                    print("True")
                    self.btnSave.setEnabled(True)
                else:
                    print("False")
                    self.btnSave.setEnabled(False)
            else:
                self.btnSave.setEnabled(False)
        else:
            self.btnSave.setEnabled(False)

    def startSaveProcess(self):
        print("Save btn pushed")
        (path, _) = QFileDialog.getSaveFileName(self, 'Save Image...')

        embeddedArr = self.carrier1.embedPayload(self.payload1, override=self.applyOverrideVal)
        imsave(path, embeddedArr)

    def newCarrier2(self):
        print("Carrier2")
        self.carrier2InPlace = True

        scene = QtGui.QGraphicsScene()
        scene.clear()
        self.viewPayload2.setScene(scene)
        self.viewPayload2.show()

        self.car2Img = self.viewCarrier2.imgArr
        self.carrier2 = Steganography.Carrier(img=self.car2Img)

        self.existsPayload2 = self.carrier2.payloadExists()

        if self.existsPayload2:
            self.btnExtract.setEnabled(True)
            self.btnClean.setEnabled(True)
            self.lblCarrierEmpty.setText("")
        else:
            self.btnExtract.setEnabled(False)
            self.btnClean.setEnabled(False)
            self.lblCarrierEmpty.setText(">>>> Carrier Empty <<<<")

    def startExtractProcess(self):
        print("Extract Image")
        payload = self.carrier2.extractPayload()

        scene = QtGui.QGraphicsScene()
        imsave('temp.png', payload.img)
        pixMap = QtGui.QPixmap('temp.png')
        PixItem = scene.addPixmap(pixMap)
        self.viewPayload2.setScene(scene)
        self.viewPayload2.fitInView(PixItem,  Qt.KeepAspectRatio)
        self.viewPayload2.show()

        self.btnExtract.setEnabled(False)

    def startCleanProcess(self):
        print("Clean Image")
        # print(self.viewCarrier2.name)
        cleanImg = self.carrier2.clean()

        scene = QtGui.QGraphicsScene()
        scene.clear()
        self.viewPayload2.setScene(scene)
        self.viewPayload2.show()

        # scene = QtGui.QGraphicsScene()
        imsave(self.viewCarrier2.name, cleanImg)
        # pixMap = QtGui.QPixmap(self.viewCarrier2.name)
        # PixItem = scene.addPixmap(pixMap)

        self.lblCarrierEmpty.setText(">>>> Carrier Empty <<<<")
        # self.viewPayload2.setScene(scene)
        # self.viewPayload2.fitInView(PixItem,  Qt.KeepAspectRatio)
        # self.viewPayload2.show()

        self.btnClean.setEnabled(False)

currentApp = QApplication(sys.argv)
currentForm = SteganographyConsumer()

currentForm.show()
currentApp.exec_()