import json
import os
import threading

import customtkinter as ctk
from tkinter.filedialog import askdirectory, askopenfilename

from PIL import Image
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

from backend import GeneticAlgorithm
from frontend import Api, ConsoleRedirector

VIOLET_DARK = "#414166"
VIOLET_LIGHT = "#B7B7CC"
BACKGROUND_COLOR = "#E2E3EB"
TEXT_COLOR = "#232323"
WHITE_COLOR = "#FFFFFF"

FONT_HEAD = "Kharkiv"
FONT_BODY = "Kharkiv"
FONT_BUTTONS = "HeliosExtBlack"


def print_to_widget(obj, text_widget, data):
    generation = data["generation"]
    string_state = ""
    if generation % 30 == 0:
        string_state += f"\n{'':>12} {'Best':>12} {'Mean':>12} {'Stall':>12}\n" + \
                        f"{'Generation':>12} {'Penalty':>12} {'Penalty':>12} {'Generations':>12}\n"
    if data["best"]:
        if isinstance(data["best"], list):
            best_penalty = data["best"][-1]
        else:
            best_penalty = data["best"]
    else:
        best_penalty = min(data["scores"])
    mean_penalty = sum(data["scores"]) / len(data["scores"])
    stall_generations = max(data["generation"] - data["last_improvement"], 0)
    string_state += f"{generation:>12} {format_number(best_penalty):>12} " + \
                    f"{format_number(mean_penalty):>12} {stall_generations:>12}\n"

    text_widget.insert(ctk.END, string_state)
    text_widget.see(ctk.END)
    text_widget.update_idletasks()
    obj[0] += string_state


def format_number(num):
    if abs(num) > 999999 or (abs(num) < 0.00001 and num != 0):
        return f"{num:.3e}"
    elif abs(num) < 1:
        amount_of_digits = min(len(str(num).split(".")[1]), 6)
        return f"{num:.{amount_of_digits}f}"
    else:
        return f"{num:.2f}"


def create_graph_window(master, budgets, profits, allow_exit=False, draw_line=True):
    window = ctk.CTkToplevel(master)
    window.title("Budget vs Profit")

    budgets = [int(budget) for budget in budgets]
    profits = [int(profit) for profit in profits]

    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()

    width = int(screen_width * 0.95)
    height = int(screen_height * 0.90)
    x = (screen_width - width) // 2
    y = (screen_height - height) // 2

    window.geometry(f"{width}x{height}+{x}+{y}")

    if not allow_exit:
        window.protocol("WM_DELETE_WINDOW", lambda: None)

    frame = ctk.CTkFrame(window)
    frame.pack(fill="both", expand=True)

    fig = Figure(figsize=(10, 6), dpi=100)
    ax = fig.add_subplot(111)

    if len(budgets) > 1 and draw_line:
        for i in range(len(budgets) - 1):
            color = 'red' if i % 2 == 0 else 'blue'
            ax.plot(budgets[i:i + 2], profits[i:i + 2], 'o-', color=color)
    else:
        for i, (budget, profit) in enumerate(zip(budgets, profits)):
            color = 'red' if i % 2 == 0 else 'blue'
            ax.plot(budget, profit, 'o', color=color)

    for i, (budget, profit) in enumerate(zip(budgets, profits)):
        color = 'red' if i % 2 == 0 else 'blue'
        if i % 2 == 0:
            ax.annotate(f'B-{budget}\nP-{profit}', (budget, profit),
                        textcoords="offset points", xytext=(-20, 5), ha='center', color=color)
        else:
            ax.annotate(f'B-{budget}\nP-{profit}', (budget, profit),
                        textcoords="offset points", xytext=(25, -25), ha='center', color=color)

    ax.set_xlabel("Budget")
    ax.set_ylabel("Profit")
    ax.set_title("Budget vs Profit")
    ax.legend()

    canvas = FigureCanvasTkAgg(fig, master=frame)
    canvas.draw()
    canvas.get_tk_widget().pack(fill="both", expand=True)

    return window


