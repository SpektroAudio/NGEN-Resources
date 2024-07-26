# DRUMGEN TEMPLATE GENERATOR

# Developed by Spektro Audio
# spektroaudio.com

# 03/2023

import dearpygui.dearpygui as dpg
import math
import random
from numpy import spacing
import sys

dpg.create_context()
dpg.create_viewport(title='DrumGen Template Creator', width=1400, height=800)

MAX_STEP_VALUE = 10
VELOCITIES = ["127", "80 ", "30 "]

def _hsv_to_rgb(h, s, v):
    if s == 0.0: return (v, v, v)
    i = int(h*6.) # XXX assume int() truncates!
    f = (h*6.)-i; p,q,t = v*(1.-s), v*(1.-s*f), v*(1.-s*(1.-f)); i%=6
    if i == 0: return (255*v, 255*t, 255*p)
    if i == 1: return (255*q, 255*v, 255*p)
    if i == 2: return (255*p, 255*v, 255*t)
    if i == 3: return (255*p, 255*q, 255*v)
    if i == 4: return (255*t, 255*p, 255*v)
    if i == 5: return (255*v, 255*p, 255*q)

def duplicate_16_to_32():
    for p in range(4):
        for r in range(3):
            for s in range(16):
                dest = "{}_{}_{}".format(p, r, s + 16)
                # print(dest)
                # print("Copying {} to {}".format("{}_{}_{}".format(p, r, s), dest))
                dpg.set_value(dest, dpg.get_value("{}_{}_{}".format(p, r, s)))

def callback(sender, app_data):
    print('OK was clicked.')
    print("Sender: ", sender)
    print("App Data: ", app_data)


def test_callback(sender, data):
    print("{} : {}".format(sender, data))
    print("{} : {}".format(sender, dpg.get_value("0_0")))

def randomize_row(sender):
    sender = sender.split("_")
    probability = dpg.get_value("RND_PROB")
    rnd_min = dpg.get_value("RND_MIN")
    rnd_max = dpg.get_value("RND_MAX")
    rnd_mode = dpg.get_value("RND_MODE")
    print("Random mode: {}".format(rnd_mode))
    for i in range(32):
        dest = "{}_{}_{}".format(sender[1], sender[2], i)
        if random.randint(0, 100) < probability:
            if rnd_mode == "SET":
                dpg.set_value(dest, random.randint(rnd_min, rnd_max))
            elif rnd_mode == "+/-":
                rnd_value = random.randint(rnd_min, rnd_max) * 2 - (rnd_max - rnd_min)
                new_value = int(dpg.get_value(dest)) + rnd_value
                if new_value > MAX_STEP_VALUE:
                    new_value = MAX_STEP_VALUE
                elif new_value < 0:
                    new_value = 0
                dpg.set_value(dest, new_value)
            elif rnd_mode == "+":
                print("Current value: {}".format(dpg.get_value(dest)))
                new_value = int(dpg.get_value(dest)) + random.randint(rnd_min, rnd_max)
                print("New value: {}".format(new_value))
                if new_value > MAX_STEP_VALUE:
                    new_value = MAX_STEP_VALUE
                dpg.set_value(dest, new_value)
            elif rnd_mode == "-":
                new_value = dpg.get_value(dest) - random.randint(rnd_min, rnd_max)
                if new_value < 0:
                    new_value = 0
                dpg.set_value(dest, new_value)


def clear_row(sender):
    sender = sender.split("_")
    for i in range(32):
        dest = "{}_{}_{}".format(sender[1], sender[2], i)
        dpg.set_value(dest, 0)

copy_buffer = []

def copy_row(sender):
    global copy_buffer
    copy_buffer = []
    sender = sender.split("_")
    for i in range(32):
        copy_buffer.append(dpg.get_value("{}_{}_{}".format(sender[1], sender[2], i)))

def paste_row(sender):
    sender = sender.split("_")
    for i in range(32):
        dest = "{}_{}_{}".format(sender[1], sender[2], i)
        dpg.set_value(dest, copy_buffer[i])

def openHexFile(sender, app_data):
    print("Opening hex file...")
    files_selected = app_data["selections"]
    first_key = list(files_selected.keys())[0]
    openFilePath = str(files_selected[first_key])
    print(openFilePath)
    with open(openFilePath, 'rb') as f:
        seq_array = f.read()
        seq_array = list(seq_array)
        print(seq_array)
        row_counter = 0
        for p in range(4):
            for r in range(3):
                for c in range(32):
                    byte_num = math.floor(c / 2)
                    index = byte_num + (row_counter * 16)
                    if c % 2 == 0:
                        value = seq_array[index] & 15
                    else:
                        value = seq_array[index] >> 4
                    dpg.set_value("{}_{}_{}".format(p, r, c), value)
                row_counter += 1
    dpg.set_value("template_name", first_key)

