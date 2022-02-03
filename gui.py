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
from TelechargementModeles import *
from carte_pour_canvas import *
# Classe d'interface graphique, les objets de cette classe
# sont appelées dans le main du projet.

class Application(Tk):
    # Héritière de Tk, cette classe code pour une interface graphique.

    def __init__(self):
        Tk.__init__(self)        # constructeur de la classe parente

        self.date_du_run = self.ObtenirDateDuRun()
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
                                     command=self.SaisirDateDuRun)
        boutton_date_du_run.pack()

        lab_run = Label(self, text="===========================")
        lab_run.pack()

        # Initalisation de la case à cocher pour le zoom.
        self.chk = 0
        self.ck = IntVar()
        zones = ("Domaines modèles entier (par défaut)","Zoom Sud-Est France",
                 "Zoom Toulouse Garonne Ariège","Zoom Grand Sud France",
                 "Zoom Lus Genève Charlieu","Zoom Grand Mont Blanc",
                 "Zoom Savoie","Zoom Écrins",)
        for zone in range(len(zones)):
            check_1 = Checkbutton(self,text = zones[zone],variable=zone,
                                  command=partial(self.ReglerZoom,zone))
            check_1.pack()

        self.CreerBarreMenus()# création de la barre des menus

        # Initalisation du paramètre d'échéance
        #pour les cartes à afficher par lumet.
        self.echh = 0
        # Échelle pour échéances
        scale_9 = Scale(self,length = 600, orient = HORIZONTAL,
                        sliderlength = 25,
                        label = "Échéance de prévision +(**)H:",
                        from_ = 0, to = 114, tickinterval = 6,
                        resolution = 1,showvalue = 1,
                        command = self.ReglerEcheance)
        scale_9.pack()

        # Initialisation du canevas qui sera modifié pour créer
        #et afficher les différentes cartes
        self.can = Canvas(self, width =50, height =50, bg ="white")
        self.can.pack(side =TOP, padx =5, pady =5)

    def CreerBarreMenus(self):
        """Barre de menus de l’interface graphique."""

        menu_bar = Menu(self)

        menu_arome = Menu(menu_bar, tearoff=0)
        menu_arome_0025 = Menu(menu_arome, tearoff=0)
        menu_arome_0025.add_command(label="Température à 2m", underline=3,
                               command=partial(self.DessinerCarteMonoParam,
                                               "AROME","0.025","T2m"))
        menu_arome_0025.add_command(label="Température point de rosée à 2m", underline=3,
                               command=partial(self.DessinerCarteMonoParam,
                                               "AROME","0.025","Td2m"))
        menu_arome_0025.add_command(label="Vent moyen à 10m", underline=3,
                               command=partial(self.DessinerCarteMonoParam,
                                               "AROME","0.025","Vent_Moy"))
        menu_arome_0025.add_command(label="Vent rafales à 10m", underline=3,
                               command=partial(self.DessinerCarteMonoParam,
                                               "AROME","0.025","Vent_Raf"))
        menu_arome_0025.add_command(label="Humidité relative à 2m", underline=3,
                               command=partial(self.DessinerCarteMonoParam,
                                               "AROME","0.025","Hu2m"))
        menu_arome_0025.add_command(label="Humidité spécifique à 2m", underline=3,
                               command=partial(self.DessinerCarteMonoParam,
                                               "AROME","0.025","Hu_specifique_2m"))
        menu_arome_0025.add_command(label="Hauteur de neige", underline=3,
                               command=partial(self.DessinerCarteMonoParam,
                                               "AROME","0.025","Neige"))
        menu_arome_0025.add_command(label="Pression au niveau de la mer", underline=3,
                               command=partial(self.DessinerCarteMonoParam,
                                               "AROME","0.025","Pmer"))
        menu_arome_0025.add_command(label="Pression à la surface 0.025° ", underline=3,
                               command=partial(self.DessinerCarteMonoParam,
                                               "AROME","0.025","Psol"))
        menu_arome_0025.add_command(label="Précipitations", underline=3,
                               command=partial(self.DessinerCarteCumuls,
                                               "AROME","0.025","Precips"))
        menu_arome_0025.add_command(label="Précipitations liquides", underline=3,
                               command=partial(self.DessinerCarteCumuls,
                                               "AROME","0.025","Precips_Eau"))
        menu_arome_0025.add_command(label="Rayonnement visible descendant (SW)", underline=3,
                               command=partial(self.DessinerCarteCumuls,
                                               "AROME","0.025","DSW"))
        menu_arome_0025.add_command(label="Nébulosité basse", underline=3,
                               command=partial(self.DessinerCarteMonoParam,
                                               "AROME","0.025","NebulBas"))
        menu_arome_0025.add_command(label="Nébulosité moyenne", underline=3,
                               command=partial(self.DessinerCarteMonoParam,
                                               "AROME","0.025","NebulMoy"))
        menu_arome_0025.add_command(label="Nébulosité haute", underline=3,
                               command=partial(self.DessinerCarteMonoParam,
                                               "AROME","0.025","NebulHaut"))
        menu_arome_0025.add_command(label="CAPE", underline=3,
                               command=partial(self.DessinerCarteMonoParam,
                                               "AROME","0.025","CAPE_INS"))
        menu_arome_0025.add_command(label="Altitude de la couche limite", underline=3,
                               command=partial(self.DessinerCarteMonoParam,
                                               "AROME","0.025","Altitude_Couche_Limite"))
        menu_arome_0025.add_command(label="Contenu total vapeur d’eau colonne atmosphérique", underline=3,
                               command=partial(self.DessinerCarteMonoParam,
                                               "AROME","0.025","Colonne_Vapeur"))
        menu_arome_0025.add_command(label="Flux de chaleur latente à la surface", underline=3,
                               command=partial(self.DessinerCarteCumuls,
                                               "AROME","0.025","Flux_Chaleur_latente_Surface"))
        menu_arome_0025.add_command(label="Flux de chaleur sensible à la surface", underline=3,
                               command=partial(self.DessinerCarteCumuls,
                                               "AROME","0.025","Flux_Chaleur_sensible_Surface"))
        menu_arome_0025.add_command(label="Rayonnement Thermique descendant à la surface", underline=3,
                               command=partial(self.DessinerCarteCumuls,
                                               "AROME","0.025","Rayonnement_Thermique_Descendant_Surface"))
        menu_arome_0025.add_command(label="Rayonnement solaire net à la surface", underline=3,
                               command=partial(self.DessinerCarteCumuls,
                                               "AROME","0.025","Rayonnement_Solaire_Net_Surface"))
        menu_arome_0025.add_command(label="Rayonnement solaire net à la surface ciel clair", underline=3,
                               command=partial(self.DessinerCarteCumuls,
                                               "AROME","0.025","Rayonnement_Solaire_Net_Surface_Ciel_Clair"))
        menu_arome_0025.add_command(label="Rayonnement thermique net à la surface", underline=3,
                               command=partial(self.DessinerCarteCumuls,
                                               "AROME","0.025","Rayonnement_Thermique_Net_Surface"))
        menu_arome_0025.add_command(label="Rayonnement thermique net à la surface ciel clair", underline=3,
                               command=partial(self.DessinerCarteCumuls,
                                               "AROME","0.025","Rayonnement_Thermique_Net_Surface_Ciel_Clair"))
        menu_arome.add_cascade(label="AROME 0.025°",
                             underline=0,menu=menu_arome_0025)
        menu_arome_0001 = Menu(menu_arome, tearoff=0)
        menu_arome_0001.add_command(label="Température à 2m", underline=3,
                               command=partial(self.DessinerCarteMonoParam,
                                               "AROME","0.01","T2m"))
        menu_arome_0001.add_command(label="Vent moyen à 10m", underline=3,
                               command=partial(self.DessinerCarteMonoParam,
                                               "AROME","0.01","Vent_Moy"))
        menu_arome_0001.add_command(label="Vent moyen à 100m", underline=3,
                               command=partial(self.DessinerCarteMonoParam,
                                               "AROME","0.01","Vent_Moy_100m"))
        menu_arome_0001.add_command(label="Vent rafales à 10m", underline=3,
                               command=partial(self.DessinerCarteMonoParam,
                                               "AROME","0.01","Vent_Raf"))
        menu_arome_0001.add_command(label="Humidité relative à 2m", underline=3,
                               command=partial(self.DessinerCarteMonoParam,
                                               "AROME","0.01","Hu2m"))