class App(ctk.CTk):
    def __init__(self, cfg_path=None, matlab_cfg_path=None, host="localhost", port=5000):
        super().__init__()
        self.alg_buffer = [""]
        self.forward_image_dark = None
        self.forward_image = None
        self.back_image_dark = None
        self.back_image = None
        self.settings_button = None
        self.forward_button = None
        self.back_button = None
        self.header = None
        self.max_budget = None
        self.min_budget = None
        self.entered_number = None
        self.selected_file_path = None
        self.solved = False
        self.first_page = {}
        self.second_page = {}
        self.third_page = {}
        self.app_state = 1
        self.budget_mode_single = True

        self.host = host
        self.port = port

        self.current_path = os.path.dirname(os.path.abspath(__file__))
        self.assets_path = os.path.join(self.current_path, "frontend/assets")

        self.title("Рекомендаційна система для роздрібної торгівлі")
        self.geometry("600x700")
        self.configure(fg_color=BACKGROUND_COLOR)
        self.resizable(False, False)
        self.protocol("WM_DELETE_WINDOW", self.show_exit_dialog)

        self.api = None

        matlab_cfg_path = os.path.join(self.current_path, "matlab_config.json") \
            if not matlab_cfg_path else matlab_cfg_path
        self.ga = GeneticAlgorithm(matlab_cfg_path, host=self.host, port=self.port)

        self.cfg_path = os.path.join(self.current_path, "app_config.json") if not cfg_path else cfg_path
        # self.ga = None

        self.pop_multiplier = 4
        self.max_gen_multiplier = 20
        self.max_stall_gen_multiplier = 3

        self.update_config()
        self.init_header()
        self.init_main_window()

        self.console_redirector = ConsoleRedirector()

    def show_exit_dialog(self):
        dialog = ctk.CTkToplevel(self)
        dialog.title("Вихід")
        dialog.geometry(self.calculate_center_position(300, 200))
        dialog.transient(self)
        dialog.configure(fg_color=BACKGROUND_COLOR)

        label = ctk.CTkLabel(dialog, text="Ви впевнені, що хочете вийти?", text_color=TEXT_COLOR, font=(FONT_BODY, 20),
                             wraplength=270)
        label.pack(expand=True, padx=10, pady=10)

        yes_button = ctk.CTkButton(dialog, text="Так", command=self.quit, fg_color=VIOLET_DARK, text_color=WHITE_COLOR,
                                   font=(FONT_BUTTONS, 26), border_width=0, height=50,
                                   width=135)
        yes_button.pack(side="left", padx=(10, 10), pady=10)

        no_button = ctk.CTkButton(dialog, text="Ні", command=dialog.destroy, fg_color=VIOLET_DARK,
                                  text_color=WHITE_COLOR, font=(FONT_BUTTONS, 26), border_width=0, height=50,
                                  width=135)
        no_button.pack(side="right", padx=(0, 10), pady=10)

        dialog.grab_set()

    def update_config(self, pop_multiplier=None, max_gen_multiplier=None, max_stall_gen_multiplier=None):
        if os.path.exists(self.cfg_path):
            with open(self.cfg_path, "r") as file:
                config = json.load(file)
        else:
            config = {}

        if pop_multiplier:
            config["pop_multiplier"] = pop_multiplier
            self.pop_multiplier = pop_multiplier
        else:
            config["pop_multiplier"] = self.pop_multiplier
        if max_gen_multiplier:
            config["max_gen_multiplier"] = max_gen_multiplier
            self.max_gen_multiplier = max_gen_multiplier
        else:
            config["max_gen_multiplier"] = self.max_gen_multiplier
        if max_stall_gen_multiplier:
            config["max_stall_gen_multiplier"] = max_stall_gen_multiplier
            self.max_stall_gen_multiplier = max_stall_gen_multiplier
        else:
            config["max_stall_gen_multiplier"] = self.max_stall_gen_multiplier

        with open(self.cfg_path, "w") as file:
            json.dump(config, file, indent=4)

    def init_header(self):
        self.header = ctk.CTkFrame(self)
        self.header.pack(side="top", pady=20, fill="x")
        self.header.configure(fg_color=BACKGROUND_COLOR)

        back_image = Image.open(os.path.join(self.assets_path, "left.png"))
        self.back_image = ctk.CTkImage(light_image=back_image, dark_image=back_image,
                                       size=(back_image.width, back_image.height))
        back_image_dark = Image.open(os.path.join(self.assets_path, "left_dark.png"))
        self.back_image_dark = ctk.CTkImage(light_image=back_image_dark, dark_image=back_image_dark,
                                            size=(back_image_dark.width, back_image_dark.height))
        forward_image = Image.open(os.path.join(self.assets_path, "right.png"))
        self.forward_image = ctk.CTkImage(light_image=forward_image, dark_image=forward_image,
                                          size=(forward_image.width, forward_image.height))
        forward_image_dark = Image.open(os.path.join(self.assets_path, "right_dark.png"))
        self.forward_image_dark = ctk.CTkImage(light_image=forward_image_dark, dark_image=forward_image_dark,
                                               size=(forward_image_dark.width, forward_image_dark.height))

        settings_image = Image.open(os.path.join(self.assets_path, "settings.png"))
        settings_image = ctk.CTkImage(light_image=settings_image, dark_image=settings_image,
                                      size=(settings_image.width, settings_image.height))

        self.back_button = ctk.CTkLabel(self.header, image=self.back_image_dark, text="")
        self.back_button.pack(side="left", padx=(20, 5))
        self.back_button.bind("<Button-1>", self.back_clicked)

        self.forward_button = ctk.CTkLabel(self.header, image=self.forward_image_dark, text="")
        self.forward_button.pack(side="left")
        self.forward_button.bind("<Button-1>", self.forward_clicked)

        self.settings_button = ctk.CTkLabel(self.header, image=settings_image, text="")
        self.settings_button.pack(side="right", padx=20)
        self.settings_button.bind("<Button-1>", lambda e: self.show_settings())

    def create_beautiful_entry(self, master, text, font_label, font_entry, pady=(0, 0), fg_color=BACKGROUND_COLOR,
                               wraplength=600):
        frame = self.get_helpful_frame(master=master, pady=pady, fg_color=fg_color)
        label = ctk.CTkLabel(frame, text=text, text_color=TEXT_COLOR, font=font_label, justify="left",
                             wraplength=wraplength)
        label.pack(side="left", padx=10)
        entry = ctk.CTkEntry(master, fg_color=VIOLET_LIGHT, text_color=TEXT_COLOR,
                             font=font_entry, justify="left", border_width=0, height=50)
        entry.pack(side="top", padx=10, pady=5, fill="x")

        return frame, label, entry

    def show_settings(self):
        if self.settings_button.cget("state") == "disabled":
            return

        settings = ctk.CTkToplevel(self)
        settings.title("Налаштування")
        settings.geometry(self.calculate_center_position(600, 440))
        settings.transient(self)
        settings.configure(fg_color=BACKGROUND_COLOR)

        pop_frame, pop_label, pop_entry = self.create_beautiful_entry(
            settings,
            "Множник кількості популяцій:",
            (FONT_BODY, 26),
            (FONT_BODY, 22),
            pady=(20, 0))
        pop_entry.insert(0, str(self.pop_multiplier))

        max_gen_frame, max_gen_label, max_gen_entry = self.create_beautiful_entry(
            settings,
            "Множник максимальної кількості поколінь:",
            (FONT_BODY, 26),
            (FONT_BODY, 22),
            pady=(10, 0))
        max_gen_entry.insert(0, str(self.max_gen_multiplier))

        max_stall_gen_frame, max_stall_gen_label, max_stall_gen_entry = self.create_beautiful_entry(
            settings,
            "Множник максимальної кількості поколінь без змін:",
            (FONT_BODY, 26),
            (FONT_BODY, 22),
            pady=(10, 0))
        max_stall_gen_entry.insert(0, str(self.max_stall_gen_multiplier))

        save_button = ctk.CTkButton(settings, text="Зберегти", command=lambda: self.save_settings(settings, pop_entry,
                                                                                                  max_gen_entry,
                                                                                                  max_stall_gen_entry),
                                    fg_color=VIOLET_DARK, text_color=WHITE_COLOR, font=(FONT_BUTTONS, 26),
                                    border_width=0, height=50)
        save_button.pack(side="top", padx=10, pady=(20, 0), fill="x")

        settings.grab_set()

    def save_settings(self, settings, pop_entry, max_gen_entry, max_stall_gen_entry):
        try:
            self.update_config(int(pop_entry.get()), int(max_gen_entry.get()), int(max_stall_gen_entry.get()))
            settings.destroy()
        except ValueError:
            self.show_dialog("Помилка", "Введіть коректні множники",
                             self.calculate_center_position(300, 100))

    def back_clicked(self, _):
        if self.back_button.cget("image") == self.back_image and self.back_button.cget("state") == "normal":
            self.move_back()

    def forward_clicked(self, _):
        if self.forward_button.cget("image") == self.forward_image and self.forward_button.cget("state") == "normal":
            self.move_forward()

    def move_forward(self, max_budget=None, min_budget=None, step=None, single=None):
        if self.app_state < 3:
            self.app_state += 1
        self.draw_state(max_budget, min_budget, step, single)

    def move_back(self):
        if self.app_state > 1:
            self.app_state -= 1
        self.draw_state()

    def draw_state(self, max_budget=None, min_budget=None, step=None, single=None):
        match self.app_state:
            case 1:
                self.back_button.configure(image=self.back_image_dark)
                if not self.min_budget and not self.max_budget:
                    self.forward_button.configure(image=self.forward_image_dark)
                else:
                    self.forward_button.configure(image=self.forward_image)
                self.init_main_window()
            case 2:
                self.back_button.configure(image=self.back_image)
                if not self.solved:
                    self.forward_button.configure(image=self.forward_image_dark)
                else:
                    self.forward_button.configure(image=self.forward_image)
                self.show_budget_input()
            case 3:
                self.back_button.configure(image=self.back_image)
                self.forward_button.configure(image=self.forward_image_dark)
                self.show_algorithm_page(max_budget, min_budget, step, single)
            case _:
                self.back_button.configure(image=self.back_image_dark)
                self.forward_button.configure(image=self.forward_image_dark)
                self.init_main_window()

    def get_helpful_frame(self, master=None, pady=(0, 0), padx=(0, 0), fg_color=BACKGROUND_COLOR,
                          height=None, fill=None, expand=False):
        if master is None:
            master = self
        file_frame = ctk.CTkFrame(master)
        file_frame.pack(side="top", padx=padx, pady=pady, fill="x" if not fill else fill, expand=expand)
        file_frame.configure(fg_color=fg_color)
        if height:
            file_frame.configure(height=height)

        return file_frame

    def init_main_window(self):
        self.clear_window()

        title_label = ctk.CTkLabel(self, text="Рекомендаційна система\nдля роздрібної торгівлі",
                                   text_color=VIOLET_DARK, font=(FONT_HEAD, 33, "bold"), justify="left")
        title_label.pack(side="top", pady=(20, 0))

        number_frame = self.get_helpful_frame(pady=(40, 0))
        number_label = ctk.CTkLabel(number_frame, text="Максимальний\nперіод замовлення:",
                                    text_color=TEXT_COLOR, font=(FONT_BODY, 37), justify="left")
        number_label.pack(side="left", padx=30)

        number_entry = ctk.CTkEntry(self, fg_color=VIOLET_LIGHT, text_color=TEXT_COLOR, font=(FONT_BODY, 26),
                                    justify="left", border_width=0, height=50)
        number_entry.pack(side="top", padx=25, pady=5, fill="x")
        if self.entered_number is not None:
            number_entry.insert(0, str(self.entered_number))

        file_frame = self.get_helpful_frame(pady=(50, 0))
        file_label = ctk.CTkLabel(file_frame, text=f"Обраний файл:",
                                  text_color=TEXT_COLOR, font=(FONT_BODY, 37), justify="left")
        file_label.pack(side="left", padx=30)
        file_entry = ctk.CTkEntry(self, fg_color=VIOLET_LIGHT, text_color=TEXT_COLOR, font=(FONT_BODY, 26),
                                  justify="left", border_width=0, height=50)
        file_entry.pack(side="top", padx=25, pady=(5, 0), fill="x")
        file_entry.configure(state="readonly")
        if self.selected_file_path:
            file_entry.configure(state="normal")
            file_entry.delete(0, "end")
            file_entry.insert(0, self.selected_file_path)
            file_entry.configure(state="readonly")

        file_button_frame = self.get_helpful_frame(pady=(10, 0))
        file_button = ctk.CTkButton(file_button_frame, text="Обрати файл", command=self.select_file,
                                    fg_color=VIOLET_DARK, text_color=WHITE_COLOR, font=(FONT_BUTTONS, 22),
                                    border_width=0, height=50, width=270)
        file_button.pack(side="left", padx=25)

        calculate_button = ctk.CTkButton(self, text="Розрахувати бюджет", command=self.calculate_budget,
                                         fg_color=VIOLET_DARK, text_color=WHITE_COLOR, font=(FONT_BUTTONS, 32),
                                         border_width=0, height=60)
        calculate_button.pack(side="top", padx=25, pady=(65, 0), fill="x")

        self.first_page = {
            "title_label": title_label,
            "number_frame": number_frame,
            "number_label": number_label,
            "number_entry": number_entry,
            "file_frame": file_frame,
            "file_label": file_label,
            "file_entry": file_entry,
            "file_button_frame": file_button_frame,
            "file_button": file_button,
            "calculate_button": calculate_button
        }

    def calculate_center_position(self, width, height):
        main_window_x = self.winfo_x()
        main_window_y = self.winfo_y()
        main_window_width = self.winfo_width()
        main_window_height = self.winfo_height()

        dialog_x = main_window_x + (main_window_width - width) // 2
        dialog_y = main_window_y + (main_window_height - height) // 2

        return f"{width}x{height}+{dialog_x}+{dialog_y}"

    def show_dialog(self, title, message, geometry, wraplength=270, master=None):
        if not master:
            master = self

        dialog = ctk.CTkToplevel(master)
        dialog.title(title)
        dialog.geometry(geometry)
        dialog.transient(master)
        dialog.configure(fg_color=BACKGROUND_COLOR)

        label = ctk.CTkLabel(dialog, text=message, text_color=TEXT_COLOR, font=(FONT_BODY, 20), wraplength=wraplength)
        label.pack(expand=True, padx=10, pady=10)

        dialog.grab_set()

        return dialog

    def close_dialog(self, key):
        if calculating_dialog := self.first_page.get(key):
            calculating_dialog.grab_release()
            calculating_dialog.destroy()
            del self.first_page[key]

    def select_file(self):
        file_path = askopenfilename(
            title="Select file",
            filetypes=(("Excel files", "*.xlsx"), ("All files", "*.*")),
            initialdir=self.current_path
        )
        if file_path:
            self.selected_file_path = file_path
            self.first_page["file_entry"].configure(state="normal")
            self.first_page["file_entry"].delete(0, "end")
            self.first_page["file_entry"].insert(0, file_path)
            self.first_page["file_entry"].configure(state="readonly")
        else:
            self.selected_file_path = None
            self.first_page["file_entry"].configure(state="normal")
            self.first_page["file_entry"].delete(0, "end")
            self.first_page["file_entry"].configure(state="readonly")

    def calculate_budget(self):
        self.entered_number = self.first_page["number_entry"].get()
        try:
            number = float(self.entered_number) if self.ga else 45
            if number <= 0:
                raise ValueError
            if self.selected_file_path or not self.ga:
                self.first_page["calculating_dialog"] = self.show_dialog("Розрахунок бюджету",
                                                                         "Виконується розрахунок бюджету...",
                                                                         self.calculate_center_position(300, 100))
                threading.Thread(target=self.perform_calculation, args=(self.selected_file_path, number)).start()
            else:
                self.show_dialog("Помилка", "Оберіть файл",
                                 self.calculate_center_position(300, 100))
        except ValueError:
            self.show_dialog("Помилка", "Введіть коректний період замовлення",
                             self.calculate_center_position(300, 100))

    def perform_calculation(self, file_path, number):
        try:
            self.min_budget, self.max_budget = self.ga.precalculate(file_path, number) if self.ga else (0, 100)
        except Exception as e:
            self.close_dialog("calculating_dialog")
            self.show_dialog("Помилка",
                             f"Помилка обробки. Перевірте вхідні дані або зверніться до адміністратора",
                             self.calculate_center_position(300, 100))
            print(e)
            return

        self.move_forward()

    def show_budget_input(self):
        self.close_dialog("calculating_dialog")
        self.clear_window()

        mode_frame = self.get_helpful_frame(pady=(10, 0))
        mode_label = ctk.CTkLabel(mode_frame, text="Режим роботи:", text_color=TEXT_COLOR, font=(FONT_HEAD, 38),
                                  justify="left")
        mode_label.pack(side="left", padx=30)
        budget_mode_frame = self.get_helpful_frame(pady=(5, 0))
        mode_button1 = ctk.CTkButton(budget_mode_frame, text="Одне рішення", text_color=WHITE_COLOR,
                                     font=(FONT_BUTTONS, 22), height=50, width=265, fg_color=VIOLET_DARK,
                                     command=lambda: self.update_budget_input(True))
        mode_button1.pack(side="left", padx=(30, 0))
        mode_button2 = ctk.CTkButton(budget_mode_frame, text="Кілька рішень", text_color=WHITE_COLOR,
                                     font=(FONT_BUTTONS, 22), height=50, width=265, fg_color=VIOLET_DARK,
                                     command=lambda: self.update_budget_input(False)
                                     if self.min_budget < self.max_budget else None)
        mode_button2.pack(side="left", padx=(10, 30))
        if self.min_budget == self.max_budget:
            mode_button2.configure(state="disabled")

        result_frame = self.get_helpful_frame(pady=(10, 0))
        result_label = ctk.CTkLabel(result_frame, text=f"Мінімальний бюджет: {self.min_budget}$\n"
                                                       f"Максимальний бюджет: {self.max_budget}$",
                                    text_color=TEXT_COLOR, font=(FONT_BODY, 25),
                                    justify="left")
        result_label.pack(side="left", padx=30)

        self.second_page = {
            "mode_frame": mode_frame,
            "mode_label": mode_label,
            "budget_mode_frame": budget_mode_frame,
            "mode_button1": mode_button1,
            "mode_button2": mode_button2,
            "result_frame": result_frame,
            "result_label": result_label
        }

        self.update_budget_input()

    def update_budget_input(self, single=True):
        self.budget_mode_single = single

        for widget in self.second_page.get('mode', {}).values():
            widget.pack_forget()

        budget_frame = self.get_helpful_frame(pady=(10, 0), padx=20,
                                              fg_color=WHITE_COLOR, fill="both", expand=True)
        if self.budget_mode_single:
            self.second_page.get("mode_button1").configure(fg_color=VIOLET_DARK)
            self.second_page.get("mode_button2").configure(fg_color=VIOLET_LIGHT)

            max_budget_frame, max_budget_label, max_budget_entry = self.create_beautiful_entry(
                budget_frame,
                "Бюджет:",
                (FONT_BODY, 26),
                (FONT_BODY, 26),
                pady=(20, 0),
                fg_color=WHITE_COLOR
            )

            self.second_page['mode'] = {
                "budget_frame": budget_frame,
                "max_budget_frame": max_budget_frame,
                "max_budget_label": max_budget_label,
                "max_budget_entry": max_budget_entry
            }
        else:
            self.second_page.get("mode_button1").configure(fg_color=VIOLET_LIGHT)
            self.second_page.get("mode_button2").configure(fg_color=VIOLET_DARK)

            min_budget_frame, min_budget_label, min_budget_entry = self.create_beautiful_entry(
                budget_frame,
                "Мінімальний бюджет:",
                (FONT_BODY, 26),
                (FONT_BODY, 26),
                pady=(20, 0),
                fg_color=WHITE_COLOR
            )

            max_budget_frame, max_budget_label, max_budget_entry = self.create_beautiful_entry(
                budget_frame,
                "Максимальний бюджет:",
                (FONT_BODY, 26),
                (FONT_BODY, 26),
                pady=(20, 0),
                fg_color=WHITE_COLOR
            )

            step_budget_frame, step_budget_label, step_budget_entry = self.create_beautiful_entry(
                budget_frame,
                "Крок:",
                (FONT_BODY, 26),
                (FONT_BODY, 26),
                pady=(20, 0),
                fg_color=WHITE_COLOR
            )

            self.second_page['mode'] = {
                "budget_frame": budget_frame,
                "min_budget_frame": min_budget_frame,
                "min_budget_label": min_budget_label,
                "min_budget_entry": min_budget_entry,
                "max_budget_frame": max_budget_frame,
                "max_budget_label": max_budget_label,
                "max_budget_entry": max_budget_entry,
                "step_budget_frame": step_budget_frame,
                "step_budget_label": step_budget_label,
                "step_budget_entry": step_budget_entry
            }

        run_algorithm_button = ctk.CTkButton(self, text="Запуск алгоритму", command=self.run_algorithm,
                                             fg_color=VIOLET_DARK, text_color=WHITE_COLOR, font=(FONT_BUTTONS, 32),
                                             border_width=0, height=60)
        run_algorithm_button.pack(side="top", padx=25, pady=(10, 25), fill="x")

        self.second_page['mode']['run_algorithm_button'] = run_algorithm_button

    def run_algorithm(self):
        self.solved = False

        try:
            if self.budget_mode_single:
                budget_entry = self.second_page.get('mode', {}).get("max_budget_entry")
                try:
                    max_budget = float(budget_entry.get()) if budget_entry and self.ga else 100
                except ValueError:
                    raise ValueError("Введіть коректний бюджет")
                if not max_budget:
                    raise ValueError("Заповніть поле бюджету")
                elif max_budget < 0:
                    raise ValueError("Бюджет повинен бути додатнім числом")
                elif max_budget < self.min_budget:
                    raise ValueError("Бюджет повинен бути більшим за мінімальний бюджет")
                elif max_budget > self.max_budget:
                    raise ValueError("Бюджет повинен бути меншим за максимальний бюджет")
                min_budget = 0
                step = 0
                single = True
            else:
                min_budget_entry = self.second_page.get('mode', {}).get("min_budget_entry")
                max_budget_entry = self.second_page.get('mode', {}).get("max_budget_entry")
                step_budget_entry = self.second_page.get('mode', {}).get("step_budget_entry")
                try:
                    min_budget = float(min_budget_entry.get()) if min_budget_entry and self.ga else 0
                except ValueError:
                    raise ValueError("Введіть коректний мінімальний бюджет")
                try:
                    max_budget = float(max_budget_entry.get()) if max_budget_entry and self.ga else 100
                except ValueError:
                    raise ValueError("Введіть коректний максимальний бюджет")
                try:
                    step = float(step_budget_entry.get()) if step_budget_entry and self.ga else 0
                except ValueError:
                    raise ValueError("Введіть коректний крок")
                if not min_budget or not max_budget or not step:
                    raise ValueError("Заповніть всі поля")
                elif step < 0:
                    raise ValueError("Крок повинен бути додатнім числом")
                elif step > max_budget - min_budget:
                    raise ValueError("Крок повинен бути меншим за різницю між максимальним і мінімальним бюджетом")
                elif min_budget > max_budget:
                    raise ValueError("Мінімальний бюджет повинен бути меншим за максимальний")
                if min_budget < self.min_budget:
                    raise ValueError("Мінімальний бюджет повинен бути більшим за мінімальний бюджет")
                if max_budget > self.max_budget:
                    raise ValueError("Максимальний бюджет повинен бути меншим за максимальний бюджет")
                single = False

            self.move_forward(max_budget, min_budget, step, single)
        except ValueError as e:
            self.show_dialog("Помилка", f"Помилка: {str(e)}",
                             self.calculate_center_position(400, 200), wraplength=370)

    def show_algorithm_page(self, max_budget, min_budget, step, single):
        self.clear_window()

        alg_frame = self.get_helpful_frame(pady=(20, 0))
        alg_label = ctk.CTkLabel(alg_frame, text="Виконується алгоритм...", text_color=TEXT_COLOR,
                                 font=(FONT_HEAD, 33), justify="left")
        alg_label.pack(side="left", padx=30)

        update_text = ctk.CTkTextbox(self, fg_color=TEXT_COLOR, font=("Consolas", 12))
        update_text.pack(side="top", padx=30, pady=10, fill="both", expand=True)

        self.third_page["update_text"] = update_text
        self.third_page["alg_frame"] = alg_frame
        self.third_page["alg_label"] = alg_label

        if self.ga and not self.solved:
            self.api = Api(lambda data: print_to_widget(self.alg_buffer, update_text, data))
            self.api.run()

            self.console_redirector.enable(update_text)

            self.toggle_buttons_state("disabled")

            threading.Thread(target=self.perform_run_algorithm,
                             args=(max_budget, min_budget, step, single)).start()
        else:
            update_text.insert(ctk.END, self.alg_buffer[0])
            update_text.see(ctk.END)
            update_text.update_idletasks()

            self.show_final_results()

    def perform_run_algorithm(self, max_budget, min_budget, step, single):
        try:
            self.ga.run(max_budget, min_budget, step, single=single,
                        pop_multiplier=self.pop_multiplier, max_gen_multiplier=self.max_gen_multiplier,
                        max_stall_gen_multiplier=self.max_stall_gen_multiplier) if self.ga else ""
        except Exception as e:
            self.close_dialog("calculating_dialog")
            self.show_dialog("Помилка",
                             "Помилка обробки. Перевірте вхідні дані або зверніться до адміністратора",
                             self.calculate_center_position(300, 100))
            print(e)
            return

        self.show_final_results()

    def show_final_results(self):
        self.console_redirector.disable()
        if self.api:
            self.api.stop()
            self.api = None
        self.toggle_buttons_state("normal")

        self.solved = True

        self.third_page["alg_label"].configure(text="Алгоритм завершено.")

        if self.ga and self.ga.solutions_amount > 1:
            # if True:
            budget_frame = self.get_helpful_frame(pady=(10, 0))
            budget_label = ctk.CTkLabel(budget_frame, text="Оберіть бюджет:", text_color=TEXT_COLOR,
                                        font=(FONT_BODY, 25), justify="left")
            budget_label.pack(side="left", padx=30)
            entry_var = ctk.StringVar()
            entry_var.trace_add(
                "write",
                lambda arg1, arg2, arg3, var=entry_var:
                self.third_page.get("save_button").configure(text="Зберегти всі рішення",
                                                             command=self.save_all_solutions)
                if not entry_var.get() else
                self.third_page.get("save_button").configure(text="Зберегти одне рішення",
                                                             command=self.save_one_solution)
            )
            budget_entry = ctk.CTkEntry(self, fg_color=VIOLET_LIGHT, text_color=TEXT_COLOR,
                                        font=(FONT_BODY, 26), justify="left", border_width=0, height=50,
                                        textvariable=entry_var)
            budget_entry.pack(side="top", padx=30, pady=5, fill="x")

            save_button = ctk.CTkButton(self, text="Зберегти всі рішення",
                                        command=self.save_all_solutions, fg_color=VIOLET_DARK,
                                        text_color=WHITE_COLOR, font=(FONT_BUTTONS, 26),
                                        border_width=0, height=50)
            save_button.pack(side="top", padx=30, pady=(10, 25), fill="x")

            graph_window = create_graph_window(self, self.ga.budgets, self.ga.profits)

            self.third_page["budget_frame"] = budget_frame
            self.third_page["budget_label"] = budget_label
            self.third_page["budget_entry"] = budget_entry
            self.third_page["save_button"] = save_button
            self.third_page["graph_window"] = graph_window
        else:
            save_button = ctk.CTkButton(self, text="Зберегти рішення",
                                        command=lambda: self.save_one_solution(single=True), fg_color=VIOLET_DARK,
                                        text_color=WHITE_COLOR, font=(FONT_BUTTONS, 32),
                                        border_width=0, height=50)
            save_button.pack(side="top", padx=30, pady=(10, 25), fill="x")

            self.third_page["save_button"] = save_button

    def save_one_solution(self, single=False):
        if budget_entry := self.third_page.get("budget_entry"):
            budget = float(budget_entry.get())
        else:
            budget = None

        if self.ga:
            if budget and budget in self.ga.budgets or single:
                selected_dir = askdirectory(
                    title="Оберіть папку для збереження",
                    initialdir=self.current_path
                )
                if selected_dir:
                    self.ga.save_solution(selected_dir, budget if not single else None)
                    self.show_dialog("Рішення збережено", "Рішення збережено успішно",
                                     self.calculate_center_position(300, 100))
            else:
                self.show_dialog("Помилка", "Введіть коректний бюджет",
                                 self.calculate_center_position(300, 100))

    def save_all_solutions(self):
        selected_dir = askdirectory(
            title="Оберіть папку для збереження",
            initialdir=self.current_path
        )

        if selected_dir and self.ga:
            self.ga.save_solution(selected_dir)
            self.show_dialog("Рішення збережено", "Рішення збережені успішно",
                             self.calculate_center_position(300, 100))

    def toggle_buttons_state(self, state):
        for widget in (list(self.first_page.values()) + list(self.second_page.values()) +
                       list(self.second_page.get('mode', {}).values()) + list(self.third_page.values())):
            if isinstance(widget, ctk.CTkEntry) or isinstance(widget, ctk.CTkButton):
                widget.configure(state=state)
        for widget in [self.forward_button, self.back_button, self.settings_button]:
            if widget:
                widget.configure(state=state)

    def clear_window(self):
        for widget in self.winfo_children():
            if widget != self.header and widget not in self.header.winfo_children():
                if not isinstance(widget, ctk.CTkToplevel):
                    widget.pack_forget()
                else:
                    widget.destroy()


if __name__ == "__main__":
    app = App()
    app.mainloop()
