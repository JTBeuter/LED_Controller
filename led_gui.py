import time
import tkinter as tk
import telnetlib

HOST = "af.doorsign.int"
PORT = 4711
LED_ON_COMMAND = b"set led on\n"
LED_OFF_COMMAND = b"set led off\n"
TICK_ON_COMMAND = b"set tick on\n"
#input_value = 
#SET_VALUE_COMMAND = b"set value " + input_value + "\n"

class TelnetLEDController:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.telnet_connection = None

    def connect(self):
        try:
            self.telnet_connection = telnetlib.Telnet(self.host, self.port, timeout=1)
            return True
        except Exception as e:
            print(f"Error: {e}")
            return False

    def send_command(self, command):
        try:
            self.telnet_connection.write(command)
            self.telnet_connection.read_until(b"\n", timeout=1)  # Read server response (optional)
            return True
        except Exception as e:
            print(f"Error: {e}")
            return False

    def read_messages(self):
        try:
            message = self.telnet_connection.read_until(b"\n", timeout=1)
            return message.decode("utf-8")
        except Exception as e:
            print(f"Error: {e}")
            return None

    def close_connection(self):
        if self.telnet_connection:
            self.telnet_connection.close()

controller = 0

def on_led_toggle():
    if ledGUI[5].get():
        success = controller.send_command(LED_ON_COMMAND)
        ledGUI[4].config(text="LED Status: ON" if success else "Failed to turn ON LED")
    else:
        success = controller.send_command(LED_OFF_COMMAND)
        ledGUI[4].config(text="LED Status: OFF" if success else "Failed to turn OFF LED")

connected = False

def on_reconnect():
    global connected
    if not connected:
        if controller.connect():
            print("reconnected")
            ledGUI[0].config(text="Connected", fg="green1", bg="gray15", font=(25))
            ledGUI[3].after(1000, set_tick_on)
    else:
        print("Failed to re-establish Telnet connection.")

def set_tick_on():
    controller.send_command(TICK_ON_COMMAND)

def print_messages():
    global connected
    message = controller.read_messages()
    if message:
        if not connected:
            print("connected")
            connected = True
            ledGUI[2]["state"] = "disabled"
            ledGUI[1]["state"] = "normal"
        print("Received message:", message.strip())
    elif connected:
        for i in range(0,4):
            message = controller.read_messages()
            time.sleep(0.5)
            if message.__contains__("TICK"):
                break
            #nicht fertig
        print("disconnected")
        ledGUI[0].config(text="Disconnected", fg="red1", bg="gray15", font=(25))
        connected = False
        ledGUI[2]["state"] = "normal"
        ledGUI[1]["state"] = "disabled"
    ledGUI[3].after(500, print_messages)  # Check for new messages every 0.5 second

def ledSwitchGUI(connectScreen):
    connectScreen.destroy()
    
    ledSwitch = tk.Tk()
    ledSwitch.configure(background='gray15')
    ledSwitch.geometry('400x300+200+200')
    ledSwitch.title("LED Controller")

    connection_state = tk.Label(ledSwitch, text="Disconnected", fg="red", bg="gray15", font=(25))
    connection_state.pack()

    led_state = tk.BooleanVar()

    toggle_button = tk.Checkbutton(ledSwitch, text="Toggle LED", variable=led_state, command=on_led_toggle, bg="gray15", selectcolor="gray15", highlightbackground="gray19", highlightcolor="gray19", activebackground="gray19", disabledforeground="gray19", background="gray15", fg="white", activeforeground="white", font=(25))
    toggle_button.pack()

    reconnect_button = tk.Button(ledSwitch, text="Reconnect", command=on_reconnect, bg="gray15", fg="white", font=(25))
    reconnect_button.pack()

    label = tk.Label(ledSwitch, text="LED Status: OFF", bg="gray15", fg="white", font=(25))
    label.pack()

    return connection_state, toggle_button, reconnect_button, ledSwitch, label, led_state

def LEDController(connectScreen, HOST, PORT):
    global ledGUI
    global controller
    controller = TelnetLEDController(HOST, PORT)
    ledGUI = ledSwitchGUI(connectScreen)
    if controller.connect():
        ledGUI[0].config(text="Connected", fg="green", bg="gray15", font=(25))
        ledGUI[3].after(1000, set_tick_on)
        ledGUI[3].after(1000, print_messages)  # Start checking for messages
        ledGUI[3].mainloop()
        # Close the telnet connection when the application is closed
        controller.close_connection()
    else:
        print("Failed to establish Telnet connection.")

def connectscreenGUI():
    connectScreen =  tk.Tk()
    iplabel = tk.Label(connectScreen, text="IP Address:")
    iplabel.pack()

    ipinput = tk.Entry(connectScreen, width=15)
    ipinput.insert(0, 'af.doorsign.int')
    ipinput.pack()

    portlabel = tk.Label(connectScreen, text="Port:")
    portlabel.pack()

    portinput = tk.Entry(connectScreen, width=15)
    portinput.insert(0, '4711')
    portinput.pack()

    connectButton = tk.Button(connectScreen, text="Connect", command= lambda: LEDController(connectScreen, ipinput.get(), portinput.get()))
    connectButton.pack()

    spacer = tk.Label(connectScreen)
    spacer.pack()
    connectScreen.mainloop()

connectscreenGUI()
ledGUI = []
