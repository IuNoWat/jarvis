import os
import time
import traceback

import pygame
import subprocess

import cts_api

pygame.init()
pygame.mouse.set_visible(False)

debug_font=pygame.font.Font("/home/pi/Desktop/jarvis/unifont.otf",10)
time_font=pygame.font.Font("/home/pi/Desktop/jarvis/unifont.otf",60)
app_title_font=pygame.font.Font("/home/pi/Desktop/jarvis/unifont.otf",15)
app_update_font=pygame.font.Font("/home/pi/Desktop/jarvis/unifont.otf",12)

SCREEN = pygame.display.set_mode((320,480),pygame.FULLSCREEN)
CLOCK = pygame.time.Clock()
STARTUP_TIMESTAMP = time.strftime("%y/%m/%d-%H:%M:%S")
FPS=15
on=True

class App() : #The App class is a base to make something visible
    def __init__(self,name,startup_method,update_method,render_method,update_interval=5,render_length=40) :
        
        self.on_startup = startup_method
        self.on_update = update_method
        self.on_render = render_method
        
        #ID of APP
        self.name = name

        #Info on APP
        self.active = False
        self.errors = []
        
        #Settings of APP
        self.update_interval = update_interval

        #Visual settings
        self.render_length = render_length

        #Variables
        self.startup_timestamp = time.time()
        self.last_update_timestamp = time.time()

        #Launching
        self.on_startup(self)
        self.on_update(self)

    def update(self) :
        
        current_time =  time.time()

        if current_time-self.last_update_timestamp>self.update_interval*60 :
            print("UPDATING")
            
            self.on_update(self)
            
            self.last_update_timestamp = current_time

    def base_render(self) :
        width = 280
        self.to_render = pygame.Surface((width,self.render_length))
        pygame.draw.line(self.to_render,pygame.Color(255,255,255),(0,10),(width-1,10),1)
        pygame.draw.line(self.to_render,pygame.Color(255,255,255),(width-1,10),(width-1,self.render_length-1),1)
        pygame.draw.line(self.to_render,pygame.Color(255,255,255),(width-1,self.render_length-1),(0,self.render_length-1),1)
        pygame.draw.line(self.to_render,pygame.Color(255,255,255),(0,self.render_length-1),(0,10),1)

        last_update = time.strftime("%y/%m/%d-%H:%M:%S",time.localtime(self.last_update_timestamp))

        first_line = f"{self.name} | {self.active} (Errors : {len(self.errors)})"
        second_line = f"Last update : {last_update} ({int(self.update_interval*60)} sec)"

        self.to_render.blit(app_title_font.render(first_line,1,pygame.Color(255,255,255),pygame.Color(0,0,0)),(0,0))
        self.to_render.blit(app_update_font.render(second_line,1,pygame.Color(255,255,255),pygame.Color(0,0,0)),(5,20))
    
    def render(self) :
        self.base_render()
        self.on_render(self)
        return self.to_render
    
    def add_error(self,error) :
        self.errors.append(error)
        print(traceback.TracebackException.from_exception(error))

    
    def on_startup(self) :
        """
        Method meant to be replaced for each app
        """
        pass
    
    def on_update(self) :
        """
        Method meant to be replaced for each app
        """
        pass

    def on_render(self) :
        """
        Method meant to be replaced for each app
        """
        pass

def search_IDs() :
    print(f"Searching corresponding IDs with command "+f"pgrep -x syncthing")
    msg = subprocess.run(f"pgrep -x syncthing",shell=True, capture_output=True,encoding="latin-1")
    output = msg.stdout
    print(f"Output : {output}")
    found_IDs = output.splitlines()
    print(f'Found IDs : {found_IDs}')
    return found_IDs

def delete_all() :
    print("Deleting all found processes")
    IDs = search_IDs()
    for i,entry in enumerate(IDs) :
        print(f"{i} - Deleting process {entry}")
        msg = subprocess.run(f"kill -9 {entry}",shell=True, capture_output=True)
        print(f"{i} - Result : {msg}")

def syncthing_startup(self) :
    delete_all()
    print(f"Launching command : syncthing --no-browser")
    subprocess.Popen("syncthing --no-browser",shell=True)

    self.IDs=[]

def syncthing_update(self) :

    self.IDs = ",".join(search_IDs())

    if len(self.IDs)>3 :
        self.active=True
    else :
        self.active=False

def syncthing_render(self) :
    found_IDs = f"IDs : {self.IDs}"

    self.to_render.blit(app_update_font.render(found_IDs,1,pygame.Color(255,255,255),pygame.Color(0,0,0)),(10,35))

APP_SYNCTHING = App(
    name="Syncthing",
    startup_method=syncthing_startup,
    update_method=syncthing_update,
    render_method=syncthing_render,
    update_interval=10,
    render_length=60
)

def cts_startup(self) :
    self.stop_code="517"
    self.infos = []

def cts_update(self) :
    vehicles = cts_api.get_visits(self.stop_code)
    infos = []
    for entry in vehicles :
        infos.append(cts_api.get_info(entry))

    if infos!=[] :
        self.active=True
    else :
        self.active=False
    self.infos =  infos    

def inline_infos(info) :
    return info["type"] + " " + info["line"] + " - " +  info["direction"] + " : " + str(info["arrival_in"])

def cts_render(self) :
    for i,entry in enumerate(self.infos) :
        self.to_render.blit(app_update_font.render(inline_infos(entry),1,pygame.Color(255,255,255),pygame.Color(0,0,0)),(10,35+i*15))

APP_CTS = App(
    name="CTS",
    startup_method=cts_startup,
    update_method=cts_update,
    render_method=cts_render,
    update_interval=1,
    render_length=250#140
)

APPS = [
    APP_SYNCTHING,
    APP_CTS
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


    cursor=100
    for i,app in enumerate(APPS) :
        try :
            app.update()
            SCREEN.blit(app.render(),(10,cursor))
            cursor+=app.render_length+5
        except Exception as error :
            print("ERROR")
            app.add_error(error)


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
