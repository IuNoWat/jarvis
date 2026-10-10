import pygame
import os
import time
import subprocess

pygame.init()

debug_font=pygame.font.Font("/home/pi/Desktop/jarvis/unifont.otf",10)
time_font=pygame.font.Font("/home/pi/Desktop/jarvis/unifont.otf",60)
app_title_font=pygame.font.Font("/home/pi/Desktop/jarvis/unifont.otf",15)
app_update_font=pygame.font.Font("/home/pi/Desktop/jarvis/unifont.otf",12)

SCREEN = pygame.display.set_mode((320,480),pygame.FULLSCREEN)
CLOCK = pygame.time.Clock()
STARTUP_TIMESTAMP = time.strftime("%y/%m/%d-%H:%M:%S")
FPS=15
on=True

class App() : #The App class 
    def __init__(self,name,process,command,must_be_on=True,update_interval=5) :
        #ID of APP
        self.name = name
        self.process = process
        self.command = command

        #Info on APP
        self.IDs = None
        self.active = False
        
        #Settings of APP
        self.must_be_on = must_be_on
        self.update_interval = update_interval

        #Variables
        self.startup_timestamp = time.time()
        self.last_update_timestamp = time.time()

        #First time launching
        self.delete_all()
        self.launch()
        
    def launch(self) :
        print(f"Launching command : {self.command}")
        subprocess.Popen(f"{self.command}",shell=True)
    
    def delete_all(self) :
        print("Deleting all found processes")
        self.search_IDs()
        for i,entry in enumerate(self.IDs) :
            print(f"{i} - Deleting process {entry}")
            msg = subprocess.run(f"kill -9 {entry}",shell=True, capture_output=True)
            print(f"{i} - Result : {msg}")
    
    def search_IDs(self) :
        print(f"Searching corresponding IDs with command "+f"pgrep -x {self.process}")
        msg = subprocess.run(f"pgrep -x {self.process}",shell=True, capture_output=True,encoding="latin-1")
        output = msg.stdout
        print(f"Output : {output}")
        found_IDs = output.splitlines()
        print(f'Found IDs : {found_IDs}')
        self.IDs = found_IDs
    
    def update(self) :
        
        current_time =  time.time()

        if current_time-self.last_update_timestamp>self.update_interval*60 :
            print("UPDATING")
            
            self.search_IDs()
            if len(self.IDs)>0 :
                self.active=True
            else :
                self.active=False
            
            self.last_update_timestamp = current_time

    def render(self) :
        to_return = pygame.Surface((300,40))

        first_line = f"{self.name} | {self.active} ({",".join(self.IDs)})"

        last_update = time.strftime("%y/%m/%d-%H:%M:%S",time.localtime(self.last_update_timestamp))

        second_line = f"Last update : {last_update} ({int(self.update_interval*60)} sec)"

        to_return.blit(app_title_font.render(first_line,1,pygame.Color(255,255,255),pygame.Color(0,0,0)),(0,0))
        to_return.blit(app_update_font.render(second_line,1,pygame.Color(255,255,255),pygame.Color(0,0,0)),(5,20))

        return to_return

class Note() : #The App class 
    def __init__(self,name,path_to_note,update_interval=5) :
        #ID of APP
        self.name = name
        self.path = path_to_note

        #Settings of Note
        self.update_interval = update_interval

        #Variables
        self.startup_timestamp = time.time()
        self.last_update_timestamp = time.time()
        self.txt = "Not Updated Yet"

        #First time launching
        self.update()
        
    
    def update(self) :
        
        current_time =  time.time()

        if current_time-self.last_update_timestamp>self.update_interval*60 :
            print("UPDATING")

            file = open(self.path,"r")
                        
            
            self.last_update_timestamp = current_time


    def render(self) :
        to_return = pygame.Surface((300,40))

        first_line = f"{self.name} | {self.active} ({",".join(self.IDs)})"

        last_update = time.strftime("%y/%m/%d-%H:%M:%S",time.localtime(self.last_update_timestamp))

        second_line = f"Last update : {last_update} (every {int(self.update_interval*60)} seconds)"

        to_return.blit(app_title_font.render(first_line,1,pygame.Color(255,255,255),pygame.Color(0,0,0)),(0,0))
        to_return.blit(app_update_font.render(second_line,1,pygame.Color(255,255,255),pygame.Color(0,0,0)),(5,20))

        return to_return

APPS = [
    App(
        name="Notes Syncthing",
        process="syncthing",
        command="syncthing --no-browser",
        must_be_on=True,
        update_interval=10
    ),
    App(
        name="Test",
        process="meh",
        command="echo \"Hello World from test_App\"",
        must_be_on=True,
        update_interval=10
    )
]

def refresh_tft_screen(screen) :
    f = open("/dev/fb1","wb")
    f.write(screen.convert(16,0).get_buffer())
    f.close()

def do_the_thing() :
    #Cleaning of Screen
    SCREEN.fill(pygame.Color(0,0,0))

    #Event handling
    for event in pygame.event.get():
        keys = pygame.key.get_pressed()
        if event.type == pygame.QUIT:
            on = False

        if keys[pygame.K_ESCAPE] : # ECHAP : Quitter
            on=False
    
    rendered_time = time_font.render(time.strftime("%H:%M:%S"),1,pygame.Color(255,255,255),pygame.Color(0,0,0))
    SCREEN.blit(rendered_time,(35,25))

    for i,app in enumerate(APPS) :
        app.update()
        SCREEN.blit(app.render(),(10,100+40*i))


    fps = str(round(CLOCK.get_fps(),1))
    startup = STARTUP_TIMESTAMP
    txt = f"FPS : {fps} | launch_date : {startup} | wifi : à venir"
    to_blit=debug_font.render(txt,1,pygame.Color(255,255,255),pygame.Color(0,0,0))
    SCREEN.blit(to_blit,(5,5))

    #End of loop
    pygame.display.update()
    refresh_tft_screen(SCREEN)
    delta_time = CLOCK.tick(FPS) 

while on :
    do_the_thing()
