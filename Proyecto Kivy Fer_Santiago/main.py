# -*- coding: utf-8 -*-
# En ocasiones el widget TextInput muestra un error para
# solucionar instala xclip 
# $ sudo apt-get install xclip
"""
Proyecto Final PROGRAMACION II
Autores: Fer Jara, Santiago Sosa
"""
### Importamos las Librerias a utilizar #############################   
import kivy
import os
import sqlite3

from kivy.config import Config
Config.set("graphics","width","340")
Config.set("graphics","hight","640")

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.popup import Popup
from kivy.uix.label import Label 
from kivy.uix.screenmanager import ScreenManager, Screen 
from kivy.uix.screenmanager import FadeTransition
from kivy.properties import StringProperty
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
#####################################################################   

###### Conexión a la base de datos ##################################   
def connect_to_database(path):
    try:
        con = sqlite3.connect(path)
        cursor = con.cursor()
        create_table_productos(cursor)
        con.commit()
        con.close()
    except Exception as e:
        print(e)
#####################################################################   

##### Crear la tabla de Productos ###################################   
def create_table_productos(cursor):
    cursor.execute(
        '''
        CREATE TABLE Productos(
        ID        tinyint   PRIMARY KEY  NOT NULL,
        Nombre    TEXT               NOT NULL,
        Marca     TEXT               NOT NULL,
        Costo     FLOAT              NOT NULL,
        Almacen   tinyint                NOT NULL
        );'''
    )
#####################################################################   

##### Class MessagePopup Error ######################################
class MessagePopup(Popup):
    pass
#####################################################################   

####  Desarrollo para la base de datos ##############################
class MainWid(ScreenManager):
    def __init__(self,**kwargs):
        super(MainWid,self).__init__()
        self.APP_PATH = os.getcwd()
        self.DB_PATH = self.APP_PATH+'/dbproductos.db'
        self.StartWid = StartWid(self)
        self.DataBaseWid = DataBaseWid(self)
        self.InsertDataWid = BoxLayout()
        self.UpdateDataWid = BoxLayout()
        self.Popup = MessagePopup()
        
        wid = Screen(name='Empezar')
        wid.add_widget(self.StartWid)
        self.add_widget(wid)
        wid = Screen(name='Base de Datos')
        wid.add_widget(self.DataBaseWid)
        self.add_widget(wid)
        wid = Screen(name='Insertar Datos')
        wid.add_widget(self.InsertDataWid)
        self.add_widget(wid)
        wid = Screen(name='Actualizar Datos')
        wid.add_widget(self.UpdateDataWid)
        self.add_widget(wid)
        
        self.goto_start()
        
    def goto_start(self):
        self.current = 'Empezar'
        
    def goto_database(self):
        self.DataBaseWid.check_memory()
        self.current = 'Base de Datos'
        
    def goto_insertdata(self):
        self.InsertDataWid.clear_widgets()
        wid = InsertDataWid(self)
        self.InsertDataWid.add_widget(wid)
        self.current = 'Insertar Datos'

    def goto_updatedata(self,data_id):
        self.UpdateDataWid.clear_widgets()
        wid = UpdateDataWid(self,data_id)
        self.UpdateDataWid.add_widget(wid)
        self.current = 'Actualizar Datos'
#####################################################################   

#######  Clase para crear componentes ###############################   
class StartWid(BoxLayout):
    def __init__(self,mainwid,**kwargs):
        super(StartWid,self).__init__()
        self.mainwid = mainwid
        
    def create_database(self):
        connect_to_database(self.mainwid.DB_PATH)
        self.mainwid.goto_database()
#####################################################################   

