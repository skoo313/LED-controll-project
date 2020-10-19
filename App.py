import tkinter as tk
from tkinter import ttk
from tkinter import *
from tkinter.ttk import *
from tkinter import *
from tkmacosx import Button, ColorVar, Marquee, Colorscale
import socket
import sys
import json
from colorsys import rgb_to_hls, hls_to_rgb
from colour import Color

# definiuję adres:port modułu wifi z którym bede sie łączył
HOST, PORT = "192.168.0.241", 8888 #241   157

# główne okno aplikacji
root = tk.Tk()


# definicje stylów i kolorów 
LARGE_FONT = ("ariel", 20) # dont know what you had here
def_color= '#202020'
def_color2='#252525'
style = Style()
style.theme_use("clam")
style.configure("Treeview.Heading",background="#434343", foreground="white", relief="flat")
style.configure("Treeview", background="#353535", fieldbackground="#282828", foreground="white")
style.configure('Header.Label', font=('Arial', 30, 'bold'), foreground ='#D3D3D3', background=def_color)
style.configure('TButton', font = ('Arial', 20, 'bold'),foreground ='#A8A8A8', background="#353535")
style.configure('TCheckbutton', font=('Arial', 10),foreground ='#A8A8A8', background="#353535")

def hex_rgb(col):
    return tuple(int(col.lstrip('#')[i:i+2], 16) for i in (0, 2, 4))

class Main():
    """ Główna klasa aplikacji odpowiedzialna za stworzenie głównych obszarów (Frame) i wypełnianie ich odpowiednią zawartością"""   
    def __init__(self,root):
       
        root.grid_rowconfigure(0, weight=1) # this needed to be added
        root.grid_columnconfigure(0, weight=1) # as did this

      
        # tworzy główny kontener na zawartość 
        main_container = Frame(root)
        main_container.grid(column=0, row=0, sticky = "nsew")
        main_container.grid_rowconfigure(0, weight = 1)
        main_container.grid_columnconfigure(0, weight = 1)

       
        self.frames = {}

        # tworzy i ustawia wartości początkowe dla istniejących klas (podstron)
        for fr in (MainPage,OneColorPage, GradientColorPage):
            frame = fr(main_container, self)
            self.frames[fr] = frame
            frame.grid(row = 0, column = 0, sticky = "nsew")
        
        self.show_frame(MainPage)
    def show_frame(self, pointer):
        """ Funkcja wywołująca odpowiednią klasę w ramce (Frame) """ 
        frame = self.frames[pointer]
        frame.tkraise()

class MainPage(tk.Frame):
    """ Klasa będąca stroną startową aplikacji """
    def __init__(self, parent, controller):

        # inicjuje ramkę dla podstrony
        tk.Frame.__init__(self, parent,bg=def_color)

        # ustawia odpowiednie szerokosci i wysokości kolumn i rzędów w układzie elementów
        self.columnconfigure(0, weight = 1)
        self.columnconfigure(1, weight = 1)

        self.rowconfigure(0, weight = 1)
        self.rowconfigure(1, weight = 1)
        self.rowconfigure(2, weight = 1)

        # Nagłówek aplikacji
        label = ttk.Label(self,style="Header.Label", text = "LED Controller", font = LARGE_FONT)
        label.grid(row = 0,column=0, columnspan=2, padx = 10, pady = 10)

        # Przyciski z dostępnymi opcjami
        button1 = ttk.Button(self, text = "One color", command = lambda: controller.show_frame(OneColorPage))
        button1.grid(row = 1,column=0, sticky = 'nswe', padx=10, pady=10)

        button2 = ttk.Button(self, text = "Gradient color",command = lambda: controller.show_frame(GradientColorPage))
        button2.grid(row = 1, column=1,sticky = 'nswe', pady=10)

        button3 = ttk.Button(self, text = "OPT_3")
        button3.grid(row = 2,column=0, sticky = 'nswe', padx=10)
        
        button4 = ttk.Button(self, text = "OPT_4")
        button4.grid(row = 2,column=1, sticky = 'nswe')

