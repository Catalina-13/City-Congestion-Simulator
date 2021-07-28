from tkinter import *
from tkinter import messagebox
from tkinter.ttk import *
from typing import Callable
from tkcalendar import Calendar
from PIL import ImageTk, Image
from datetime import *

class UI:
    def set_image(self, fp) -> None:
        i = Image.open(fp)
        i = i.resize((700, 500), Image.ANTIALIAS)
        i = ImageTk.PhotoImage(i)
        self.img.configure(image=i)
        self.img.image = i

    def open_window(self, onclick: Callable[[Tk, datetime, str], None]) -> None:
        master = Tk()
        master.title("idk")
        master.geometry("700x800")

        def range_changed(s):
            r = float(s)
            setattr(w, "range", r)
            lbl["text"] = str(int(r)) + "h"

        w = Scale(master, from_=0, to=23.999, length=700, command=range_changed)
        setattr(w, "range", 0.0)
        w.pack()
        lbl = Label()
        lbl["text"] = "0h"
        lbl.pack()
        cal = Calendar(master, selectmode='day', year=datetime.now().year, month=datetime.now().month, day=1)
        cal.pack()

        def predict():
            if self.switch_variable.get() == "":
                messagebox.showerror("Error", "No type selected")
                return
            d = datetime.combine(cal.selection_get(), time()) + timedelta(seconds=int(w.range * 3600))
            self.button["state"] = "disabled"
            self.button["text"] = "Loading..."
            master.update()
            onclick(master, d, self.switch_variable.get())
            self.button["state"] = "enabled"
            self.button["text"] = "Predict"
            master.update()

        switch_frame = Frame(master)
        switch_frame.pack()

        self.switch_variable = switch_variable = StringVar(value="")
        heatmap = Radiobutton(switch_frame, text="Heatmap", variable=switch_variable,
                                    value="heatmap", width=8)
        streetmap = Radiobutton(switch_frame, text="Street map", variable=switch_variable,
                                    value="streetmap", width=8)
        heatmap.pack(side="left")
        streetmap.pack(side="left")


        self.button = Button(master, text="Predict", command=predict)
        self.button.pack()

        self.img = Label(master)
        self.img.pack(side="bottom", fill="both", expand=True)

        Style().theme_use("aqua") # ('aqua', 'clam', 'alt', 'default', 'classic')

        mainloop()


if __name__ == "__main__":
    ui = UI()
    ui.open_window(lambda _, _1, _2: ui.set_image(open("data_visualisation/2009.png", "rb")))
