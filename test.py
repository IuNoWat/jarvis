import subprocess

class App() :
    def __init__(self,name,path,must_be_on=True) :
        self.name = name
        self.path = path

        self.must_be_on = must_be_on
        
    def launch(self) :
        print(f"Launching path : {self.path}")
        subprocess.Popen(f"{self.path}")
    
    def is_active(self) :
        print(f"Checking status with command"+f"pgrep -xl {self.name}")
        msg = subprocess.run(f"pgrep -xl {self.name}",shell=True)
        print(msg)

