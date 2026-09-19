import tkinter as tk
from tkinter import ttk

class AcceptanceTestApp:
    def __init__(self, root):
        self.root = root
        self.root.title("CognitiveOS Active Sandbox")
        self.root.geometry("400x300")
        
        # Heading
        self.lbl_head = tk.Label(root, text="CognitiveOS Grounding Test Page", font=("Helvetica", 12, "bold"))
        self.lbl_head.pack(pady=10)
        
        # Textbox Input
        self.frame_input = tk.Frame(root)
        self.frame_input.pack(pady=5)
        self.lbl_input = tk.Label(self.frame_input, text="Input Text:")
        self.lbl_input.pack(side=tk.LEFT)
        self.entry = tk.Entry(self.frame_input, width=20)
        self.entry.pack(side=tk.LEFT, padx=5)
        
        # Checkbox
        self.check_val = tk.BooleanVar()
        self.checkbox = tk.Checkbutton(root, text="Enable Sandbox Mode", variable=self.check_val, command=self.on_toggle_check)
        self.checkbox.pack(pady=5)
        
        # Dropdown / Combobox
        self.frame_drop = tk.Frame(root)
        self.frame_drop.pack(pady=5)
        self.lbl_drop = tk.Label(self.frame_drop, text="Profile:")
        self.lbl_drop.pack(side=tk.LEFT)
        self.combobox = ttk.Combobox(self.frame_drop, values=["BALANCED", "STEALTH", "OVERCLOCK"], width=15)
        self.combobox.set("BALANCED")
        self.combobox.pack(side=tk.LEFT, padx=5)
        
        # Buttons Frame
        self.frame_buttons = tk.Frame(root)
        self.frame_buttons.pack(pady=10)
        
        self.btn_submit = tk.Button(self.frame_buttons, text="Submit", command=self.on_submit, width=10)
        self.btn_submit.pack(side=tk.LEFT, padx=5)
        
        self.btn_disabled = tk.Button(self.frame_buttons, text="Restricted", state=tk.DISABLED, width=10)
        self.btn_disabled.pack(side=tk.LEFT, padx=5)
        
        # Results area
        self.lbl_status = tk.Label(root, text="STATUS: Idle", font=("Courier", 10), fg="cyan", bg="black", width=40, height=3)
        self.lbl_status.pack(pady=15)

    def on_submit(self):
        val = self.entry.get()
        self.lbl_status.config(text=f"STATUS: Received '{val}'", fg="green")

    def on_toggle_check(self):
        state = "Enabled" if self.check_val.get() else "Disabled"
        self.lbl_status.config(text=f"STATUS: Sandbox {state}", fg="yellow")

if __name__ == "__main__":
    root = tk.Tk()
    app = AcceptanceTestApp(root)
    root.mainloop()
