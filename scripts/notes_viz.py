import tkinter as tk 
import numpy as np 
import sounddevice as sd 
 
from matplotlib.figure import Figure 
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg 
 
# NOTES 
# 
# C4 = Middle C 
# A4 = 440 Hz 
############################################################################### 
NOTE_FREQUENCIES = { 
    "C":     261.63, 
    "C#/Db": 277.18, 
    "D":     293.66, 
    "D#/Eb": 311.13, 
    "E":     329.63, 
    "F":     349.23, 
    "F#/Gb": 369.99, 
    "G":     392.00, 
    "G#/Ab": 415.30, 
    "A":     440.00, 
    "A#/Bb": 466.16, 
    "B":     493.88,
    "A3":    220.00
} 
 
 
############################################################################### 
# COMPUTER KEYBOARD MAPPING 
#       W   E       T   Y   U 
#       C#  D#      F#  G#  A# 
# 
#     A   S   D   F   G   H   J 
#     C   D   E   F   G   A   B 
############################################################################### 
KEY_MAP = { 
    "a": "C", 
    "w": "C#/Db", 
    "s": "D", 
    "e": "D#/Eb", 
    "d": "E", 
    "f": "F", 
    "t": "F#/Gb", 
    "g": "G", 
    "y": "G#/Ab", 
    "h": "A", 
    "u": "A#/Bb", 
    "j": "B",
    "k": "A3"
} 
 
 
# AUDIO SETTINGS 
############################################################################### 
SAMPLE_RATE = 44100 
BLOCK_SIZE = 1024 
VOLUME = 0.3 
 
active_notes = set() 
 
phase = { 
    note: 0.0 
    for note in NOTE_FREQUENCIES 
} 
 
# AUDIO CALLBACK 
############################################################################### 
def audio_callback(outdata, frames, time_info, status): 
    output = np.zeros(frames) 
    notes = active_notes.copy() 
    if notes: 
        for note in notes: 
            frequency = NOTE_FREQUENCIES[note] 
            phase_increment = (2 * np.pi * frequency / SAMPLE_RATE) 
            phases = (phase[note] + phase_increment * np.arange(frames)) 
            output += np.sin(phases) 
 
            phase[note] = (phases[-1] + phase_increment) % (2 * np.pi) 
 
        output /= len(notes) 
        output *= VOLUME 
 
    outdata[:, 0] = output 
 
 
# Start audio stream 
stream = sd.OutputStream( 
    channels=1, 
    samplerate=SAMPLE_RATE, 
    blocksize=BLOCK_SIZE, 
    callback=audio_callback 
) 
 
stream.start() 
 
 
# GUI 
############################################################################### 
root = tk.Tk() 
root.title("Python Piano") 
root.geometry("1000x650") 
 
title = tk.Label( 
    root, 
    text="Python Piano", 
    font=("Arial", 24, "bold") 
) 
 
title.pack(pady=10) 
 
 
instructions = tk.Label( 
    root, 
    text="White keys: A S D F G H J     Black keys: W E T Y U", 
    font=("Arial", 13) 
) 
 
instructions.pack() 
 
 
note_label = tk.Label( 
    root, 
    text="Play a note!", 
    font=("Arial", 14) 
) 
 
note_label.pack(pady=5) 
 
 
# GRAPH 
############################################################################### 
figure = Figure( 
    figsize=(8, 3), 
    dpi=100 
) 
 
ax = figure.add_subplot(111) 
 
canvas = FigureCanvasTkAgg( 
    figure, 
    master=root 
) 
 
canvas.get_tk_widget().pack( 
    fill=tk.BOTH, 
    expand=True, 
    padx=20, 
    pady=20 
) 
 
 
def update_graph(): 
    ax.clear() 
    ax.set_title("Combined Sine Wave") 
    ax.set_xlabel("Time (seconds)") 
    ax.set_ylabel("Amplitude") 
    ax.set_ylim(-1.2, 1.2) 
    # Show 30 milliseconds 
    t = np.linspace(0,0.03,2000) 
    wave = np.zeros_like(t) 
 
    for note in active_notes: 
        frequency = NOTE_FREQUENCIES[note] 
        wave += np.sin(2 * np.pi * frequency * t) 
 
    if active_notes: 
        wave /= len(active_notes) 
        notes = " + ".join(sorted(active_notes)) 
 
        frequencies = ", ".join( 
            f"{NOTE_FREQUENCIES[note]:.2f} Hz" 
            for note in sorted(active_notes) 
        ) 
 
        note_label.config(text=f"Playing: {notes} | {frequencies}") 
 
    else: 
        note_label.config(text="Play a note!") 
 
    ax.plot(t, wave) 
    canvas.draw_idle() 
 
 
def note_on(note): 
    if note not in active_notes: 
        active_notes.add(note) 
        update_graph() 
 
 
def note_off(note): 
    if note in active_notes: 
        active_notes.remove(note) 
        update_graph() 
 
 
# COMPUTER KEYBOARD 
def key_pressed(event): 
    key = event.keysym.lower() 
    if key in KEY_MAP: 
        note_on(KEY_MAP[key]) 
 
 
def key_released(event): 
    key = event.keysym.lower() 
    if key in KEY_MAP: 
        note_off(KEY_MAP[key]) 
 
 
root.bind( 
    "<KeyPress>", 
    key_pressed 
) 
 
root.bind( 
    "<KeyRelease>", 
    key_released 
) 
 
 
# CLOSE PROGRAM 
def close_program(): 
    stream.stop() 
    stream.close() 
    root.destroy() 
 
 
root.protocol("WM_DELETE_WINDOW",close_program) 
 
update_graph() 
 
root.mainloop()