class ColorMain(tk.Frame):
    """ Klasa z głównymi funkcjami wyboru kolorów """
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent,bg=def_color)

        # ustawia odpowiednie szerokosci i wysokości kolumn i rzędów w układzie elementów
        self.columnconfigure(0, weight = 1)
        self.columnconfigure(1, weight = 1)
  
    def switchVar(self,op, var1,var2):
        """ Funkcja ustawiająca wybór użytkownika dotyczący sposobu educji koloru (checkbox'y). Aktywna może być tylko jedna opcja. """
        if( op=='basic'):
            if(var1.get()==1):
                var2.set(0)
            elif(var2.get()==0):
                var1.set(1)
            self.load_color_opt("basic")
        elif(op=='rgb'):
            if(var2.get()==1):
                var1.set(0)
            elif(var1.get()==0):
                var2.set(1)
            self.load_color_opt("rgb")
        elif(op=='color_from'):
            if(var1.get()==1):
                var2.set(0)
            elif(var2.get()==0):
                var1.set(1)
        elif(op=='color_to'):
            if(var2.get()==1):
                var1.set(0)
            elif(var1.get()==0):
                var2.set(1)

    def load_color_opt(self, opt):

        for widget in self.color_chooser_frame.winfo_children():
            widget.destroy()

        if(opt=="basic"):
            self.color_chooser_frame.rowconfigure(0, weight = 1)
            self.color_chooser_frame.rowconfigure(1, weight = 1)
            self.color_chooser_frame.rowconfigure(2, weight = 0)
            self.color_chooser_frame.columnconfigure(0, weight = 1)
            self.color_chooser_frame.columnconfigure(1, weight = 1)
            # ,,Slider'y" dla koloru i jasnosci
            var2 = ColorVar(value='white')
            var3= ColorVar(value='white')
            Colorscale(self.color_chooser_frame, value='hex',showinfo=False, command=lambda var3: self.changeColor(var3),            variable=self.colorTmp, mousewheel=1)                                  .grid(row=0, column=0, columnspan=2,sticky="nesw")
            Colorscale(self.color_chooser_frame, value='hex',showinfo=False, command= lambda var2 : self.changeBrightness(var2), variable=var2, mousewheel=1, gradient=('#000000', '#FFFFFF')).grid(row=1, column=0, columnspan=2,sticky="nesw")
        else:
            self.color_chooser_frame.rowconfigure(0, weight = 1)
            self.color_chooser_frame.rowconfigure(1, weight = 1)
            self.color_chooser_frame.rowconfigure(2, weight = 1)
            
            self.color_chooser_frame.columnconfigure(0, weight = 3)
            self.color_chooser_frame.columnconfigure(1, weight = 1)
            
            # ,,Slider'y" dla koloru i jasnosci
            r = ColorVar(value='white')
            r.set('#000000')
            g = ColorVar(value='white')
            g.set('#000000')
            b = ColorVar(value='white')
            b.set('#000000')
            Colorscale(self.color_chooser_frame, value='hex',showinfo=False,command=lambda r: self.changeColorRGB(r,g.get(),b.get()),  variable=r, mousewheel=1, gradient=('#000000', '#ff0000'))                                  .grid(row=0, column=0,sticky="nesw")
            Colorscale(self.color_chooser_frame, value='hex',showinfo=False, command= lambda g : self.changeColorRGB(r.get(),g,b.get()), variable=g, mousewheel=1, gradient=('#000000', '#00FF00')).grid(row=1, column=0,sticky="nesw")
            Colorscale(self.color_chooser_frame, value='hex',showinfo=False, command= lambda b : self.changeColorRGB(r.get(),g.get(),b), variable=b, mousewheel=1, gradient=('#000000', '#0000FF')).grid(row=2, column=0,sticky="nesw")

            self.rLabel=Label(self.color_chooser_frame,font = ('Arial', 20, 'bold'),foreground ='#A8A8A8', background="#353535", text="R:"+str(hex_rgb(r.get())[0]), bg=def_color)
            self.rLabel.grid(row=0, column=1, sticky="nesw")

            self.gLabel=Label(self.color_chooser_frame,font = ('Arial', 20, 'bold'),foreground ='#A8A8A8', background="#353535", text="G:"+str(hex_rgb(g.get())[0]), bg=def_color)
            self.gLabel.grid(row=1, column=1, sticky="nesw")
           
            self.bLabel=Label(self.color_chooser_frame,font = ('Arial', 20, 'bold'),foreground ='#A8A8A8', background="#353535", text="B:"+str(hex_rgb(b.get())[0]), bg=def_color)
            self.bLabel.grid(row=2, column=1, sticky="nesw")
    
    def changeColorRGB(self,red,green,blue):
        print(red)
        # wartość koloru w formacie hex przelicza na rgb
        
        r=hex_rgb(red)
        g=hex_rgb(green)
        b=hex_rgb(blue)

        self.rLabel.configure(text="R:"+str(r[0]))
        self.gLabel.configure(text="R:"+str(g[1]))
        self.bLabel.configure(text="R:"+str(b[2]))
        print(b)
        
        self._colorValue.set(value='#%02x%02x%02x' % (int(r[0]),int(g[1]),int(b[2])))
        
        self.colorTmp.set(self._colorValue.get())
        print(self.colorTmp.get())

    def changeColor(self,X):

        """ Funkcja wywoływana zmianą wartości na pasku wyboru koloru. Zapisuje wybór użytkownika do odpowiedniej zmiennej. """
        self._colorValue.set(X)

    def changeBrightness(self,X):
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

        print("XXXX: ", self.brightness.get() )
        print(brightness)

        print(color)
        print(brightness)

        r=int(color[0])
        g=int(color[1])
        b=int(color[2])
        # print(r," X ", g," X ",b)
        
        # oblicza kolor uzywany przy jego podglądzie i 
        self.colorTmp.set(value='#%02x%02x%02x' % (self.adjust_color_lightness(r,g,b,brightness[0]/100)))
    
    def adjust_color_lightness(self, r, g, b, factor):
        """ Funkcja dostosowująca kolor rgb zależnie od jego jasności (model hsv) """
        h, l, s = rgb_to_hls(r / 255.0, g / 255.0, b / 255.0)
        l = max(min(l * factor, 1.0), 0.0)
        r, g, b = hls_to_rgb(h, l, s)
        return int(r * 255), int(g * 255), int(b * 255)
    
    def send(self,data):
        finalData = json.dumps(data)

        # Create a socket (SOCK_STREAM means a TCP socket)
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
           # Connect to server and send data
           sock.connect((HOST, PORT))
           sock.sendall(bytes(finalData,encoding="utf-8"))
           
           # Receive data from the server and shut down
           received = sock.recv(1024)
           received = received.decode("utf-8")
           
        finally:
           sock.close()

