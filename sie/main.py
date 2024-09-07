import sys
from PyQt5.QtWidgets import (QApplication, QMainWindow, QLabel, QAction, 
                             QFileDialog, QInputDialog, QMessageBox, QMenu, QStatusBar)
from PyQt5.QtGui import QIcon, QPixmap, QImage
from PyQt5.QtCore import Qt
from PIL import Image, ImageOps
from io import BytesIO
import psd_tools

class ImageEditor(QMainWindow):
    def __init__(self):
        super().__init__()
        self.image = None
        self.image_history = []
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Python Image Editor')
        self.setGeometry(100, 100, 800, 600)

        # Create a label to display the image
        self.imageLabel = QLabel(self)
        self.imageLabel.setAlignment(Qt.AlignCenter)
        self.setCentralWidget(self.imageLabel)

        # Create menu bar
        menubar = self.menuBar()

        # File menu
        fileMenu = menubar.addMenu('File')

        openAction = QAction('Open', self)
        openAction.triggered.connect(self.openImage)
        fileMenu.addAction(openAction)

        saveAction = QAction('Save', self)
        saveAction.triggered.connect(self.saveImage)
        fileMenu.addAction(saveAction)

        # Edit menu
        editMenu = menubar.addMenu('Edit')

        resizeAction = QAction('Resize', self)
        resizeAction.triggered.connect(self.resizeImage)
        editMenu.addAction(resizeAction)

        cropAction = QAction('Crop', self)
        cropAction.triggered.connect(self.cropImage)
        editMenu.addAction(cropAction)

        grayscaleAction = QAction('Convert to Grayscale', self)
        grayscaleAction.triggered.connect(self.convertToGrayscale)
        editMenu.addAction(grayscaleAction)

        undoAction = QAction('Undo', self)
        undoAction.triggered.connect(self.undo)
        editMenu.addAction(undoAction)

        # Create status bar
        self.statusBar = QStatusBar()
        self.setStatusBar(self.statusBar)
        self.updateStatusBar()

    def openImage(self):
        fileName, _ = QFileDialog.getOpenFileName(self, "Open Image", "", 
                                                  "Image Files (*.png *.jpg *.bmp *.webp *.gif *.psd)")
        if fileName:
            if fileName.lower().endswith('.psd'):
                psd = psd_tools.PSDImage.open(fileName)
                self.image = psd.compose()
            else:
                self.image = Image.open(fileName)
            
            # Convert to RGB if necessary
            if self.image.mode != 'RGB':
                self.image = self.image.convert('RGB')
            
            self.image_history = []  # Clear history when opening a new image
            self.displayImage()
            self.updateStatusBar()

    def displayImage(self):
        if self.image:
            buffer = BytesIO()
            self.image.save(buffer, format="PNG")
            qimage = QImage.fromData(buffer.getvalue())
            pixmap = QPixmap.fromImage(qimage)
            self.imageLabel.setPixmap(pixmap.scaled(self.imageLabel.size(), 
                                                    Qt.KeepAspectRatio, 
                                                    Qt.SmoothTransformation))

    def resizeImage(self):
        if self.image:
            self.image_history.append(self.image.copy())
            width, ok = QInputDialog.getInt(self, 'Resize Image', 'Enter new width:',
                                            min=1, max=10000, step=1)
            if ok:
                height = int(self.image.size[1] * (width / self.image.size[0]))
                self.image = self.image.resize((width, height), Image.LANCZOS)
                self.displayImage()
                self.updateStatusBar()

    def cropImage(self):
        if self.image:
            self.image_history.append(self.image.copy())
            width, ok = QInputDialog.getInt(self, 'Crop Image', 'Enter crop width:',
                                            min=1, max=self.image.width, step=1)
            if ok:
                height, ok = QInputDialog.getInt(self, 'Crop Image', 'Enter crop height:',
                                                 min=1, max=self.image.height, step=1)
                if ok:
                    left = (self.image.width - width) // 2
                    top = (self.image.height - height) // 2
                    right = left + width
                    bottom = top + height
                    self.image = self.image.crop((left, top, right, bottom))
                    self.displayImage()
                    self.updateStatusBar()

    def saveImage(self):
        if self.image:
            fileName, _ = QFileDialog.getSaveFileName(self, "Save Image", "", 
                                                      "PNG (*.png);;JPEG (*.jpg *.jpeg);;BMP (*.bmp);;WebP (*.webp);;GIF (*.gif)")
            if fileName:
                file_format = fileName.split('.')[-1].upper()
                if file_format == 'JPG':
                    file_format = 'JPEG'
                elif file_format == 'WEBP':
                    file_format = 'WebP'
                
                try:
                    if file_format == 'GIF':
                        # For GIF, we need to handle potential palettes
                        self.image.save(fileName, format=file_format, save_all=True)
                    else:
                        self.image.save(fileName, format=file_format)
                    QMessageBox.information(self, "Save Successful", "Image saved successfully!")
                except Exception as e:
                    QMessageBox.warning(self, "Save Failed", f"Failed to save image: {str(e)}")

    def convertToGrayscale(self):
        if self.image:
            self.image_history.append(self.image.copy())
            # Convert the image to grayscale
            self.image = ImageOps.grayscale(self.image)
            # Convert back to RGB mode for consistency in display and saving
            self.image = self.image.convert('RGB')
            self.displayImage()
            self.updateStatusBar()
            QMessageBox.information(self, "Conversion Successful", "Image converted to grayscale!")

    def undo(self):
        if self.image_history:
            self.image = self.image_history.pop()
            self.displayImage()
            self.updateStatusBar()
            QMessageBox.information(self, "Undo Successful", "Last operation undone!")
        else:
            QMessageBox.information(self, "Undo", "No more operations to undo!")

    def updateStatusBar(self):
        if self.image:
            width, height = self.image.size
            self.statusBar.showMessage(f"Image size: {width}x{height}")
        else:
            self.statusBar.showMessage("No image loaded")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = ImageEditor()
    ex.show()
    sys.exit(app.exec_())