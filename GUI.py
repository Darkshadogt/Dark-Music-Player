from tkinter import *
import customtkinter as ctk
from PIL import Image
from tkinter import filedialog
from tkinter import messagebox
import threading
import json
import os
import pygame
import music_player

ctk.set_default_color_theme("dark-blue")
ctk.set_appearance_mode("dark")

#Creating a child class of customtkinter
class Interface(ctk.CTk):
    def __init__(self):
        super().__init__()
        pygame.init()
        pygame.mixer.pre_init(44100, -16, 2, 2048)
        pygame.mixer.init()
        
        #Creating variables for the images of the buttons
        self.play_button = ctk.CTkImage(Image.open("Play_Button.png"))
        self.pause_button = ctk.CTkImage(Image.open("Pause_Button.png"))
        self.left_button = ctk.CTkImage(Image.open("Left_Button.png"))
        self.right_button = ctk.CTkImage(Image.open("Right_Button.png"))
        self.search_button = ctk.CTkImage(Image.open("Search_Button.png"))
        self.settings_button = ctk.CTkImage(Image.open("Settings_Button.png"))
        self.help_button = ctk.CTkImage(Image.open("Help_Button.png"))

        #User's playlist
        self.playlist_name = []
        self.playlists = {}
        self.playlist_song = []
        self.current_song = None
        
        #Variable to keep track of the current playlist selection
        self.playlist_selection = ctk.StringVar()

        #Variable to keep track of the current song selection
        self.song_selection = StringVar()

        #Variable to keep track of the slider
        self.slider = ctk.IntVar()
        
        #Variable to keep track of the end time of current song
        self.slider_end_time = ctk.StringVar()
        
        #Variable to keep track of the current time of the current song
        self.slider_current_time = ctk.StringVar()
        
        #Variable to keep track of user search
        self.search_input = ctk.StringVar()
        self.search_input.trace("w", self.reset_middlebox)
        
        #Updates the song list box
        self.change_middle_box = False
        
        #If user searches for a song
        self.user_song_search = False
        
        #Checks if repeat is on or off
        self.repeat_on = False

        #Checks if shuffle is on or off
        self.shuffle_on = False

        #Whether the music is playing or not
        self.playing = False
        self.paused = False
        
        #Used to set the end events of a song
        self.song_ended = pygame.USEREVENT+1
        pygame.mixer.music.set_endevent(self.song_ended)

        #If there is data in the file, it loads them
        if os.path.getsize("user_playlist.py") != 0:
            with open("user_playlist.py") as user_file:
                data = user_file.read()
                self.playlists = json.loads(data)
                self.playlist_name = list(self.playlists.keys())

        if len(self.playlists) != 0:
            self.playlist_selection.set(self.playlist_name[0])

        self.playlist_selection.trace("w", self.current_playlist_label_change)
    
    #Settings for the window
    def window(self):
        self.title("Dark Music Player")
        self.geometry("700x575")
        self.resizable("False", "False")

    #Settings for the top
    def top(self):
        check_search = self.register(self.check_input)
        
        search_bar = ctk.CTkEntry(self, width=300, placeholder_text="Search for a song", validate="key", validatecommand=(check_search, "%P"), border_color=["#3a7ebf", "#1f538d"], textvariable=self.search_input)
        search_bar.place(x=185, y=30)

        search_button = ctk.CTkButton(self, image=self.search_button, text="", width=30, command=self.search_song)
        search_button.place(x=495, y=30)
    
    #Settings for the middle
    def middle(self):
        
        self.middlebox = Listbox(self, width=100, height=19, bg="gray15", font=("Arial", 15), selectmode=SINGLE, listvariable=self.song_selection, selectbackground="white")
        self.middlebox.place(x=0, y=75)
        
        if self.check_any_song() == True:
            if self.user_song_search == True and self.search_input.get() != "":
                #Deletes everything
                self.middlebox.delete(0, END)
                for y in self.playlists[self.playlist_selection.get()]:
                    #Searches for the song and insert it in the box
                    if self.search_input.get() in y[0]:
                        self.middlebox.insert(END, y[0])
                self.user_song_search = False
            else:
                self.middlebox.delete(0, END)
                for song in self.playlists[self.playlist_selection.get()]:
                    self.middlebox.insert(END, song[0])

    #Settings for the bottom bar
    def bottom_bar(self):
        
        global play_button
        #Play button for the user to play their songs
        play_button = ctk.CTkButton(self, image=self.play_button, text="", width=100, command=self.play_songs)
        play_button.place(x=300, y=500)

        left_button = ctk.CTkButton(self, image=self.left_button, text="", width=100, command=self.play_last)
        left_button.place(x=180, y=500)

        right_button = ctk.CTkButton(self, image=self.right_button, text="", width=100, command=self.play_next)
        right_button.place(x=420, y=500)

        settings_button = ctk.CTkButton(self, image=self.settings_button, text="", width=50, command=self.settings_window)
        settings_button.place(x=650, y=545)
        
        shuffle_button = ctk.CTkSwitch(self, width=50, text="Shuffle", text_color="#3a7ebf", font=("Arial", 15, "bold"), onvalue="on", offvalue="off", command=self.turn_shuffle_on)
        shuffle_button.place(x=0, y=435)

        repeat_button = ctk.CTkSwitch(self, width=50, text="Repeat", text_color="#3a7ebf", font=("Arial", 15, "bold"), onvalue="on", offvalue="off", command=self.turn_repeat_on)
        repeat_button.place(x=605, y=435)

        #Slider to display the time of the song playing
        self.time_slider = ctk.CTkSlider(self, from_=0, to=100, width=425, variable=self.slider, command=self.drag_slider)
        self.time_slider.place(x=140, y=440)
        self.slider.set(0)
        
        slider_current_time = ctk.CTkLabel(self, text="", text_color="#3a7ebf", font=("Arial", 15, "bold"), textvariable=self.slider_current_time)
        slider_current_time.place(x=145, y=458)
        
        slider_end_time = ctk.CTkLabel(self, text="", text_color="#3a7ebf", font=("Arial", 15, "bold"), textvariable=self.slider_end_time)
        slider_end_time.place(x=539, y=458)
        
        help_button = ctk.CTkButton(self, width=50, image=self.help_button, text="", command=self.help_page)
        help_button.place(x=0, y=545)
    
    #Used to check the entry for the search bar
    def check_input(self, input):
        if len(input) < 39:
            return(True)
        else:
            return(False)
    
    #Plays the song
    def play_songs(self):
        if self.check_any_song() == True:
            #Threads to play the music
            play_music = threading.Thread(target=music_player.MusicPlayer.play_song, args=(self,))
            pause_music = threading.Thread(target=music_player.MusicPlayer.pause_song, args=(self,))
            
            #If song isn't playing and there are songs in the playlist, it plays
            if self.playing == False:
                play_music.start()
                play_button.configure(image=self.pause_button)
            #If song is playing, it pauses the song
            else:
                pause_music.start()
                play_button.configure(image=self.play_button)
        else:
            messagebox.showerror("Empty Song List", "Please add songs before playing")
    
    #Plays the next song
    def play_next(self):
        music_player.MusicPlayer.play_next_song(self)
    
    #Checks if there are songs in any playlist
    def check_any_song(self):
        song = False
        if len(self.playlists) > 0:
            for x in self.playlists:
                if len(self.playlists[x]) > 0:
                    song = True
        return(song)
    
    #Plays the song before the current one
    def play_last(self):
        music_player.MusicPlayer.play_last_song(self)
    
    #Searches the song user asked for
    def search_song(self):
        #Calls the function to change the song list box
        self.user_song_search = True
        self.middle()
    
    #If the entry is clear, songs in playlist reappears
    def reset_middlebox(self, *args):
        if self.search_input.get() == "":
            self.middle()
    
    #Checking whether the repeat is on or off
    def turn_repeat_on(self):
        if self.repeat_on == False:
            self.repeat_on = True
        else:
            self.repeat_on = False
    
    #Checks whether the shuffle is on or off
    def turn_shuffle_on(self):
        if self.shuffle_on == False:
            self.shuffle_on = True
        else:
            self.shuffle_on = False

    #Checks if the song ended or not
    def check_song_status(self):
        for event in pygame.event.get():
            if event.type == self.song_ended:
                music_player.MusicPlayer.play_next_song(self)
                
        #Keeps checking if song ended or not
        check_end = threading.Thread(target=self.after, args=(100, self.check_song_status))
        check_end.start()
    
    #Changes the position of the song according to the timer user dragged
    def drag_slider(self, time):
        #Check if songs exist
        if self.check_any_song() == True:
            music_player.MusicPlayer.set_song_timer(self, time)
    
    #Displays how to use the music player
    def help_page(self):
        #Creates the new window
        help_window = ctk.CTkToplevel(self)
        help_window.title("Help")
        help_window.geometry("400x300")
        help_window.resizable(False, False)

        help_textbox = ctk.CTkTextbox(help_window, width=400, height=290)
        help_textbox.place(x=0, y=10)

        help_textbox.insert(END, "Short explanation on how to use the music player:\n")
        help_textbox.insert(END, "-Inside the settings button, you can select, add, and remove playlists to songs.\n")
        help_textbox.insert(END, "-In order to add a song, you need to add a playlist to add the song into.\n")
        help_textbox.insert(END, "-Adding a song will open a file dialog which asks you to select an music file to play.\n")
        help_textbox.insert(END, "-There are buttons you can use.\n")
        help_textbox.insert(END, "-There are currently, shuffle, repeat, play, play last song, and play next song.\n")
        help_textbox.insert(END, "-The box in the middle displays the songs you have in your current playlist.\n")
        help_textbox.insert(END, "-The search button on the top allows you to see which song is in your playlist.\n")
        help_textbox.insert(END, "-There is also a library menu in the settings window which shows you all the songs currently in all the playlists.\n")

        help_textbox.configure(state=DISABLED)
    
    #Popup window for settings
    def settings_window(self):
        
        #Made copies of the playlists and song
        global playlist_name_copy
        playlist_name_copy = self.playlist_name.copy()
        global playlists_copy
        playlists_copy = self.playlists.copy()
        global playlist_song_copy
        playlist_song_copy = self.playlist_song.copy()
        
        #Creates another window for settings
        global setting_window
        setting_window = ctk.CTkToplevel(self)
        setting_window.title("Settings")
        setting_window.geometry("320x320")
        setting_window.resizable(False, False)
        
        tab = ctk.CTkTabview(setting_window, width=310, height=310)
        tab.place(x=5, y=5)

        playlist_tab = tab.add("Playlists")
        song_tab = tab.add("Songs")
        
        current_playlist_label = ctk.CTkLabel(playlist_tab, text="Current playlist: ", text_color="#3a7ebf", font=("Arial", 15, "bold"))
        current_playlist_label.place(x=5, y=20)

        select_playlist_label = ctk.CTkLabel(playlist_tab, text="Select a playlist: ", text_color="#3a7ebf", font=("Arial", 15, "bold"))
        select_playlist_label.place(x=5, y=60)
        
        global current_playlist_word_label
        current_playlist_word_label = ctk.CTkLabel(playlist_tab, text=self.playlist_selection.get(), width=150, text_color="#3a7ebf", font=("Arial", 15, "bold"), anchor=CENTER)
        current_playlist_word_label.place(x=125, y=20)
        
        global play_list
        play_list = ctk.CTkOptionMenu(playlist_tab, values=self.playlist_name, width=175, variable=self.playlist_selection, anchor=CENTER, text_color="#3a7ebf", font=("Arial", 15, "bold"), dynamic_resizing=FALSE, command=self.update_middle_box)
        play_list.place(x=125, y=60)

        add_playlist = ctk.CTkButton(playlist_tab, command=self.add_playlist, text="Add Playlist")
        add_playlist.place(x=5, y=120)

        remove_playlist = ctk.CTkButton(playlist_tab, command=self.remove_playlist, text="Remove Playlist")
        remove_playlist.place(x=155, y=120)
        
        current_song_label = ctk.CTkLabel(song_tab, text="Current song: ", text_color="#3a7ebf", font=("Arial", 15, "bold"))
        current_song_label.place(x=5, y=20)
        
        self.current_song_word_label = ctk.CTkLabel(song_tab, width=150, text="", text_color="#3a7ebf", font=("Arial", 15, "bold"), anchor=CENTER)
        self.current_song_word_label.place(x=125, y=20)
        
        add_song = ctk.CTkButton(song_tab, text="Add Song", command=self.add_song)
        add_song.place(x=5, y=120)

        remove_song = ctk.CTkButton(song_tab, text="Remove Song", command=self.remove_song)
        remove_song.place(x=155, y=120)

        ok_button = ctk.CTkButton(setting_window, text="Ok", command=self.update_changes)
        ok_button.place(x=15, y=215)

        cancel_button = ctk.CTkButton(setting_window, text="Cancel", command=self.cancel_changes)
        cancel_button.place(x=165, y=215)

    #Command to add a playlist
    def add_playlist(self):
        
        #User inputs the name of the playlist to add
        add_play_list = ctk.CTkInputDialog(text="Name of the playlist to add", title="Add Playlist")
        playlist_name = add_play_list.get_input()
        if playlist_name != "":
            if playlist_name in playlist_name_copy:
                messagebox.showerror("Error", "Current name is already being used. Please select a different name!")
            elif len(self.playlist_name) == 0:
                playlist_name_copy.append(playlist_name)
                playlists_copy[playlist_name] = []
                self.playlist_selection.set(playlist_name)
            elif len(playlist_name) > 15:
                messagebox.showerror("Error", "Please select a shorter name")
            else:
                #Adds the playlist
                playlist_name_copy.append(playlist_name)
                playlists_copy[playlist_name] = []
                
                #Changes the value of the playlist
                play_list.configure(values=playlist_name_copy)
        else:
            #User can't input blank for the name of the playlist
            messagebox.showerror("Error", "Please add a correct for the playlist")
    
    #Command to remove a playlist
    def remove_playlist(self):
       
        #User inputs the name of the playlist to delete
        remove_play_list = ctk.CTkInputDialog(text="Name of the playlist to remove", title="Remove Playlist")
        remove_play_list = remove_play_list.get_input()
        if remove_play_list in playlist_name_copy:
            #Deletes the playlist
            playlist_name_copy.remove(remove_play_list)
            del playlists_copy[remove_play_list]
            
            #Updates the option for optionmenu
            play_list.configure(values=playlist_name_copy)
        else:
            messagebox.showerror("Error", "No playlist found")
    
    #Changes the playlist selection according to the playlist
    def current_playlist_label_change(self, *args):
        #Changing the current playlist text label everytime playlist is changed
        current_playlist_word_label.configure(text=self.playlist_selection.get())
    
    #Changes the middle box based on the selection of the playlist
    def update_middle_box(self, *args):
        #Deleting everything in the middlebox
        self.middlebox.delete(0, END)
        for x in self.playlists[self.playlist_selection.get()]:
            #Adding every song from the current playlist to the middle box
            self.middlebox.insert(END, x[0])
    
    #Adds a song to current playlist
    def add_song(self):
        #Making sure there is a playlist
        if len(playlist_name_copy) == 0:
            messagebox.showerror("Error", "Please add a playlist before adding a song")
        #Making sure it gets added to a playlist
        elif self.playlist_selection.get() == "":
            messagebox.showerror("Error", "Please select a playlist to add the song to")
        else:
            song_name = ctk.CTkInputDialog(text="Song Name", title="Add Song")
            song_name = song_name.get_input()
            #Checks if the song is already in the playlist
            if song_name in playlist_name_copy:
                messagebox.showerror("Error", "Current name is already being used. Please select a different name!")
            elif len(song_name) > 0 and song_name != "":
                song_file = filedialog.askopenfilename(title="Select a song", filetypes=(("mp3 file", "*.mp3"), ("wav file", "*.wav")))
                #Checks if user clicked cancel for filedialog
                if song_file != "":
                    playlists_copy[self.playlist_selection.get()].append((song_name, song_file))
                    playlist_song_copy.append(song_name)
            else:
                #Stopping users from adding blank name for the songs
                messagebox.showerror("Error", "Please choose a correct name for the song")
    
    #Deletes a song from current playlist
    def remove_song(self):
        found = False
        if len(playlist_name_copy) == 0:
            messagebox.showerror("Error", "Please add a playlist before trying to delete a song")
        else:
            song_name = ctk.CTkInputDialog(text="Song Name", title="Add Song")
            song_name = song_name.get_input()
            #Iterating through the playlist to find the correct tuple containing the song name and file
            #Then deleting it if found 
            for x in playlists_copy[self.playlist_selection.get()]:
                if x[0] == song_name:
                    playlists_copy[self.playlist_selection.get()].remove(x)
                    playlist_song_copy.remove(song_name)
                    found = True
            
            #If song is not found, there will be an error
            if not found:
                messagebox.showerror("Error", "Couldn't find the song")
            elif found:
                found = False

    
    #Function for ok button in settings
    def update_changes(self):
        song_change = False
        playlist_change = False

        if len(playlist_song_copy) != len(self.playlist_song):
            song_change = True
        
        if len(playlist_name_copy) != len(self.playlist_name):
            playlist_change = True
        
        #Making it the same for the copies if user clicks ok
        self.playlist_name = playlist_name_copy.copy()
        self.playlists = playlists_copy.copy()
        self.playlist_song = playlist_song_copy.copy()
        
        #If user added a song or deleted any song
        if song_change == True:
            self.middle()
            song_change = False
        
        #If user added a playlist or deleted any playlist
        if playlist_change == True:
            #Changing the values of the playlist
            play_list.configure(values=self.playlist_name)
        
        #Fixing the current playlist label
        if self.playlist_selection.get() not in self.playlists:
            self.playlist_selection.set("")
            if len(playlist_name_copy) > 0:
                self.middlebox.delete(0, END)
                self.playlist_selection.set(self.playlist_name[0])
            else:
                self.middlebox.delete(0, END)
        
        #Fixing the current song label
        if self.song_selection.get() not in self.playlist_song:
            self.song_selection.set("")

        #Saving user's playlist and songs into a file
        with open("user_playlist.py", "w") as user_file:
            user_file.write(json.dumps(self.playlists))
        
        #Closes the setting window
        setting_window.destroy()
    
    #Function to cancel changes
    def cancel_changes(self):
        #Deletes all the changes
        playlist_song_copy.clear()
        playlist_name_copy.clear()
        playlists_copy.clear()
        #Closes the setting window
        setting_window.destroy()

if __name__ == "__main__":
    app = Interface()
    app.window()
    app.top()
    app.middle()
    app.bottom_bar()
    app.mainloop()