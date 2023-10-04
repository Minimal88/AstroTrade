import tkinter as tk

# Create the main window
window = tk.Tk()

# Create a label
label = tk.Label(text="Symbol")

# Create a text box
text_box = tk.Entry()

# Create a button
button = tk.Button(text="Simulate Trade")

# Set the layout of the widgets
label.pack()
text_box.pack()
button.pack()

# Bind the button to a function
button.config(command=lambda: simulate_trade(text_box.get()))

# Start the main loop
window.mainloop()