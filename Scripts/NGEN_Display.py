import serial
from rich.console import Console
import time
import png
import sys
import datetime
import time
import os
import send2trash
import pygame
import threading
import subprocess

newConsole = Console()

last_buffer = []

# ser = serial.Serial('/dev/cu.usbmodem84316801')  # open serial port

# print(ser.name)         # check which port was really used

SAVE_VIDEO = False

buffer = []
receiving = False
line_buff = ""
file_index = 0
files_location = sys.path[0] + '/output/'
png_files = []


def randomizeBuffer():
    global last_buffer
    last_buffer = []
    for i in range(64):
        last_buffer.append([])
        for j in range(128):
            last_buffer[i].append(1)

def printHeader():
    newConsole.print("""[bold green]
   _  _  ___ ___ _  _   ___ ___ ___ ___ _      ___   __
  | \| |/ __| __| \| | |   \_ _/ __| _ \ |    /_\ \ / /
  | .` | (_ | _|| .` | | |) | |\__ \  _/ |__ / _ \ V / 
  |_|\_|\___|___|_|\_| |___/___|___/_| |____/_/ \_\_|  
                                                       
    """)
    
    newConsole.print("\n[bold green]by Spektro Audio\nspektroaudio,com/ngen")
    newConsole.print("""
[bold purple]COMMANDS:
[not bold white]SPACE - Start/stop recording video
S -  Take a screenshot
""")

