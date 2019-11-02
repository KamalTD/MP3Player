"""
Author : Mahmoud Kamal

        2/11/2019

        MP3 player

* Python Version:
    - Python 3.7.5
* Third Party Modules :
    - PyQt 5
    - pygame
    - mutagen
    - qtmodern


"""





import sys
from PyQt5.QtWidgets import *
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QDockWidget
from PyQt5.QtCore import QSize
from PyQt5.QtCore import Qt,QTimer
from mutagen.mp3 import MP3
import random
import os
from pygame import mixer
import qtmodern.styles
import qtmodern.windows


#======================================== Global Variables Definition

mixer.init()
music_list = []
mute = False
play = False
count = 0
song_length = 0
current_song=0
current_song_name = ""
pause = False





class player(QMainWindow):
    # Main Player Class

    def __init__(self):
        super(player, self).__init__()
        self.setWindowTitle("Kamal MP3 Player")
        self.setGeometry(450,150,480,700)
        self.UI()
        self.show()


    def UI(self):
        # Build UI GUI and Layout
        self.widgets()
        self.layout()


    def widgets(self):
        # Setup the Widgets for UI

            #================================ Setup Dock Widgets =======================================================


        self.dock_list = QDockWidget()
        self.dock_control = QDockWidget()
        self.addDockWidget(Qt.DockWidgetArea(1), self.dock_control)
        self.addDockWidget(Qt.DockWidgetArea(1), self.dock_list)
        self.dock_list.setWindowTitle(QApplication.translate("self", "Music List", None))
        self.dock_control.setWindowTitle(QApplication.translate("self", "Control Pad", None))

            # =============================== Setup Menu Bar and Menus =================================================

        self.menu = self.menuBar()
        self.file = self.menu.addMenu("File")
        self.control_pad_show = QAction("Show Control Pad")
        self.control_pad_show.setShortcut("Shift+C")
        self.control_pad_show.triggered.connect(self.show_control_pad)
        self.file.addAction(self.control_pad_show)

        self.music_list_show = QAction("Show Music List")
        self.music_list_show.setShortcut("Shift+M")
        self.music_list_show.triggered.connect(self.show_music_list)
        self.file.addAction(self.music_list_show)

            # =============================== Setup all Widgets (Buttons , List ) ======================================

        # Music Progress Bar
        self.progress_bar = QSlider(Qt.Horizontal)
        self.progress_bar.sliderPressed.connect(self.change_time_slider)
        self.progress_bar.sliderMoved.connect(self.slider_released)
        self.progress_bar.sliderReleased.connect(self.slider_released)

        # Add song Btton
        self.add_button = QToolButton()
        self.add_button.setIcon(QIcon("icons/23937_52032_add_gtk.png"))
        self.add_button.setIconSize(QSize(48,48))
        self.add_button.setToolTip("Add a song")
        self.add_button.clicked.connect(self.add_song)

        # Shuffle Button
        self.shuffle_button = QToolButton()
        self.shuffle_button.setIcon(QIcon("icons/shuffle.png"))
        self.shuffle_button.setIconSize(QSize(48, 48))
        self.shuffle_button.setToolTip("Shuffle")
        self.shuffle_button.clicked.connect(self.shuffle_song_list)

        # Previous Button (Play Previous song)
        self.previous_button = QToolButton()
        self.previous_button.setIcon(QIcon("icons/backward.png"))
        self.previous_button.setIconSize(QSize(48, 48))
        self.previous_button.setToolTip("Play Previous")
        self.previous_button.clicked.connect(self.play_previous)

        # Play Button
        self.play_button = QToolButton()
        self.play_button.setIcon(QIcon("icons/play.png"))
        self.play_button.setIconSize(QSize(64, 64))
        self.play_button.setToolTip("Play")
        self.play_button.clicked.connect(self.play_song)

        # Pause Button
        self.pause_button = QToolButton()
        self.pause_button.setIcon(QIcon("icons/pause.png"))
        self.pause_button.setIconSize(QSize(64, 64))
        self.pause_button.setToolTip("Pause")
        self.pause_button.clicked.connect(self.pause_song)

        # Forward Button (Play Next Song)
        self.forward_button = QToolButton()
        self.forward_button.setIcon(QIcon("icons/forwards.png"))
        self.forward_button.setIconSize(QSize(48, 48))
        self.forward_button.setToolTip("Play Next")
        self.forward_button.clicked.connect(self.play_forward)

        # Mute Button
        self.mute_button = QToolButton()
        self.mute_button.setIcon(QIcon("icons/volume-adjustment.png"))
        self.mute_button.setIconSize(QSize(24, 24))
        self.mute_button.setToolTip("Mute")
        self.mute_button.clicked.connect(self.set_mute)

        # Volume Slider
        self.volume_slider = QSlider(Qt.Horizontal)
        self.volume_slider.setToolTip("Volume")
        self.volume_slider.setMaximumWidth(50)
        self.volume_slider.setMinimumWidth(50)
        self.volume_slider.setMaximum(100)
        self.volume_slider.setValue(70)
        self.volume_slider.valueChanged.connect(self.volume_change)
        mixer.music.set_volume(0.7)

        # Music List
        self.song_list = QListWidget()
        self.song_list.doubleClicked.connect(self.play_song)

        # Seek Timer
        self.timer = QTimer()
        self.timer.setInterval(1000)
        self.timer.timeout.connect(self.update_progress)
        self.timer.stop()

        # Song Time Labels
        self.song_timer_label = QLabel("00:00")
        self.song_length_label = QLabel("/ 00:00")



    def layout(self):

        #==================================== Setup Main Layouts =======================================================

        self.main_layout = QVBoxLayout()
        self.top_mainlayout = QVBoxLayout()
        self.top_group_box = QGroupBox(self)
        self.top_group_box.setMaximumHeight(150)
        self.top_layout = QHBoxLayout()
        self.middle_layout = QHBoxLayout()

        #==================================== Build Middle Layout=======================================================
        self.middle_layout.addStretch()
        self.middle_layout.addWidget(self.add_button)
        self.middle_layout.addWidget(self.shuffle_button)
        self.middle_layout.addWidget(self.previous_button)
        self.middle_layout.addWidget(self.play_button)
        self.middle_layout.addWidget(self.pause_button)
        self.middle_layout.addWidget(self.forward_button)
        self.middle_layout.addWidget(self.volume_slider)
        self.middle_layout.addWidget(self.mute_button)
        self.middle_layout.addStretch()

        # ================================ Build Top Layout=============================================================

        self.top_layout.addWidget(self.progress_bar)
        self.top_layout.addWidget(self.song_timer_label)
        self.top_layout.addWidget(self.song_length_label)


        #================================ Add Top layout and Middle Layout to Top main Layout ==========================

        self.top_mainlayout.addLayout(self.top_layout)
        self.top_mainlayout.addLayout(self.middle_layout)



        #=============================== Add Top main Layout to Top Group Box ==========================================

        self.top_group_box.setLayout(self.top_mainlayout)

        # ================================ Add Music List and Top Groub Box to Dock Widgets ============================

        self.dock_list.setWidget(self.song_list)

        self.dock_control.setWidget(self.top_group_box)



    def add_song(self):

        # This Function is To add Music To Music List

        song_path = QFileDialog.getOpenFileNames(self,"Add Song","C:/Users/Mahmoud/Downloads/Music","Sound Files(*.mp3)") # Open FIle Dialog to import Music Files

        for file in song_path[0]:

            file_name = os.path.basename(file)

            item = QListWidgetItem(str(file_name))

            song_length = MP3(file)

            song_length = song_length.info.length # Get Music Track Length in seconds

            min,sec = divmod(song_length,60) #Convert Seconds To Minuts and Seconds

            self.song_list.addItem("{:02d}:{:02d} | ".format(round(min),round(sec) ) + item.text() ) # Add item to Music List

            music_list.append("{:02d}:{:02d} | ".format(round(min),round(sec) ) + file ) # This Music List to add Full Music File Path and Track Length EX (04:35 | C:\Music_Folder\Amr-diab\amr diab - tamally maak.mp3


    def shuffle_song_list(self):

        # Shuffle Music List

        global current_song
        global current_song_name

        random.shuffle(music_list)

        self.song_list.clear() # clear music list

        for song in music_list:

            get_song = song.split(" | ")

            get_current_song = get_song[1] # Get the full path of th song EX :: C:\Music_Folder\Amr-diab\amr diab - tamally maak.mp3

            self.song_list.addItem(get_song[0] + " | " + os.path.basename(get_current_song)) # Add the track name and length to music list

    def play_song(self):
        # Play Current Selected Track

        global song_length
        global play
        global count
        global index
        global current_song
        global current_song_name

        current_song = self.song_list.currentRow() # Get The Current Selected Track ID

        self.song_list.setCurrentRow(current_song)

        try:
            current_song_name = self.song_list.currentItem().text()
            if play == False:                                                                                               # Main Idea it to Check If playing or not
                get_current_song = music_list[current_song]                                                                 #  and Get the Current Selected Song From Music List By Id
                get_current_song = get_current_song.split(" | ")                                                            #  Split Item To get full path of current song to play
                get_current_song = get_current_song[1]
                mixer.music.load(get_current_song)#music_list[current_song])                                                # Load The file to pygame.mixer

                mixer.music.play()                                                                                          # and play It

                play = True

                self.timer.start()

                self.play_button.setIcon(QIcon("icons/stop.png"))

                count = 0

                sound = MP3(str(get_current_song))
                song_length = sound.info.length
                print("Song Length" , song_length)
                song_length = round(song_length)
                self.progress_bar.setMaximum(song_length)
                self.progress_bar.setValue(0)
                min, sec = divmod(song_length, 60)
                self.song_length_label.setText("/ {:02d}:{:02d}".format(min, sec))

            else:
                mixer.music.pause()
                play = False
                self.timer.stop()
                self.play_button.setIcon(QIcon("icons/play.png"))
                self.song_timer_label.setText("00:00")
                self.progress_bar.setValue(0)
        except:

            pass


    def volume_change(self):
        # Volume Slider
        global mute

        self.volume = self.volume_slider.value()/100
        mixer.music.set_volume(self.volume)

        if self.volume_slider.value() <=0:
            self.mute_button.setIcon(QIcon("icons/mute.png"))
            self.mute_button.setToolTip("UnMute")
            mute = True

        else:
            self.mute_button.setIcon(QIcon("icons/volume-adjustment.png"))
            self.mute_button.setToolTip("Mute")
            mute=False

    def set_mute(self):
        # Mute and UnMute
        global mute
        if mute==False:
            mixer.music.set_volume(0.0)
            mute = True
            self.mute_button.setIcon(QIcon("icons/mute.png"))
            self.mute_button.setToolTip("UnMute")
            self.volume_slider.setValue(0.0)
        elif mute==True:
            mixer.music.set_volume(self.volume)
            mute=False
            self.mute_button.setIcon(QIcon("icons/volume-adjustment.png"))
            self.mute_button.setToolTip("Mute")
            self.volume_slider.setValue(70)

    def update_progress(self):
        #Update Progress Slider
        global count
        global song_length
        global play
        count += 1
        self.progress_bar.setValue(count)
        min,sec = divmod(count,60)

        self.song_timer_label.setText("{:02d}:{:02d}".format(round(min),round(sec) )) # Update Track Time
        if count >= song_length: # Rest all After Track Ended
            self.timer.stop()
            self.play_button.setIcon(QIcon("icons/play.png"))
            self.pause_button.setIcon(QIcon("icons/pause.png"))
            count = 0
            self.progress_bar.setValue(0)
            self.play_forward()


    def play_forward(self):
        # PLay Next Track
        # Its almost the same as Play Function Except I Increment the current song ID
        global song_length
        global play
        global count
        global index
        global current_song
        global current_song_name

        current_song = self.song_list.currentRow()
        current_song += 1
        self.song_list.setCurrentRow(current_song)


        try:
            current_song_name = self.song_list.currentItem().text()
            if play == True:
                get_current_song = music_list[current_song]
                get_current_song = get_current_song.split(" | ")
                get_current_song = get_current_song[1]
                mixer.music.load(get_current_song)

                mixer.music.play()
                #play = True
                self.timer.start()
                self.play_button.setIcon(QIcon("icons/stop.png"))
                self.pause_button.setIcon(QIcon("icons/pause.png"))
                count = 0
                sound = MP3(str(get_current_song))
                song_length = sound.info.length
                song_length = round(song_length)
                self.progress_bar.setMaximum(song_length)
                self.progress_bar.setValue(0)
                min,sec = divmod(song_length,60)
                self.song_length_label.setText("/ {:02d}:{:02d}".format(min,sec))

            else:
                mixer.music.pause()
                play = False
                self.timer.stop()
                self.play_button.setIcon(QIcon("icons/play.png"))
        except:

            pass

    def play_previous(self):
        # Playe Previous Song in the Music List
        # Again Its almost the same as Play Function Except I decrement the current song ID
        global song_length
        global play
        global count
        global index
        global current_song
        global current_song_name

        current_song = self.song_list.currentRow()
        if current_song > 0:
            current_song -= 1
        else:
            current_song = 0
        self.song_list.setCurrentRow(current_song)


        try:
            current_song_name = self.song_list.currentItem().text()
            if play == True:
                get_current_song = music_list[current_song]
                get_current_song = get_current_song.split(" | ")
                get_current_song = get_current_song[1]
                mixer.music.load(get_current_song)#music_list[current_song])
                mixer.music.play()
                #play = True
                self.timer.start()
                self.play_button.setIcon(QIcon("icons/stop.png"))
                self.pause_button.setIcon(QIcon("icons/pause.png"))
                count = 0
                sound = MP3(str(get_current_song))
                song_length = sound.info.length
                song_length = round(song_length)
                self.progress_bar.setMaximum(song_length)
                self.progress_bar.setValue(0)
                min,sec = divmod(song_length,60)
                self.song_length_label.setText("/ {:02d}:{:02d}".format(min,sec))

            else:
                mixer.music.pause()
                play = False
                self.timer.stop()
                self.play_button.setIcon(QIcon("icons/play.png"))
        except:

            pass
    def pause_song(self):
        # Pause Current Playing Song
        global pause
        if play == True:
            if pause==False:

                self.timer.stop()
                mixer.music.pause()
                self.pause_button.setIcon(QIcon("icons/pause_down.png"))

                pause = True

            else:

                self.timer.start()
                mixer.music.unpause()
                self.pause_button.setIcon(QIcon("icons/pause.png"))
                self.play_button.setIcon(QIcon("icons/stop.png"))

                pause=False
        else:
            pass

    def change_time_slider(self):
        # Stop The timer
        self.timer.stop()


    def slider_released(self):
        # after the user change seek slider , it will Set position of the track relative to the seek slider
        try:
            global count
            global song_length
            self.change_time_slider()
            new_time_value = self.progress_bar.value()

            count = new_time_value

            mixer.music.rewind()

            mixer.music.set_pos(count)


            self.timer.start()

        except:
            pass



    def show_control_pad(self):
        # SHow Dock of Control Pad
        self.dock_control.show()


    def show_music_list(self):
        #SHow Dock of Music List
        self.dock_list.show()
def main():

    app = QApplication(sys.argv)

    window = player()

    qtmodern.styles.dark(app)

    mw = qtmodern.windows.ModernWindow(window) # apply style to window

    mw.show()

    sys.exit(app.exec_())

if __name__ == "__main__":
    main()