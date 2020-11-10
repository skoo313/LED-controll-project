import tkinter as tk
from tkinter import ttk
from tkinter import *
from tkinter.ttk import *
from tkinter import *
from tkmacosx import Button, ColorVar, Marquee, Colorscale
import socket
import sys
import os
import ast
import time
import json
from colorsys import rgb_to_hls, hls_to_rgb
from colour import Color
from tkinter import *
from tkscrolledframe import ScrolledFrame
# definiuję adres:port modułu wifi z którym bede sie łączył
HOST, PORT = "192.168.0.241", 8888  # 241   157

# główne okno aplikacji
root = tk.Tk()


# definicje stylów i kolorów
LARGE_FONT = ("ariel", 20)  # dont know what you had here
def_color = '#202020'
def_color2 = '#252525'
style = Style()
style.theme_use("clam")
style.configure("Treeview.Heading", background="#434343",
                foreground="white", relief="flat")
style.configure("Treeview", background="#353535",
                fieldbackground="#282828", foreground="white")
style.configure('Header.Label', font=('Arial', 30, 'bold'),
                foreground='#D3D3D3', background=def_color)
style.configure('TButton', font=('Arial', 20, 'bold'),
                foreground='#A8A8A8', background="#353535")
style.configure('TCheckbutton', font=('Arial', 10),
                foreground='#A8A8A8', background="#353535")

s = ttk.Style()
s.configure("TMenubutton", background="red")


def hex_rgb(col):
    return tuple(int(col.lstrip('#')[i:i+2], 16) for i in (0, 2, 4))

dictionary={"OrangeRed": "#ff4500", "orange":"#ffa500","cyan":"#00FFFF","lime":"#bfff00","chartreuse":"#7fff00", "magenta":"#ff0090","black":"#000000","SpringGreen":"#00ff7f","DeepSkyBlue":"#00bfff", "blue":"#0000ff"}
def error_colors(name):
    global dictionary
    if name in dictionary.keys():
        print("Replaced "+name+" to: "+ str(dictionary[name]))

        return dictionary[name]
    else:
        print("No such value in dict...")
        return "#000000"


class Main():
    """ Główna klasa aplikacji odpowiedzialna za stworzenie głównych obszarów (Frame) i wypełnianie ich odpowiednią zawartością"""

    def __init__(self, root):

        root.grid_rowconfigure(0, weight=1)  # this needed to be added
        root.grid_columnconfigure(0, weight=1)  # as did this

        # tworzy główny kontener na zawartość
        main_container = Frame(root)
        main_container.grid(column=0, row=0, sticky="nsew")
        main_container.grid_rowconfigure(0, weight=1)
        main_container.grid_columnconfigure(0, weight=1)

        self.frames = {}

        # tworzy i ustawia wartości początkowe dla istniejących klas (podstron)
        for fr in (MainPage, OneColorPage, GradientColorPage, TPM, SegmentColorPage):
            frame = fr(main_container, self)
            self.frames[fr] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame(MainPage)

    def show_frame(self, pointer):
        """ Funkcja wywołująca odpowiednią klasę w ramce (Frame) """
        frame = self.frames[pointer]
        frame.tkraise()


class MainPage(tk.Frame):
    """ Klasa będąca stroną startową aplikacji """

    def __init__(self, parent, controller):

        # inicjuje ramkę dla podstrony
        tk.Frame.__init__(self, parent, bg=def_color)

        # ustawia odpowiednie szerokosci i wysokości kolumn i rzędów w układzie elementów
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)

        self.rowconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)
        self.rowconfigure(2, weight=1)

        # Nagłówek aplikacji
        label = ttk.Label(self, style="Header.Label",
                          text="LED Controller", font=LARGE_FONT)
        label.grid(row=0, column=0, columnspan=2, padx=10, pady=10)

        # Przyciski z dostępnymi opcjami
        button1 = ttk.Button(self, text="One color",
                             command=lambda: controller.show_frame(OneColorPage))
        button1.grid(row=1, column=0, sticky='nswe', padx=10, pady=10)

        button2 = ttk.Button(self, text="Gradient color",
                             command=lambda: controller.show_frame(GradientColorPage))
        button2.grid(row=1, column=1, sticky='nswe', pady=10)

        button3 = ttk.Button(
            self, text="TPM", command=lambda: controller.show_frame(TPM))
        button3.grid(row=2, column=0, sticky='nswe', padx=10)

        button4 = ttk.Button(self, text="OPT_4")
        button4.grid(row=2, column=1, sticky='nswe')