class App:
    def __init__(self):
        self._running = True
        self.scale = 4
        self.size = self.width, self.height = 150 * self.scale, 84 * self.scale
        self.display = pygame.display.set_mode((self.width, self.height))
        self.lastDrawnBuffer = []
 
    def on_init(self):
        newConsole.print("\n[bold green]Initializing display...")
        pygame.display.set_caption('NGEN Display')

        pygame.init()
        self._running = True
 
    def on_event(self, event):
        global SAVE_VIDEO
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                SAVE_VIDEO = not SAVE_VIDEO
                print("Saving video: {}".format(SAVE_VIDEO))
                if SAVE_VIDEO:
                    createFolder(sys.path[0] + '/output/' + datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S"))
                else:
                    exportMP4()
            if event.key == pygame.K_s:
                # self._running = False
                screenshot_location = sys.path[0] + '/output/NGEN_Screenshot_' + datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S") + ".jpeg"
                pygame.image.save(self.display, screenshot_location)
                newConsole.print("[purple]Saved screenshot to: {}".format(screenshot_location))

        if event.type == pygame.QUIT:
            self._running = False


    def on_loop(self):
        pass
    def on_render(self):
        pygame.draw.rect(self.display, (0, 0, 0), pygame.Rect(0, 0, self.width, self.height))
        for row in range(len(last_buffer)):
            for col in range(len(last_buffer[0])):
            # Calculate the x and y position of the cell
                x = col * self.scale
                y = row * self.scale

                # Get the value of the cell
                value = last_buffer[row][col]
                

                # Set the color based on the value of the cell
                if value == 1:
                    # print("{} / {}".format(x, y))
                    # Draw the cell on the display
                    pygame.draw.rect(self.display, (255, 255, 255), pygame.Rect(x, y, self.scale, self.scale))
        if SAVE_VIDEO:
            pygame.draw.ellipse(self.display, (255, 0, 0), pygame.Rect(10, 10, 10 * self.scale, 10 * self.scale))
        self.lastDrawnBuffer = last_buffer
        pygame.display.update()

    def on_cleanup(self):
        pygame.quit()
 
    def on_execute(self):
        if self.on_init() == False:
            self._running = False
 
        while( self._running ):
            for event in pygame.event.get():
                self.on_event(event)
            self.on_loop()
            self.on_render()
        self.on_cleanup()

class ReadLine:
    def __init__(self, s):
        self.buf = bytearray()
        self.s = s
    
    def readline(self):
        i = self.buf.find(b"\n")
        if i >= 0:
            r = self.buf[:i+1]
            self.buf = self.buf[i+1:]
            return r
        while True:
            i = max(1, min(2048, self.s.in_waiting))
            data = self.s.read(i)
            i = data.find(b"\n")
            if i >= 0:
                r = self.buf + data[:i+1]
                self.buf[0:] = data[i+1:]
                return r
            else:
                self.buf.extend(data)


def createFolder(path):
    global files_location
    try:
        if not os.path.exists(path):
            os.makedirs(path)
            files_location = path + "/"
    except OSError:
        print ('Error: Creating directory. ' +  path)

def exportMP4():
    print("Exporting MP4 file...")
    os.system("ffmpeg -r 20 -i \"{}img_%04d.png\" -vcodec mpeg4 -y \"{}movie.mp4\"".format(files_location, files_location))
    print("MP4 file exported: " + files_location + "/movie.mp4")
    for f in png_files:
        send2trash.send2trash(f)

def savePNG(s):
    global last_buffer
    global file_index

    print("Saving screenshot PNG file...")

    s = [[int(c) for c in row] for row in s]

    # print(str(s))
    new = []
    counter = 0
    scale = 2
    total = 0
    for i in s:
        counter += 1
        line = i
        new_line = []
        for x in line:
            for z in range(scale):
                new_line.append(x)
        for t in range(scale):
            new.append(new_line)

    # if buffer != last_buffer:
    #     last_buffer = buffer
        # filename = input("Enter file name: ")
    filename = "img_{}".format(str(file_index).zfill(4))
    w = png.Writer(len(new[0]), len(new), greyscale=True, bitdepth=1)
    filepath = '{}{}.png'.format(files_location, filename)
    f = open(filepath, 'wb')
    w.write(f, new)
    f.close()
    png_files.append(filepath)
    file_index += 1
    # print("Screenshot saved: " + filepath)


# createFolder(sys.path[0] + '/output/' + datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S"))

def printBuffer(buffer):
    # print("Updating buffer...")
    global last_buffer
    new_buffer = []
    for i in buffer:
        row = []
        for x in i:
            row.append(int(x))
        new_buffer.append(row)
    last_buffer = new_buffer
    if (SAVE_VIDEO):
        savePNG(new_buffer)
    # print(last_buffer)


def getSerialPort():
    newConsole.print("\n[bold green]Initializing serial port...")
    results = subprocess.Popen(["ls", "/dev"], stdout=subprocess.PIPE)
    results = subprocess.Popen(["grep", "usbmodem"], stdin=results.stdout, stdout=subprocess.PIPE)
    ports = results.stdout.read().decode("UTF-8").strip().split("\n")
    newConsole.print("[bold green]Available serial ports: ")
    for i in range(len(ports)):
        newConsole.print("{} - {}".format(i, ports[i]))
    port = int(input("Select port: "))
    selected_port = "/dev/{}".format(ports[port])
    newConsole.print("[bold green]Opening port: {}".format(selected_port))
    ser = serial.Serial(selected_port, 9600)
    rl = ReadLine(ser)
    return rl

def SerialThread(rl):
    global buffer
    while True:
        line = rl.readline().decode("UTF-8")
        try:
            if int(line) == 1010001:
                receiving = True
                buffer = []
                # print("Receiving screenshot...")
                
            if receiving:
                if int(line) == 1010002:
                    # print("NEW LINE...")
                    line_buff = ""
                elif int(line) == 1010003:
                    # print("APPENDING PREVIOUS LINE...")
                    buffer.append(line_buff)
                    # print(line_buff)
                elif int(line) == 1010004:
                    receiving = False
                    # print(str(len(buffer)))
                    printBuffer(buffer)
                
                else:
                    line_buff += str(int(line)) 
                    # print(line)
            # else:
                # newConsole.print(line)

                # if int(line) == 1010005 and file_index > 0 and SAVE_VIDEO:
                #     exportMP4()
        except:
            pass

def createSerialThread(rl):
    thread = threading.Thread(target=SerialThread, args=(rl,))
    thread.daemon = True
    thread.start()

if __name__ == "__main__" :
    printHeader()
    serial_port = getSerialPort()
    createSerialThread(serial_port)
    # randomizeBuffer()
    theApp = App()
    theApp.on_execute()
    