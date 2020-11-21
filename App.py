import tkinter as tk
from tkinter import ttk
from tkinter import *
from tkinter.ttk import *
from tkinter import *
from tkmacosx import Button, ColorVar, Marquee, Colorscale
import socket
import sys
import os

import time
import json
from colorsys import rgb_to_hls, hls_to_rgb
from colour import Color
from tkinter import *
from time import strftime
import threading

from netaddr import IPNetwork, IPAddress

# definiuję adres:port modułu wifi z którym bede sie łączył
HOST, PORT = "192.168.4.22", 8888  # 241   157
#            "192.168.4.22 / 192.168.0.241


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

def sequence(*functions):
    def func(*args, **kwargs):
        return_value = None
        for function in functions:
            return_value = function(*args, **kwargs)
        return return_value
    return func

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
        for fr in (MainPage, OneColorPage, GradientColorPage, SegmentColorPage, SegmentColorPage,OtherOptPage):
            frame = fr(main_container, self)
            self.frames[fr] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame(MainPage)

    def show_frame(self, pointer, arg=None):
        """ Funkcja wywołująca odpowiednią klasę w ramce (Frame) """

        print("xd=====")
        print(arg)
        frame = self.frames[pointer]
        frame.tkraise()
        
        if arg:
            frame.some_function(arg)

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
            self, text="Segment color", command=lambda: controller.show_frame(SegmentColorPage))
        button3.grid(row=2, column=0, sticky='nswe', padx=10)

        button4 = ttk.Button(self, text="Other options", command=lambda: controller.show_frame(OtherOptPage))
        button4.grid(row=2, column=1, sticky='nswe')

        
class ColorMain(tk.Frame):
    """ Klasa z głównymi funkcjami wyboru kolorów """

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent, bg=def_color)
        
        # ustawia odpowiednie szerokosci i wysokości kolumn i rzędów w układzie elementów
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)

    def save(self, data):
        popup = Toplevel()
        popup.grab_set()
        popup.title('Save as') 
        popup["bg"] = def_color
        popup.geometry("300x200")
        popup.columnconfigure(0,weight=1)
        popup.columnconfigure(1,weight=1)
        
        ttk.Label(popup, text="Name",style="Header.Label",font=('Arial', 20, 'bold')).grid(row=0, pady=10)

        name = tk.Entry(popup)

        name.grid(row=0, column=1)

        var2 = IntVar(value=0)
        tk.Checkbutton(popup, command=lambda: print("X"),   activebackground='red', foreground='red', background="#353535", font=('Arial', 15), text="Apply after save", variable=var2).grid(row=1, column=0,columnspan=2, sticky="news")
        
        
        
        print(data)
        okButton = ttk.Button(popup, text="Apply", command=lambda: sequence(assign(data,name,var2),popup.destroy())) 
        okButton.grid(row=2, column=0,columnspan=2, sticky='nswe', pady=10)
        
        def assign(data, name, var2): 

            data["OPTION"]="Save"
            data["name"]=name.get()
            data["apply"]=var2.get()
            self.send(data)

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

        if IPAddress("192.168.0.241") in IPNetwork("192.168.0.0/24"):
            HOST = "192.168.0.241"
        else:
            HOST =  "192.168.4.22"
        print(HOST)

        # Create a socket (SOCK_STREAM means a TCP socket)
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        result=""
        try:
            # Connect to server and send data
            sock.connect((HOST, PORT))

            time.sleep(.5)
            sock.sendall(bytes(finalData, encoding="utf-8"))
            
            data = sock.recv(1024)
            if data:
                data=data.decode("utf-8")
                print("Received message: " + data)
                result=data
            # Receive data from the server and shut down

            
        finally:
            sock.close()
            return result

    def navigationButtons(self, controller):
        self.main_controllFrame = Frame(self, bg=def_color)
        self.main_controllFrame.grid(column=0, columnspan=4, row=0, sticky="nsew")
        # ustawia odpowiednie szerokosci i wysokości kolumn i rzędów w układzie elementów
        self.main_controllFrame.columnconfigure(0, weight=1)
        self.main_controllFrame.columnconfigure(1, weight=1)
        self.main_controllFrame.columnconfigure(2, weight=1)
        self.main_controllFrame.rowconfigure(0, weight=2)

        # przyciski nawigujące
        button1 = ttk.Button(self.main_controllFrame, style='TButton', text="Apply", command=lambda: self.applySegments())
        button1.grid(row=0, column=0, sticky='nswe', padx=10, pady=10)

        button3 = ttk.Button(self.main_controllFrame, text="Save as",command=lambda: self.apply(False))
        button3.grid(row=0, column=1, sticky='nswe', pady=10)

        button2 = ttk.Button(self.main_controllFrame, text="Back",command=lambda: controller.show_frame(MainPage))
        button2.grid(row=0, column=2, sticky='nswe', pady=10)

