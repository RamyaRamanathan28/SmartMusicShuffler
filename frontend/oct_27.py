import os
import glob
import threading
import queue
import time
import tkinter.messagebox
from tkinter import *
from tkinter import filedialog

from tkinter import ttk
from ttkthemes import themed_tk as tk

import mutagen
from mutagen.mp3 import MP3
from mutagen.easyid3 import EasyID3


from pygame import mixer

root = tk.ThemedTk()
#print (root.get_themes())                 # Returns a list of all themes that can be set
'''
['classic', 'ubuntu', 'keramik_alt', 'elegance', 'equilux', 'black', 'default', 'arc', 'smog', 'radiance', 'itft1', 'plastik', 'aquativo', 'keramik', 'clam', 'winxpblue', 'clearlooks', 'kroc', 'blue', 'alt']
'''
root.set_theme("plastik")         # Sets an available theme

# Fonts - Arial (corresponds to Helvetica), Courier New (Courier), Comic Sans MS, Fixedsys,
# MS Sans Serif, MS Serif, Symbol, System, Times New Roman (Times), and Verdana
#
# Styles - normal, bold, roman, italic, underline, and overstrike.

statusbar = ttk.Label(root, text="Welcome to Melody", relief=SUNKEN, anchor=W, font='Times 10 italic')
statusbar.pack(side=BOTTOM, fill=X)

# Create the menubar
menubar = Menu(root)
root.config(menu=menubar)

# Create the submenu

subMenu = Menu(menubar, tearoff=0)

playlist = []


# playlist - contains the full path + filename
# playlistbox - contains just the filename
# Fullpath + filename is required to play the music inside play_music load function

def browse_file():
    global filename_path
    filename_path = filedialog.askdirectory()
    x = ''
    for x in glob.glob(filename_path + '/**/*.mp3'):
        add_to_playlist(x)

    print ('PLAYLIST DONE')
    print (x)
    mixer.music.queue(x)


def add_to_playlist(filename_path):

    print ()
    print (filename_path)
    print ()
    filename = os.path.basename(filename_path)
    index = 0
    playlistbox.insert(index, filename)
    playlist.insert(index, filename_path)
    index += 1


menubar.add_cascade(label="File", menu=subMenu)
subMenu.add_command(label="Open", command=browse_file)
subMenu.add_command(label="Exit", command=root.destroy)

mixer.init()  # initializing the mixer

root.title("Melody")
#root.iconphoto(True, 'images/melody.ico')

# Root Window - StatusBar, LeftFrame, RightFrame
# LeftFrame - The listbox (playlist)
# RightFrame - TopFrame,MiddleFrame and the BottomFrame

leftframe = Frame(root)
leftframe.pack(side=LEFT, padx=30, pady=30)

playlistbox = Listbox(leftframe)
playlistbox.pack()

addBtn = ttk.Button(leftframe, text="+ Add", command=browse_file)
addBtn.pack(side=LEFT)


def del_song():
    selected_song = playlistbox.curselection()
    selected_song = int(selected_song[0])
    playlistbox.delete(selected_song)
    playlist.pop(selected_song)


delBtn = ttk.Button(leftframe, text="- Del", command=del_song)
delBtn.pack(side=LEFT)

rightframe = Frame(root)
rightframe.pack(pady=30)

topframe = Frame(rightframe)
topframe.pack()

bottomframe = Frame(rightframe)
bottomframe.pack()

titlelabel = ttk.Label(topframe, text = '')
titlelabel.pack(pady = 5)

artistlabel = ttk.Label(topframe, text = '')
artistlabel.pack(pady = 5)

currenttimelabel = ttk.Label(topframe, text='--:-- / --:--', relief=GROOVE)
currenttimelabel.pack()


song_run_time = 0
COMPLETED = False

def show_details(play_song):
    file_data = os.path.splitext(play_song)

    if file_data[1] == '.mp3':
        audio = MP3(play_song)
        total_length = audio.info.length
    else:
        a = mixer.Sound(play_song)
        total_length = a.get_length()

    audio = EasyID3(play_song)
    title = audio['title'][0]
    artist = audio['artist'][0]
    album = audio['album'][0]
    print (title, artist, album)

    # div - total_length/60, mod - total_length % 60
    mins, secs = divmod(total_length, 60)
    mins = round(mins)
    secs = round(secs)
    titlelabel['text'] = title
    artistlabel['text'] = artist + ' - ' + album

    t1 = threading.Thread(target=start_count, args=(total_length,))
    t1.start()