############                  #######################################
class DataBaseWid(BoxLayout):
    registro = []
    def __init__(self,mainwid,**kwargs):
        super(DataBaseWid,self).__init__()
        self.mainwid = mainwid
        
    def check_memory(self):
        self.ids.container.clear_widgets()
        con = sqlite3.connect(self.mainwid.DB_PATH)
        cursor = con.cursor()
        cursor.execute('select ID, Nombre, Marca, Costo, Almacen from Productos')
        #rows = cursor.fetchall()
        for i in cursor:
            wid = DataWid(self.mainwid)
            r1 = 'ID: '+str(100000000+i[0])[1:9]+'\n'
            r2 = i[1]+', '+i[2]+'\n'
            r3 = 'Precio por unidad: '+'$'+str(i[3])+'\n'
            r4 = 'En almacen: '+str(i[4])
            print(i)
            #print(i[0])
            wid.data_id = str(i[0])
            wid.data = r1+r2+r3+r4
            self.ids.container.add_widget(wid)
            self.ids.container
          #  self.registro.append(i)
        #print(self.registro)
        #resultado=cursor.fetchall()
        #print(len(resultado))
        #for i in range(0,len(resultado),1):
            #print(resultado[i])
        wid = NewDataButton(self.mainwid)
        w = NewDataButtonPDF(self.mainwid)
        self.ids.container.add_widget(wid)
        self.ids.container.add_widget(w)
        con.close()
#####################################################################   

###### Clase para actualizar datos insertados #######################
class UpdateDataWid(BoxLayout):
    def __init__(self,mainwid,data_id,**kwargs):
        super(UpdateDataWid,self).__init__()
        self.mainwid = mainwid
        self.data_id = data_id
        self.check_memory()

    def check_memory(self):
        con = sqlite3.connect(self.mainwid.DB_PATH)
        cursor = con.cursor()
        s = 'select Nombre, Marca, Costo, Almacen from Productos where ID='
        cursor.execute(s+self.data_id)
        for i in cursor:
            self.ids.ti_nombre.text = i[0]
            self.ids.ti_marca.text = i[1]
            self.ids.ti_costo.text = str(i[2])
            self.ids.ti_almacen.text = str(i[3])
        con.close()

    def update_data(self):
        con = sqlite3.connect(self.mainwid.DB_PATH)
        cursor = con.cursor()
        d1 = self.ids.ti_nombre.text
        d2 = self.ids.ti_marca.text
        d3 = self.ids.ti_costo.text
        d4 = self.ids.ti_almacen.text
        a1 = (d1,d2,d3,d4)
        s1 = 'UPDATE Productos SET'
        s2 = 'Nombre="%s",Marca="%s",Costo=%s,Almacen=%s' % a1
        s3 = 'WHERE ID=%s' % self.data_id
        try:
            cursor.execute(s1+' '+s2+' '+s3)
            con.commit()
            con.close()
            self.mainwid.goto_database()
        except Exception as e:
            message = self.mainwid.Popup.ids.message
            self.mainwid.Popup.open()
            self.mainwid.Popup.title = "Error en la Base de Datos"
            if '' in a1:
                message.text = 'Uno o más campos están vacíos'
            else: 
                message.text = str(e)
            con.close()

    # Metodo para eliminar un registro de la base de datos 
    def delete_data(self):
        con = sqlite3.connect(self.mainwid.DB_PATH)
        cursor = con.cursor()
        s = 'delete from productos where ID='+self.data_id
        cursor.execute(s)
        con.commit()
        con.close()
        self.mainwid.goto_database()

    def back_to_dbw(self):
        self.mainwid.goto_database()
#####################################################################   

############## Clase para insertar datos  ###########################   
class InsertDataWid(BoxLayout):
    def __init__(self,mainwid,**kwargs):
        super(InsertDataWid,self).__init__()
        self.mainwid = mainwid

    def insert_data(self):
        con = sqlite3.connect(self.mainwid.DB_PATH)
        cursor = con.cursor()
        d1 = self.ids.ti_id.text
        d2 = self.ids.ti_nombre.text
        d3 = self.ids.ti_marca.text
        d4 = self.ids.ti_costo.text
        d5 = self.ids.ti_almacen.text
        a1 = (d1,d2,d3,d4,d5)
        s1 = 'INSERT INTO Productos(ID, Nombre, Marca, Costo, Almacen)'
        s2 = 'VALUES(%s,"%s","%s",%s,%s)' % a1
        try:
            cursor.execute(s1+' '+s2)
            con.commit()
            con.close()
            self.mainwid.goto_database()
        except Exception as e:
            message = self.mainwid.Popup.ids.message
            self.mainwid.Popup.open()
            self.mainwid.Popup.title = "Error en la Base de Datos"
            if '' in a1:
                message.text = 'Uno o más campos están vacíos'
            else: 
                message.text = str(e)
            con.close()

    def back_to_dbw(self):
        self.mainwid.goto_database()