class OneColorPage(ColorMain):
    """ Klasa z widokiem umożliwiającym ustawienia jednolicie świecących ledów """
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent,bg=def_color)

        
        # ustawia odpowiednie szerokosci i wysokości kolumn i rzędów w układzie elementów
        self.columnconfigure(0, weight = 1)
        self.columnconfigure(1, weight = 1)

        self.rowconfigure(0, weight = 1)
        self.rowconfigure(1, weight = 2)
        # self.rowconfigure(2, weight = 1)
        self.rowconfigure(3, weight = 3)
        
        # self.rowconfigure(4, weight = 4)
        # self.rowconfigure(5, weight = 4)

        self.main_controllFrame = Frame(self, bg=def_color)
        self.main_controllFrame.grid(column=0, columnspan=2, row=0, sticky = "nsew")
        # ustawia odpowiednie szerokosci i wysokości kolumn i rzędów w układzie elementów
        self.main_controllFrame.columnconfigure(0, weight = 1)
        self.main_controllFrame.columnconfigure(1, weight = 1)
        self.main_controllFrame.rowconfigure(0, weight = 2)
        
        # przyciski nawigujące
        button1 = ttk.Button(self.main_controllFrame,style = 'TButton' ,text = "Apply", command = lambda: self.apply(self._colorValue.get(),self.brightness.get()))
        button1.grid(row = 0,column=0, sticky = 'nswe', padx=10, pady=10)

        button2 = ttk.Button(self.main_controllFrame, text = "Back", command = lambda: controller.show_frame(MainPage))
        button2.grid(row = 0, column=1,sticky = 'nswe', pady=10)



        # wartości początkowe:
        self.brightness=ColorVar(value='white') # jasność koloru
        
        self._colorValue=ColorVar(value='black') # barwa koloru
        self.colorTmp = ColorVar(value='black') # zmienna pomocnicza dla wizualizacji ustawianego koloru
        
        # zmienne dla pasków wyboru
        
        fgvar = ColorVar(value='white')

        


        # obszar z podglądem wybranego koloru
        Label(self, text="\n\n\n\n",bg=self.colorTmp, fg=fgvar).grid(row=1, column=0, columnspan=2,sticky="nesw", pady=50,padx=50)

        var1 = IntVar(value=1)
        var2 = IntVar(value=0)
        tk.Checkbutton(self, command=lambda: self.switchVar('basic', var1,var2),   activebackground='red',foreground ='red', background="#353535",font=('Arial', 15), text="Basic color chooser", variable=var1).grid(row=2, column=0, sticky="news",padx=10,pady=10)    
        tk.Checkbutton(self, command=lambda: self.switchVar('rgb',var1,var2),      activebackground='red',foreground ='red', background="#353535",font=('Arial', 15), text="RGB color chooser",   variable=var2).grid(row=2, column=1, sticky="news",padx=10,pady=10)
        
        
        # self.grid_columnconfigure(2, weight=24) # as did this

        self.color_chooser_frame = Frame(self)
        self.color_chooser_frame.grid(column=0, columnspan=2, row=3, sticky = "nsew")
        self.load_color_opt("basic")      

    def apply(self,X,Y):
        """ Funkcja konwertująca kolor i jasność do json'a i wysyłająca go na zadany adres """
        # wartość koloru w formacie hex przelicza na rgb
        colour = hex_rgb(X)

        # wartość jasności w formacie hex przelicza na rgb 
        # b = self.brightness.get().lstrip('#')
        # brightness= tuple(int(b[i:i+2], 16) for i in (0, 2, 4))
        brightness = hex_rgb(self.brightness.get())
        m={}
        
        m["num"]=1
        m["r"]=int(colour[0])
        m["g"]=int(colour[1])
        m["b"]=int(colour[2])
        m["brightness"]=int(brightness[0])
       
        print(m)
        
        self.send(m)
        print("Done")

