import sys
import tkinter as tk


class ConsoleRedirector:
    class TkRedirector:
        def __init__(self, text_widget):
            self.text_widget = text_widget
            self.console = sys.stdout

        def write(self, message):
            self.text_widget.insert(tk.END, message)
            self.text_widget.see(tk.END)
            self.console.write(message)

        def flush(self):
            pass

    def __init__(self):
        self.text_widget = None
        self.enabled = False

    def enable(self, text_widget):
        sys.stdout = self.TkRedirector(text_widget)
        sys.stderr = self.TkRedirector(text_widget)
        self.text_widget = text_widget
        self.enabled = True

    def disable(self):
        sys.stdout = sys.__stdout__
        sys.stderr = sys.__stderr__
        self.text_widget = None
        self.enabled = False