#        menu_arome.add_command(label="Hauteur de neige", underline=3,
#                               accelerator="CTRL+N",
#                               command=partial(self.DessinerCarteMonoParam,
#                                               "AROME","0.01","Neige"))
        menu_arome_0001.add_command(label="Pression à la surface", underline=3,
                               command=partial(self.DessinerCarteMonoParam,
                                               "AROME","0.01","Psol"))
        menu_arome_0001.add_command(label="Précipitations", underline=3,
                               command=partial(self.DessinerCarteCumuls,
                                               "AROME","0.01","Total_Water_Precips"))
        menu_arome_0001.add_command(label="Nébulosité basse", underline=3,
                               command=partial(self.DessinerCarteMonoParam,
                                               "AROME","0.01","NebulBas"))
        menu_arome_0001.add_command(label="Nébulosité moyenne", underline=3,
                               command=partial(self.DessinerCarteMonoParam,
                                               "AROME","0.01","NebulMoy"))
        menu_arome_0001.add_command(label="Nébulosité haute", underline=3,
                               command=partial(self.DessinerCarteMonoParam,
                                               "AROME","0.01","NebulHaut"))
        menu_arome_0001.add_command(label="CAPE", underline=3,
                               command=partial(self.DessinerCarteMonoParam,
                                               "AROME","0.01","CAPE_INS"))
        menu_arome_0001.add_command(label="Température de brillance", underline=3,
                               command=partial(self.DessinerCarteMonoParam,
                                               "AROME","0.01","Temp_Brillance"))
        menu_arome_0001.add_command(label="Altitude surface modèle, constante échéance 0h", underline=3,
                               command=partial(self.DessinerCarteMonoParam,
                                               "AROME","0.01","Altitude_Surface"))
        menu_arome.add_cascade(label="AROME 0.01°",
                             underline=0,menu=menu_arome_0001)
        menu_bar.add_cascade(label="AROME", underline=0, menu=menu_arome)
        menu_arpege = Menu(menu_bar, tearoff=0)
        menu_arpege_01 = Menu(menu_arpege, tearoff=0)
        menu_arpege_01.add_command(label="Température à 2m", underline=3,
                               command=partial(self.DessinerCarteMonoParam,
                                               "ARPEGE","0.1","T2m"))
        menu_arpege_01.add_command(label="Vent moyen à 10m", underline=3,
                               command=partial(self.DessinerCarteMonoParam,
                                               "ARPEGE","0.1","Vent_Moy"))
        menu_arpege_01.add_command(label="Vent rafales à 10m", underline=3,
                               command=partial(self.DessinerCarteMonoParam,
                                               "ARPEGE","0.1","Vent_Raf"))
        menu_arpege_01.add_command(label="Humidité relative à 2m", underline=3,
                               command=partial(self.DessinerCarteMonoParam,
                                               "ARPEGE","0.1","Hu2m"))
        menu_arpege_01.add_command(label="Pression au niveau de la mer", underline=3,
                               command=partial(self.DessinerCarteMonoParam,
                                               "ARPEGE","0.1","Pmer"))
        menu_arpege.add_cascade(label="ARPEGE 0.1°",
                             underline=0,menu=menu_arpege_01)
        menu_bar.add_cascade(label="ARPEGE", underline=0, menu=menu_arpege)
        menu_tele_modeles = Menu(menu_bar,tearoff=0)
        menu_tele_base = Menu(menu_tele_modeles, tearoff=0)
        menu_tele_base.add_command(label="Arome 0.025°: SP1",
                                      command=partial(
                                      self.TelechargementModeles,"AROME",
                                      "0.025","SP1"))
        menu_tele_base.add_command(label="Arome 0.025°: IP5",
                                      command=partial(
                                      self.TelechargementModeles,"AROME",
                                      "0.025","IP5"))
        menu_tele_base.add_command(label="Arome 0.01°: SP1",
                                      command=partial(
                                      self.TelechargementModeles,"AROME",
                                      "0.01","SP1"))
        menu_tele_base.add_command(label="Arpege 0.1°: SP1",
                                      command=partial(
                                      self.TelechargementModeles,"ARPEGE",
                                      "0.1","SP1"))        
        menu_tele_base.add_command(label="Arpege 0.1°: IP4",
                                      command=partial(
                                      self.TelechargementModeles,"ARPEGE",
                                      "0.1","IP4"))        
        menu_tele_base.add_command(label="Arpege 0.5°: SP1",
                                      command=partial(
                                      self.TelechargementModeles,"ARPEGE",
                                      "0.5","SP1"))        
        menu_tele_base.add_command(label="Arpege 0.5°: IP4",
                                      command=partial(
                                      self.TelechargementModeles,"ARPEGE",
                                      "0.5","IP4"))
        menu_tele_modeles.add_cascade(label="Téléchargement paquets de base",
                             underline=0,menu=menu_tele_base)
        
        menu_tele_params_tous_1 = Menu(menu_tele_modeles, tearoff=0)
        menu_tele_params_tous_1.add_command(label="Arome 0.025°: SP2 - "+\
                                      "paramètres additionnels à la surface",
                                      command=partial(
                                      self.TelechargementModeles,"AROME",
                                      "0.025","SP2"))
        menu_tele_params_tous_1.add_command(label="Arome 0.025°: SP3 - " + \
                                      "paramètres additionnels (2) à la surface",
                                      command=partial(
                                      self.TelechargementModeles,"AROME",
                                      "0.025","SP3"))
        menu_tele_params_tous_1.add_command(label="Arome 0.025°: IP1 - "+ \
                                      "paramètres courants en niveaux isobares",
                                      command=partial(
                                      self.TelechargementModeles,"AROME",
                                      "0.025","IP1"))
        menu_tele_params_tous_1.add_command(label="Arome 0.025°: IP2 - "+\
                                      "paramètres additionnels en niveaux isobares",
                                      command=partial(
                                      self.TelechargementModeles,"AROME",
                                      "0.025","IP2"))
        menu_tele_params_tous_1.add_command(label="Arome 0.025°: IP3 - "+\
                                      "paramètres additionnels (2) en niveaux isobares",
                                      command=partial(
                                      self.TelechargementModeles,"AROME",
                                      "0.025","IP3"))
        menu_tele_params_tous_1.add_command(label="Arome 0.025°: IP4 - "+\
                                            "paramètres additionnels (3) en niveaux isobares",
                                            command=partial(
                                            self.TelechargementModeles,"AROME",
                                            "0.025","IP4"))          
        menu_tele_params_tous_1.add_command(label="Arome 0.025°: HP1 - "+\
                                      "paramètres courants en niveaux hauteur",
                                      command=partial(
                                      self.TelechargementModeles,"AROME",
                                      "0.025","HP1"))
        menu_tele_params_tous_1.add_command(label="Arome 0.025°: HP2 - "+\
                                      "paramètres additionnels en niveaux hauteur",
                                      command=partial(
                                      self.TelechargementModeles,"AROME",
                                      "0.025","HP2"))
        menu_tele_params_tous_1.add_command(label="Arome 0.025°: HP3 - "+\
                                      "paramètres additionnels (2) en niveaux hauteur",
                                      command=partial(
                                      self.TelechargementModeles,"AROME",
                                      "0.025","HP3"))
        menu_tele_modeles.add_cascade(label="Télé add AROME 0.025",
                             underline=0,menu=menu_tele_params_tous_1)
        
        menu_tele_params_tous_2 = Menu(menu_tele_modeles, tearoff=0)
        menu_tele_params_tous_2.add_command(label="Arome 0.01°: SP2 - "+\
                                      "paramètres additionnels à la surface",
                                      command=partial(
                                      self.TelechargementModeles,"AROME",
                                      "0.01","SP2"))
        menu_tele_params_tous_2.add_command(label="Arome 0.01°: SP3 - " + \
                                      "paramètres additionnels (2) à la surface",
                                      command=partial(
                                      self.TelechargementModeles,"AROME",
                                      "0.01","SP3"))
        menu_tele_params_tous_2.add_command(label="Arome 0.01°: HP1 - "+ \
                                      "paramètres courants en niveaux hauteur",
                                      command=partial(
                                      self.TelechargementModeles,"AROME",
                                      "0.01","HP1"))
        menu_tele_modeles.add_cascade(label="Télé add AROME 0.01",
                             underline=0,menu=menu_tele_params_tous_2)
        
        menu_tele_params_tous_3 = Menu(menu_tele_modeles, tearoff=0)
        menu_tele_params_tous_3.add_command(label="Arpege 0.1°: SP2 - "+\
                                      "paramètres additionnels à la surface",
                                      command=partial(
                                      self.TelechargementModeles,"ARPEGE",
                                      "0.1","SP2"))
        menu_tele_params_tous_3.add_command(label="Arpege 0.1°: IP1 - "+ \
                                      "paramètres courants en niveaux isobares",
                                      command=partial(
                                      self.TelechargementModeles,"ARPEGE",
                                      "0.1","IP1"))
        menu_tele_params_tous_3.add_command(label="Arpege 0.1°: IP2 - "+\
                                      "paramètres additionnels en niveaux isobares",
                                      command=partial(
                                      self.TelechargementModeles,"ARPEGE",
                                      "0.1","IP2"))
        menu_tele_params_tous_3.add_command(label="Arpege 0.1°: IP3 - "+\
                                      "paramètres additionnels (2) en niveaux isobares",
                                      command=partial(
                                      self.TelechargementModeles,"ARPEGE",
                                      "0.1","IP3"))
        menu_tele_params_tous_3.add_command(label="Arpege 0.1°: IP4 - "+\
                                            "paramètres additionnels (3) en niveaux isobares",
                                            command=partial(
                                            self.TelechargementModeles,"ARPEGE",
                                            "0.1","IP4"))          
        menu_tele_params_tous_3.add_command(label="Arpege 0.1°: HP1 - "+\
                                      "paramètres courants en niveaux hauteur",
                                      command=partial(
                                      self.TelechargementModeles,"ARPEGE",
                                      "0.1","HP1"))
        menu_tele_params_tous_3.add_command(label="Arpege 0.1°: HP2 - "+\
                                      "paramètres additionnels en niveaux hauteur",
                                      command=partial(
                                      self.TelechargementModeles,"ARPEGE",
                                      "0.1","HP2"))
        menu_tele_modeles.add_cascade(label="Télé add ARPEGE 0.1",
                             underline=0,menu=menu_tele_params_tous_3)  

        menu_tele_params_tous_4 = Menu(menu_tele_modeles, tearoff=0)
        menu_tele_params_tous_4.add_command(label="Arpege 0.5°: SP2 - "+\
                                      "paramètres additionnels à la surface",
                                      command=partial(
                                      self.TelechargementModeles,"ARPEGE",
                                      "0.5","SP2"))
        menu_tele_params_tous_4.add_command(label="Arpege 0.5°: IP1 - "+ \
                                      "paramètres courants en niveaux isobares",
                                      command=partial(
                                      self.TelechargementModeles,"ARPEGE",
                                      "0.5","IP1"))
        menu_tele_params_tous_4.add_command(label="Arpege 0.5°: IP2 - "+\
                                      "paramètres additionnels en niveaux isobares",
                                      command=partial(
                                      self.TelechargementModeles,"ARPEGE",
                                      "0.5","IP2"))
        menu_tele_params_tous_4.add_command(label="Arpege 0.5°: IP3 - "+\
                                      "paramètres additionnels (2) en niveaux isobares",
                                      command=partial(
                                      self.TelechargementModeles,"ARPEGE",
                                      "0.5","IP3"))       
        menu_tele_params_tous_4.add_command(label="Arpege 0.5°: HP1 - "+\
                                      "paramètres courants en niveaux hauteur",
                                      command=partial(
                                      self.TelechargementModeles,"ARPEGE",
                                      "0.5","HP1"))
        menu_tele_params_tous_4.add_command(label="Arpege 0.5°: HP2 - "+\
                                      "paramètres additionnels en niveaux hauteur",
                                      command=partial(
                                      self.TelechargementModeles,"ARPEGE",
                                      "0.5","HP2"))
        menu_tele_modeles.add_cascade(label="Télé add ARPEGE 0.5",
                             underline=0,menu=menu_tele_params_tous_4)  
        menu_bar.add_cascade(label="Téléchargement données modèles",
                             underline=0,menu=menu_tele_modeles)

        self.config(menu=menu_bar)

    def ObtenirDateDuRun(self):
        """Obtenir une date du run à partir de la date du lancement de lumet"""

        mod = "AROME"
        res = "0.025"
        daterun = TelechargerDonneesModeles(modele=mod,
                                            resolution=res,
                                            verification = 0)
        return daterun.donner_date_du_run()

    def SaisirDateDuRun(self):
        """Saisie manuelle de la date d’un run antérieur pour lequel on dispose
        des données."""

        #Entrer_date_du_run = Entry(self, width=20).pack(pady=20)
        self.date_du_run = self.entrer_date_du_run.get()
        self.event_generate('<Control-Z>')
        print(self.date_du_run)

    def TelechargementModeles(self,mod,res,paquet):
        """Téléchargement des données des modèles météos."""

        #mod = "AROME"
        #res = "0.025"
        paquet=paquet
        self.telecharger_donnees = TelechargerDonneesModeles(modele=mod,
                                                             resolution=res,
                                                             verification = 0)
        self.telecharger_donnees.telecharger_donnes_modeles(paquet)

    def ReglerZoom(self,zone):
        """Réglage de la zone de zoom"""

        self.chk = self.ck.get()
        self.chk = zone
        self.event_generate('<Control-Z>')

    def ReglerEcheance(self,f):
        """Réglage de l’échéance d’intérêt"""

        self.echh = int(f)
        self.event_generate('<Control-Z>')

    def DessinerCarteMonoParam(self,modele,resolution,variable):
        """Ajout de cartes à un seul paramètre dans un canevas"""

        self.can.delete(ALL)
        self.c2 = CarteMonoParam(self,self.can,self.date_du_run,
                           modele,resolution,echeance=self.echh,
                           type_carte=variable,zoom = self.chk,
                           verification = 0)
        self.c2.envoyer_carte_vers_gui()

    def DessinerCarteCumuls(self,modele,resolution,variable):
        """Ajout de cartes à un seul paramètre dans un canevas"""

        self.can.delete(ALL)
        self.c2 = CarteCumuls(self,self.can,self.date_du_run,
                           modele,resolution,echeance=self.echh,
                           type_carte=variable,zoom = self.chk,
                           verification = 0)
        self.c2.envoyer_carte_vers_gui()