def start_count(t):
    global paused
    # mixer.music.get_busy(): - Returns FALSE when we press the stop button (music stop playing)
    # Continue - Ignores all of the statements below it. We check if music is paused or not.
    current_time = 0
    mins, secs = divmod(t, 60)
    mins = round(mins)
    secs = round(secs)
    timeformattotal = '{:02d}:{:02d}'.format(mins, secs)
    print ('total time : ', t)
    while current_time <= t and mixer.music.get_busy():
        if paused:
            continue
        else:
            mins, secs = divmod(current_time, 60)
            mins = round(mins)
            secs = round(secs)
            timeformat = '{:02d}:{:02d}'.format(mins, secs)
            currenttimelabel['text'] = timeformat + ' / ' + timeformattotal
            time.sleep(1)
            current_time += 1
            if current_time<=25:
                global song_run_time
                song_run_time = current_time

    print ('current time : ', current_time)
   
    if current_time>=int(t):
            global COMPLETED
            COMPLETED = True
            print ('completed')


def play_music():
    global paused
    if paused:
        mixer.music.unpause()
        statusbar['text'] = "Music Resumed"
        paused = FALSE
    else:
#        try:
                stop_music()
                time.sleep(1)
                global COMPLETED
                if COMPLETED == False:
                    print ('box')
                    selected_song = playlistbox.curselection()
                    selected_song = int(selected_song[0])
                COMPLETED = False
                play_it = playlist[selected_song]
                print ()
                mixer.music.load(play_it)
                mixer.music.play()
                statusbar['text'] = "Playing music" + ' - ' + os.path.basename(play_it)
                print ('showing details')
                show_details(play_it)
                if COMPLETED == True:
                    '''
                    selected_song = get_next_song(selected_song)    #function needs to write next song to DB or whatever
                    '''
                    selected_song = selected_song + 1
                    print ('song completed')
'''
        except:
            tkinter.messagebox.showerror('File not found', 'Melody could not find the file. Please check again.')
'''

def stop_music():
    mixer.music.stop()
    statusbar['text'] = "Music Stopped"
    global song_run_time
    print ('Stopped')
    print (song_run_time)


paused = FALSE


def pause_music():
    global paused
    paused = TRUE
    mixer.music.pause()
    statusbar['text'] = "Music Paused"


def skip_music():
    mixer.music.stop()
    statusbar['text'] = "Music Skipped"


def set_vol(val):
    volume = float(val) / 100
    mixer.music.set_volume(volume)
    # set_volume of mixer takes value only from 0 to 1. Example - 0, 0.1,0.55,0.54.0.99,1


muted = FALSE


def mute_music():
    global muted
    if muted:  # Unmute the music
        mixer.music.set_volume(0.7)
        volumeBtn.configure(image=volumePhoto)
        scale.set(70)
        muted = FALSE
    else:  # mute the music
        mixer.music.set_volume(0)
        volumeBtn.configure(image=mutePhoto)
        scale.set(0)
        muted = TRUE


middleframe = Frame(rightframe)
middleframe.pack(pady=30, padx=30)

playPhoto = PhotoImage(file='images/play.png')
playBtn = ttk.Button(middleframe, image=playPhoto, command=play_music)
playBtn.grid(row=0, column=0, padx=10)

pausePhoto = PhotoImage(file='images/pause.png')
pauseBtn = ttk.Button(middleframe, image=pausePhoto, command=pause_music)
pauseBtn.grid(row=0, column=1, padx=10)

stopPhoto = PhotoImage(file='images/stop.png')
stopBtn = ttk.Button(middleframe, image=stopPhoto, command=stop_music)
stopBtn.grid(row=0, column=2, padx=10)

# Bottom Frame for volume, rewind, mute etc.

bottomframe = Frame(rightframe)
bottomframe.pack()

nextPhoto = PhotoImage(file='images/next.png')
nextBtn = ttk.Button(bottomframe, image=nextPhoto, command=skip_music)
nextBtn.grid(row=0, column=0, padx = 10)    

mutePhoto = PhotoImage(file='images/mute.png')
volumePhoto = PhotoImage(file='images/volume.png')
volumeBtn = ttk.Button(bottomframe, image=volumePhoto, command=mute_music)
volumeBtn.config()
volumeBtn.grid(row=0, column=1)

scale = ttk.Scale(bottomframe, from_=0, to=100, orient=HORIZONTAL, command=set_vol)
scale.set(70)  # implement the default value of scale when music player starts
mixer.music.set_volume(0.7)
scale.grid(row=0, column=2, pady=15, padx=30)


def on_closing():
    stop_music()
    root.destroy()


root.protocol("WM_DELETE_WINDOW", on_closing)
root.mainloop()