class OneColorPage(ColorMain):
    """ Klasa z widokiem umożliwiającym ustawienia jednolicie świecących ledów """

    def __init__(self, parent, controller, args=[] ):
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

        self.navigationButtons(controller)


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

    def apply(self, use=True):
        """ Funkcja konwertująca kolor i jasność do json'a i wysyłająca go na zadany adres """
        # wartość koloru w formacie hex przelicza na rgb

        print("OneColorPageApply")
        colour = hex_rgb(self._colorValue.get())
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
        if(use):
            self.send(LED)
        else:
            self.save(LED)
        print("Done")

    def some_function(self,a):
        print(a)

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
        
        # ustawia odpowiednie szerokosci i wysokości kolumn i rzędów w układzie elementów
        self.navigationButtons(controller)

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

    def apply(self, use=True):
        """ Funkcja obliczająca kolory wchodzące w skład gradientu i przekazujące je dalej do wysłania. """
        print("GradientPageApply")
        LED = {}
        LED["SegNum"] = 1
        LED["indexing"] = "normal"
        colors = list(Color(self.colorFrom.get()).range_to(Color(self.colorTo.get()), 80))
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
        print(LED)
        if(use):
            self.send(LED)
        else:
            self.save(LED)
        print("Done")

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


        self.navigationButtons(controller)
        

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
        self.el_NUM = Spinbox(self.segmentOptFrame, from_=1, to=80, justify=CENTER, command=lambda: self.elementSizeChange(), font=('Arial', 15, 'bold'), foreground='#A8A8A8', background="#353535", textvariable=self.slen)
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
        
        self.colorTmp.trace_add('write', lambda name, index, mode, c1=col1, c2=col2: self.changeColorCallback(c1, c2, self.active_index))

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
        self.draw()
    
    def draw(self):
        for i in range(int(self.segmentNum.get())):
            self.colorFrame.columnconfigure(i, weight=1)
            self.colorFrame.columnconfigure(i+1, weight=0)
            GradientFrame(self.colorFrame, self.colorsFrom[i], self.colorsTo[i], borderwidth=1, relief="sunken").grid(row=0, column=i, sticky="nesw", padx=1)

            tk.Checkbutton(self.colorFrame, variable=self.edit[i], command=lambda i=i: self.set_as_editing(i), activebackground='red', foreground='red', background="#353535", font=('Arial', 15), text="Edit").grid(row=1, column=i, sticky="nesw", padx=1)
        
    def elementSizeChange(self):
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

    def changeColorCallback(self, col1, col2, i):
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

    def apply(self, use=True):
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
        if(use):
            self.send(LED)
        else:
            self.save(LED)
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

