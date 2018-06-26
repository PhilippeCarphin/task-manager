import tkinter as tk
from tkinter import ttk

class Task:
    def __init__(self, id, value=None, due_date=None, due_date_importance=None,
            past_due_importance_decrease_rate=None, time_per_week=None,
            description=None):
        self.id = id
        self.value = value
        self.due_date = due_date
        self.due_date_importance = due_date_importance
        self.past_due_importance_decrease_rate = past_due_importance_decrease_rate
        self.description = description
        self.time_per_week = time_per_week

    @property
    def importance(self):
        # if not past due
        return value * due_date_importance * (1.0 / nb_days_left)
        # else
        return value * (due_date_importance - past_due_importance_decrease_rate * nb_days_past_due)

class Hobby(Task):
    def __init__(self, id, value=None, due_date=None, due_date_importance=None,
            past_due_importance_decrease_rate=None, time_per_week=None,
            description=None):
        super().__init__(self, id, value=None, due_date=None, due_date_importance=None,
            past_due_importance_decrease_rate=None, time_per_week=None,
            description=None)

    @property
    def importance(self):
        return value * time_per_week

class Application(tk.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.pack()
        self.create_widgets()

    def create_widgets(self):
        self.hi_there = ttk.Button(self)
        self.hi_there["text"] = "Hello World\n(click me)"
        self.hi_there["command"] = self.say_hi
        self.hi_there.pack(side="top")
        self.input1 = tk.Entry(self)
        self.input1.insert(0,"value")
        self.input1.pack()

        self.quit = tk.Button(self, text="QUIT", fg="red",
                              command=root.destroy)
        self.quit.pack(side="bottom")

    def say_hi(self):
        print("hi there, everyone!")
        print(self.input1.get())

root = tk.Tk()
app = Application(master=root)
app.mainloop()
