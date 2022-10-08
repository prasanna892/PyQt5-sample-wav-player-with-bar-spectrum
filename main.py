# importing required module
import sys, wave, numpy
from scipy.fftpack import dct, fft, rfft, fftfreq, dst
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtTest import *
from PyQt5 import QtMultimedia
from os.path import expanduser
from datetime import timedelta

# creating class
class AudioSpectrum(QMainWindow):
    # initializating
    def __init__(self, parent = None):
        super(AudioSpectrum, self).__init__(parent)

        # Setting spectrum bar and window size
        self.bar_property(rfft) # setting type of fourier transform
        self.screen_width = self.Number * self.WIDTH
        self.screen_height = 50 + self.HEIGHT

        # Setting window position
        self.setGeometry(0, 0, self.screen_width, self.screen_height)

        # Centering window position
        qtRectangle = self.frameGeometry()
        centerPoint = QDesktopWidget().availableGeometry().center()
        qtRectangle.moveCenter(centerPoint)
        self.move(qtRectangle.topLeft())

        # Set title of the MainWindow
        self.setWindowTitle('WAV Player')
		
		# Create Menubar
        self.createMenubar()

        # Creating label to show info
        self.song_name_ = QLabel(self)
        self.song_name_.setFont(QFont("Consolas", 15, 10, True))
        self.song_name_.setText("Now Playing:")
        self.song_name_.setGeometry(QRect(20, 5, 200, 50))
        self.song_name_.setAlignment(Qt.AlignBottom)
        self.song_name_.setStyleSheet("color: yellow")

        self.song_name = QLabel(self)
        self.song_name.setFont(QFont("Consolas", 15, 10, True))
        self.song_name.setText("-----------------------------------------")
        self.song_name.setGeometry(QRect(200, 5, 600, 50))
        self.song_name.setAlignment(Qt.AlignBottom)
        self.song_name.setStyleSheet("color: yellow")
        
        self.song_time_ = QLabel(self)
        self.song_time_.setFont(QFont("Times New Roman", 15, 10, True))
        self.song_time_.setText("Time Elapsed:")
        self.song_time_.setGeometry(QRect(self.screen_width-350, 5, 250, 50))
        self.song_time_.setAlignment(Qt.AlignBottom)
        self.song_time_.setStyleSheet("color: cyan")

        self.song_time = QLabel(self)
        self.song_time.setFont(QFont("Times New Roman", 15, 10, True))
        self.song_time.setText("0:00:00")
        self.song_time.setGeometry(QRect(self.screen_width-190, 5, 250, 50))
        self.song_time.setAlignment(Qt.AlignBottom)
        self.song_time.setStyleSheet("color: cyan")
        
        # Initializating timer to update window
        self.load_timer = QTimer()
        self.load_timer.timeout.connect(self.loadTime)
        self.load_timer.start(3000)

        self.value_timer = QTimer()
        self.value_timer.timeout.connect(self.change_value)

        # Initializating required variable
        self.FPS = 10
        self.bar_total = []
        self.song_list = []
        self.song_changed_ = False
        self.song_current_sec = 0
        
        # Creating media player and player list
        self.player = QtMultimedia.QMediaPlayer(self)
        self.playlist = QtMultimedia.QMediaPlaylist(self.player)

    # Creating menu bar
    def createMenubar(self):
        menubar = self.menuBar()
        filemenu = menubar.addMenu('add songs') 
        filemenu.addAction(self.folderOpen())

    # Open folder dialog box
    def folderOpen(self):
        folderAc = QAction('Open Folder',self)
        folderAc.setShortcut('Ctrl+D')
        folderAc.triggered.connect(self.addFiles)

    # Adding all .wav file in selected folder to player list
    def addFiles(self):
        folderChoosen = QFileDialog.getExistingDirectory(self,'Open Music Folder', expanduser('~'))
        if folderChoosen != None:
            it = QDirIterator(folderChoosen)
            it.next()
            while it.hasNext():
                if it.fileInfo().isDir() == False and it.filePath() != '.':
                    fInfo = it.fileInfo()
                    if fInfo.suffix() in ('wav'):#('mp3','ogg','wav'):
                        self.song_list.append((fInfo.filePath(), fInfo.fileName()))
                        self.playlist.addMedia(QtMultimedia.QMediaContent(QUrl.fromLocalFile(it.filePath())))
                it.next()

    # Funvtion to set bar property
    def bar_property(self, fft_type):
        self.Ftransform = fft_type
        
        bar_scale = 1 # Change value to increase or decrease bar count
        self.Number = 240//bar_scale # number of bars
        self.HEIGHT = 270 # self.HEIGHT of a bar
        self.WIDTH = 5*bar_scale #self.WIDTH of a bar

    # Wait until user select the songs
    def loadTime(self):
        if self.playlist.mediaCount() != 0:
            self.load_timer.stop()
            self.loaded = True

            self.media_setting()
            self.wave_process()
            self.get_all_data()

            self.player.play()
            self.value_timer.start(1000//self.FPS)

    # Process the .wav file to get wave information in time domain
    def wave_process(self):
        self.bar_total = []
        f = wave.open(self.song_path, 'rb')
        params = f.getparams()
        self.nchannels, self.sampwidth, self.framerate, self.nframes = params[:4]
        str_data = f.readframes(self.nframes)
        f.close()

        self.duration = int(self.nframes / self.framerate)

        self.wave_data = numpy.frombuffer(str_data, dtype = numpy.short)
        self.wave_data.shape = -1, 2
        self.wave_data = self.wave_data.T

    # Process data from time domain to frequency domain by fft
    def Visualizer(self, nums):
        num = int(nums)
        try:
            h = [min(self.HEIGHT, int(i**(1 / 2.5) * self.HEIGHT / 100)) for i in abs(self.Ftransform(self.wave_data[0][self.nframes - num:self.nframes - num + self.Number]))]
            self.bars_pos(h)
        except:
            pass

    # Method to set bar size depend upon frequency
    def bars_pos(self, h):
        bars = []
        for i in h:
            bars.append(QRectF(len(bars) * self.WIDTH , 50 + self.HEIGHT - i, self.WIDTH - 1, i))
        self.bar_total.append(bars)

    # Method to convert all data in .wav file
    def get_all_data(self):
        num = self.nframes
        for i in range(int((self.nframes / self.framerate)*10)):
            num -= self.framerate / self.FPS
            self.Visualizer(num)
        self.bar_total.append(QRectF(0,0,0,0))

    # Method to setting player and player list property
    def media_setting(self):
        self.song_path = self.song_list[0][0]
        self.song_name.setText(self.song_list[0][1])
        self.player.setPlaylist(self.playlist)
        self.player.playlist().setCurrentIndex(0)
        self.player.playlist().setPlaybackMode(QtMultimedia.QMediaPlaylist.Loop)
        self.player.play()

        # Connection when property changed
        self.player.positionChanged.connect(self.song_time_update)
        self.playlist.currentIndexChanged.connect(self.song_changed)

    # Method for update song time
    def song_time_update(self, pos):
        if not self.song_changed_:
            td = str(timedelta(seconds=(pos//1000)+1))
            self.song_time.setText(td)

    # Re-setting media when song changed
    def song_changed(self, song_index):
        self.song_time.setText('0:00:00')
        self.song_name.setText("------------------")
        self.song_changed_ = True
        QTest.qWait(2000)
        self.song_changed_ = False
        self.song_current_sec = 0
        self.song_path = self.song_list[song_index][0]
        self.song_name.setText(self.song_list[song_index][1])
        self.wave_process()
        self.get_all_data()

    # paint event to draw bar spectrum
    def paintEvent(self, event):
        # creating and setting painter 
        painter = QPainter(self)
        painter.setRenderHint(QPainter.HighQualityAntialiasing, True)
        painter.setBrush(QBrush(Qt.black))

        painter.drawRect(QRect(0, 0, self.screen_width, self.screen_height)) # Background

        # color gradiant
        gradiant = QLinearGradient(QPoint(self.screen_width, self.screen_height), QPoint(self.screen_width, 50))
        gradiant.setColorAt(0.9, Qt.red)
        gradiant.setColorAt(0.6, Qt.yellow)
        gradiant.setColorAt(0.1, Qt.blue)

        painter.setBrush(QBrush(gradiant))
        try:
            painter.drawRects(self.bar_total[self.song_current_sec]) # Drawing bars
        except:
            pass

        # close painter
        painter.end()

    # Method to update bar value
    def change_value(self):
        self.update()
        pos = self.player.position()
        if self.song_current_sec < len(self.bar_total)-1:
            self.song_current_sec = pos//100

# creating QApplication
def load():
    app = QApplication(sys.argv)  # Creating App
    audio_spectrum = AudioSpectrum()
    audio_spectrum.show()
    app.exec()   # exit from app

# main code
if __name__ == '__main__':
    load()