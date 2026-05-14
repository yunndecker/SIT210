import tkinter as tk
import RPi.GPIO as GPIO

GPIO.setmode(GPIO.BCM)

LED_PINS = {
    "Living Room": 17,
    "Bathroom": 27,
    "Closet": 22
}

def setup_leds():
    for pin in LED_PINS.values():
        GPIO.setup(pin, GPIO.OUT)
        GPIO.output(pin, False)

def update_lights():
    for room_name, pin in LED_PINS.items():
        if room_vars[room_name].get() ==1:
            GPIO.output(pin, True)
        else:
            GPIO.output(pin,False)

def exit_app():
    for pin in LED_PINS.values():
        GPIO.output(pin, False)
    GPIO.cleanup()
    root.destroy()

root = tk.Tk()
root.title("House Lights")
root.geometry("250x250")

room_vars = {}

setup_leds()

tk.Label(root, text="Select a Room", font=("Helvetica", 14, "bold"), bg ="lightblue").pack(pady=10)

for room_name in LED_PINS:
    room_vars[room_name] = tk.IntVar()
    
    tk.Checkbutton(root,text=room_name,variable=room_vars[room_name],command=update_lights).pack(anchor="w", padx=20)

tk.Button(root, text="Exit", command=exit_app).pack(pady=15)

root.mainloop()
