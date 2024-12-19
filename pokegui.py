#window drawing
from tkinter import messagebox
from PIL import Image, ImageTk
import tkinter as tk
from pokedata import Pokedata
import time


def start_root():
    root = tk.Tk()
    return root

class PokeGUI:
    def __init__(self, root, pokeparty):
        self.root = root
        self.pokeparty = pokeparty
        self.dialog = tk.Toplevel(self.root)
        self.dialog.title('Team Stats')
        
        # Initial setup for your GUI elements here
        self.label_msg = tk.Label(self.dialog, text="")
        self.label_msg.pack(pady=10)
        
        # Assuming you have functions for loading and updating images
        self.photo = None
        self.label_image = tk.Label(self.dialog)
        self.label_image.pack()
        
        self.stop_button = tk.Button(self.dialog, text="Stop", command=self.stop_updates)
        self.stop_button.pack()

        # Control variable for running updates
        self.running = True

        # Start the update loop
        self.update_info()

    def update_info(self):
        if not self.running:
            exit()
        
        start_time = time.time()
        
        # Update battle info
        self.pokeparty.get_battle_info()
        
        # Update GUI
        self.draw_info_window(self.pokeparty.active_player_pokemon)
        
        # Calculate sleep time to maintain frequency
        elapsed_time = time.time() - start_time
        interval = 1  # or whatever interval you want in seconds
        sleep_time = max(0, interval - elapsed_time)
        
        # Schedule the next update with the calculated delay
        self.dialog.after(int(sleep_time * 1000), self.update_info)

    def stop_updates(self):
        self.running = False
        self.stop_button.config(state=tk.DISABLED)

    def draw_info_window(self, active_pokemon):
        # Update the message based on 'active_pokemon'
        msg = f'''Active Pokemon:\n{active_pokemon['name']}\n\n
                Level: {active_pokemon['level']}\n
                Status: {active_pokemon['status']}\n
                Current HP / Max HP: \t{active_pokemon['current_hp']} / {active_pokemon['max_hp']}
                Attack: {active_pokemon['attack']}\tDefense: {active_pokemon['defense']}
                Speed: {active_pokemon['speed']}\tSpecial: {active_pokemon['special']}
                '''

        # Update the text in the label
        self.label_msg.config(text=msg)
        new_photo = self.load_image('igglybuff.png')
        if new_photo:
            self.label_image.config(image=new_photo)
            self.label_image.image = new_photo

    def load_image(self, image_path):
    # Implement your image loading logic here
        try:
            original_img = Image.open(image_path)
            img = original_img.resize((int(original_img.width * 0.25), int(original_img.height * 0.25)))
            return ImageTk.PhotoImage(img)
        except Exception as e:
            print(f"Could not load image: {e}")
            return None