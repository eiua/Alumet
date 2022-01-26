#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""@author: lucas
Classes nécéssaires à l'interface graphique de Lumet v0.6
Licence GPL euia / Lucas GRIGIS copyleft
"""
# Import des librairies externes à lumet
# from multiprocessing import Pool
# from datetime import datetime
# from datetime import timedelta
# import cartopy.crs as ccrs
# import cartopy.feature as cfeature
from tkinter import *
#from PIL import Image, ImageTk
from functools import partial
import threading
#import queue
#from Tkinter import *
#import matplotlib
#matplotlib.use("TkAgg")
#import matplotlib.pyplot as plt
#import matplotlib.dates as mdates
#import matplotlib.colors as mcolors
#from matplotlib.backends.backend_tkagg import FigureCanvasTk
#from matplotlib.backends.backend_tkagg import NavigationToolbar2Tk
#from matplotlib.figure import Figure
#import pygrib
#import numpy as np
#import time
# Import des librairies internes à Lumet
from v0_6_arome_carte_pour_canvas import *
from v0_6_arome_cartes import *
from telechargement_modeles import *

# Classe d'interface graphique, les objets de cette classe
# sont appelées dans le main du projet.

class Application(Tk):
    # Héritière de Tk, cette classe code pour une interface graphique.

    def __init__(self):
        Tk.__init__(self)        # constructeur de la classe parente

        #self.queue = queue.Queue()

        self.date_du_run = self.obtenir_date_du_run()
        lab_run = Label(self, text="\nPrévisions en date du " + \
                        self.date_du_run[6:8] + "/"+ \
                        self.date_du_run[4:6] + "/" + self.date_du_run[0:4]+\
                        " run de " + self.date_du_run[-2:] + "H")
        lab_run.pack()
        #print(self.date_du_run)

        self.creer_barre_menus()# création de la barre des menus

        # Initialisation du canevas qui sera modifié pour créer
        #et afficher les différentes cartes
        self.can = Canvas(self, width =50, height =50, bg ="white")
        self.can.pack(side =TOP, padx =5, pady =5)

        # Initalisation des paramètres d'échéances et de zoom
        #pour les cartes à afficher par lumet.
        self.echh = 0
        self.zoomi = 0

        # Initalisation de la case à cocher pour le zoom.
        self.chk = 0
        self.ck = IntVar()
        zones = ("Domaines modèles entier (par défaut)","Zoom Sud-Est France",
                 "Zoom Toulouse Garonne Ariège","Zoom Grand Sud France",
                 "Zoom Lus Genève Charlieu","Zoom Grand Mont Blanc",
                 "Zoom Savoie","Zoom Écrins",)
        for zone in range(len(zones)):
            check_1 = Checkbutton(self,text = zones[zone],variable=zone,
                                  command=partial(self.regler_zoom,zone))
            check_1.pack()

        # Échelle pour échéances
        scale_9 = Scale(self,length = 600, orient = HORIZONTAL,
                        sliderlength = 25,
                        label = "Échéance de prévision +(**)H:",
                        from_ = 0, to = 114, tickinterval = 6,
                        resolution = 1,showvalue = 1,
                        command = self.regler_echeance)
        scale_9.pack()

        # Champ Entry et bouton pour que l’utilisateur rentre la date du run
        self.entrer_date_du_run = StringVar(self)
        lab_run = Label(self, text="==========================="+
                        "\nTélécharger les dernières prévisions,"+\
                        "\nDonnées du " + self.date_du_run[6:8] + "/"+ \
                        self.date_du_run[4:6] + "/" + self.date_du_run[0:4]+\
                        " run de " + self.date_du_run[-2:] + "H")
        lab_run.pack()

        boutton_telech_aro_0025 = Button(self, height=1,
                                     text="Télécharger AROME 0.025°",
                                     command=partial(
                                     self.telechargement_modeles,
                                     "AROME","0.025"))
        boutton_telech_aro_0025.pack()

        boutton_telech_aro_001 = Button(self, height=1,
                                     text="Télécharger AROME 0.01°",
                                     command=partial(
                                     self.telechargement_modeles,
                                     "AROME","0.01"))
        boutton_telech_aro_001.pack()

        boutton_telech_arp_01 = Button(self, height=1,
                                     text="Télécharger ARPEGE 0.1°",
                                     command=partial(
                                     self.telechargement_modeles,
                                     "ARPEGE","0.1","SP1"))
        boutton_telech_arp_01.pack()

        # Champ Entry et bouton pour que l’utilisateur rentre la date du run
        # qu’il veut
        self.entrer_date_du_run = StringVar(self)
        lab_run = Label(self, text="==========================="+
                        "\nUtiliser un autre run ? Saisissez votre date d’intérêt\nFormat "+
                        "\"yyyymmjjrr\" ex 1er nov 2021 run de 03h "+
                        "= 2021011103")
        lab_run.pack()

        entrer_date_du_run = Entry(self,textvariable=self.entrer_date_du_run,
                                   width=20)
        entrer_date_du_run.pack(pady=20)

        boutton_date_du_run = Button(self, height=1,
                                     text="Valider date du run",
                                     command=self.saisir_date_du_run)
        boutton_date_du_run.pack()

    # Barre de menus
    def creer_barre_menus(self):
        menu_bar = Menu(self)

        menu_arome = Menu(menu_bar, tearoff=0)
        menu_arome.add_command(label="Température à 2m", underline=3,
                               accelerator="CTRL+N",
                               command=partial(self.dessiner_carte_mono_param,
                                               "AROME","0.025","T2m"))
        menu_arome.add_command(label="Humidité relative à 2m", underline=3,
                               accelerator="CTRL+N",
                               command=partial(self.dessiner_carte_mono_param,
                                               "AROME","0.025","Hu2m"))
        menu_arome.add_command(label="Humidité relative à 2m 0.01°", underline=3,
                               accelerator="CTRL+N",
                               command=partial(self.dessiner_carte_mono_param,
                                               "AROME","0.01","Hu2m"))
        menu_arome.add_command(label="Hauteur de neige", underline=3,
                               accelerator="CTRL+N",
                               command=partial(self.dessiner_carte_mono_param,
                                               "AROME","0.025","neige"))
        menu_arome.add_command(label="Hauteur de neige 0.01° ", underline=3,
                               accelerator="CTRL+N",
                               command=partial(self.dessiner_carte_mono_param,
                                               "AROME","0.01","neige"))
        menu_arome.add_command(label="Pression à la surface 0.025° ", underline=3,
                               accelerator="CTRL+N",
                               command=partial(self.dessiner_carte_mono_param,
                                               "AROME","0.025","Psol"))
        menu_arome.add_command(label="Pression à la surface 0.01° ", underline=3,
                               accelerator="CTRL+N",
                               command=partial(self.dessiner_carte_mono_param,
                                               "AROME","0.01","Psol"))
        menu_arome.add_command(label="Pression surface ARP 0.1° ", underline=3,
                               accelerator="CTRL+N",
                               command=partial(self.dessiner_carte_mono_param,
                                               "ARPEGE","0.1","Psol"))
        menu_arome.add_command(label="Pression surface ARP 0.5° ", underline=3,
                               accelerator="CTRL+N",
                               command=partial(self.dessiner_carte_mono_param,
                                               "ARPEGE","0.5","Psol"))
        menu_arome.add_command(label="Précipitations", underline=3,
                               accelerator="CTRL+N",
                               command=partial(self.dessiner_carte,
                                               "AROME","0.025","Precips"))

        menu_arome.add_command(label="Pmer vent rafales", underline=1,
                               accelerator="CTRL+N",
                               command=partial(self.dessiner_carte,
                                               "AROME","0.025","Pmer"))

        #menu_arome.add_separator()
        menu_arome.add_command(label="TPW850hPa + altitude Z1.5 pvu",
                               underline=0, accelerator="CTRL+O",
                               command=partial(self.dessiner_carte,
                                               "AROME","0.025",
                                               "TPW850_Z1.5pvu"))

        menu_arome.add_command(label="Z1.5pvu + Jet à la Z1.5 pvu",
                               underline=0, accelerator="CTRL+S",
                               command=partial(self.dessiner_carte,
                                               "AROME","0.025","Jet_Z1.5pvu"))

        menu_arome.add_command(label="Rayonnement SW descendant", underline=0,
                               accelerator="CTRL+N",
                               command=partial(self.dessiner_carte,
                                               "AROME","0.025","DSW"))

        menu_arome.add_separator()

        menu_arome.add_command(label="T2m Arome 0.01°", underline=1,
                               command=partial(self.dessiner_carte,
                                               "AROME","0.01","T2m"))

        menu_bar.add_cascade(label="AROME", underline=0, menu=menu_arome)

        self.bind_all("<Control-n>", lambda x: self.do_something())
        self.bind_all("<Control-o>", lambda x: self.open_file())
        self.bind_all("<Control-s>", lambda x: self.do_something())

        menu_arpege = Menu(menu_bar, tearoff=0)
        menu_arpege.add_command(label="Température à 2m", underline=0,
                                accelerator="CTRL+N",
                                command=partial(self.dessiner_carte_mono_param,
                                                "ARPEGE","0.1","T2m"))

        menu_arpege.add_command(label="Précipitations", underline=0,
                                accelerator="CTRL+N",
                                command=partial(self.dessiner_carte,
                                                "ARPEGE","0.1","Precips"))

        menu_arpege.add_command(label="Pmer vent rafales", underline=1,
                                accelerator="CTRL+N",
                                command=partial(self.dessiner_carte,
                                                "ARPEGE","0.1","Pmer"))

        menu_arpege.add_command(label="Arp 0.5° Température à 2m", underline=0,
                                accelerator="CTRL+N",
                                command=partial(self.dessiner_carte_mono_param,
                                                "ARPEGE","0.5","T2m"))

        menu_bar.add_cascade(label="ARPEGE", underline=0, menu=menu_arpege)

        menu_tout_arome = Menu(menu_bar, tearoff=0)
        #menu_tout_arome.add_command(label="Température à 2m",
          #                           command=self.dessiner_tout_aro_0025_T2m)
        menu_tout_arome.add_command(label="Température à 2m",
                                    command=threading.Thread(
                                    target=self.dessiner_tout_aro_0025_T2m)
                                    .start)
        # menu_tout_arome.add_command(label="T2m Arome 0.01°",
        #                             command=self.dessiner_tout_aro_001_T2m)      
        menu_tout_arome.add_command(label="T2m Arome 0.01°",
                                    command=threading.Thread(
                                    target=self.dessiner_tout_aro_001_T2m)
                                    .start)
        menu_bar.add_cascade(label="tracer tout Arome",
                              underline=0, menu=menu_tout_arome)

        menu_tout_arpege = Menu(menu_bar, tearoff=0)
        menu_tout_arpege.add_command(label="Température à 2m",
                                     command=threading.Thread(
                                     target=self.dessiner_tout_arp_01_T2m)
                                     .start)
        menu_bar.add_cascade(label="tracer tout Arpege", underline=0,
                             menu=menu_tout_arpege)

        menu_tele_modeles = Menu(menu_bar,tearoff=0)  
        
        menu_tele_base = Menu(menu_tele_modeles, tearoff=0)
        menu_tele_base.add_command(label="Arome 0.025°: SP1",
                                      command=partial(
                                      self.telechargement_modeles,"AROME",
                                      "0.025","SP1"))
        menu_tele_base.add_command(label="Arome 0.025°: IP5",
                                      command=partial(
                                      self.telechargement_modeles,"AROME",
                                      "0.025","IP5"))
        menu_tele_base.add_command(label="Arome 0.01°: SP1",
                                      command=partial(
                                      self.telechargement_modeles,"AROME",
                                      "0.01","SP1"))
        menu_tele_base.add_command(label="Arpege 0.1°: SP1",
                                      command=partial(
                                      self.telechargement_modeles,"ARPEGE",
                                      "0.1","SP1"))        
        menu_tele_base.add_command(label="Arpege 0.1°: IP4",
                                      command=partial(
                                      self.telechargement_modeles,"ARPEGE",
                                      "0.1","IP4"))        
        menu_tele_base.add_command(label="Arpege 0.5°: SP1",
                                      command=partial(
                                      self.telechargement_modeles,"ARPEGE",
                                      "0.5","SP1"))        
        menu_tele_base.add_command(label="Arpege 0.5°: IP4",
                                      command=partial(
                                      self.telechargement_modeles,"ARPEGE",
                                      "0.5","IP4"))
        menu_tele_modeles.add_cascade(label="Téléchargement paquets de base",
                             underline=0,menu=menu_tele_base)
        
        menu_tele_params_tous_1 = Menu(menu_tele_modeles, tearoff=0)
        menu_tele_params_tous_1.add_command(label="Arome 0.025°: SP2 - "+\
                                      "paramètres additionnels à la surface",
                                      command=partial(
                                      self.telechargement_modeles,"AROME",
                                      "0.025","SP2"))
        menu_tele_params_tous_1.add_command(label="Arome 0.025°: SP3 - " + \
                                      "paramètres additionnels (2) à la surface",
                                      command=partial(
                                      self.telechargement_modeles,"AROME",
                                      "0.025","SP3"))
        menu_tele_params_tous_1.add_command(label="Arome 0.025°: IP1 - "+ \
                                      "paramètres courants en niveaux isobares",
                                      command=partial(
                                      self.telechargement_modeles,"AROME",
                                      "0.025","IP1"))
        menu_tele_params_tous_1.add_command(label="Arome 0.025°: IP2 - "+\
                                      "paramètres additionnels en niveaux isobares",
                                      command=partial(
                                      self.telechargement_modeles,"AROME",
                                      "0.025","IP2"))
        menu_tele_params_tous_1.add_command(label="Arome 0.025°: IP3 - "+\
                                      "paramètres additionnels (2) en niveaux isobares",
                                      command=partial(
                                      self.telechargement_modeles,"AROME",
                                      "0.025","IP3"))
        menu_tele_params_tous_1.add_command(label="Arome 0.025°: IP4 - "+\
                                            "paramètres additionnels (3) en niveaux isobares",
                                            command=partial(
                                            self.telechargement_modeles,"AROME",
                                            "0.025","IP4"))          
        menu_tele_params_tous_1.add_command(label="Arome 0.025°: HP1 - "+\
                                      "paramètres courants en niveaux hauteur",
                                      command=partial(
                                      self.telechargement_modeles,"AROME",
                                      "0.025","HP1"))
        menu_tele_params_tous_1.add_command(label="Arome 0.025°: HP2 - "+\
                                      "paramètres additionnels en niveaux hauteur",
                                      command=partial(
                                      self.telechargement_modeles,"AROME",
                                      "0.025","HP2"))
        menu_tele_params_tous_1.add_command(label="Arome 0.025°: HP3 - "+\
                                      "paramètres additionnels (2) en niveaux hauteur",
                                      command=partial(
                                      self.telechargement_modeles,"AROME",
                                      "0.025","HP3"))
        menu_tele_modeles.add_cascade(label="Télé add AROME 0.025",
                             underline=0,menu=menu_tele_params_tous_1)
        
        menu_tele_params_tous_2 = Menu(menu_tele_modeles, tearoff=0)
        menu_tele_params_tous_2.add_command(label="Arome 0.01°: SP2 - "+\
                                      "paramètres additionnels à la surface",
                                      command=partial(
                                      self.telechargement_modeles,"AROME",
                                      "0.01","SP2"))
        menu_tele_params_tous_2.add_command(label="Arome 0.01°: SP3 - " + \
                                      "paramètres additionnels (2) à la surface",
                                      command=partial(
                                      self.telechargement_modeles,"AROME",
                                      "0.01","SP3"))
        menu_tele_params_tous_2.add_command(label="Arome 0.01°: HP1 - "+ \
                                      "paramètres courants en niveaux hauteur",
                                      command=partial(
                                      self.telechargement_modeles,"AROME",
                                      "0.01","HP1"))
        menu_tele_modeles.add_cascade(label="Télé add AROME 0.01",
                             underline=0,menu=menu_tele_params_tous_2)
        
        menu_tele_params_tous_3 = Menu(menu_tele_modeles, tearoff=0)
        menu_tele_params_tous_3.add_command(label="Arpege 0.1°: SP2 - "+\
                                      "paramètres additionnels à la surface",
                                      command=partial(
                                      self.telechargement_modeles,"ARPEGE",
                                      "0.1","SP2"))
        menu_tele_params_tous_3.add_command(label="Arpege 0.1°: IP1 - "+ \
                                      "paramètres courants en niveaux isobares",
                                      command=partial(
                                      self.telechargement_modeles,"ARPEGE",
                                      "0.1","IP1"))
        menu_tele_params_tous_3.add_command(label="Arpege 0.1°: IP2 - "+\
                                      "paramètres additionnels en niveaux isobares",
                                      command=partial(
                                      self.telechargement_modeles,"ARPEGE",
                                      "0.1","IP2"))
        menu_tele_params_tous_3.add_command(label="Arpege 0.1°: IP3 - "+\
                                      "paramètres additionnels (2) en niveaux isobares",
                                      command=partial(
                                      self.telechargement_modeles,"ARPEGE",
                                      "0.1","IP3"))
        menu_tele_params_tous_3.add_command(label="Arpege 0.1°: IP4 - "+\
                                            "paramètres additionnels (3) en niveaux isobares",
                                            command=partial(
                                            self.telechargement_modeles,"ARPEGE",
                                            "0.1","IP4"))          
        menu_tele_params_tous_3.add_command(label="Arpege 0.1°: HP1 - "+\
                                      "paramètres courants en niveaux hauteur",
                                      command=partial(
                                      self.telechargement_modeles,"ARPEGE",
                                      "0.1","HP1"))
        menu_tele_params_tous_3.add_command(label="Arpege 0.1°: HP2 - "+\
                                      "paramètres additionnels en niveaux hauteur",
                                      command=partial(
                                      self.telechargement_modeles,"ARPEGE",
                                      "0.1","HP2"))
        menu_tele_modeles.add_cascade(label="Télé add ARPEGE 0.1",
                             underline=0,menu=menu_tele_params_tous_3)  

        menu_tele_params_tous_4 = Menu(menu_tele_modeles, tearoff=0)
        menu_tele_params_tous_4.add_command(label="Arpege 0.5°: SP2 - "+\
                                      "paramètres additionnels à la surface",
                                      command=partial(
                                      self.telechargement_modeles,"ARPEGE",
                                      "0.5","SP2"))
        menu_tele_params_tous_4.add_command(label="Arpege 0.5°: IP1 - "+ \
                                      "paramètres courants en niveaux isobares",
                                      command=partial(
                                      self.telechargement_modeles,"ARPEGE",
                                      "0.5","IP1"))
        menu_tele_params_tous_4.add_command(label="Arpege 0.5°: IP2 - "+\
                                      "paramètres additionnels en niveaux isobares",
                                      command=partial(
                                      self.telechargement_modeles,"ARPEGE",
                                      "0.5","IP2"))
        menu_tele_params_tous_4.add_command(label="Arpege 0.5°: IP3 - "+\
                                      "paramètres additionnels (2) en niveaux isobares",
                                      command=partial(
                                      self.telechargement_modeles,"ARPEGE",
                                      "0.5","IP3"))       
        menu_tele_params_tous_4.add_command(label="Arpege 0.5°: HP1 - "+\
                                      "paramètres courants en niveaux hauteur",
                                      command=partial(
                                      self.telechargement_modeles,"ARPEGE",
                                      "0.5","HP1"))
        menu_tele_params_tous_4.add_command(label="Arpege 0.5°: HP2 - "+\
                                      "paramètres additionnels en niveaux hauteur",
                                      command=partial(
                                      self.telechargement_modeles,"ARPEGE",
                                      "0.5","HP2"))
        menu_tele_modeles.add_cascade(label="Télé add ARPEGE 0.5",
                             underline=0,menu=menu_tele_params_tous_4)  
        menu_bar.add_cascade(label="Téléchargements données modèles",
                             underline=0,menu=menu_tele_modeles)  

        self.config(menu=menu_bar)

    def regler_echeance(self,f):

        self.echh = int(f)
        self.event_generate('<Control-Z>')

    def regler_zoom(self,zone):

        self.chk = self.ck.get()
        self.chk = zone
        self.event_generate('<Control-Z>')

    def saisir_date_du_run(self):

        #Entrer_date_du_run = Entry(self, width=20).pack(pady=20)
        self.date_du_run = self.entrer_date_du_run.get()
        self.event_generate('<Control-Z>')
        print(self.date_du_run)

    def obtenir_date_du_run(self):
        mod = "AROME"
        res = "0.025"
        daterun = TelechargerDonneesModeles(modele=mod,
                                            resolution=res,
                                            verification = 0)
        return daterun.donner_date_du_run()

###########################################################################
##################### AROME 0.025° dans canevas de la gui #################
    def dessiner_carte_mono_param(self,modele,resolution,variable):

        self.can.delete(ALL)
        self.c2 = CarteMonoParam(self,self.can,self.date_du_run,
                           modele,resolution,echeance=self.echh,
                           type_carte=variable,zoom = self.chk,
                           verification = 0)
        self.c2.envoyer_carte_vers_gui()
        
    def dessiner_carte(self,modele,resolution,variable):

        self.can.delete(ALL)
        if variable == "T2m":
            self.c2 = CarteT2m(self,self.can,self.date_du_run,
                                modele,resolution,echeance=self.echh,
                                type_carte=variable,zoom = self.chk,
                                verification = 0)

        elif variable == "Precips":
            self.c2 = CartePrecips(self,self.can,self.date_du_run,
                                    modele,resolution,echeance=self.echh,
                                    type_carte=variable,zoom = self.chk,
                                    verification = 0)

        elif variable == "Pmer":
            self.c2 = CartePmer(self,self.can,self.date_du_run,
                                    modele,resolution,echeance=self.echh,
                                    type_carte=variable,zoom = self.chk,
                                    verification = 0)

        elif variable == "DSW":
            self.c2 = CarteDsw(self,self.can,self.date_du_run,
                                modele,resolution,echeance=self.echh,
                                type_carte=variable,zoom = self.chk,
                                verification = 0)

        elif variable == "TPW850_Z1.5pvu":
            self.c2 = CarteTpw850Z15Pvu(self,self.can,self.date_du_run,
                                          modele,resolution,
                                          echeance=self.echh,
                                          type_carte=variable,zoom = self.chk,
                                          verification = 0)

        elif variable == "Jet_Z1.5pvu":
            self.c2 = CarteZ15PvuJet(self,self.can,self.date_du_run,
                                       modele,resolution,echeance=self.echh,
                                       type_carte=variable,zoom = self.chk,
                                       verification = 0)

        self.c2.envoyer_carte_vers_gui()

##############################################################################
# Télécharger les données de prévisions météo

    def telechargement_modeles(self,mod,res,paquet):
        #mod = "AROME"
        #res = "0.025"
        paquet=paquet
        self.telecharger_donnees = TelechargerDonneesModeles(modele=mod,
                                                             resolution=res,
                                                             verification = 0)
        self.telecharger_donnees.telecharger_donnes_modeles(paquet)

#######################################################
######## Tout charger les cartes ######################
    # les quatres méthodes pour dessiner toutes les cartes Arome 0.025°
    #sont à peu près équilibrées entre elles
    # pour leur temps de compilation, j'ai essayé de faire en
    #sorte de minimiser le temps total.
    # Ainsi, en lançant ces quatres méthodes simultanément, j'arrive à réduire
    #le temps total à moins de 10 minutes.
    def dessiner_tout_aro_0025_T2m(self):
        
        mod = "AROME"
        res = "0.025"
        tout_aro_0025 = AromeCartes(self.date_du_run,
                                          modele=mod,resolution=res,
                                          zoom = self.chk,verification = 0)
        #threading.Thread(self.tout_aro_0025.cartes_t2m()).start()
        tout_aro_0025.cartes_t2m()

    def dessiner_tout_aro_001_T2m(self):
        mod = "AROME"
        res = "0.01"
        tout_aro_001 = AromeCartes(self.date_du_run,
                                         modele=mod,resolution=res,
                                         zoom = self.chk, verification = 0)
        #threading.Thread(self.tout_aro_001.cartes_t2m()).start()
        tout_aro_001.cartes_t2m()

    def dessiner_tout_arp_01_T2m(self):
        mod = "ARPEGE"
        res = "0.1"
        tout_aro_001 = AromeCartes(self.date_du_run,
                                         modele=mod,resolution=res,
                                         zoom = self.chk, verification = 0)
        tout_aro_001.cartes_t2m()