class ColorMain(tk.Frame):
    """ Klasa z głównymi funkcjami wyboru kolorów """

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent, bg=def_color)

        # ustawia odpowiednie szerokosci i wysokości kolumn i rzędów w układzie elementów
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)

    def switchVar(self, op, var1, var2):
        """ Funkcja ustawiająca wybór użytkownika dotyczący sposobu educji koloru (checkbox'y). Aktywna może być tylko jedna opcja. """
        if(op == 'basic'):
            if(var1.get() == 1):
                var2.set(0)
            elif(var2.get() == 0):
                var1.set(1)
            self.load_color_opt("basic")
        elif(op == 'rgb'):
            if(var2.get() == 1):
                var1.set(0)
            elif(var1.get() == 0):
                var2.set(1)
            self.load_color_opt("rgb")

        elif(op == 'color_from'):
            if(var1.get() == 1):
                var2.set(0)
            elif(var2.get() == 0):
                var1.set(1)
        elif(op == 'color_to'):
            if(var2.get() == 1):
                var1.set(0)
            elif(var1.get() == 0):
                var2.set(1)

        if(op == 'solid_color'):
            var1.set(1)
            var2.set(1)

    def load_color_opt(self, opt):

        for widget in self.color_chooser_frame.winfo_children():
            widget.destroy()

        if(opt == "basic"):
            self.color_chooser_frame.rowconfigure(0, weight=1)
            self.color_chooser_frame.rowconfigure(1, weight=1)
            self.color_chooser_frame.rowconfigure(2, weight=0)
            self.color_chooser_frame.columnconfigure(0, weight=1)
            self.color_chooser_frame.columnconfigure(1, weight=1)
            # ,,Slider'y" dla koloru i jasnosci
            var2 = ColorVar(value='white')
            var3 = ColorVar(value='white')
            Colorscale(self.color_chooser_frame, value='hex', showinfo=False, command=lambda var3: self.changeColor(
                var3),            variable=self.colorTmp, mousewheel=1)                                  .grid(row=0, column=0, columnspan=2, sticky="nesw")
            Colorscale(self.color_chooser_frame, value='hex', showinfo=False, command=lambda var2: self.changeBrightness(
                var2), variable=var2, mousewheel=1, gradient=('#000000', '#FFFFFF')).grid(row=1, column=0, columnspan=2, sticky="nesw")
        else:
            self.color_chooser_frame.rowconfigure(0, weight=1)
            self.color_chooser_frame.rowconfigure(1, weight=1)
            self.color_chooser_frame.rowconfigure(2, weight=1)

            self.color_chooser_frame.columnconfigure(0, weight=3)
            self.color_chooser_frame.columnconfigure(1, weight=1)

            # ,,Slider'y" dla koloru i jasnosci
            r = ColorVar(value='white')
            r.set('#000000')
            g = ColorVar(value='white')
            g.set('#000000')
            b = ColorVar(value='white')
            b.set('#000000')
            Colorscale(self.color_chooser_frame, value='hex', showinfo=False, command=lambda r: self.changeColorRGB(r, g.get(), b.get(
            )),  variable=r, mousewheel=1, gradient=('#000000', '#ff0000'))                                  .grid(row=0, column=0, sticky="nesw")
            Colorscale(self.color_chooser_frame, value='hex', showinfo=False, command=lambda g: self.changeColorRGB(
                r.get(), g, b.get()), variable=g, mousewheel=1, gradient=('#000000', '#00FF00')).grid(row=1, column=0, sticky="nesw")
            Colorscale(self.color_chooser_frame, value='hex', showinfo=False, command=lambda b: self.changeColorRGB(
                r.get(), g.get(), b), variable=b, mousewheel=1, gradient=('#000000', '#0000FF')).grid(row=2, column=0, sticky="nesw")

            self.rLabel = Label(self.color_chooser_frame, font=('Arial', 20, 'bold'), foreground='#A8A8A8',
                                background="#353535", text="R:"+str(hex_rgb(r.get())[0]), bg=def_color)
            self.rLabel.grid(row=0, column=1, sticky="nesw")

            self.gLabel = Label(self.color_chooser_frame, font=('Arial', 20, 'bold'), foreground='#A8A8A8',
                                background="#353535", text="G:"+str(hex_rgb(g.get())[0]), bg=def_color)
            self.gLabel.grid(row=1, column=1, sticky="nesw")

            self.bLabel = Label(self.color_chooser_frame, font=('Arial', 20, 'bold'), foreground='#A8A8A8',
                                background="#353535", text="B:"+str(hex_rgb(b.get())[0]), bg=def_color)
            self.bLabel.grid(row=2, column=1, sticky="nesw")

    def changeColorRGB(self, red, green, blue):
        print(red)
        # wartość koloru w formacie hex przelicza na rgb

        r = hex_rgb(red)
        g = hex_rgb(green)
        b = hex_rgb(blue)

        self.rLabel.configure(text="R:"+str(r[0]))
        self.gLabel.configure(text="R:"+str(g[1]))
        self.bLabel.configure(text="R:"+str(b[2]))
        print(b)

        self._colorValue.set(value='#%02x%02x%02x' %
                             (int(r[0]), int(g[1]), int(b[2])))

        self.colorTmp.set(self._colorValue.get())
        print(self.colorTmp.get())

    def changeColor(self, X):
        """ Funkcja wywoływana zmianą wartości na pasku wyboru koloru. Zapisuje wybór użytkownika do odpowiedniej zmiennej. """
        self._colorValue.set(X)

    def changeBrightness(self, X):
        """ Funkcja wywoływana zmianą wartości na pasku wyboru jasności. Zapisuje wybór użytkownika oraz przelicza podgląd koloru dopasowując go do wybranej jasności. """

        # wartość koloru w formacie hex przelicza na rgb
        # h = self._colorValue.get().lstrip('#')
        # color= tuple(int(h[i:i+2], 16) for i in (0, 2, 4))
        color = hex_rgb(self._colorValue.get())

        self.brightness.set(X)

        # wartość jasności w formacie hex przelicza na rgb
        # b = X.lstrip('#')
        # brightness= tuple(int(b[i:i+2], 16) for i in (0, 2, 4))
        brightness = hex_rgb(X)

        print("XXXX: ", self.brightness.get())
        print(brightness)

        print(color)
        print(brightness)

        r = int(color[0])
        g = int(color[1])
        b = int(color[2])
        # print(r," X ", g," X ",b)

        # oblicza kolor uzywany przy jego podglądzie i
        self.colorTmp.set(value='#%02x%02x%02x' % (
            self.adjust_color_lightness(r, g, b, brightness[0]/100)))

    def adjust_color_lightness(self, r, g, b, factor):
        """ Funkcja dostosowująca kolor rgb zależnie od jego jasności (model hsv) """
        h, l, s = rgb_to_hls(r / 255.0, g / 255.0, b / 255.0)
        l = max(min(l * factor, 1.0), 0.0)
        r, g, b = hls_to_rgb(h, l, s)
        return int(r * 255), int(g * 255), int(b * 255)

    def send(self, data):
        finalData = json.dumps(data)

        # Create a socket (SOCK_STREAM means a TCP socket)
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        try:
            # Connect to server and send data
            sock.connect((HOST, PORT))

            time.sleep(.5)
            sock.sendall(bytes(finalData, encoding="utf-8"))
            # Receive data from the server and shut down

            # print("Received message: " + received)
        finally:
            sock.close()


