#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""@author: lucas
Classes nécéssaires à l'interface graphique de Lumet v0.6
Licence GPL euia / Lucas GRIGIS copyleft
"""
# Import des librairies externes à lumet
from tkinter import *
from functools import partial
import threading

# Import des librairies internes à Lumet
from telechargement_modeles import *

# Classe d'interface graphique, les objets de cette classe
# sont appelées dans le main du projet.

class Application(Tk):
    # Héritière de Tk, cette classe code pour une interface graphique.

    def __init__(self):
        Tk.__init__(self)        # constructeur de la classe parente

        self.date_du_run = self.obtenir_date_du_run()
        lab_run = Label(self, text="\nPrévisions en date du " + \
                        self.date_du_run[6:8] + "/"+ \
                        self.date_du_run[4:6] + "/" + self.date_du_run[0:4]+\
                        " run de " + self.date_du_run[-2:] + "H")
        lab_run.pack()

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

        self.creer_barre_menus()# création de la barre des menus

    def creer_barre_menus(self):
        """Barre de menus de l’interface graphique."""

        menu_bar = Menu(self)

        menu_arome = Menu(menu_bar, tearoff=0)

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

    def obtenir_date_du_run(self):
        """Obtenir une date du run à partir de la date du lancement de lumet"""

        mod = "AROME"
        res = "0.025"
        daterun = TelechargerDonneesModeles(modele=mod,
                                            resolution=res,
                                            verification = 0)
        return daterun.donner_date_du_run()

    def saisir_date_du_run(self):
        """Saisie manuelle de la date d’un run antérieur pour lequel on dispose
        des données."""

        #Entrer_date_du_run = Entry(self, width=20).pack(pady=20)
        self.date_du_run = self.entrer_date_du_run.get()
        self.event_generate('<Control-Z>')
        print(self.date_du_run)

    def telechargement_modeles(self,mod,res,paquet):
        """Téléchargement des données des modèles météos."""

        #mod = "AROME"
        #res = "0.025"
        paquet=paquet
        self.telecharger_donnees = TelechargerDonneesModeles(modele=mod,
                                                             resolution=res,
                                                             verification = 0)
        self.telecharger_donnees.telecharger_donnes_modeles(paquet)
