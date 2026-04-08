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

def turn_all_off():
    for pin in LED_PINS.values():
        GPIO.output(pin, False)

def select_room():
    selected_room = room_var.get()
    turn_all_off()
    GPIO.output(LED_PINS[selected_room], True)

def exit_app():
    turn_all_off()
    GPIO.cleanup()
    root.destroy()

root = tk.Tk()
root.title("House Lights")
root.geometry("250x250")

room_var = tk.StringVar()

setup_leds()

tk.Label(root, text="Select a Room", font=("Helvetica", 14, 'bold'), bg ="lightblue").pack(pady=10)

for room_name in LED_PINS:
    tk.Radiobutton(root,text=room_name,variable=room_var,value=room_name, command=select_room).pack(anchor="w", padx=20)

tk.Button(root, text="Exit", command=exit_app).pack(pady=15)

root.mainloop()