class OneColorPage(ColorMain):
    """ Klasa z widokiem umożliwiającym ustawienia jednolicie świecących ledów """

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent, bg=def_color)

        # ustawia odpowiednie szerokosci i wysokości kolumn i rzędów w układzie elementów
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)

        self.rowconfigure(0, weight=2)
        self.rowconfigure(1, weight=4)
        self.rowconfigure(2, weight=1)
        self.rowconfigure(3, weight=6)

        # self.rowconfigure(4, weight = 4)
        # self.rowconfigure(5, weight = 4)

        self.main_controllFrame = Frame(self, bg=def_color)
        self.main_controllFrame.grid(
            column=0, columnspan=2, row=0, sticky="nsew")
        # ustawia odpowiednie szerokosci i wysokości kolumn i rzędów w układzie elementów
        self.main_controllFrame.columnconfigure(0, weight=1)
        self.main_controllFrame.columnconfigure(1, weight=1)
        self.main_controllFrame.rowconfigure(0, weight=2)

        # przyciski nawigujące
        button1 = ttk.Button(self.main_controllFrame, style='TButton', text="Apply",
                             command=lambda: self.apply(self._colorValue.get(), self.brightness.get()))
        button1.grid(row=0, column=0, sticky='nswe', padx=10, pady=10)

        button2 = ttk.Button(self.main_controllFrame, text="Back",
                             command=lambda: controller.show_frame(MainPage))
        button2.grid(row=0, column=1, sticky='nswe', pady=10)

        # wartości początkowe:
        self.brightness = ColorVar(value='white')  # jasność koloru

        self._colorValue = ColorVar(value='black')  # barwa koloru
        # zmienna pomocnicza dla wizualizacji ustawianego koloru
        self.colorTmp = ColorVar(value='black')

        # zmienne dla pasków wyboru

        fgvar = ColorVar(value='white')

        # obszar z podglądem wybranego koloru
        Label(self, text="\n\n\n\n", bg=self.colorTmp, fg=fgvar).grid(
            row=1, column=0, columnspan=2, sticky="nesw", pady=50, padx=50)

        xFrame = Frame(self, bg=def_color)
        xFrame.grid(column=0, columnspan=2, row=2, sticky="nsew")
        xFrame.columnconfigure(0, weight=3)
        xFrame.columnconfigure(1, weight=3)
        xFrame.columnconfigure(2, weight=1)

        var1 = IntVar(value=1)
        var2 = IntVar(value=0)
        tk.Checkbutton(xFrame, command=lambda: self.switchVar('basic', var1, var2),   activebackground='red', foreground='red', background="#353535", font=(
            'Arial', 15), text="Basic color chooser", variable=var1).grid(row=0, column=0, sticky="news", padx=10, pady=10)
        tk.Checkbutton(xFrame, command=lambda: self.switchVar('rgb', var1, var2),  activebackground='red', foreground='red', background="#353535", font=(
            'Arial', 15), text="RGB color chooser", variable=var2).grid(row=0, column=1, sticky="news", padx=10, pady=10)

        self.delayNum = Spinbox(xFrame, foreground='red', background="#353535", font=('Arial', 15), from_=0, to=3, format="%.2f", text="S", increment=0.01, justify=CENTER, width=30)
        self.delayNum .grid(row=0, column=2, sticky="nwes", padx=10, pady=10)

        # self.grid_columnconfigure(2, weight=24) # as did this

        self.color_chooser_frame = Frame(self)
        self.color_chooser_frame.grid(
            column=0, columnspan=2, row=3, sticky="nsew")
        self.load_color_opt("basic")

    def apply(self, X, Y):
        """ Funkcja konwertująca kolor i jasność do json'a i wysyłająca go na zadany adres """
        # wartość koloru w formacie hex przelicza na rgb

        print("OneColorPageApply")
        colour = hex_rgb(X)
        brightness = hex_rgb(self.brightness.get())
        LED = {}
        LED["SegNum"] = 1
        LED["indexing"] = "normal"
        segment = {}
        segment["n"] = 80
        segment["d"] = str((float(self.delayNum.get())*1000))
        segment["br"]=int(brightness[0])

        for i in range(80):
            m={}
            m["r"] = int(colour[0])
            m["g"] = int(colour[1])
            m["b"] = int(colour[2])
            segment["L"+str(i)] = m
        LED["S0"] = segment

        print(LED)
        print("App message: sending...")
        self.send(LED)
        print("Done")



