import os
import threading
import tkinter as tk
from tkinter import filedialog
from tkinter.filedialog import askdirectory
from tkinter.scrolledtext import ScrolledText

from backend.python.genetic_algorithm import GeneticAlgorithm
from frontend.console_redirector import ConsoleRedirector


class App(tk.Tk):
    def __init__(self):
        super().__init__()
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
        self.budget_mode = tk.StringVar(value="Single")

        self.current_path = os.path.dirname(os.path.abspath(__file__))
        self.parent_path = os.path.abspath(os.path.join(self.current_path, os.pardir))

        self.title("Рекомендаційна система для роздрібної торгівлі")
        self.geometry("1280x720")

        self.ga = GeneticAlgorithm("../backend/config.json")

        self.init_main_window()

        self.console_redirector = ConsoleRedirector()

    def init_main_window(self):
        self.clear_window()

        self.header = tk.Frame(self)
        self.header.pack(side="top", pady=10, fill="x")

        self.forward_button = tk.Button(self.header, text="Вперед", command=self.show_budget_input)
        self.forward_button.pack(side="right", padx=10)
        if self.min_budget is not None and self.max_budget is not None:
            self.forward_button.config(state="normal")
        else:
            self.forward_button.config(state="disabled")

        number_label = tk.Label(self, text="Введіть максимальний період замовлення:")
        number_label.pack(side="top", pady=10)

        number_entry = tk.Entry(self)
        number_entry.pack(side="top", padx=10, pady=5)
        if self.entered_number is not None:
            number_entry.insert(0, str(self.entered_number))

        file_label = tk.Label(self, text=f"Обраний файл: {self.selected_file_path or 'Немає'}")
        file_label.pack(side="top", pady=10)

        file_button = tk.Button(self, text="Обрати файл", command=self.select_file)
        file_button.pack(side="top", padx=10, pady=5)

        calculate_button = tk.Button(self, text="Розрахувати бюджет", command=self.calculate_budget)
        calculate_button.pack(side="top", padx=10, pady=5)

        result_label = tk.Label(self, text="")
        result_label.pack(side="top", pady=10)

        self.first_page = {
            "number_label": number_label,
            "number_entry": number_entry,
            "file_label": file_label,
            "file_button": file_button,
            "calculate_button": calculate_button,
            "result_label": result_label
        }

    def calculate_center_position(self, width, height):
        main_window_x = self.winfo_x()
        main_window_y = self.winfo_y()
        main_window_width = self.winfo_width()
        main_window_height = self.winfo_height()

        dialog_x = main_window_x + (main_window_width - width) // 2
        dialog_y = main_window_y + (main_window_height - height) // 2

        return f"{width}x{height}+{dialog_x}+{dialog_y}"

    def show_dialog(self, title, message, geometry):
        dialog = tk.Toplevel(self)
        dialog.title(title)
        dialog.geometry(geometry)
        dialog.transient(self)

        label = tk.Label(dialog, text=message)
        label.pack(expand=True, padx=10, pady=10)

        dialog.grab_set()

        return dialog

    def close_dialog(self, key):
        if calculating_dialog := self.first_page.get(key):
            calculating_dialog.grab_release()
            calculating_dialog.destroy()
            del self.first_page[key]

    def select_file(self):
        file_path = filedialog.askopenfilename(
            title="Select file",
            filetypes=(("Excel files", "*.xlsx"), ("All files", "*.*")),
            initialdir=self.parent_path
        )
        if file_path:
            self.selected_file_path = file_path
            self.first_page["file_label"].config(text=f"Обраний файл: {file_path}")
        else:
            self.selected_file_path = None
            self.first_page["file_label"].config(text="Обраний файл: Немає")

    def calculate_budget(self):
        self.entered_number = self.first_page["number_entry"].get()
        try:
            number = float(self.entered_number)
            if number <= 0:
                raise ValueError
            if self.selected_file_path:
                self.toggle_buttons_state("disabled")
                self.first_page["calculating_dialog"] = self.show_dialog("Розрахунок бюджету",
                                                                         "Виконується розрахунок бюджету...",
                                                                         self.calculate_center_position(300, 100))
                threading.Thread(target=self.perform_calculation, args=(self.selected_file_path, number)).start()
            else:
                self.first_page["result_label"].config(text="Помилка: оберіть файл")
        except ValueError:
            self.first_page["result_label"].config(text="Помилка: введіть коректний період замовлення")

    def perform_calculation(self, file_path, number):
        try:
            self.min_budget, self.max_budget = self.ga.precalculate(file_path, number)
            # self.min_budget = 0; self.max_budget = 100
            result = f"Мінімальний бюджет: {self.min_budget}$\nМаксимальний бюджет: {self.max_budget}$"
        except Exception as e:
            result = f"Помилка: {str(e)}"

        self.first_page["result_label"].after(0, self.show_budget_input, result)

    def show_budget_input(self, result=None):
        self.first_page["result_label"].config(text=result)
        self.close_dialog("calculating_dialog")
        self.toggle_buttons_state("normal")
        self.clear_window()

        self.header = tk.Frame(self)
        self.header.pack(side="top", pady=10, fill="x")

        self.back_button = tk.Button(self.header, text="Повернутись", command=self.init_main_window)
        self.back_button.pack(side="left", padx=10)

        self.forward_button = tk.Button(self.header, text="Вперед", command=self.show_final_results)
        self.forward_button.pack(side="right", padx=10)
        if self.solved:
            self.forward_button.config(state="normal")
        else:
            self.forward_button.config(state="disabled")

        budget_mode_frame = tk.Frame(self)
        budget_mode_frame.pack(side="top", pady=10)

        self.first_page["result_label"] = tk.Label(self,
                                                   text=f"Мінімальний бюджет: {self.min_budget}$\n"
                                                        f"Максимальний бюджет: {self.max_budget}$")
        self.first_page["result_label"].pack(side="top", pady=10)

        mode_label = tk.Label(budget_mode_frame, text="Оберіть режим роботи:")
        mode_label.pack(side="top", pady=5)
        mode_button1 = tk.Radiobutton(budget_mode_frame, text="Одне рішення", variable=self.budget_mode,
                                      value="Single", command=self.update_budget_input)
        mode_button1.pack(side="left")
        mode_button2 = tk.Radiobutton(budget_mode_frame, text="Кілька рішень", variable=self.budget_mode,
                                      value="Multiple", command=self.update_budget_input)
        mode_button2.pack(side="left")

        self.second_page = {
            "mode_label": mode_label,
            "mode_button1": mode_button1,
            "mode_button2": mode_button2
        }

        self.update_budget_input()

    def update_budget_input(self):
        for widget in self.second_page.get('mode', {}).values():
            widget.pack_forget()

        if self.budget_mode.get() == "Single":
            max_budget_label = tk.Label(self, text="Бюджет:")
            max_budget_label.pack(side="top", pady=5)
            max_budget_entry = tk.Entry(self)
            max_budget_entry.pack(side="top", padx=10, pady=5)

            self.second_page['mode'] = {
                "max_budget_label": max_budget_label,
                "max_budget_entry": max_budget_entry
            }
        else:
            min_budget_label = tk.Label(self, text="Мінімальний бюджет:")
            min_budget_label.pack(side="top", pady=5)
            min_budget_entry = tk.Entry(self)
            min_budget_entry.pack(side="top", padx=10, pady=5)

            max_budget_label = tk.Label(self, text="Максимальний бюджет:")
            max_budget_label.pack(side="top", pady=5)
            max_budget_entry = tk.Entry(self)
            max_budget_entry.pack(side="top", padx=10, pady=5)

            step_budget_label = tk.Label(self, text="Крок:")
            step_budget_label.pack(side="top", pady=5)
            step_budget_entry = tk.Entry(self)
            step_budget_entry.pack(side="top", padx=10, pady=5)

            self.second_page['mode'] = {
                "min_budget_label": min_budget_label,
                "min_budget_entry": min_budget_entry,
                "max_budget_label": max_budget_label,
                "max_budget_entry": max_budget_entry,
                "step_budget_label": step_budget_label,
                "step_budget_entry": step_budget_entry
            }

        run_algorithm_button = tk.Button(self, text="Запуск алгоритму", command=self.run_algorithm)
        run_algorithm_button.pack(side="top", padx=10, pady=5)

        error_label = tk.Label(self, text="")
        error_label.pack(side="top", pady=10)

        self.second_page['mode']['run_algorithm_button'] = run_algorithm_button
        self.second_page['mode']['error_label'] = error_label

    def run_algorithm(self):
        try:
            if self.budget_mode.get() == "Single":
                budget_entry = self.second_page.get('mode', {}).get("max_budget_entry")
                max_budget = float(budget_entry.get()) if budget_entry else None
                if not max_budget:
                    raise ValueError
                elif max_budget < self.min_budget:
                    max_budget = self.min_budget
                elif max_budget > self.max_budget:
                    max_budget = self.max_budget
                min_budget = 0
                step = 0
                single = True
            else:
                min_budget_entry = self.second_page.get('mode', {}).get("min_budget_entry")
                max_budget_entry = self.second_page.get('mode', {}).get("max_budget_entry")
                step_budget_entry = self.second_page.get('mode', {}).get("step_budget_entry")
                min_budget = float(min_budget_entry.get()) if min_budget_entry else None
                max_budget = float(max_budget_entry.get()) if max_budget_entry else None
                step = float(step_budget_entry.get()) if step_budget_entry else None
                if not min_budget or not max_budget or not step:
                    raise ValueError("Заповніть всі поля")
                elif step < 0:
                    raise ValueError("Крок повинен бути додатнім числом")
                elif step > max_budget - min_budget:
                    raise ValueError("Крок повинен бути меншим за різницю між максимальним і мінімальним бюджетом")
                elif min_budget > max_budget:
                    raise ValueError("Мінімальний бюджет повинен бути меншим за максимальний")
                if min_budget < self.min_budget:
                    min_budget = self.min_budget
                if max_budget > self.max_budget:
                    max_budget = self.max_budget
                single = False

            self.toggle_buttons_state("disabled")
            dialog = self.first_page["calculating_dialog"] = self.show_dialog(
                "Виконання алгоритму",
                "Йде виконання алгоритму...",
                self.calculate_center_position(640, 480)
            )
            # text_widget = ScrolledText(dialog, wrap=tk.WORD)
            # text_widget.pack(expand=True, fill="both", padx=10, pady=10)
            # self.console_redirector.enable(text_widget)

            threading.Thread(target=self.perform_run_algorithm, args=(max_budget, min_budget, step, single)).start()
            self.second_page.get('mode', {})["error_label"].config(text="")
        except ValueError as e:
            self.second_page.get('mode', {})["error_label"].config(text=f"Помилка: {str(e)}")

    def perform_run_algorithm(self, max_budget, min_budget, step, single):
        try:
            result = self.ga.run(max_budget, min_budget, step, single=single)
            # self.min_budget = 0; self.max_budget = 100
        except Exception as e:
            result = f"Помилка: {str(e)}"

        self.first_page["result_label"].after(0, self.show_final_results, result)

    def show_final_results(self, result=None):
        self.first_page["result_label"].config(text=result)
        # self.console_redirector.disable()
        self.close_dialog("calculating_dialog")
        self.toggle_buttons_state("normal")
        self.clear_window()

        self.solved = True

        self.header = tk.Frame(self)
        self.header.pack(side="top", pady=10, fill="x")

        self.back_button = tk.Button(self.header, text="Повернутись", command=self.show_budget_input)
        self.back_button.pack(side="left", padx=10)

        final_results_frame = tk.Frame(self)
        final_results_frame.pack(side="top", pady=10)

        if self.ga.solutions_amount > 1:
            budget_label = tk.Label(final_results_frame, text="Оберіть бюджет:")
            budget_label.pack(side="top", padx=10)
            budget_entry = tk.Entry(final_results_frame)
            budget_entry.pack(side="top", padx=10, pady=5)

            save_one_button = tk.Button(final_results_frame, text="Зберегти одне рішення",
                                        command=self.save_one_solution)
            save_one_button.pack(side="left", padx=10, pady=5)
            save_all_button = tk.Button(final_results_frame, text="Зберегти всі рішення",
                                        command=self.save_all_solutions)
            save_all_button.pack(side="left", padx=10, pady=5)

            self.third_page["budget_label"] = budget_label
            self.third_page["budget_entry"] = budget_entry
            self.third_page["save_one_button"] = save_one_button
            self.third_page["save_all_button"] = save_all_button
        else:
            self.save_one_solution()

    def save_one_solution(self):
        selected_dir = askdirectory(
            title="Оберіть папку для збереження",
            initialdir=self.parent_path
        )

        if budget_entry := self.third_page.get("budget_entry"):
            budget = float(budget_entry.get())
        else:
            budget = None

        if selected_dir:
            self.ga.save_solution(selected_dir, budget)
            self.first_page["result_label"].config(text="Рішення збережено")

    def save_all_solutions(self):
        selected_dir = askdirectory(
            title="Оберіть папку для збереження",
            initialdir=self.parent_path
        )

        if selected_dir:
            self.ga.save_solution(selected_dir)
            self.first_page["result_label"].config(text="Рішення збережені")

    def toggle_buttons_state(self, state):
        for widget in (list(self.first_page.values()) + list(self.second_page.values()) +
                       list(self.second_page.get('mode', {}).values()) + list(self.third_page.values())):
            if hasattr(widget, "config"):
                widget.config(state=state)

    def clear_window(self):
        for widget in self.winfo_children():
            widget.pack_forget()


if __name__ == "__main__":
    app = App()
    app.mainloop()
