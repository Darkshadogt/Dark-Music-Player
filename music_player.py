import GUI
import pygame
import random
import audioread
import time


class MusicPlayer(GUI.Interface):

    def __init__(self):
        #Current time into the song
        self.current_time = 0
        #User selected song
        self.song_selection = None
        #Checks whether if user selected a song or not
        self.user_selected = False
    
    #Plays the song of the user playlist
    def play_song(self):
        
        #Sets self.playing to true
        self.playing = True

        #If it is true, the while loop would execute, if false, it stops
        while self.playing == True:
            #If user selected that song, it will play
            if len(self.middlebox.curselection()) != 0:
                self.song_selection = self.middlebox.curselection()
                #Finding the song in playlist
                for song in self.playlists[self.playlist_selection.get()]:
                    if song[0] == self.middlebox.get(self.song_selection):
                        #Setting it to the current song
                        self.current_song = song
                        #Remove user selection
                        self.middlebox.selection_clear(self.song_selection[0])
                        self.user_selected = True
                        #Disable the box so user can't select when another song is playing
                        self.middlebox.configure(state="disabled")
            
            #If there are no songs, it will play the first one in the playlist
            elif self.current_song == None:
                self.current_song = self.playlists[self.playlist_selection.get()][0]
                self.song_selection = (0,)

            #If user changes the playlist, wouldn't cause any error
            if self.current_song not in self.playlists[self.playlist_selection.get()]:
                self.current_song = self.playlists[self.playlist_selection.get()][0]
            
            self.current_song_word_label.configure(text=self.current_song[0])
            
            #Changing the to value of the slider to the length of the song
            song_length = MusicPlayer.song_length(self)
            self.time_slider.configure(to=song_length)
            
            #Checking if user put repeats on
            if (self.shuffle_on == True and self.repeat_on == True) or self.repeat_on == True:
                #Checks if the music got paused 
                if self.paused == False or self.user_selected == True:
                    pygame.mixer.music.load(self.current_song[-1])
                    #If it didn't play the music
                    pygame.mixer.music.play(loops=-1)
                    #Resetting the time for the song
                    self.current_time = 0
                    self.user_selected = False
                else:
                    #If it did, resume music
                    pygame.mixer.music.unpause()
                    self.paused = False
            
            #If it is shuffle, randomly select a song
            elif self.shuffle_on == True:
                random_song = random.choice(self.playlists[self.playlist_selection.get()])
                if self.paused == False or self.user_selected == True:
                    pygame.mixer.music.load(random_song[-1])
                    pygame.mixer.music.play()
                    self.current_time = 0
                    self.user_selected = False
                else:
                    pygame.mixer.music.unpause()
                    self.paused = False
            #If shuffle and repeat both aren't on, play song normally
            else:
                if self.paused == False or self.user_selected == True:
                    pygame.mixer.music.load(self.current_song[-1])
                    pygame.mixer.music.play()
                    self.current_time = 0
                    self.user_selected = True
                else:
                    pygame.mixer.music.unpause()
                    self.paused = False
            #Plays the music
            while pygame.mixer.music.get_busy():
                #If music file is a hour or longer, it uses hour format
                if song_length >= 3600:
                    converted_end_time = time.strftime("%H:%M:%S", time.gmtime(song_length))
                    converted_current_time = time.strftime("%H:%M:%S", time.gmtime(self.current_time))
                #Else it uses minute and time format
                else:
                    converted_end_time = time.strftime("%M:%S", time.gmtime(song_length))
                    converted_current_time = time.strftime("%M:%S", time.gmtime(self.current_time))
                pygame.time.Clock().tick(10)
                #Adds time and changing the slider position
                self.current_time += 1
                #Setting the slider positions and labels
                self.slider.set(self.current_time)
                self.slider_current_time.set(converted_current_time)
                self.slider_end_time.set(converted_end_time)
                time.sleep(1)
    
    #Pause the song
    def pause_song(self):
        #Allows the user to select a song to play
        self.middlebox.configure(state="normal")
        self.playing = False
        self.paused = True
        pygame.mixer.music.pause()

    #Plays the next song
    def play_next_song(self):
        #Getting the index of the current song
        index = self.playlists[self.playlist_selection.get()].index(self.current_song)
        #Checking if there are any songs after the current song
        if index + 1 < len(self.playlists[self.playlist_selection.get()]):
            self.current_song = self.playlists[self.playlist_selection.get()][index+1]
            pygame.mixer.music.load(self.current_song[-1])
        #If not, it plays the first song
        else:
            self.current_song = self.playlists[self.playlist_selection.get()][0]
            pygame.mixer.music.load(self.current_song[-1])
    
    #Plays the song before the current one
    def play_last_song(self):
        #Getting the index
        index = self.playlists[self.playlist_selection.get()].index(self.current_song)
        #Checking if there is any song before the current one
        if index - 1 >= 0:
            self.current_song = self.playlists[self.playlist_selection.get()][index-1]
            pygame.mixer.music.load(self.current_song[-1])
        #If not it plays the first song in the playlist
        else:
            self.current_song = self.playlists[self.playlist_selection.get()][-1]
            pygame.mixer.music.load(self.current_song[-1])

    #Returns the length of the song in seconds
    def song_length(self):
        #Reading the music file
        with audioread.audio_open(self.current_song[-1]) as song:
            length = int(song.duration)
        return(length)

    #Sets the new time of the song user dragged
    def set_song_timer(self, time):
        #Turns the time into seconds to an integer
        new_time = int(time)
        #Changes the song time accordingly
        self.current_time = new_time
        self.slider.set(new_time)
        pygame.mixer.music.set_pos(new_time)