class GradientColorPage(ColorMain):
    """ Klasa z widokiem umożliwiającym ustawienia gradientu ledów """

    def __init__(self, parent, controller):

        tk.Frame.__init__(self, parent, bg=def_color)

        # ustawia odpowiednie szerokosci i wysokości kolumn i rzędów w układzie elementów
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)

        self.rowconfigure(0, weight=5)
        self.rowconfigure(1, weight=1)
        self.rowconfigure(2, weight=1)
        self.rowconfigure(3, weight=1)
        self.rowconfigure(4, weight=11)
        self.main_controllFrame = Frame(self, bg=def_color)
        self.main_controllFrame.grid(
            column=0, columnspan=2, row=0, sticky="nsew")
        # ustawia odpowiednie szerokosci i wysokości kolumn i rzędów w układzie elementów
        self.main_controllFrame.columnconfigure(0, weight=1)
        self.main_controllFrame.columnconfigure(1, weight=1)
        self.main_controllFrame.rowconfigure(0, weight=2)

        # R1 przyciski nawigujące
        button1 = ttk.Button(self.main_controllFrame, style='TButton', text="Apply",
                             command=lambda: self.apply_gradient(self.colorFrom.get(), self.colorTo.get()))
        button1.grid(row=0, column=0, sticky='nswe', padx=10, pady=10)

        button2 = ttk.Button(self.main_controllFrame, text="Back",
                             command=lambda: controller.show_frame(MainPage))
        button2.grid(row=0, column=1, sticky='nswe', pady=10)

        # wartości początkowe:
        self.brightness = ColorVar(value='white')  # jasność koloru

        self._colorValue = ColorVar(value='black')  # barwa koloru
        # zmienna pomocnicza dla wizualizacji ustawianego koloru
        self.colorTmp = ColorVar(value='black')
        self.colorFrom = ColorVar(value='black')
        self.colorTo = ColorVar(value='black')
        # zmienne dla pasków wyboru

        fgvar = ColorVar(value='white')

        col1 = IntVar(value=1)
        col2 = IntVar(value=0)

        tk.Checkbutton(self, command=lambda: self.switchVar('color_from', col1, col2),   activebackground='red', foreground='red',
                       background="#353535", font=('Arial', 15), text="Start color", variable=col1).grid(row=1, column=0, sticky="news", padx=10, pady=10)
        tk.Checkbutton(self, command=lambda: self.switchVar('color_to', col1, col2),  activebackground='red', foreground='red',
                       background="#353535", font=('Arial', 15), text="End color", variable=col2).grid(row=1, column=1, sticky="news", padx=10, pady=10)

        # obszar z podglądem wybranego koloru
        # Label(self, text="\n\n\n\n",bg=self.colorTmp, fg=fgvar).grid(row=2, column=0, columnspan=2,sticky="nesw", pady=50,padx=50)
        self.GF = GradientFrame(self, self.colorFrom, self.colorTo).grid(
            row=2, column=0, columnspan=2, sticky="nesw")

        xFrame = Frame(self, bg=def_color)
        xFrame.grid(column=0, columnspan=2, row=3, sticky="nsew")
        xFrame.columnconfigure(0, weight=3)
        xFrame.columnconfigure(1, weight=3)
        xFrame.columnconfigure(2, weight=1)

        var1 = IntVar(value=1)
        var2 = IntVar(value=0)
        tk.Checkbutton(xFrame, command=lambda: self.switchVar('basic', var1, var2),   activebackground='red', foreground='red', background="#353535", font=(
            'Arial', 15), text="Basic color chooser", variable=var1).grid(row=0, column=0, sticky="news", padx=10, pady=10)
        tk.Checkbutton(xFrame, command=lambda: self.switchVar('rgb', var1, var2),  activebackground='red', foreground='red', background="#353535", font=(
            'Arial', 15), text="RGB color chooser", variable=var2).grid(row=0, column=1, sticky="news", padx=10, pady=10)

        self.delayNum = Spinbox(xFrame, foreground='red', background="#353535", font=(
            'Arial', 15), from_=0, to=1, format="%.2f", text="S", increment=0.01, justify=CENTER, width=30, command=self.print_item_values)
        self.delayNum .grid(row=0, column=2, sticky="nwes", padx=10, pady=10)

        # self.grid_rowconfigure(3, weight=4) # this needed to be added
        # self.grid_columnconfigure(2, weight=24) # as did this

        self.color_chooser_frame = Frame(self)
        self.color_chooser_frame.grid(
            column=0, columnspan=2, row=4, sticky="nsew")

        self.colorTmp.trace_add(
            'write', lambda name, index, mode, c1=col1, c2=col2: self.my_callback(c1, c2))

        self.load_color_opt("basic")

    def print_item_values(self):
        print(self.delayNum.get())

    def my_callback(self, col1, col2):
        """ Funkcja ustawiająca kolor koloru od/do """

        if(col1.get()):
            self.colorFrom.set(self.colorTmp.get())
        elif(col2.get()):
            self.colorTo.set(self.colorTmp.get())

        # ustawia podgląd gradientu
        self.GF = GradientFrame(self, self.colorFrom, self.colorTo, borderwidth=1, relief="sunken").grid(
            row=2, column=0, columnspan=2, sticky="nesw")

    def apply_gradient(self, colorFrom, colorTo):
        """ Funkcja obliczająca kolory wchodzące w skład gradientu i przekazujące je dalej do wysłania. """

        LED = {}
        LED["SegNum"] = 1
        LED["indexing"] = "normal"
        colors = list(Color(colorFrom).range_to(Color(colorTo), 80))
        print("LEN: ", len(colors))

        segment = {}
        
        segment["n"] = 80
        segment["d"] = str((float(self.delayNum.get())*1000))
        for i in range(len(colors)):
            c = colors[i]
            # DO POPRAWIENIA!
            if(str(c)[0] is not '#'):
                print(c)
                f = open("error_colors2.txt", "a")
                f.write(str(c))
                f.write("\n")
                f.close()

                c=error_colors(str(c))
                
                
            elif(len(str(c)) == 4):
                a=str(c)
                a= a[0]+2*a[1]+2*a[2]+2*a[3]
                c=a

            col = hex_rgb(str(c))
            m = {}
            m["r"] = str(col[0])
            m["g"] = str(col[1])
            m["b"] = str(col[2])
            segment["L"+str(i)] = m
        LED["S0"] = segment
        # print(LED)
        self.send(LED)

        print("Done")


