import tkinter as tk
from gpiozero import LED
import adafruit_dht
import board
import cv2
from PIL import Image, ImageTk
from datetime import datetime

#Hardware setup
ceiling_light = LED(23)
bedside_light = LED(17)
heating_led = LED(22)
cooling_led = LED(27)
dht_sensor = adafruit_dht.DHT11(board.D4)

#temp Limits
COLD_LIMIT = 18
HOT_LIMIT = 28

#Manual overrides
ceiling_manual = False
bedside_manual = False
aircon_manual = False

#Camera variables
camera = None           #Camera used to read frames
camera_running = False  #Flag to ensure no repeat windows can open
camera_window = None    #main window that opens
camera_label = None     #Space where video shows up


#LIGHT FUNCTIONS
def update_lights_auto():
    global ceiling_manual, bedside_manual

    current_hour = datetime.now().hour

    if not ceiling_manual:
        if 10 <= current_hour < 19:
            ceiling_var.set(1)
            ceiling_light.on()
        else:
            ceiling_var.set(0)
            ceiling_light.off()

    if not bedside_manual:
        if 19 <= current_hour < 21:
            bedside_var.set(1)
            bedside_light.on()
        else:
            bedside_var.set(0)
            bedside_light.off()

    root.after(60000, update_lights_auto)

#Manual overrides
def manual_ceiling():
    global ceiling_manual
    ceiling_manual = True

    if ceiling_var.get() == 1:
        ceiling_light.on()
    else:
        ceiling_light.off()


def manual_bedside():
    global bedside_manual
    bedside_manual = True

    if bedside_var.get() == 1:
        bedside_light.on()
    else:
        bedside_light.off()

#Returning to Auto Light Functionality
def return_lights_auto():
    global ceiling_manual, bedside_manual
    ceiling_manual = False
    bedside_manual = False
    update_lights_auto()


#AIR CONDITIONING FUNCTIONS
def aircon_off():
    global aircon_manual
    aircon_manual = True

    heating_led.off()
    cooling_led.off()
    aircon_label.config(text="Air Conditioning: OFF (Manual)")


def aircon_heat():
    global aircon_manual
    aircon_manual = True

    heating_led.on()
    cooling_led.off()
    aircon_label.config(text="Air Conditioning: Heating ON (Manual)")


def aircon_cool():
    global aircon_manual
    aircon_manual = True

    cooling_led.on()
    heating_led.off()
    aircon_label.config(text="Air Conditioning: Cooling ON (Manual)")


def return_aircon_auto():
    global aircon_manual
    aircon_manual = False
    update_temperature()

#Main Air Con loop
def update_temperature():
    try:
        temperature = dht_sensor.temperature
        humidity = dht_sensor.humidity

        if temperature is not None and humidity is not None:
            temp_label.config(text=f"Temperature: {temperature}°C")
            humidity_label.config(text=f"Humidity: {humidity}%")

            if not aircon_manual:
                if temperature < COLD_LIMIT:
                    heating_led.on()
                    cooling_led.off()
                    aircon_label.config(text="Air Conditioning: Heating ON")

                elif temperature > HOT_LIMIT:
                    cooling_led.on()
                    heating_led.off()
                    aircon_label.config(text="Air Conditioning: Cooling ON")

                else:
                    heating_led.off()
                    cooling_led.off()
                    aircon_label.config(text="Air Conditioning: OFF")

    except RuntimeError:
        temp_label.config(text="Temperature: Error")
        humidity_label.config(text="Humidity: Error")

    root.after(5000, update_temperature)


#CAMERA FUNCTIONS
def open_camera():
    global camera, camera_running, camera_window, camera_label

    if camera_running:
        return

    camera = cv2.VideoCapture(0)
    camera_running = True

    camera_window = tk.Toplevel(root)
    camera_window.title("Camera View")

    camera_label = tk.Label(camera_window)
    camera_label.pack(padx=10, pady=10)

    close_button = tk.Button(camera_window, text="Close Camera", command=close_camera)
    close_button.pack(pady=10)

    camera_window.protocol("WM_DELETE_WINDOW", close_camera)

    update_camera()

#Main Camera logic loop
def update_camera():
    if camera_running and camera is not None:
        ret, frame = camera.read()

        if ret:
            frame = cv2.resize(frame, (360, 240))
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

            image = Image.fromarray(frame)
            photo = ImageTk.PhotoImage(image)

            camera_label.config(image=photo)
            camera_label.image = photo

        root.after(30, update_camera)

#Camera closing function
def close_camera():
    global camera, camera_running, camera_window

    camera_running = False

    if camera is not None:
        camera.release()
        camera = None

    if camera_window is not None:
        camera_window.destroy()
        camera_window = None


#EXIT FUNCTION
def exit_app():
    close_camera()

    ceiling_light.off()
    bedside_light.off()
    heating_led.off()
    cooling_led.off()

    root.destroy()


#MAIN GUI
root = tk.Tk()
root.title("Smart Assisted Living System")
root.geometry("420x620")

title_label = tk.Label(root, text="Smart Assisted Living System", font=("Arial", 16, "bold"))
title_label.pack(pady=10)

#Environment section
tk.Label(root, text="Environment Monitoring", font=("Arial", 13, "bold")).pack(pady=5)

temp_label = tk.Label(root, text="place hold temperature")
temp_label.pack()

humidity_label = tk.Label(root, text="place hold humidity")
humidity_label.pack()

aircon_label = tk.Label(root, text="Air Conditioning: OFF")
aircon_label.pack(pady=5)

tk.Button(root, text="Air Conditioning OFF", command=aircon_off).pack(pady=2)
tk.Button(root, text="Hot Air / Heating", command=aircon_heat).pack(pady=2)
tk.Button(root, text="Cold Air / Cooling", command=aircon_cool).pack(pady=2)
tk.Button(root, text="Return Air Conditioning to Auto", command=return_aircon_auto).pack(pady=5)

#Lighting section
tk.Label(root, text="Lighting Control", font=("Arial", 13, "bold")).pack(pady=10)

ceiling_var = tk.IntVar()
bedside_var = tk.IntVar()

tk.Checkbutton(root, text="Ceiling Light", variable=ceiling_var, command=manual_ceiling).pack()
tk.Checkbutton(root, text="Bedside Light", variable=bedside_var, command=manual_bedside).pack()

tk.Button(root, text="Return Lights to Auto", command=return_lights_auto).pack(pady=5)

#Camera section
tk.Label(root, text="Camera", font=("Arial", 13, "bold")).pack(pady=10)
tk.Button(root, text="Open Camera View", command=open_camera).pack(pady=5)

#Exit button
tk.Button(root, text="Exit", command=exit_app).pack(pady=20)

update_temperature()
update_lights_auto()

root.protocol("WM_DELETE_WINDOW", exit_app)
root.mainloop()