class GradientColorPage(ColorMain):
    """ Klasa z widokiem umożliwiającym ustawienia gradientu ledów """
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent,bg=def_color)

        
        # ustawia odpowiednie szerokosci i wysokości kolumn i rzędów w układzie elementów
        self.columnconfigure(0, weight = 1)
        self.columnconfigure(1, weight = 1)

        self.rowconfigure(0, weight = 1)
        self.rowconfigure(1, weight = 2)
        self.rowconfigure(4, weight = 3)
        # self.rowconfigure(4, weight = 4)
        # self.rowconfigure(5, weight = 4)

        self.main_controllFrame = Frame(self, bg=def_color)
        self.main_controllFrame.grid(column=0, columnspan=2, row=0, sticky = "nsew")
        # ustawia odpowiednie szerokosci i wysokości kolumn i rzędów w układzie elementów
        self.main_controllFrame.columnconfigure(0, weight = 1)
        self.main_controllFrame.columnconfigure(1, weight = 1)
        self.main_controllFrame.rowconfigure(0, weight = 2)
        
        # przyciski nawigujące
        button1 = ttk.Button(self.main_controllFrame,style = 'TButton' ,text = "Apply", command = lambda: self.apply_gradient(self.colorFrom.get(),self.colorTo.get()))
        button1.grid(row = 0,column=0, sticky = 'nswe', padx=10, pady=10)

        button2 = ttk.Button(self.main_controllFrame, text = "Back", command = lambda: controller.show_frame(MainPage))
        button2.grid(row = 0, column=1,sticky = 'nswe', pady=10)



        # wartości początkowe:
        self.brightness=ColorVar(value='white') # jasność koloru
        
        self._colorValue=ColorVar(value='black') # barwa koloru
        self.colorTmp = ColorVar(value='black') # zmienna pomocnicza dla wizualizacji ustawianego koloru
        self.colorFrom=ColorVar(value='black') 
        self.colorTo=ColorVar(value='black') 
        # zmienne dla pasków wyboru
        
        fgvar = ColorVar(value='white')

        


        # obszar z podglądem wybranego koloru
        # Label(self, text="\n\n\n\n",bg=self.colorTmp, fg=fgvar).grid(row=2, column=0, columnspan=2,sticky="nesw", pady=50,padx=50)
        GradientFrame(self,self.colorFrom, self.colorTo, borderwidth=1, relief="sunken").grid(row=2, column=0, columnspan=2,sticky="nesw", pady=50,padx=50)

        col1 = IntVar(value=1)
        col2 = IntVar(value=0)
        
        tk.Checkbutton(self, command=lambda: self.switchVar('color_from', col1,col2),   activebackground='red',foreground ='red', background="#353535",font=('Arial', 15), text="Start color", variable=col1).grid(row=1, column=0, sticky="news",padx=10,pady=10)    
        tk.Checkbutton(self, command=lambda: self.switchVar('color_to',col1,col2),  activebackground='red',foreground ='red', background="#353535",font=('Arial', 15), text="End color", variable=col2).grid(row=1, column=1, sticky="news",padx=10,pady=10)
        

        var1 = IntVar(value=1)
        var2 = IntVar(value=0)
        tk.Checkbutton(self, command=lambda: self.switchVar('basic', var1,var2),   activebackground='red',foreground ='red', background="#353535",font=('Arial', 15), text="Basic color chooser", variable=var1).grid(row=3, column=0, sticky="news",padx=10,pady=10)    
        tk.Checkbutton(self, command=lambda: self.switchVar('rgb',var1,var2),  activebackground='red',foreground ='red', background="#353535",font=('Arial', 15), text="RGB color chooser", variable=var2).grid(row=3, column=1, sticky="news",padx=10,pady=10)
        
        # self.grid_rowconfigure(3, weight=4) # this needed to be added
        # self.grid_columnconfigure(2, weight=24) # as did this

        self.color_chooser_frame = Frame(self)
        self.color_chooser_frame.grid(column=0, columnspan=2, row=4, sticky = "nsew")

        self.colorTmp.trace_add('write', lambda name, index, mode, c1=col1,c2=col2: self.my_callback(c1,c2)) 
    
        self.load_color_opt("basic")     

    def my_callback(self,col1,col2): 
        """ Funkcja ustawiająca kolor koloru od/do """

        if(col1.get()):
            self.colorFrom.set(self.colorTmp.get())
        elif(col2.get()):
            self.colorTo.set(self.colorTmp.get())

        # ustawia podgląd gradientu
        GradientFrame(self, self.colorFrom, self.colorTo, borderwidth=1, relief="sunken").grid(row=2, column=0, columnspan=2,sticky="nesw", pady=50,padx=50)

    def apply_gradient(self,colorFrom,colorTo):
        """ Funkcja obliczająca kolory wchodzące w skład gradientu i przekazujące je dalej do wysłania. """

        colors = list(Color(colorFrom).range_to(Color(colorTo),65))
        
        print("LEN: ", len(colors))
        
        m={}
        m["num"]=65

        for i in range(len(colors)):
            c=colors[i]
            
            # DO POPRAWIENIA! 
            if(len(str(c))==4 or str(c)[0] is not '#'):
                print(c)
                c="#000000"
                
            col=hex_rgb(str(c))
            
            m["r" + str(i)]=col[0]
            m["g"+ str(i)]=col[1]
            m["b"+ str(i)]=col[2]
        
        self.send(m)
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
      (r1,g1,b1) = self.winfo_rgb(self._color1)
      (r2,g2,b2) = self.winfo_rgb(self._color2)
      r_ratio = float(r2-r1) / limit
      g_ratio = float(g2-g1) / limit
      b_ratio = float(b2-b1) / limit
      for i in range(limit):
          nr = int(r1 + (r_ratio * i))
          ng = int(g1 + (g_ratio * i))
          nb = int(b1 + (b_ratio * i))
          color = "#%4.4x%4.4x%4.4x" % (nr,ng,nb)
          self.create_line(i,0,i,height, tags=("gradient",), fill=color)
      self.lower("gradient")  
          
app = Main(root)
root.geometry("1280x720")
root["bg"] = def_color
root.mainloop()