class TPM(ColorMain):
    """ Klasa z widokiem umożliwiającym ustawienia gradientu ledów """

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent, bg=def_color)

        # ustawia odpowiednie szerokosci i wysokości kolumn i rzędów w układzie elementów
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=5)

        self.rowconfigure(0, weight=1)
        self.rowconfigure(1, weight=8)

        self.main_controllFrame = Frame(self, bg=def_color)
        self.main_controllFrame.grid(
            column=0, columnspan=2, row=0, sticky="nsew")
        # ustawia odpowiednie szerokosci i wysokości kolumn i rzędów w układzie elementów
        self.main_controllFrame.columnconfigure(0, weight=1)
        self.main_controllFrame.columnconfigure(1, weight=1)
        self.main_controllFrame.rowconfigure(0, weight=2)

        self.leftFrame = Frame(self, bg=def_color)
        self.leftFrame.grid(column=0, row=1,  sticky="nsew")

        self.rightFrame = Frame(self, bg=def_color)
        self.rightFrame.grid(column=1, row=1,  sticky="nsew")
        self.rightFrame.rowconfigure(0, weight=1)
        self.rightFrame.rowconfigure(1, weight=8)
        self.rightFrame.rowconfigure(3, weight=8)
        self.rightFrame.columnconfigure(0, weight=1)
        self.rightFrame.columnconfigure(1, weight=1)

        # R1 przyciski nawigujące
        button1 = ttk.Button(self.main_controllFrame, style='TButton', text="Apply",
                             command=lambda: self.apply_gradient(self.colorFrom.get(), self.colorTo.get()))
        button1.grid(row=0, column=0, sticky='nswe', padx=10, pady=10)

        button2 = ttk.Button(self.main_controllFrame, text="Back",
                             command=lambda: controller.show_frame(MainPage))
        button2.grid(row=0, column=1, sticky='nswe', pady=10)

        self.loadRightFrame()

        self.leftFrame.rowconfigure(0, weight=1)
        self.leftFrame.rowconfigure(1, weight=10)
        self.leftFrame.columnconfigure(0, weight=1)
        self.leftFrame.columnconfigure(1, weight=1)
        self.leftFrame.columnconfigure(2, weight=1)
        self.leftFrame.columnconfigure(3, weight=1)

        tree = Treeview(self.leftFrame, selectmode="extended",
                        columns=("OD", "DO", "Del", "Col1", "Col2"))
        tree.grid(row=1, column=0, columnspan=4,
                  sticky="news", pady=50, padx=10)
        tree.heading("#0", text="Seq")
        tree.column("#0", minwidth=0, width=100, stretch=NO)

        tree.heading("OD", text="OD")
        tree.column("OD", minwidth=0, width=100, stretch=NO)

        tree.heading("DO", text="DO")
        tree.column("DO", minwidth=0, width=100, stretch=NO)

        tree.heading("Del", text="Del")
        tree.column("Del", minwidth=0, width=100, stretch=NO)

        tree.heading("Col1", text="Col")
        tree.column("Col1", minwidth=0, width=100, stretch=YES)

        tree.heading("Col2", text=" ")
        tree.column("Col2", minwidth=0, width=100, stretch=YES)

        tree.insert('', 'end', 'foo', text='Foo',
                    values=[1, 2, 3], tags=['red_fg'])
        tree.insert('foo', 'end', text='Foo', values=[
                    1, 2, 3], tags=['red_fg'])

        # self.listBox =  ttk.Treeview(self.leftFrame, columns=cols, show='headings')
        # self.listBox.column("SEQ", minwidth=0, width=100, stretch=NO)
        # for col in cols:
        #    self.listBox.heading(col, text=col)
        # self.listBox

        ttk.Button(self.leftFrame, text="Add seq", command=lambda: controller.show_frame(
            SegmentColorPage)).grid(row=0, column=0, sticky='nswe', pady=10)
        ttk.Button(self.leftFrame, text="Add").grid(
            row=0, column=1, sticky='nswe', pady=10)
        ttk.Button(self.leftFrame, text="Delete").grid(
            row=0, column=2, sticky='nswe', pady=10)
        ttk.Button(self.leftFrame, text="Add delay").grid(
            row=0, column=3, sticky='nswe', pady=10)

    def loadRightFrame(self):
        # wartości początkowe:
        self.brightness = ColorVar(value='white')  # jasność koloru

        self._colorValue = ColorVar(value='black')  # barwa koloru
        # zmienna pomocnicza dla wizualizacji ustawianego koloru
        self.colorTmp = ColorVar(value='black')
        self.colorFrom = ColorVar(value='black')
        self.colorTo = ColorVar(value='black')
        # zmienne dla pasków wyboru

        fgvar = ColorVar(value='white')

        col1 = IntVar(value=1)
        col2 = IntVar(value=0)

        tk.Checkbutton(self.rightFrame, command=lambda: self.switchVar('color_from', col1, col2),   activebackground='red', foreground='red',
                       background="#353535", font=('Arial', 15), text="Start color", variable=col1).grid(row=0, column=0, sticky="news", padx=10, pady=10)
        tk.Checkbutton(self.rightFrame, command=lambda: self.switchVar('color_to', col1, col2),  activebackground='red', foreground='red',
                       background="#353535", font=('Arial', 15), text="End color", variable=col2).grid(row=0, column=1, sticky="news", padx=10, pady=10)

        # obszar z podglądem wybranego koloru
        # Label(self, text="\n\n\n\n",bg=self.colorTmp, fg=fgvar).grid(row=2, column=0, columnspan=2,sticky="nesw", pady=50,padx=50)
        self.GF = GradientFrame(self.rightFrame, self.colorFrom, self.colorTo).grid(
            row=1, column=0, columnspan=2, sticky="nesw")

        xFrame = Frame(self.rightFrame, bg=def_color)
        xFrame.grid(column=0, columnspan=2, row=2, sticky="nsew")
        xFrame.columnconfigure(0, weight=3)
        xFrame.columnconfigure(1, weight=3)
        xFrame.columnconfigure(2, weight=1)

        var1 = IntVar(value=1)
        var2 = IntVar(value=0)
        tk.Checkbutton(xFrame, command=lambda: self.switchVar('basic', var1, var2),   activebackground='red', foreground='red', background="#353535", font=(
            'Arial', 15), text="Basic color chooser", variable=var1).grid(row=0, column=0, sticky="news", padx=10, pady=10)
        tk.Checkbutton(xFrame, command=lambda: self.switchVar('rgb', var1, var2),  activebackground='red', foreground='red', background="#353535", font=(
            'Arial', 15), text="RGB color chooser", variable=var2).grid(row=0, column=1, sticky="news", padx=10, pady=10)

        self.delayNum = Spinbox(xFrame, foreground='red', background="#353535", font=(
            'Arial', 15), from_=0, to=1, format="%.2f", text="S", increment=0.01, justify=CENTER, width=30, command=self.print_item_values)
        self.delayNum .grid(row=0, column=2, sticky="nwes", padx=10, pady=10)

        # self.grid_rowconfigure(3, weight=4) # this needed to be added
        # self.grid_columnconfigure(2, weight=24) # as did this

        self.color_chooser_frame = Frame(self.rightFrame)
        self.color_chooser_frame.grid(
            column=0, columnspan=2, row=3, sticky="nsew")

        self.colorTmp.trace_add(
            'write', lambda name, index, mode, c1=col1, c2=col2: self.my_callback(c1, c2))

        self.load_color_opt("basic")

    def print_item_values(self):
        print(self.delayNum.get())

    def my_callback(self, col1, col2):
        """ Funkcja ustawiająca kolor koloru od/do """

        if(col1.get()):
            self.colorFrom.set(self.colorTmp.get())
        elif(col2.get()):
            self.colorTo.set(self.colorTmp.get())

        # ustawia podgląd gradientu
        self.GF = GradientFrame(self.rightFrame, self.colorFrom, self.colorTo).grid(
            row=1, column=0, columnspan=2, sticky="nesw")

