import tkinter as tk

class Utils:
    def is_valid_float(self, new_value):
        if new_value == "":
            return True
        try:
            float(new_value)
            return True
        except ValueError:
            return False

    def update_send_to_screen(self):
        # ... (rest of the update_send_to_screen code)
        return True