def createHexFile():
    seq_array = []
    row_counter = 0
    columns = 32
    for i in range(192):
        seq_array.append(0)

    for p in range(4):
        for r in range(3):
            for c in range(32):
                byte_num = math.floor(c / 2)
                step_value = int(dpg.get_value("{}_{}_{}".format(p, r, c)))
                index = byte_num + (row_counter * 16)
                if c % 2 == 0:
                    seq_array[index] = (step_value % 16) & 15
                else:
                    value = (step_value % 16) & 15
                    value = value << 4
                    seq_array[index] = seq_array[index] | value
            row_counter += 1
    
    print("Exporting hex file...")
    saveFilePath = sys.path[0] + "/" + dpg.get_value("template_name")
    with open(saveFilePath, 'wb') as f:
        for i in seq_array:
            f.write(bytes((i,)))

with dpg.file_dialog(directory_selector=False, show=False, callback=openHexFile, tag="file_picker", width=800, height=400):
    dpg.add_file_extension(".*")
    # dpg.add_file_extension("", color=(150, 255, 150, 255))
    dpg.add_file_extension(".hex", color=(0, 255, 0, 255), custom_text="[HEX]")

with dpg.window(label="DRUMGEN Template Creator", width=1080) as f:
    with dpg.group():
        vert_space = 6
        with dpg.group(horizontal=True):
            
            dpg.add_button(label="Open File", callback=lambda: dpg.show_item("file_picker"))
            dpg.add_button(label="Export HEX file", callback=createHexFile)
        dpg.add_spacer(height=vert_space)
        dpg.add_input_text(label="Name", default_value="NEW_TEMPLATE.hex", width=200, tag="template_name")
        dpg.add_spacer(height=vert_space)
        dpg.add_separator()
        dpg.add_text("EDITING TOOLS")

        with dpg.group(horizontal=True):
            dpg.add_button(label="COPY 16 > 32", callback=duplicate_16_to_32)
            dpg.add_text("| RND - PROB")
            dpg.add_slider_int(tag="RND_PROB", label="", default_value=10, max_value=100, min_value=0, height=34, width=100)
            dpg.add_text("MIN")
            dpg.add_slider_int(tag="RND_MIN", label="", default_value=0, max_value=MAX_STEP_VALUE, min_value=0, height=34, width=100)
            dpg.add_text("MAX")
            dpg.add_slider_int(tag="RND_MAX", label="", default_value=MAX_STEP_VALUE, max_value=MAX_STEP_VALUE, min_value=0, height=34, width=100)
            dpg.add_text("MODE")
            dpg.add_combo(("SET", "+/-", "+", "-"), tag="RND_MODE", default_value="+/-", width=60)
        dpg.add_spacer(height=vert_space)
        # dpg.add_separator()
        
        
        dpg.add_spacer(height=vert_space)
        for p in range(4):
            dpg.add_spacer(height=vert_space)
            dpg.add_separator()
            dpg.add_text("PART {}".format(p+1))
            with dpg.theme(tag="theme_{}".format(p)):
                with dpg.theme_component(0):
                    i = p
                    dpg.add_theme_color(dpg.mvThemeCol_FrameBg, _hsv_to_rgb(i/7.0, 0.5, 0.1))
                    dpg.add_theme_color(dpg.mvThemeCol_SliderGrab, _hsv_to_rgb(i/7.0, 0.9, 0.9))
                    dpg.add_theme_color(dpg.mvThemeCol_FrameBgActive, _hsv_to_rgb(i/7.0, 0.7, 0.2))
                    dpg.add_theme_color(dpg.mvThemeCol_FrameBgHovered, _hsv_to_rgb(i/7.0, 0.6, 0.3))

            dpg.add_spacer(height=vert_space)
            with dpg.group():
                for i in range(3):
                    with dpg.group(horizontal=True):
                        dpg.add_text("{}".format(VELOCITIES[i]))
                        dpg.add_spacer()
                        with dpg.group():
                            with dpg.group(horizontal=True):
                                rnd_tag = "rnd_{}_{}".format(p, i)
                                dpg.add_button(tag=rnd_tag, label="R", callback=randomize_row)

                                clear_tag = "clear_{}_{}".format(p, i)
                                dpg.add_button(tag=clear_tag, label="X", callback=clear_row)
                            with dpg.group(horizontal=True):
                                copy_tag = "copy_{}_{}".format(p, i)
                                dpg.add_button(tag=copy_tag, label="C", callback=copy_row)

                                paste_tag = "paste_{}_{}".format(p, i)
                                dpg.add_button(tag=paste_tag, label="P", callback=paste_row)
                        # dpg.add_separator()
                        dpg.add_spacer()
                        # dpg.add_text(" ")
                        for j in range(32):
                            if ((j % 4) == 0):
                                # dpg.add_separator()
                                dpg.add_text("  ")
                            alias = "{}_{}_{}".format(p, i, j)
                            dpg.add_slider_int(tag=alias, label="", default_value=0, vertical=True, max_value=10, min_value=0, height=34, width=16)
                            dpg.bind_item_theme(dpg.last_item(), "theme_{}".format(p))
                    dpg.add_spacer(height=vert_space / 4) 
        dpg.add_separator()

s
if __name__ == "__main__":
    dpg.setup_dearpygui()
    dpg.show_viewport()
    dpg.start_dearpygui()
    dpg.destroy_context()