class SegmentColorPage(ColorMain):
    """ Klasa z widokiem umożliwiającym ustawienia gradientu ledów """

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent, bg=def_color)

        # ustawia odpowiednie szerokosci i wysokości kolumn i rzędów w układzie elementów
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)
        self.columnconfigure(2, weight=1)
        self.columnconfigure(3, weight=1)
        self.rowconfigure(0, weight=2)
        self.rowconfigure(1, weight=1)
        self.rowconfigure(3, weight=4)

        self.main_controllFrame = Frame(self, bg=def_color)
        self.main_controllFrame.grid(
            column=0, columnspan=4, row=0, sticky="nsew")
        # ustawia odpowiednie szerokosci i wysokości kolumn i rzędów w układzie elementów
        self.main_controllFrame.columnconfigure(0, weight=1)
        self.main_controllFrame.columnconfigure(1, weight=1)
        self.main_controllFrame.rowconfigure(0, weight=2)

        # przyciski nawigujące
        button1 = ttk.Button(self.main_controllFrame, style='TButton',
                             text="Apply", command=lambda: self.applySegment())
        button1.grid(row=0, column=0, sticky='nswe', padx=10, pady=10)

        button2 = ttk.Button(self.main_controllFrame, text="Back",
                             command=lambda: controller.show_frame(MainPage))
        button2.grid(row=0, column=1, sticky='nswe', pady=10)

        # wartości początkowe (zmienne do wizualizacji):
        self.brightness = ColorVar(value='white')  # jasność koloru
        self._colorValue = ColorVar(value='black')  # barwa koloru
        # zmienna pomocnicza dla wizualizacji ustawianego koloru
        self.colorTmp = ColorVar(value='black')

        # listy przechowujace dane o kolorach w segmencie
        self.colorsTo = [ColorVar(value='black')]
        self.colorsFrom = [ColorVar(value='black')]

        # zmienna do checkbox ow 
        self.edit = [IntVar(value=1)]

        # dlugosc danego koloru
        self.colorsNum = [1]

        # ,,linie czasu" - ktore segmenty maja byc zapalane razem
        self.timelinesMembers = [[0]]

        # indeks aktualnie edytowanego elementu
        self.active_index = 0

        # zmienne dla pasków wyboru
        fgvar = ColorVar(value='white')

        self.loadColorFrame()
        
        self.addSegmentFrame = Frame(self,bg=def_color)
        self.addSegmentFrame.grid(
            column=0, columnspan=4, row=2, sticky="nsew")
        
        #  ----- wybór koloru rgb -----
        var1 = IntVar(value=1)
        var2 = IntVar(value=0)
        tk.Checkbutton(self.addSegmentFrame, command=lambda: self.switchVar('basic', var1, var2),   activebackground='red', foreground='red', background="#353535", font=(
            'Arial', 15), text="Basic color chooser", variable=var1).grid(row=2, column=0, sticky="news", padx=10, pady=10)
        tk.Checkbutton(self.addSegmentFrame, command=lambda: self.switchVar('rgb', var1, var2),  activebackground='red', foreground='red', background="#353535", font=(
            'Arial', 15), text="RGB color chooser", variable=var2).grid(row=2, column=1, sticky="news", padx=10, pady=10)
        # -------------------------

        # ----- liczba segmentów -----
        ttk.Label(self.addSegmentFrame, style="Header.Label", text="Segments number:",font=LARGE_FONT, justify=RIGHT).grid(row=2, column=3, padx=10, pady=10)
        
        self.segmentNum = Spinbox(self.addSegmentFrame, from_=1, to=15, justify=CENTER, command=lambda: self.load_segment_opt(), font=('Arial', 30, 'bold'), foreground='#A8A8A8', background="#353535")
        self.segmentNum.grid(row=2, column=4, padx=10, pady=10)
        # -------------------------


        # ----- frame z wyborem koloru -----
        self.color_chooser_frame = Frame(self,bg=def_color)
        self.color_chooser_frame.grid(column=0, columnspan=2, row=3, sticky="nsew")
        self.color_chooser_frame.columnconfigure(0, weight=1)

        self.load_color_opt("basic")
        self.load_segment_opt()
        #-------------------------

        # ----- ramka opcji segmentu -----
        self.segmentOptFrame = Frame(self, bg=def_color)
        self.segmentOptFrame.grid(column=2, columnspan=2, row=3, sticky="news")
        self.segmentOptFrame .columnconfigure(0, weight=1)
        self.segmentOptFrame .columnconfigure(1, weight=1)
        self.segmentOptFrame .columnconfigure(2, weight=1)
        self.segmentOptFrame .columnconfigure(3, weight=1)
        
        # wybór solid/gradient 
        OPTIONS = [
            "           Solid        ",
            "        Gradient     "
        ]  # etc

        self.colorMode = StringVar(self.segmentOptFrame)
        self.colorMode.set(OPTIONS[0])  # default value

        self.colorModeChooser = OptionMenu(self.segmentOptFrame, self.colorMode, *OPTIONS)
        self.colorModeChooser.config(font=('Arial', 10), foreground='#A8A8A8',background="#353535")
        self.colorModeChooser.grid(row=0, column=0, sticky="nesw", padx=10, pady=10)

        col1 = IntVar(value=1)
        col2 = IntVar(value=0)


        tk.Checkbutton(self.segmentOptFrame, command=lambda: self.switchVar('color_from', col1, col2),   activebackground='red', foreground='red',background="#353535", font=('Arial', 15), text="Start color", variable=col1).grid(row=0, column=1, sticky="news", padx=10, pady=10)
        tk.Checkbutton(self.segmentOptFrame, command=lambda: self.switchVar('color_to', col1, col2),  activebackground='red', foreground='red',background="#353535", font=('Arial', 15), text="End color", variable=col2).grid(row=0, column=2, sticky="news", padx=10, pady=10)
        #-------------------------

        # Ilość pixeli w jednym segmencie
        self.slen = StringVar(self.segmentOptFrame)
        self.slen.set("1")
        ttk.Label(self.segmentOptFrame, style="Header.Label", text="Element length:",
                  font=LARGE_FONT).grid(row=1, column=0, pady=10)
        self.el_NUM = Spinbox(self.segmentOptFrame, from_=1, to=80, justify=CENTER, command=lambda: self.load_element_opt(
        ), font=('Arial', 15, 'bold'), foreground='#A8A8A8', background="#353535", textvariable=self.slen)
        self.el_NUM.grid(row=1, column=1, pady=10)
        #-------------------------


        # linie czasowe
        self.timelines = [
            "        1      ",
        ] 
        self.timeLineVar = StringVar(self.segmentOptFrame)
        self.timeLineVar.set(self.timelines[0])  # default value

        self.timeLineChooser= OptionMenu(self.segmentOptFrame, self.timeLineVar, *self.timelines, command=self.addToTimeLine)
        self.timeLineChooser.config(font=('Arial', 10), foreground='#A8A8A8',background="#353535")
        self.timeLineChooser.grid(row=2, column=1, sticky="nesw", pady=10)

        ttk.Button(self.segmentOptFrame, style='TButton', text="Add time line", command=lambda: self.addTimeline()).grid(row=2, column=0, pady=10)
        
        ttk.Label(self.segmentOptFrame, style="Header.Label", text="Delay [s]:", font=LARGE_FONT).grid(row=3, column=0, padx=10, pady=10)
        
        self.delayNum = Spinbox(self.segmentOptFrame, foreground='#A8A8A8', background="#353535", font=('Arial', 15), from_=0, to=1, format="%.2f", text="S",increment=0.01, justify=CENTER)
        self.delayNum .grid(row=3, column=1, sticky="nwes", pady=10)
        #-------------------------
        
        self.colorTmp.trace_add('write', lambda name, index, mode, c1=col1, c2=col2: self.my_callback(c1, c2, self.active_index))

    def loadColorFrame(self):
        self.colorFrame = Frame(self, bg=def_color)
        self.colorFrame.grid(column=0, columnspan=4, row=1, sticky="nsew")
        self.colorFrame .columnconfigure(0, weight=1)
        self.colorFrame .rowconfigure(0, weight=1)
        self.colorFrame .rowconfigure(1, weight=1)
        self.colorFrame .rowconfigure(2, weight=1)

        # obszar z podglądem wybranego koloru
        GradientFrame(self.colorFrame, ColorVar(value="black"), ColorVar(value="black")).grid(row=0, column=0, sticky="nesw")


    def addTimeline(self):
        num=int(len(self.timelines))+1
        self.timelines.append("        "+str(num)+"      ")
        self.timeLineChooser= OptionMenu(self.segmentOptFrame, self.timeLineVar, *self.timelines, command=self.addToTimeLine)
        self.timeLineChooser.config(font=('Arial', 10), foreground='#A8A8A8',background="#353535")
        self.timeLineChooser.grid(row=2, column=1, sticky="nesw", pady=10)
        self.timelinesMembers.append([])
        print(self.timelinesMembers)
            
    def addToTimeLine(self, tl_index):
        for i in range(len(self.timelinesMembers)):
            if self.active_index in self.timelinesMembers[i]: self.timelinesMembers[i].remove(self.active_index)
            
        self.timelinesMembers[int(self.timeLineVar.get())-1].append(self.active_index)
    
        print(self.timelinesMembers)

    def definedPixels(self, index):
        num=0
        for i in range(index):
            num += self.colorsNum[i]

        print("NUM:",end="")
        print(num)
        return num

    def load_segment_opt(self):

        print("load_segment_opt")
        for widget in self.colorFrame.winfo_children():
            widget.destroy()

        if(int(self.segmentNum.get()) > len(self.colorsTo)):
            print("Add")
            self.colorsFrom.append(ColorVar(value='black'))
            self.colorsTo.append(ColorVar(value='black'))
            self.edit.append(IntVar(value=0))
            self.colorsNum.append(1)
            self.timelinesMembers[0].append(len(self.colorsNum)-1)


        elif(int(self.segmentNum.get()) < len(self.colorsTo)):
            print("Remove")
            self.colorsFrom.pop()
            self.colorsTo.pop()
            self.edit.pop()
           

            for i in range(len(self.timelinesMembers)):
                if len(self.colorsNum)-1 in self.timelinesMembers[i]: self.timelinesMembers[i].remove(len(self.colorsNum)-1)
            self.colorsNum.pop()
        print(self.timelinesMembers)

        for i in range(int(self.segmentNum.get())):
            print("W:1 "+str(i))
            self.colorFrame.columnconfigure(i, weight=1)
            print("W:0 "+str(i+1))
            self.colorFrame.columnconfigure(i+1, weight=0)
            GradientFrame(self.colorFrame, self.colorsFrom[i], self.colorsTo[i], borderwidth=1, relief="sunken").grid(
                row=0, column=i, sticky="nesw", padx=1)

            tk.Checkbutton(self.colorFrame, variable=self.edit[i], command=lambda i=i: self.set_as_editing(i), activebackground='red', foreground='red', background="#353535", font=('Arial', 15), text="Edit").grid(row=1, column=i, sticky="nesw", padx=1)
    
    def load_element_opt(self):
        print(self.el_NUM.get())
        self.colorsNum[self.active_index] = int(self.el_NUM.get())

    def set_as_editing(self, active):
        for i in range(len(self.edit)):
            self.edit[i].set(0)

        self.edit[active].set(1)
        self.active_index = active
        self.slen.set(self.colorsNum[self.active_index])
        self.timeLineChooser
        
        for i in range(len(self.edit)):
            print(self.edit[i].get(), end=" ")
        print()

    def my_callback(self, col1, col2, i):
        """ Funkcja ustawiająca kolor od/do """
        print("EDITING: "+str(i))
        if(self.colorMode.get() == "        Gradient     "):
            if(col1.get()):
                self.colorsFrom[i].set(self.colorTmp.get())
            elif(col2.get()):
                self.colorsTo[i].set(self.colorTmp.get())
        else:
            self.colorsTo[i].set(self.colorTmp.get())
            self.colorsFrom[i].set(self.colorTmp.get())

        # ustawia podgląd gradientu
        GradientFrame(self.colorFrame, self.colorsFrom[i], self.colorsTo[i], borderwidth=1, relief="sunken").grid(
            row=0, column=i, sticky="nesw")

    def applySegment(self):
        """ Funkcja obliczająca kolory wchodzące w skład segmentu i przekazujące je dalej do wysłania. """
        print("self.colorsNum: ",end="")
        print(self.colorsNum)

        print("self.segmentNum.get(): ",end="")
        print(self.segmentNum.get())
        startIndex=[]
        for i in range(int(self.segmentNum.get())):
            print("X:",end="")
            print(i)
            startIndex.append(self.definedPixels(i))
        
        print("Start index: ",end="")
        print(startIndex)


        segments=0
        notEmptySeg=[]
        
        for i in range(len(self.timelinesMembers)):
            if len(self.timelinesMembers[i]) > 0: 
                
                segments+=1
                notEmptySeg.append(self.timelinesMembers[i])
        print("segNUM: "+ str(segments))
        print(notEmptySeg)

        LED = {}
        LED["SegNum"] = segments
        LED["indexing"] = "specified"
        for seg in range(segments):
            num=0
            segment = {}
            dupa=0
            for el in range(len(notEmptySeg[seg])):
                print("notEmptySeg[seg]")
                print(len(notEmptySeg[seg]))
                num+=self.colorsNum[notEmptySeg[seg][el]]
                colors = list(Color(self.colorsFrom[notEmptySeg[seg][el]].get()).range_to(Color(self.colorsTo[notEmptySeg[seg][el]].get()), self.colorsNum[notEmptySeg[seg][el]]))
                
                for i in range(len(colors)):
                    c = colors[i]

                    # DO POPRAWIENIA!
                    if(len(str(c)) == 4 or str(c)[0] is not '#'):
                       
                        # print(c)
                        
                        f = open("error_colors.txt", "a")
                        f.write(c)
                        f.close()
                        c = "#000000"
                    col = hex_rgb(str(c))
                    m = {}
                    print("startIndex[notEmptySeg[seg][el]]:  ",end="")
                    print(startIndex[notEmptySeg[seg][el]])
                    x=startIndex[notEmptySeg[seg][el]]
                    print("WTF: "+str(x))

                    m["i"]= x+i
                    m["r"] = str(col[0])
                    m["g"] = str(col[1])
                    m["b"] = str(col[2])
                    
                    segment["L"+str(dupa)] = m
                    dupa+=1
            print()
            
            segment["n"]=num
            segment["d"] = str((float(self.delayNum.get())*1000))
            LED["S"+str(seg)] = segment

        print(LED)
        self.send(LED)
        print("Done")


class GradientFrame(tk.Canvas):
    '''A gradient frame which uses a canvas to draw the background'''

    def __init__(self, parent, color1, color2, **kwargs):
        tk.Canvas.__init__(self, parent, **kwargs)
        self._color1 = color1.get()
        self._color2 = color2.get()
        self.bind("<Configure>", self._draw_gradient)

    def _draw_gradient(self, event=None):
        '''Draw the gradient'''
        self.delete("gradient")
        width = self.winfo_width()
        height = self.winfo_height()
        limit = width
        (r1, g1, b1) = self.winfo_rgb(self._color1)
        (r2, g2, b2) = self.winfo_rgb(self._color2)
        r_ratio = float(r2-r1) / limit
        g_ratio = float(g2-g1) / limit
        b_ratio = float(b2-b1) / limit
        for i in range(limit):
            nr = int(r1 + (r_ratio * i))
            ng = int(g1 + (g_ratio * i))
            nb = int(b1 + (b_ratio * i))
            color = "#%4.4x%4.4x%4.4x" % (nr, ng, nb)
            self.create_line(i, 0, i, height, tags=("gradient",), fill=color)
        self.lower("gradient")


app = Main(root)
root.geometry("1500x720")
root["bg"] = def_color
root.mainloop()