#####################################################################   

#####                       #########################################   
class DataWid(BoxLayout):
    def __init__(self,mainwid,**kwargs):
        super(DataWid,self).__init__()
        self.mainwid = mainwid
        
    def update_data(self,data_id):
        self.mainwid.goto_updatedata(data_id)
#####################################################################   

###### Boton Agregar Producto #######################################   
class NewDataButton(Button):
    def __init__(self,mainwid,**kwargs):
        super(NewDataButton,self).__init__()
        self.mainwid = mainwid
        
    def create_new_product(self):
        self.mainwid.goto_insertdata()
#####################################################################  

###### Boton PDF ####################################################   
class NewDataButtonPDF(Button):
    registro = []
    def __init__(self,mainwid,**kwargs):
        super(NewDataButtonPDF,self).__init__()
        self.mainwid = mainwid
        
    def create_new_pdf(self):
        width, height = letter
        print(width, height,letter)
        c = canvas.Canvas("Productos.pdf", pagesize=letter)
        con = sqlite3.connect(self.mainwid.DB_PATH)
        cursor = con.cursor()
        cursor.execute('select ID, Nombre, Marca, Costo, Almacen from Productos')
        #rows = cursor.fetchall()
        for i in cursor:
            wid = DataWid(self.mainwid)
            r1 = 'ID: '+str(100000000+i[0])[1:9]+'\n'
            r2 = i[1]+', '+i[2]+'\n'
            r3 = 'Precio por unidad: '+'$'+str(i[3])+'\n'
            r4 = 'En almacen: '+str(i[4])
            print(i)
            #print(i[0])
            wid.data_id = str(i[0])
            wid.data = r1+r2+r3+r4
            self.registro.append(i)
        print(self.registro)
        if len(self.registro)==0:
            c.line(40, 660, 572, 660)
            c.drawCentredString(306, 661, "NO HAY PRODUCTOS")
            c.showPage()
        else:
            for i in range(0,len(self.registro),1):
                print(self.registro[i][0])
                print(self.registro[i][1])
                print(self.registro[i][2])
                print(self.registro[i][3])
                print(self.registro[i][4])
            c.line(40, 720, 572, 720)
            c.drawCentredString(93, 705, "ID ")
            c.drawCentredString(199.25, 705, "Nombre")
            c.drawCentredString(305.75, 705, "Marca")
            c.drawCentredString(412.25, 705, "Precio")
            c.drawCentredString(518.5, 705, "Cantidad")
            c.line(40, 700, 572, 700)
            a = 700
            print('hola')
            print(len(self.registro))
            for i in range(0, len(self.registro), 1):
                b = a
                a = a - 20
                c.line(40, a, 572, a) #linea inferior
                c.line(40, b, 40, a)#primer linea vertical
                c.drawCentredString(93, a+5, str(self.registro[i][0]))
                c.line(146, b, 146, a)#
                c.drawCentredString(199.25, a+5, str(self.registro[i][1]))
                c.line(252.5, b, 252.5, a)
                c.drawCentredString(305.75, a+5, str(self.registro[i][2]))
                c.line(359, b, 359, a)
                c.drawCentredString(412.25, a+5, "$"+str(self.registro[i][3]))
                c.line(465.5, b, 465.5, a)
                c.drawCentredString(518.5, a+5, str(self.registro[i][4]))
                c.line(572, b, 572, a)
        c.save()
##################################################################### 
   
class MainApp(App):
    title = 'Fer y Santiago Inventario'
    def build(self):
        return MainWid()
        
if __name__ == '__main__':
    MainApp().run()
