import tkinter as tk
from tkinter import ttk
from threading import Thread
from AutoSelect import AutoSelect

# Create instance
win = tk.Tk()

# Set window title
win.title("LOL Champion Selection")

# Create the LeagueClient class
lc = AutoSelect()

# Create function for start button
def start():
    print("Start Button Clicked!")
    # Prepare requests when creating the class
    lc.get_lockfile()
    lc.prepare_requests()
    lc_thread = Thread(target=lc.start)
    lc_thread.start()

# Create function for stop button
def stop():
    print("Stop Button Clicked!")
    lc.stop()  # You need to implement the stop method in your LeagueClient class

# Create start button
start_button = ttk.Button(win, text="Start", command=start)
start_button.grid(column=0, row=0)

# Create stop button
stop_button = ttk.Button(win, text="Stop", command=stop)
stop_button.grid(column=0, row=1)

# Create dropdown for champion selection
champion = tk.StringVar()
champion_chosen = ttk.Combobox(win, width=12, textvariable=champion)
champion_chosen['values'] = ('Yuumi', 'Annie', 'Olaf', 'Galio', 'Twisted Fate', 'Xin Zhao')  # Add all champion names
champion_chosen.grid(column=1, row=0)
champion_chosen.current(0)  # set selection default

# Create entry for queue id
queue_id = tk.StringVar()
queue_id_entry = ttk.Entry(win, width=12, textvariable=queue_id)
queue_id_entry.grid(column=1, row=1)

# Create entry for message
message = tk.StringVar()
message_entry = ttk.Entry(win, width=12, textvariable=message)
message_entry.grid(column=1, row=2)

# Run GUI
win.mainloop()
