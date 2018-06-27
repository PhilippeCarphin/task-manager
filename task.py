import tkinter as tk
import json
from datetime import datetime, time
from tkinter import ttk

import sqlalchemy
from sqlalchemy import Column, Integer, String, DateTime, Time, Boolean
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.types import TypeDecorator


class TextPickleType(TypeDecorator):

    impl = sqlalchemy.Text(3000)

    def process_bind_param(self, value, dialect):
        if value is not None:
            value = json.dumps(value)
        return value

    def process_result_value(self, value, dialect):
        if value is not None:
            value = json.loads(value)
        return value


Base = declarative_base()


class Task(Base):
    __tablename__ = 'tasks'

    id = Column(Integer, primary_key=True)
    value = Column(Integer)
    due_date = Column(DateTime)
    due_date_importance = Column(Integer)
    past_due_importance_decrease_rate = Column(Integer)
    description = Column(String(3000))
    time_per_week = Column(Time)
    absolute_date = Column(Boolean)
    extra = Column(TextPickleType)

    def __str__(self):
        return str(self.__dict__)

    @classmethod
    def get_column_names(cls):
        return [c.name for c in cls.__table__.columns]

    @property
    def time_left(self):
        tl = self.due_date - datetime.now()
        return tl.days * 24 + tl.seconds/3600

    @property
    def past_due(self):
        return self.due_date < datetime.now()

    @property
    def importance(self):
        if not self.past_due:
            return self.value * self.due_date_importance * (24/self.time_left)
        else:
            return self.value * self.due_date_importance / (self.past_due_importance_decrease_rate * (-self.time_left))


engine = create_engine('sqlite:////home/pcarphin/Documents/GitHub/task-manager/db.sqlite', echo=True)
SessionClass = sessionmaker(bind=engine)
Base.metadata.create_all(engine)


class Application(tk.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.pack()
        self.inputs = {}
        self.submit = None
        self.quit = None
        self.create_widgets()

    def create_widgets(self):
        for attr in Task.get_column_names():
            self.inputs[attr] = ttk.Entry(self)
            self.inputs[attr].pack()
        self.inputs['value'].insert(0, '8')
        self.inputs['due_date'].insert(0, datetime.now().strftime('%Y/%m/%d %H:%M'))
        self.inputs['due_date_importance'].insert(0, '1')
        self.inputs['past_due_importance_decrease_rate'].insert(0, 7)
        self.inputs['description'].insert(0, 'This is the description of the task')
        self.inputs['time_per_week'].insert(0, '1,2,3,4')
        self.inputs['absolute_date'].insert(0, 'False')
        self.inputs['extra'].insert(0, '{"bonjour":"allo"}')
        self.submit = ttk.Button(self)
        self.submit["text"] = "Submit Task"
        self.submit["command"] = self.create_task
        self.submit.pack(side="top")

        self.quit = tk.Button(self, text="QUIT", fg="red", command=root.destroy)
        self.quit.pack(side="bottom")

    def create_task(self):
        t = Task()
        for attr, input_field in [i for i in self.inputs.items() if i[0] != 'id']:
            if attr == 'id':
                pass
            elif attr == 'due_date':
                t.due_date = datetime.strptime(input_field.get(), '%Y/%m/%d %H:%M')
            elif attr == 'time_per_week':
                t.time_per_week = time(*(map(int, input_field.get().split(','))))
            elif attr == 'absolute_date':
                t.absolute_date = True if input_field.get() in ['True', 'true', '1', 1] else False
            elif attr == 'extra':
                t.extra = json.loads(input_field.get())
            else:
                t.__dict__[attr] = input_field.get()
        session = SessionClass()
        session.add(t)
        session.commit()
        print(t.importance)
        self.inputs['id'].delete(0, 'end')
        self.inputs['id'].insert(0, t.id)


if __name__ == '__main__':
    root = tk.Tk()
    app = Application(master=root)
    app.mainloop()
