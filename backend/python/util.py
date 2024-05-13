from tkinter import Tk
from tkinter.simpledialog import askstring
from tkinter.ttk import Label, Button


def ask_integer(prompt):
    root = Tk()
    root.withdraw()

    while True:
        try:
            prompt_int = int(askstring("Input", prompt))
            root.destroy()
            return prompt_int
        except ValueError:
            pass


def questdlg(question, title='Question', options=('Option 1', 'Option 2', 'Option 3')):
    def on_button_click(choice):
        nonlocal user_choice
        user_choice = choice
        dialog.destroy()

    dialog = Tk()
    dialog.title(title)
    dialog.geometry('300x150')

    Label(dialog, text=question, wraplength=280).pack(pady=10)

    user_choice = ""
    for option in options:
        Button(dialog, text=option, command=lambda choice=option: on_button_click(choice)).pack(fill='x', pady=5)

    dialog.mainloop()
    return user_choice