class OtherOptPage(ColorMain):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent, bg=def_color)
        # ustawia odpowiednie szerokosci i wysokości kolumn i rzędów w układzie elementów
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)
        self.columnconfigure(2, weight=1)
        self.columnconfigure(3, weight=1)
        self.rowconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)
        self.rowconfigure(2, weight=1)
        self.rowconfigure(3, weight=1)
        self.rowconfigure(4, weight=4)
        self.main_controllFrame = Frame(self, bg=def_color2)
        self.main_controllFrame.grid(column=0, columnspan=4, row=0, sticky="nsew")

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

        configWifi = ttk.Button(self, style='TButton',text="Configure WiFi", command=lambda: self.WiFiSettings())
        configWifi.grid(row=1, column=0,columnspan=4, sticky='nswe', padx=10, pady=20)

        configTimer = ttk.Button(self, style='TButton',text="Configure Timer", command=lambda: self.TimerSettings())
        configTimer.grid(row=2, column=0,columnspan=4, sticky='nswe', padx=10, pady=20)
        
        configSaved = ttk.Button(self, style='TButton',text="Configure Saved", command=lambda: self.SavedOptionsSettings(controller))
        configSaved.grid(row=3, column=0,columnspan=4, sticky='nswe', padx=10, pady=20)

    def WiFiSettings(self):
        def sendWiFiOpt(ssid, passw):
            data={}
            data["OPTION"]="WifiConfig"
            data["ssid"]=ssid
            data["password"]=passw
            self.send(data)
            print(data)   
        
        popup = Toplevel()
        popup.grab_set()
        popup.title('WiFi Settings') 
        popup["bg"] = def_color
        popup.geometry("300x200")
        popup.columnconfigure(0,weight=1)
        popup.columnconfigure(1,weight=1)
        
        ttk.Label(popup, text="Name",style="Header.Label",font=('Arial', 20, 'bold')).grid(row=0, pady=10)
        ttk.Label(popup, text="Password",style="Header.Label",font=('Arial', 20, 'bold')).grid(row=1)

        WiFi_name = tk.Entry(popup)
        WiFi_pass = tk.Entry(popup, show="*")

        WiFi_name.grid(row=0, column=1)
        WiFi_pass.grid(row=1, column=1)

        okButton = ttk.Button(popup, text="Apply", command=lambda: sequence(sendWiFiOpt(WiFi_name.get(),WiFi_pass.get()),popup.destroy())) 
        okButton.grid(row=2, column=0,columnspan=2, sticky='nswe', pady=10)
     
    def TimerSettings(self):
        def OneSecClock():
	        string = strftime('%H:%M:%S %p') 
	        self.lbl.config(text = string) 
	        self.lbl.after(1000, OneSecClock) 

        def loadData():
            print("loadData")
            req={}
            req["OPTION"]="Load"
            req["dir"]="SavedOptions"
            saved= self.send(req)


            saved = saved.split(";") #dzieli na pliki
            saved[:] = [x[:-4] for x in saved if x] #usuwa puste i koncówkę .txt z pozostałych

            print(saved)
            self.OPTIONS = []

            for s in saved:
                self.OPTIONS.append(s)

            self.optionChooser.set(self.OPTIONS[0])
            self.colorModeChooser = OptionMenu(self.rightFr, self.optionChooser, *self.OPTIONS)
            self.colorModeChooser.config(font=('Arial', 10), foreground='#A8A8A8',background="#353535")
            self.colorModeChooser.config(width=20)
            self.colorModeChooser.grid(row=3, column=1, sticky="ew")

        def right():
            xxx=str(self.lbl.cget("text"))
            xxx = xxx.split(':')
            self.hourstr=tk.StringVar(self.rightFr,xxx[0])

            self.hour = Spinbox(self.rightFr,from_=0,to=23,width=0,justify=CENTER,font=('Arial', 20, 'bold'), foreground='#A8A8A8', background="#353535", textvariable=self.hourstr)
            self.hour.grid(row=0,column=0, sticky="ew")

            self.minstr=tk.StringVar(self.rightFr,xxx[1])
            self.minstr.trace("w",trace_var)
            self.last_value = ""
            self.min = Spinbox(self.rightFr,from_=0,to=59,width=0,justify=CENTER,font=('Arial', 20, 'bold'), foreground='#A8A8A8', background="#353535", textvariable=self.minstr)

            self.min.grid(row=0,column=1, sticky="ew")

            offButton = ttk.Button(self.rightFr, text="Turn on", width=0, command=lambda: sequence(add_item("ON"))) 
            offButton.grid(row=1, column=0, sticky='we')

            onButton = ttk.Button(self.rightFr, text="Turn off",width=0, command=lambda: sequence(add_item("OFF"))) 
            onButton.grid(row=1, column=1,sticky='we')

            a = ttk.Label(self.rightFr, style="Header.Label",anchor = 'center', text="Choose defined:",font=('Arial', 20, 'bold'),background = def_color) 
            a.grid(row=3, column=0, sticky="news")
             
            useButton = ttk.Button(self.rightFr, text="Use", width=0, command=lambda: sequence(add_item(self.optionChooser.get()))) 
            useButton.grid(row=2, column=0, sticky='we')

            def runAsThread():
                x = threading.Thread(target=loadData, args=())
                x.start()
                print("x started")

            loadButton = ttk.Button(self.rightFr, text="Load",width=0, command=lambda: runAsThread()) 
            loadButton.grid(row=2, column=1,sticky='we')

            

            self.OPTIONS = [
            "No data"
            ]  # etc
            
            self.optionChooser = StringVar(self.rightFr)
            self.optionChooser.set(self.OPTIONS[0])  # default value

            self.colorModeChooser = OptionMenu(self.rightFr, self.optionChooser, *self.OPTIONS)
            self.colorModeChooser.config(font=('Arial', 10), foreground='#A8A8A8',background="#353535")
            self.colorModeChooser.config(width=20)

            self.colorModeChooser.grid(row=3, column=1, sticky="ew")

            deleteButton = ttk.Button(self.rightFr, text="Delete action", command=lambda: print(remove_item())) 
            deleteButton.grid(row=4, column=0,columnspan=2, sticky='we', pady=10)
        
        def left():
                
            self.tree = Treeview(self.leftFr, selectmode="extended",columns=("Time", "Action"))
            self.tree.grid(row=0, column=0,sticky="news")

            self.tree.column("#0", minwidth=0, width=0, stretch=NO)

            self.tree.heading("Time", text="Time")
            self.tree.column("Time", minwidth=40, width=40, stretch=NO)

            self.tree.heading("Action", text="Action")
            self.tree.column("Action", minwidth=15, width=10, stretch=YES)


            # load from ?
            self.tree.insert('', 'end', text='',values=["15:31", "ON"], tags=['red_fg'])
            self.tree.insert('', 'end', text='',values=["21:58", "OFF" ],tags=['red_fg'])

        def add_item(mode):
            
            if mode != "No data":
                time=self.hourstr.get()+":"+self.minstr.get()
                self.tree.insert('', 'end', text='',values=[time, mode], tags=['red_fg'])

        def remove_item():
            selected_items = self.tree.selection() 

            curItem = self.tree.focus()
            print(self.tree.item(curItem)["values"])

            for selected_item in selected_items:          
               self.tree.delete(selected_item)

        def trace_var(*args):
            if self.last_value == "59" and self.minstr.get() == "0":
                self.hourstr.set(int(self.hourstr.get())+1 if self.hourstr.get() !="23" else 0)
            self.last_value = self.minstr.get()


        popup = Toplevel()
        popup.grab_set()
        popup.title('Timer Settings') 
        popup["bg"] = def_color
        popup.geometry("600x600")
        popup.rowconfigure(1,weight=1)
        popup.columnconfigure(0,weight=5)
        popup.columnconfigure(1,weight=1)


        self.lbl = ttk.Label(popup, style="Header.Label",anchor = 'center', background = def_color2) 
        self.lbl.grid(row=0, column=0, columnspan=4, sticky="news")
        
        OneSecClock()
        self.leftFr = Frame(popup, bg="red")
        self.leftFr.grid(column=0, row=1, sticky="nsew", padx=5)

        # ustawia odpowiednie szerokosci i wysokości kolumn i rzędów w układzie elementów
        self.leftFr.columnconfigure(0, weight=1)
        self.leftFr.rowconfigure(0, weight=1)

        self.rightFr = Frame(popup, bg=def_color)
        self.rightFr.grid(column=1,  row=1, sticky="nsew")

        # ustawia odpowiednie szerokosci i wysokości kolumn i rzędów w układzie elementów
        self.rightFr.columnconfigure(0, weight=1)
        self.rightFr.columnconfigure(1, weight=1)

        self.rightFr.rowconfigure(0, weight=1)
        self.rightFr.rowconfigure(1, weight=1)
        self.rightFr.rowconfigure(2, weight=1)
        self.rightFr.rowconfigure(3, weight=1)
        self.rightFr.rowconfigure(4, weight=1)

        okButton = ttk.Button(popup, text="Apply", command=lambda: sequence(popup.destroy())) 
        okButton.grid(row=2, column=0,columnspan=4, sticky='nswe', pady=10)

        right()
        left()

    def SavedOptionsSettings(self,controller):
        popup = Toplevel()
        popup.grab_set()
        popup.title('Timer Settings') 
        popup["bg"] = def_color
        popup.geometry("600x600")
        popup.rowconfigure(0,weight=1)
        popup.rowconfigure(1,weight=1)
        popup.rowconfigure(2,weight=1)
        popup.rowconfigure(3,weight=1)
        popup.rowconfigure(4,weight=1)
        popup.rowconfigure(5,weight=1)
        popup.columnconfigure(0,weight=1)
        popup.columnconfigure(1,weight=1)
        popup.columnconfigure(2,weight=1)

        self.navFrame = Frame(popup)
        self.navFrame.grid(column=0, columnspan=3, row=0)

        # ustawia odpowiednie szerokosci i wysokości kolumn i rzędów w układzie elementów
        self.navFrame.columnconfigure(0, weight=1)
        self.navFrame.columnconfigure(1, weight=1)
        self.navFrame.columnconfigure(2, weight=1)
        self.navFrame.rowconfigure(3, weight=1)

        


        self.tree = Treeview(popup, selectmode="extended",columns=("Action"))
        self.tree.grid(row=1,rowspan=5, column=0, columnspan=2, sticky="news")
        self.tree.column("#0", minwidth=0, width=0, stretch=NO)

        self.tree.heading("Action", text="Saved option name")
        self.tree.column("Action", minwidth=15, width=10, stretch=YES)
        # load from ?
        self.tree.insert('', 'end', text='',values=["ON"], tags=['red_fg'])
        self.tree.insert('', 'end', text='',values=["OFF" ],tags=['red_fg'])


        applyButton = ttk.Button(popup, text="Apply",command=lambda: popup.destroy())
        applyButton.grid(row=1, column=2, sticky='we',padx=10, pady=10)
        
        loadButton = ttk.Button(popup, text="Load",command=lambda: popup.destroy())
        loadButton.grid(row=2, column=2, sticky='we',padx=10, pady=10)
        
        deleteButton = ttk.Button(popup, text="Delete",command=lambda: popup.destroy())
        deleteButton.grid(row=3, column=2, sticky='we',padx=10, pady=10)

        editButton = ttk.Button(popup, text="Edit",command=lambda: sequence(controller.show_frame(OneColorPage,"XSDASDFAS"), popup.destroy()))
        editButton.grid(row=4, column=2, sticky='we',padx=10, pady=10)

        backButton = ttk.Button(popup, text="Back",command=lambda: popup.destroy())
        backButton.grid(row=5, column=2, sticky='we',padx=10, pady=10)
        
app = Main(root)
root.geometry("1500x720")
root["bg"] = def_color
root.mainloop()
