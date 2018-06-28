import tkinter as tk
import json
import os
from datetime import datetime, time
from tkinter import ttk

import sqlalchemy
from sqlalchemy import Column, Integer, String, DateTime, Time, Boolean
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.types import TypeDecorator

DEFAULTS = {
        'value': '8',
        'due_date': datetime.now().strftime('%Y/%m/%d %H:%M'),
        'due_date_importance': '1',
        'past_due_importance_decrease_rate': 7,
        'description': 'This is the description of the task',
        'time_per_week': '1,2,3,4',
        'absolute_date': 'False',
        'extra': '{"bonjour":"allo"}'
}


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

    id = Column(Integer, sqlalchemy.Sequence('user-id-seq'), primary_key=True)
    value = Column(Integer)
    due_date = Column(DateTime)
    due_date_importance = Column(Integer)
    past_due_importance_decrease_rate = Column(Integer)
    description = Column(String(3000))
    time_per_week = Column(Time)
    absolute_date = Column(Boolean)
    extra = Column(TextPickleType)

    def __repr__(self):
        return "<{}(id={}, description='{}'. importance={})".format(
            __class__.__name__, self.id, self.description, self.importance
        )

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

    def as_list(self):
        return [self.id, self.value, self.due_date, self.due_date_importance, self.past_due_importance_decrease_rate,
                self.description, self.time_per_week, self.absolute_date, self.extra, self.importance]

    @classmethod
    def query_all(cls):
        sesh = SessionClass()
        return sesh.query(cls).order_by(cls.id)

    @classmethod
    def delete_list(cls, id_list):
        sesh = SessionClass()
        for elem_id in id_list:
            sesh.query(Task).filter(Task.id == elem_id).delete()
        sesh.commit()

def dbpath():
    this_file = os.path.abspath(__file__)
    this_dir = os.path.dirname(this_file)
    return os.path.join(this_dir, 'db.sqlite')

engine = create_engine('sqlite:///' + dbpath())
SessionClass = sessionmaker(bind=engine)
Base.metadata.create_all(engine)


class TaskView(ttk.Treeview):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs,  height=10, columns=list(Task.get_column_names()) + ['importance'],
                         displaycolumns=[0, 1, 2, 3, 4, 5, 6, 7, 8, 9], show='headings')
        n = 0
        for c in Task.get_column_names():
            self.heading(n, text=c)
            n += 1

    def show_list(self, task_list):
        for t in task_list:
            self.insert('', 0, iid=t.id, values=t.as_list()+[t.importance])


class Application(tk.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.pack()
        self.inputs = {}
        self.submit = ttk.Button(self)
        self.quit = tk.Button(self)
        self.task_view = TaskView(self)
        self.delete = tk.Button(self)
        self.create_widgets()

    def create_widgets(self):
        for attr in Task.get_column_names():
            self.inputs[attr] = ttk.Entry(self)
            self.inputs[attr].pack()
            attr != 'id' and self.inputs[attr].insert(0, DEFAULTS[attr])

        self.submit.config(text="Submit Task", command=self.create_task)
        self.submit.pack(side="top")

        self.task_view.pack()
        self.task_view.show_list(Task.query_all())

        self.quit.configure(text="QUIT", fg="red", command=root.destroy)
        self.quit.pack(side="bottom")

        self.delete.configure(text="delete_selected", fg='red', command=self.delete_selected)
        self.delete.pack()

    def task_from_inputs(self):
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
        return t

    def create_task(self):
        new_task = self.task_from_inputs()

        session = SessionClass()
        session.add(new_task)
        session.commit()

        self.task_view.insert('', 0, new_task.id, values=new_task.as_list())

    def delete_selected(self):
        sel = self.task_view.selection()
        Task.delete_list(sel)
        self.task_view.delete(*sel)


if __name__ == '__main__':
    root = tk.Tk()
    app = Application(master=root)
    app.mainloop()
