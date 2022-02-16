#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""@author: lucas
Classes nécéssaires à l'interface graphique de Lumet v0.6
Licence GPL euia / Lucas GRIGIS copyleft
"""
# Import des librairies externes à lumet
from tkinter import ttk
from functools import partial
import threading
from datetime import date, timedelta

# Import des librairies internes à Lumet
from TelechargementModeles import *
from carte_pour_canvas import *
# Classe d'interface graphique, les objets de cette classe
# sont appelées dans le main du projet.



class Application(Tk):
    # Héritière de Tk, cette classe code pour une interface graphique.

    def __init__(self):
        Tk.__init__(self)        # constructeur de la classe parente

        tabControl = ttk.Notebook(self)

        tab1 = ttk.Frame(tabControl)
        tab2 = ttk.Frame(tabControl)
        tab3 = ttk.Frame(tabControl)
        tabControl.add(tab1, text = "Run")
        tabControl.add(tab2, text = "Échéances")
        tabControl.add(tab3, text = "Zooms")
        tabControl.pack(expand = 1, fill ="both")

        self.date_du_run = self.ObtenirDateDuRun()
        lab_run = Label(tab1, text="\nPrévisions en date du " + \
                        self.date_du_run[6:8] + "/"+ \
                        self.date_du_run[4:6] + "/" + self.date_du_run[0:4]+\
                        " run de " + self.date_du_run[-2:] + "H")
        lab_run.pack()

        # Champ Entry et bouton pour que l’utilisateur rentre la date du run
        # qu’il veut
        self.entrer_date_du_run = StringVar(self)
        lab_run = Label(tab1, text="==========================="+
                        "\nUtiliser un autre run ? Saisissez votre date d’intérêt\nFormat "+
                        "\"yyyymmjjrr\" ex 1er nov 2021 run de 03h "+
                        "= 2021011103")
        lab_run.pack()

        entrer_date_du_run = Entry(tab1,textvariable=self.entrer_date_du_run,
                                   width=20)
        entrer_date_du_run.pack(pady=20)

        boutton_date_du_run = Button(tab1, height=1,
                                     text="Valider date du run",
                                     command=self.SaisirDateDuRun)
        boutton_date_du_run.pack()

        lab_run.pack()

        # Initalisation du paramètre d'échéance
        #pour les cartes à afficher par lumet.
        self.echh = 0
        # Échelle pour échéances
        scale_9 = Scale(tab2,length = 600, orient = HORIZONTAL,
                        sliderlength = 25,
                        label = "Échéance de prévision +(**)H:",
                        from_ = 0, to = 114, tickinterval = 6,
                        resolution = 1,showvalue = 1,
                        command = self.ReglerEcheance)
        scale_9.pack()

        niveaux_iso = [100,125,150,175,200,225,250,275,300,350,400,450,500,550,600,650,700,750,800,850,900,925,950,1000]

        labelTop = Label(tab2,text = "Niveaux verticaux (hPa)")
        labelTop.pack()
        self.niv_iso = IntVar()
        comboExample = ttk.Combobox(tab2, values=niveaux_iso, textvariable=self.niv_iso)
        comboExample["state"] = "readonly"
#        self.niv_iso = comboExample.current(1)
        comboExample.pack()

        comboExample.bind("<<ComboboxSelected>>", self.ReglerNiveauIso)

        dates_obs = []
        start_date = datetime(1996, 1, 1, 0)
        end_date = datetime(2022, 2, 15, 12)
        delta = timedelta(hours=3)
        while start_date <= end_date:
            #print(start_date.strftime("%Y-%m-%d %H")+"H")
            dates_obs.append(start_date.strftime("%Y-%m-%d %H"))
            start_date += delta

        #print(dates_obs)

        labelTop = Label(tab2,text = "Dates des observations de surface SYNOP")
        labelTop.pack()
        self.date_obs = StringVar()
        comboExample = ttk.Combobox(tab2, values=dates_obs, textvariable=self.date_obs)
        comboExample["state"] = "readonly"
#        self.niv_iso = comboExample.current(1)
        comboExample.pack()

        comboExample.bind("<<ComboboxSelected>>", self.ReglerDateObs)

        # Initalisation de la case à cocher pour les niveaux isobares
        self.chk_iso = 0
        #self.ck_iso = IntVar()
#        niveaux_iso = (100, 125, 150, 175, 200, 225, 250, 275, 300, 350, 400, 450, 500, 550, 600, 650, 700, 7500, 800, 850, 900, 925, 950, 1000,)
#        for niveau in range(len(niveaux_iso)):
#            check_iso = Checkbutton(tab2,text = niveaux_iso[niveau],variable=niveau,
#                                  command=partial(self.ReglerNiveauIso,niveau))
#            check_iso.pack()

        # Initalisation de la case à cocher pour le zoom.
        self.chk = 0
        self.ck = IntVar()
        zones = ("Domaines modèles entier (par défaut)","Zoom Sud-Est France",
                 "Zoom Toulouse Garonne Ariège","Zoom Grand Sud France",
                 "Zoom Lus Genève Charlieu","Zoom Grand Mont Blanc",
                 "Zoom Savoie","Zoom Écrins",)
        for zone in range(len(zones)):
            check_1 = Checkbutton(tab3,text = zones[zone],variable=zone,
                                  command=partial(self.ReglerZoom,zone))
            check_1.pack()

        self.CreerBarreMenus()# création de la barre des menus

        # Initialisation du canevas qui sera modifié pour créer
        #et afficher les différentes cartes
        self.can = Canvas(self, width =50, height =50, bg ="white")
        self.can.pack(side =TOP, padx =5, pady =5)

    def CreerBarreMenus(self):
        """Barre de menus de l’interface graphique."""

        menu_bar = Menu(self)

        menu_arome = Menu(menu_bar, tearoff=0)
        menu_arome_0025_tout = Menu(menu_arome, tearoff=0)
        menu_arome_0025_surface = Menu(menu_arome_0025_tout, tearoff=0)
        menu_arome_0025_surface.add_command(label="Température à 2m", underline=3,
                               command=partial(self.DessinerCarteMonoParam,
                                               "AROME","0.025","T2m"))
        menu_arome_0025_surface.add_command(label="Température point de rosée à 2m", underline=3,
                               command=partial(self.DessinerCarteMonoParam,
                                               "AROME","0.025","Td2m"))
        menu_arome_0025_surface.add_command(label="Vent moyen à 10m", underline=3,
                               command=partial(self.DessinerCarteMonoParam,
                                               "AROME","0.025","Vent_Moy"))
        menu_arome_0025_surface.add_command(label="Vent rafales à 10m", underline=3,
                               command=partial(self.DessinerCarteMonoParam,
                                               "AROME","0.025","Vent_Raf"))
        menu_arome_0025_surface.add_command(label="Humidité relative à 2m", underline=3,
                               command=partial(self.DessinerCarteMonoParam,
                                               "AROME","0.025","Hu2m"))
        menu_arome_0025_surface.add_command(label="Humidité spécifique à 2m", underline=3,
                               command=partial(self.DessinerCarteMonoParam,
                                               "AROME","0.025","Hu_Specifique_2m"))
        menu_arome_0025_surface.add_command(label="Cumul de neige", underline=3,
                               command=partial(self.DessinerCarteMonoParam,
                                               "AROME","0.025","Neige_Cumul"))
        menu_arome_0025_surface.add_command(label="Précipitations de neige", underline=3,
                               command=partial(self.DessinerCarteCumuls,
                                               "AROME","0.025","Neige_Precips"))
        menu_arome_0025_surface.add_command(label="Pression au niveau de la mer", underline=3,
                               command=partial(self.DessinerCarteMonoParam,
                                               "AROME","0.025","Pmer"))
        menu_arome_0025_surface.add_command(label="Pression à la surface", underline=3,
                               command=partial(self.DessinerCarteMonoParam,
                                               "AROME","0.025","Psol"))
        menu_arome_0025_surface.add_command(label="Précipitations", underline=3,
                               command=partial(self.DessinerCarteCumuls,
                                               "AROME","0.025","Precips"))
        menu_arome_0025_surface.add_command(label="Précipitations liquides", underline=3,
                               command=partial(self.DessinerCarteCumuls,
                                               "AROME","0.025","Precips_Eau"))
        menu_arome_0025_surface.add_command(label="Rayonnement visible descendant (SW)", underline=3,
                               command=partial(self.DessinerCarteCumuls,
                                               "AROME","0.025","DSW"))
        menu_arome_0025_surface.add_command(label="Nébulosité basse", underline=3,
                               command=partial(self.DessinerCarteMonoParam,
                                               "AROME","0.025","NebulBas"))
        menu_arome_0025_surface.add_command(label="Nébulosité moyenne", underline=3,
                               command=partial(self.DessinerCarteMonoParam,
                                               "AROME","0.025","NebulMoy"))
        menu_arome_0025_surface.add_command(label="Nébulosité haute", underline=3,
                               command=partial(self.DessinerCarteMonoParam,
                                               "AROME","0.025","NebulHaut"))
        menu_arome_0025_surface.add_command(label="CAPE", underline=3,
                               command=partial(self.DessinerCarteMonoParam,
                                               "AROME","0.025","CAPE_INS"))
        menu_arome_0025_surface.add_command(label="Altitude de la couche limite", underline=3,
                               command=partial(self.DessinerCarteMonoParam,
                                               "AROME","0.025","Altitude_Couche_Limite"))
        menu_arome_0025_surface.add_command(label="Contenu total vapeur d’eau colonne atmosphérique", underline=3,
                               command=partial(self.DessinerCarteMonoParam,
                                               "AROME","0.025","Colonne_Vapeur"))
        menu_arome_0025_surface.add_command(label="Flux de chaleur latente à la surface", underline=3,
                               command=partial(self.DessinerCarteCumuls,
                                               "AROME","0.025","Flux_Chaleur_latente_Surface"))
        menu_arome_0025_surface.add_command(label="Flux de chaleur sensible à la surface", underline=3,
                               command=partial(self.DessinerCarteCumuls,
                                               "AROME","0.025","Flux_Chaleur_sensible_Surface"))
        menu_arome_0025_surface.add_command(label="Rayonnement Thermique descendant à la surface", underline=3,
                               command=partial(self.DessinerCarteCumuls,
                                               "AROME","0.025","Rayonnement_Thermique_Descendant_Surface"))
        menu_arome_0025_surface.add_command(label="Rayonnement solaire net à la surface", underline=3,
                               command=partial(self.DessinerCarteCumuls,
                                               "AROME","0.025","Rayonnement_Solaire_Net_Surface"))
        menu_arome_0025_surface.add_command(label="Rayonnement solaire net à la surface ciel clair", underline=3,
                               command=partial(self.DessinerCarteCumuls,
                                               "AROME","0.025","Rayonnement_Solaire_Net_Surface_Ciel_Clair"))
        menu_arome_0025_surface.add_command(label="Rayonnement thermique net à la surface", underline=3,
                               command=partial(self.DessinerCarteCumuls,
                                               "AROME","0.025","Rayonnement_Thermique_Net_Surface"))
        menu_arome_0025_surface.add_command(label="Rayonnement thermique net à la surface ciel clair", underline=3,
                               command=partial(self.DessinerCarteCumuls,
                                               "AROME","0.025","Rayonnement_Thermique_Net_Surface_Ciel_Clair"))
        menu_arome_0025_tout.add_cascade(label="Surface",
                             underline=0,menu=menu_arome_0025_surface)
        menu_arome_0025_iso = Menu(menu_arome_0025_tout, tearoff=0)
        menu_arome_0025_iso.add_command(label="Température", underline=3,
                               command=partial(self.DessinerCarteMonoParam,
                                               "AROME","0.025","T_Iso"))
        menu_arome_0025_iso.add_command(label="Température du point de rosée", underline=3,
                               command=partial(self.DessinerCarteMonoParam,
                                               "AROME","0.025","Td_Iso"))
        menu_arome_0025_iso.add_command(label="Vent moyen", underline=3,
                               command=partial(self.DessinerCarteMonoParam,
                                               "AROME","0.025","Vent_Moy_Iso"))
        menu_arome_0025_iso.add_command(label="Humidité relative", underline=3,
                               command=partial(self.DessinerCarteMonoParam,
                                               "AROME","0.025","Hu_Iso"))
        menu_arome_0025_iso.add_command(label="Humidité spécifique", underline=3,
                               command=partial(self.DessinerCarteMonoParam,
                                               "AROME","0.025","Hu_Specifique_Iso"))
        menu_arome_0025_iso.add_command(label="Géopotentiel", underline=3,
                               command=partial(self.DessinerCarteMonoParam,
                                               "AROME","0.025","Geopotentiel_Iso"))
        menu_arome_0025_iso.add_command(label="Contenu spécifique en eau liquide des nuages", underline=3,
                               command=partial(self.DessinerCarteMonoParam,
                                               "AROME","0.025","Specific_Cloud_Liquid_Water_Content_Iso"))
        menu_arome_0025_iso.add_command(label="Contenu spécifique en cristaux de glace des nuages", underline=3,
                               command=partial(self.DessinerCarteMonoParam,
                                               "AROME","0.025","Specific_Cloud_Ice_Water_Content_Iso"))
        menu_arome_0025_iso.add_command(label="Contenu spécifique des gouttes d’eau précipitantes", underline=3,
                               command=partial(self.DessinerCarteMonoParam,
                                               "AROME","0.025","Specific_Rain_Water_Content_Iso"))
        menu_arome_0025_iso.add_command(label="Contenu spécifique des flocons de neige précipitants", underline=3,
                               command=partial(self.DessinerCarteMonoParam,
                                               "AROME","0.025","Specific_Snow_Water_Content_Iso"))
        menu_arome_0025_iso.add_command(label="Fraction nuageuse", underline=3,
                               command=partial(self.DessinerCarteMonoParam,
                                               "AROME","0.025","Cloud_Fraction_Iso"))
        menu_arome_0025_iso.add_command(label="Vitesse verticale en m/s", underline=3,
                               command=partial(self.DessinerCarteMonoParam,
                                               "AROME","0.025","Geometric_Vertical_Velocity_Iso"))
        menu_arome_0025_iso.add_command(label="Vitesse verticale en Pa/s", underline=3,
                               command=partial(self.DessinerCarteMonoParam,
                                               "AROME","0.025","Vertical_Velocity_Iso"))
        menu_arome_0025_iso.add_command(label="Tourbillon potentiel", underline=3,
                               command=partial(self.DessinerCarteMonoParam,
                                               "AROME","0.025","Potential_Vorticity_Iso"))
        menu_arome_0025_iso.add_command(label="Tourbillon Absolu", underline=3,
                               command=partial(self.DessinerCarteMonoParam,
                                               "AROME","0.025","Absolute_Vorticity_Iso"))
        menu_arome_0025_iso.add_command(label="Tourbillon relatif", underline=3,
                               command=partial(self.DessinerCarteMonoParam,
                                               "AROME","0.025","Vorticity_Relative_Iso"))
        menu_arome_0025_iso.add_command(label="TKE", underline=3,
                               command=partial(self.DessinerCarteMonoParam,
                                               "AROME","0.025","Turbulent_Kinetic_Energy_Iso"))
        menu_arome_0025_iso.add_command(label="Theta’W", underline=3,
                               command=partial(self.DessinerCarteMonoParam,
                                               "AROME","0.025","Pseudo_Adiabatic_Potential_Temperature_Iso"))
        menu_arome_0025_tout.add_cascade(label="Niveaux isobares",
                             underline=0,menu=menu_arome_0025_iso)
        menu_arome.add_cascade(label="AROME 0.025°",
                             underline=0,menu=menu_arome_0025_tout)
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
        menu_arpege_01_tout = Menu(menu_arpege, tearoff=0)
        menu_arpege_01_surface = Menu(menu_arpege_01_tout, tearoff=0)
        menu_arpege_01_surface.add_command(label="Température à 2m", underline=3,
                               command=partial(self.DessinerCarteMonoParam,
                                               "ARPEGE","0.1","T2m"))
        menu_arpege_01_surface.add_command(label="Vent moyen à 10m", underline=3,
                               command=partial(self.DessinerCarteMonoParam,
                                               "ARPEGE","0.1","Vent_Moy"))
        menu_arpege_01_surface.add_command(label="Vent rafales à 10m", underline=3,
                               command=partial(self.DessinerCarteMonoParam,
                                               "ARPEGE","0.1","Vent_Raf"))
        menu_arpege_01_surface.add_command(label="Humidité relative à 2m", underline=3,
                               command=partial(self.DessinerCarteMonoParam,
                                               "ARPEGE","0.1","Hu2m"))
        menu_arpege_01_surface.add_command(label="Humidité spécifique à 2m", underline=3,
                               command=partial(self.DessinerCarteMonoParam,
                                               "ARPEGE","0.1","Hu_Specifique_2m"))
        menu_arpege_01_surface.add_command(label="Pression au niveau de la mer", underline=3,
                               command=partial(self.DessinerCarteMonoParam,
                                               "ARPEGE","0.1","Pmer"))
        menu_arpege_01_surface.add_command(label="Pression à la surface", underline=3,
                               command=partial(self.DessinerCarteMonoParam,
                                               "ARPEGE","0.1","Psol"))
        menu_arpege_01_surface.add_command(label="Précipitations", underline=3,
                               command=partial(self.DessinerCarteCumuls,
                                               "ARPEGE","0.1","Precips"))
        menu_arpege_01_surface.add_command(label="Cumul de neige", underline=3,
                               command=partial(self.DessinerCarteMonoParam,
                                               "ARPEGE","0.1","Neige_Cumul"))
        menu_arpege_01_surface.add_command(label="Précipitations de neige", underline=3,
                               command=partial(self.DessinerCarteCumuls,
                                               "ARPEGE","0.1","Neige_Precips"))
        menu_arpege_01_surface.add_command(label="Rayonnement visible descendant (SW)", underline=3,
                               command=partial(self.DessinerCarteCumuls,
                                               "ARPEGE","0.1","DSW"))
        menu_arpege_01_surface.add_command(label="Température point de rosée à 2m", underline=3,
                               command=partial(self.DessinerCarteMonoParam,
                                               "ARPEGE","0.1","Td2m"))
        menu_arpege_01_surface.add_command(label="Nébulosité basse", underline=3,
                               command=partial(self.DessinerCarteMonoParam,
                                               "ARPEGE","0.1","NebulBas"))
        menu_arpege_01_surface.add_command(label="Nébulosité moyenne", underline=3,
                               command=partial(self.DessinerCarteMonoParam,
                                               "ARPEGE","0.1","NebulMoy"))
        menu_arpege_01_surface.add_command(label="Nébulosité haute", underline=3,
                               command=partial(self.DessinerCarteMonoParam,
                                               "ARPEGE","0.1","NebulHaut"))
        menu_arpege_01_surface.add_command(label="Contenu total vapeur d’eau colonne atmosphérique", underline=3,
                               command=partial(self.DessinerCarteMonoParam,
                                               "ARPEGE","0.1","Colonne_Vapeur"))
        menu_arpege_01_surface.add_command(label="Altitude de la couche limite", underline=3,
                               command=partial(self.DessinerCarteMonoParam,
                                               "ARPEGE","0.1","Altitude_Couche_Limite"))
        menu_arpege_01_surface.add_command(label="CAPE", underline=3,
                               command=partial(self.DessinerCarteMonoParam,
                                               "ARPEGE","0.1","CAPE_INS"))
        menu_arpege_01_surface.add_command(label="Flux de chaleur latente à la surface", underline=3,
                               command=partial(self.DessinerCarteCumuls,
                                               "ARPEGE","0.1","Flux_Chaleur_latente_Surface"))
        menu_arpege_01_surface.add_command(label="Flux de chaleur sensible à la surface", underline=3,
                               command=partial(self.DessinerCarteCumuls,
                                               "ARPEGE","0.1","Flux_Chaleur_sensible_Surface"))
        menu_arpege_01_surface.add_command(label="Rayonnement Thermique descendant à la surface", underline=3,
                               command=partial(self.DessinerCarteCumuls,
                                               "ARPEGE","0.1","Rayonnement_Thermique_Descendant_Surface"))
        menu_arpege_01_surface.add_command(label="Rayonnement solaire net à la surface", underline=3,
                               command=partial(self.DessinerCarteCumuls,
                                               "ARPEGE","0.1","Rayonnement_Solaire_Net_Surface"))
        menu_arpege_01_surface.add_command(label="Rayonnement solaire net à la surface ciel clair", underline=3,
                               command=partial(self.DessinerCarteCumuls,
                                               "ARPEGE","0.1","Rayonnement_Solaire_Net_Surface_Ciel_Clair"))
        menu_arpege_01_surface.add_command(label="Rayonnement thermique net à la surface", underline=3,
                               command=partial(self.DessinerCarteCumuls,
                                               "ARPEGE","0.1","Rayonnement_Thermique_Net_Surface"))
        menu_arpege_01_surface.add_command(label="Rayonnement thermique net à la surface ciel clair", underline=3,
                               command=partial(self.DessinerCarteCumuls,
                                               "ARPEGE","0.1","Rayonnement_Thermique_Net_Surface_Ciel_Clair"))
        menu_arpege_01_tout.add_cascade(label="Surface",
                             underline=0,menu=menu_arpege_01_surface)
        menu_arpege_01_iso = Menu(menu_arpege_01_tout, tearoff=0)
        menu_arpege_01_iso.add_command(label="Température", underline=3,
                               command=partial(self.DessinerCarteMonoParam,
                                               "ARPEGE","0.1","T_Iso"))
        menu_arpege_01_iso.add_command(label="Température du point de rosée", underline=3,
                               command=partial(self.DessinerCarteMonoParam,
                                               "ARPEGE","0.1","Td_Iso"))
        menu_arpege_01_iso.add_command(label="Vent moyen", underline=3,
                               command=partial(self.DessinerCarteMonoParam,
                                               "ARPEGE","0.1","Vent_Moy_Iso"))
        menu_arpege_01_iso.add_command(label="Humidité relative", underline=3,
                               command=partial(self.DessinerCarteMonoParam,
                                               "ARPEGE","0.1","Hu_Iso"))
        menu_arpege_01_iso.add_command(label="Humidité spécifique", underline=3,
                               command=partial(self.DessinerCarteMonoParam,
                                               "ARPEGE","0.1","Hu_Specifique_Iso"))
        menu_arpege_01_iso.add_command(label="Géopotentiel", underline=3,
                               command=partial(self.DessinerCarteMonoParam,
                                               "ARPEGE","0.1","Geopotentiel_Iso"))
        menu_arpege_01_iso.add_command(label="Contenu spécifique en eau liquide des nuages", underline=3,
                               command=partial(self.DessinerCarteMonoParam,
                                               "ARPEGE","0.1","Specific_Cloud_Liquid_Water_Content_Iso"))
        menu_arpege_01_iso.add_command(label="Contenu spécifique en cristaux de glace des nuages", underline=3,
                               command=partial(self.DessinerCarteMonoParam,
                                               "ARPEGE","0.1","Specific_Cloud_Ice_Water_Content_Iso"))
        menu_arpege_01_iso.add_command(label="Fraction nuageuse", underline=3,
                               command=partial(self.DessinerCarteMonoParam,
                                               "ARPEGE","0.1","Cloud_Fraction_Iso"))
        menu_arpege_01_iso.add_command(label="Vitesse verticale en Pa/s", underline=3,
                               command=partial(self.DessinerCarteMonoParam,
                                               "ARPEGE","0.1","Vertical_Velocity_Iso"))
        menu_arpege_01_iso.add_command(label="Tourbillon potentiel", underline=3,
                               command=partial(self.DessinerCarteMonoParam,
                                               "ARPEGE","0.1","Potential_Vorticity_Iso"))
        menu_arpege_01_iso.add_command(label="Tourbillon Absolu", underline=3,
                               command=partial(self.DessinerCarteMonoParam,
                                               "ARPEGE","0.1","Absolute_Vorticity_Iso"))
        menu_arpege_01_iso.add_command(label="Tourbillon relatif", underline=3,
                               command=partial(self.DessinerCarteMonoParam,
                                               "ARPEGE","0.1","Vorticity_Relative_Iso"))
        menu_arpege_01_iso.add_command(label="TKE", underline=3,
                               command=partial(self.DessinerCarteMonoParam,
                                               "ARPEGE","0.1","Turbulent_Kinetic_Energy_Iso"))
        menu_arpege_01_iso.add_command(label="Theta’W", underline=3,
                               command=partial(self.DessinerCarteMonoParam,
                                               "ARPEGE","0.1","Pseudo_Adiabatic_Potential_Temperature_Iso"))
        menu_arpege_01_tout.add_cascade(label="Niveaux isobares",
                             underline=0,menu=menu_arpege_01_iso)
        menu_arpege.add_cascade(label="ARPEGE 0.1°",
                             underline=0,menu=menu_arpege_01_tout)
        menu_arpege_05_tout = Menu(menu_arpege, tearoff=0)
        menu_arpege_05_surface = Menu(menu_arpege_05_tout, tearoff=0)
        menu_arpege_05_surface.add_command(label="Température à 2m", underline=3,
                               command=partial(self.DessinerCarteMonoParam,
                                               "ARPEGE","0.5","T2m"))
        menu_arpege_05_surface.add_command(label="Vent moyen à 10m", underline=3,
                               command=partial(self.DessinerCarteMonoParam,
                                               "ARPEGE","0.5","Vent_Moy"))
        menu_arpege_05_surface.add_command(label="Vent rafales à 10m", underline=3,
                               command=partial(self.DessinerCarteMonoParam,
                                               "ARPEGE","0.5","Vent_Raf"))
        menu_arpege_05_surface.add_command(label="Humidité relative à 2m", underline=3,
                               command=partial(self.DessinerCarteMonoParam,
                                               "ARPEGE","0.5","Hu2m"))
        menu_arpege_05_surface.add_command(label="Humidité spécifique à 2m", underline=3,
                               command=partial(self.DessinerCarteMonoParam,
                                               "ARPEGE","0.5","Hu_Specifique_2m"))
        menu_arpege_05_surface.add_command(label="Pression au niveau de la mer", underline=3,
                               command=partial(self.DessinerCarteMonoParam,
                                               "ARPEGE","0.5","Pmer"))
        menu_arpege_05_surface.add_command(label="Pression à la surface", underline=3,
                               command=partial(self.DessinerCarteMonoParam,
                                               "ARPEGE","0.5","Psol"))
        menu_arpege_05_surface.add_command(label="Précipitations", underline=3,
                               command=partial(self.DessinerCarteCumuls,
                                               "ARPEGE","0.5","Precips"))
        menu_arpege_05_surface.add_command(label="Cumul de neige", underline=3,
                               command=partial(self.DessinerCarteMonoParam,
                                               "ARPEGE","0.5","Neige_Cumul"))
        menu_arpege_05_surface.add_command(label="Précipitations de neige", underline=3,
                               command=partial(self.DessinerCarteCumuls,
                                               "ARPEGE","0.5","Neige_Precips"))
        menu_arpege_05_surface.add_command(label="Rayonnement visible descendant (SW)", underline=3,
                               command=partial(self.DessinerCarteCumuls,
                                               "ARPEGE","0.5","DSW"))
        menu_arpege_05_surface.add_command(label="Température point de rosée à 2m", underline=3,
                               command=partial(self.DessinerCarteMonoParam,
                                               "ARPEGE","0.5","Td2m"))
        menu_arpege_05_surface.add_command(label="Nébulosité basse", underline=3,
                               command=partial(self.DessinerCarteMonoParam,
                                               "ARPEGE","0.5","NebulBas"))
        menu_arpege_05_surface.add_command(label="Nébulosité moyenne", underline=3,
                               command=partial(self.DessinerCarteMonoParam,
                                               "ARPEGE","0.5","NebulMoy"))
        menu_arpege_05_surface.add_command(label="Nébulosité haute", underline=3,
                               command=partial(self.DessinerCarteMonoParam,
                                               "ARPEGE","0.5","NebulHaut"))
        menu_arpege_05_surface.add_command(label="Contenu total vapeur d’eau colonne atmosphérique", underline=3,
                               command=partial(self.DessinerCarteMonoParam,
                                               "ARPEGE","0.5","Colonne_Vapeur"))
        menu_arpege_05_surface.add_command(label="Altitude de la couche limite", underline=3,
                               command=partial(self.DessinerCarteMonoParam,
                                               "ARPEGE","0.5","Altitude_Couche_Limite"))
        menu_arpege_05_surface.add_command(label="CAPE", underline=3,
                               command=partial(self.DessinerCarteMonoParam,
                                               "ARPEGE","0.5","CAPE_INS"))
        menu_arpege_05_surface.add_command(label="Flux de chaleur latente à la surface", underline=3,
                               command=partial(self.DessinerCarteCumuls,
                                               "ARPEGE","0.5","Flux_Chaleur_latente_Surface"))
        menu_arpege_05_surface.add_command(label="Flux de chaleur sensible à la surface", underline=3,
                               command=partial(self.DessinerCarteCumuls,
                                               "ARPEGE","0.5","Flux_Chaleur_sensible_Surface"))
        menu_arpege_05_surface.add_command(label="Rayonnement Thermique descendant à la surface", underline=3,
                               command=partial(self.DessinerCarteCumuls,
                                               "ARPEGE","0.5","Rayonnement_Thermique_Descendant_Surface"))
        menu_arpege_05_surface.add_command(label="Rayonnement solaire net à la surface", underline=3,
                               command=partial(self.DessinerCarteCumuls,
                                               "ARPEGE","0.5","Rayonnement_Solaire_Net_Surface"))
        menu_arpege_05_surface.add_command(label="Rayonnement solaire net à la surface ciel clair", underline=3,
                               command=partial(self.DessinerCarteCumuls,
                                               "ARPEGE","0.5","Rayonnement_Solaire_Net_Surface_Ciel_Clair"))
        menu_arpege_05_surface.add_command(label="Rayonnement thermique net à la surface", underline=3,
                               command=partial(self.DessinerCarteCumuls,
                                               "ARPEGE","0.5","Rayonnement_Thermique_Net_Surface"))
        menu_arpege_05_surface.add_command(label="Rayonnement thermique net à la surface ciel clair", underline=3,
                               command=partial(self.DessinerCarteCumuls,
                                               "ARPEGE","0.5","Rayonnement_Thermique_Net_Surface_Ciel_Clair"))
        menu_arpege_05_tout.add_cascade(label="Surface",
                             underline=0,menu=menu_arpege_05_surface)
        menu_arpege_05_iso = Menu(menu_arpege_05_tout, tearoff=0)
        menu_arpege_05_iso.add_command(label="Température", underline=3,
                               command=partial(self.DessinerCarteMonoParam,
                                               "ARPEGE","0.5","T_Iso"))
        menu_arpege_05_iso.add_command(label="Température du point de rosée", underline=3,
                               command=partial(self.DessinerCarteMonoParam,
                                               "ARPEGE","0.5","Td_Iso"))
        menu_arpege_05_iso.add_command(label="Vent moyen", underline=3,
                               command=partial(self.DessinerCarteMonoParam,
                                               "ARPEGE","0.5","Vent_Moy_Iso"))
        menu_arpege_05_iso.add_command(label="Humidité relative", underline=3,
                               command=partial(self.DessinerCarteMonoParam,
                                               "ARPEGE","0.5","Hu_Iso"))
        menu_arpege_05_iso.add_command(label="Humidité spécifique", underline=3,
                               command=partial(self.DessinerCarteMonoParam,
                                               "ARPEGE","0.5","Hu_Specifique_Iso"))
        menu_arpege_05_iso.add_command(label="Géopotentiel", underline=3,
                               command=partial(self.DessinerCarteMonoParam,
                                               "ARPEGE","0.5","Geopotentiel_Iso"))
        menu_arpege_05_iso.add_command(label="Contenu spécifique en eau liquide des nuages", underline=3,
                               command=partial(self.DessinerCarteMonoParam,
                                               "ARPEGE","0.5","Specific_Cloud_Liquid_Water_Content_Iso"))
        menu_arpege_05_iso.add_command(label="Contenu spécifique en cristaux de glace des nuages", underline=3,
                               command=partial(self.DessinerCarteMonoParam,
                                               "ARPEGE","0.5","Specific_Cloud_Ice_Water_Content_Iso"))
        menu_arpege_05_iso.add_command(label="Fraction nuageuse", underline=3,
                               command=partial(self.DessinerCarteMonoParam,
                                               "ARPEGE","0.5","Cloud_Fraction_Iso"))
        menu_arpege_05_iso.add_command(label="Vitesse verticale en Pa/s", underline=3,
                               command=partial(self.DessinerCarteMonoParam,
                                               "ARPEGE","0.5","Vertical_Velocity_Iso"))
        menu_arpege_05_iso.add_command(label="Tourbillon potentiel", underline=3,
                               command=partial(self.DessinerCarteMonoParam,
                                               "ARPEGE","0.5","Potential_Vorticity_Iso"))
        menu_arpege_05_iso.add_command(label="Tourbillon Absolu", underline=3,
                               command=partial(self.DessinerCarteMonoParam,
                                               "ARPEGE","0.5","Absolute_Vorticity_Iso"))
        menu_arpege_05_iso.add_command(label="Tourbillon relatif", underline=3,
                               command=partial(self.DessinerCarteMonoParam,
                                               "ARPEGE","0.5","Vorticity_Relative_Iso"))
        menu_arpege_05_iso.add_command(label="TKE", underline=3,
                               command=partial(self.DessinerCarteMonoParam,
                                               "ARPEGE","0.5","Turbulent_Kinetic_Energy_Iso"))
        menu_arpege_05_iso.add_command(label="Theta’W", underline=3,
                               command=partial(self.DessinerCarteMonoParam,
                                               "ARPEGE","0.5","Pseudo_Adiabatic_Potential_Temperature_Iso"))
        menu_arpege_05_tout.add_cascade(label="Niveaux isobares",
                             underline=0,menu=menu_arpege_05_iso)
        menu_arpege.add_cascade(label="ARPEGE 0.5°",
                             underline=0,menu=menu_arpege_05_tout)
        menu_bar.add_cascade(label="ARPEGE", underline=0, menu=menu_arpege)
        menu_export_arome = Menu(menu_bar, tearoff=0)
        menu_export_arome_0025_tout = Menu(menu_export_arome, tearoff=0)
        menu_export_arome_0025_surface = Menu(menu_export_arome_0025_tout, tearoff=0)
        menu_export_arome_0025_surface.add_command(label="Température à 2m", underline=3,
                               command=partial(self.DessinerCarteMonoParam,
                                               "AROME","0.025","T2m"))
        menu_export_arome_0025_surface.add_command(label="Température point de rosée à 2m", underline=3,
                               command=partial(self.DessinerCarteMonoParam,
                                               "AROME","0.025","Td2m"))
        menu_export_arome_0025_surface.add_command(label="Vent moyen à 10m", underline=3,
                               command=partial(self.DessinerCarteMonoParam,
                                               "AROME","0.025","Vent_Moy"))
        menu_export_arome_0025_surface.add_command(label="Vent rafales à 10m", underline=3,
                               command=partial(self.DessinerCarteMonoParam,
                                               "AROME","0.025","Vent_Raf"))
        menu_export_arome_0025_surface.add_command(label="Humidité relative à 2m", underline=3,
                               command=partial(self.DessinerCarteMonoParam,
                                               "AROME","0.025","Hu2m"))
        menu_export_arome_0025_surface.add_command(label="Humidité spécifique à 2m", underline=3,
                               command=partial(self.DessinerCarteMonoParam,
                                               "AROME","0.025","Hu_Specifique_2m"))
        menu_export_arome_0025_surface.add_command(label="Cumul de neige", underline=3,
                               command=partial(self.DessinerCarteMonoParam,
                                               "AROME","0.025","Neige_Cumul"))
        menu_export_arome_0025_surface.add_command(label="Précipitations de neige", underline=3,
                               command=partial(self.DessinerCarteCumuls,
                                               "AROME","0.025","Neige_Precips"))
        menu_export_arome_0025_surface.add_command(label="Pression au niveau de la mer", underline=3,
                               command=partial(self.DessinerCarteMonoParam,
                                               "AROME","0.025","Pmer"))
        menu_export_arome_0025_surface.add_command(label="Pression à la surface", underline=3,
                               command=partial(self.DessinerCarteMonoParam,
                                               "AROME","0.025","Psol"))
        menu_export_arome_0025_surface.add_command(label="Précipitations", underline=3,
                               command=partial(self.DessinerCarteCumuls,
                                               "AROME","0.025","Precips"))
        menu_export_arome_0025_surface.add_command(label="Précipitations liquides", underline=3,
                               command=partial(self.DessinerCarteCumuls,
                                               "AROME","0.025","Precips_Eau"))
        menu_export_arome_0025_surface.add_command(label="Rayonnement visible descendant (SW)", underline=3,
                               command=partial(self.DessinerCarteCumuls,
                                               "AROME","0.025","DSW"))
        menu_export_arome_0025_surface.add_command(label="Nébulosité basse", underline=3,
                               command=partial(self.DessinerCarteMonoParam,
                                               "AROME","0.025","NebulBas"))
        menu_export_arome_0025_surface.add_command(label="Nébulosité moyenne", underline=3,
                               command=partial(self.DessinerCarteMonoParam,
                                               "AROME","0.025","NebulMoy"))
        menu_export_arome_0025_surface.add_command(label="Nébulosité haute", underline=3,
                               command=partial(self.DessinerCarteMonoParam,
                                               "AROME","0.025","NebulHaut"))
        menu_export_arome_0025_surface.add_command(label="CAPE", underline=3,
                               command=partial(self.DessinerCarteMonoParam,
                                               "AROME","0.025","CAPE_INS"))
        menu_export_arome_0025_surface.add_command(label="Altitude de la couche limite", underline=3,
                               command=partial(self.DessinerCarteMonoParam,
                                               "AROME","0.025","Altitude_Couche_Limite"))
        menu_export_arome_0025_surface.add_command(label="Contenu total vapeur d’eau colonne atmosphérique", underline=3,
                               command=partial(self.DessinerCarteMonoParam,
                                               "AROME","0.025","Colonne_Vapeur"))
        menu_export_arome_0025_surface.add_command(label="Flux de chaleur latente à la surface", underline=3,
                               command=partial(self.DessinerCarteCumuls,
                                               "AROME","0.025","Flux_Chaleur_latente_Surface"))
        menu_export_arome_0025_surface.add_command(label="Flux de chaleur sensible à la surface", underline=3,
                               command=partial(self.DessinerCarteCumuls,
                                               "AROME","0.025","Flux_Chaleur_sensible_Surface"))
        menu_export_arome_0025_surface.add_command(label="Rayonnement Thermique descendant à la surface", underline=3,
                               command=partial(self.DessinerCarteCumuls,
                                               "AROME","0.025","Rayonnement_Thermique_Descendant_Surface"))
        menu_export_arome_0025_surface.add_command(label="Rayonnement solaire net à la surface", underline=3,
                               command=partial(self.DessinerCarteCumuls,
                                               "AROME","0.025","Rayonnement_Solaire_Net_Surface"))
        menu_export_arome_0025_surface.add_command(label="Rayonnement solaire net à la surface ciel clair", underline=3,
                               command=partial(self.DessinerCarteCumuls,
                                               "AROME","0.025","Rayonnement_Solaire_Net_Surface_Ciel_Clair"))
        menu_export_arome_0025_surface.add_command(label="Rayonnement thermique net à la surface", underline=3,
                               command=partial(self.DessinerCarteCumuls,
                                               "AROME","0.025","Rayonnement_Thermique_Net_Surface"))
        menu_export_arome_0025_surface.add_command(label="Rayonnement thermique net à la surface ciel clair", underline=3,
                               command=partial(self.DessinerCarteCumuls,
                                               "AROME","0.025","Rayonnement_Thermique_Net_Surface_Ciel_Clair"))
        menu_export_arome_0025_tout.add_cascade(label="Surface",
                             underline=0,menu=menu_export_arome_0025_surface)
        menu_export_arome_0025_iso = Menu(menu_export_arome_0025_tout, tearoff=0)
        menu_export_arome_0025_iso.add_command(label="Température", underline=3,
                               command=partial(self.DessinerCarteMonoParam,
                                               "AROME","0.025","T_Iso"))
        menu_export_arome_0025_iso.add_command(label="Température du point de rosée", underline=3,
                               command=partial(self.DessinerCarteMonoParam,
                                               "AROME","0.025","Td_Iso"))
        menu_export_arome_0025_iso.add_command(label="Vent moyen", underline=3,
                               command=partial(self.DessinerCarteMonoParam,
                                               "AROME","0.025","Vent_Moy_Iso"))
        menu_export_arome_0025_iso.add_command(label="Humidité relative", underline=3,
                               command=partial(self.DessinerCarteMonoParam,
                                               "AROME","0.025","Hu_Iso"))
        menu_export_arome_0025_iso.add_command(label="Humidité spécifique", underline=3,
                               command=partial(self.DessinerCarteMonoParam,
                                               "AROME","0.025","Hu_Specifique_Iso"))
        menu_export_arome_0025_iso.add_command(label="Géopotentiel", underline=3,
                               command=partial(self.DessinerCarteMonoParam,
                                               "AROME","0.025","Geopotentiel_Iso"))
        menu_export_arome_0025_iso.add_command(label="Contenu spécifique en eau liquide des nuages", underline=3,
                               command=partial(self.DessinerCarteMonoParam,
                                               "AROME","0.025","Specific_Cloud_Liquid_Water_Content_Iso"))
        menu_export_arome_0025_iso.add_command(label="Contenu spécifique en cristaux de glace des nuages", underline=3,
                               command=partial(self.DessinerCarteMonoParam,
                                               "AROME","0.025","Specific_Cloud_Ice_Water_Content_Iso"))
        menu_export_arome_0025_iso.add_command(label="Contenu spécifique des gouttes d’eau précipitantes", underline=3,
                               command=partial(self.DessinerCarteMonoParam,
                                               "AROME","0.025","Specific_Rain_Water_Content_Iso"))
        menu_export_arome_0025_iso.add_command(label="Contenu spécifique des flocons de neige précipitants", underline=3,
                               command=partial(self.DessinerCarteMonoParam,
                                               "AROME","0.025","Specific_Snow_Water_Content_Iso"))
        menu_export_arome_0025_iso.add_command(label="Fraction nuageuse", underline=3,
                               command=partial(self.DessinerCarteMonoParam,
                                               "AROME","0.025","Cloud_Fraction_Iso"))
        menu_export_arome_0025_iso.add_command(label="Vitesse verticale en m/s", underline=3,
                               command=partial(self.DessinerCarteMonoParam,
                                               "AROME","0.025","Geometric_Vertical_Velocity_Iso"))
        menu_export_arome_0025_iso.add_command(label="Vitesse verticale en Pa/s", underline=3,
                               command=partial(self.DessinerCarteMonoParam,
                                               "AROME","0.025","Vertical_Velocity_Iso"))
        menu_export_arome_0025_iso.add_command(label="Tourbillon potentiel", underline=3,
                               command=partial(self.DessinerCarteMonoParam,
                                               "AROME","0.025","Potential_Vorticity_Iso"))
        menu_export_arome_0025_iso.add_command(label="Tourbillon Absolu", underline=3,
                               command=partial(self.DessinerCarteMonoParam,
                                               "AROME","0.025","Absolute_Vorticity_Iso"))
        menu_export_arome_0025_iso.add_command(label="Tourbillon relatif", underline=3,
                               command=partial(self.DessinerCarteMonoParam,
                                               "AROME","0.025","Vorticity_Relative_Iso"))
        menu_export_arome_0025_iso.add_command(label="TKE", underline=3,
                               command=partial(self.DessinerCarteMonoParam,
                                               "AROME","0.025","Turbulent_Kinetic_Energy_Iso"))
        menu_export_arome_0025_iso.add_command(label="Theta’W", underline=3,
                               command=partial(self.DessinerCarteMonoParam,
                                               "AROME","0.025","Pseudo_Adiabatic_Potential_Temperature_Iso"))
        menu_export_arome_0025_tout.add_cascade(label="Niveaux isobares",
                             underline=0,menu=menu_export_arome_0025_iso)
        menu_export_arome.add_cascade(label="AROME 0.025°",
                             underline=0,menu=menu_export_arome_0025_tout)
        menu_export_arome_0001 = Menu(menu_export_arome, tearoff=0)
        menu_export_arome_0001.add_command(label="Température à 2m", underline=3,
                               command=partial(self.DessinerCarteMonoParam,
                                               "AROME","0.01","T2m"))
        menu_export_arome_0001.add_command(label="Vent moyen à 10m", underline=3,
                               command=partial(self.DessinerCarteMonoParam,
                                               "AROME","0.01","Vent_Moy"))
        menu_export_arome_0001.add_command(label="Vent moyen à 100m", underline=3,
                               command=partial(self.DessinerCarteMonoParam,
                                               "AROME","0.01","Vent_Moy_100m"))
        menu_export_arome_0001.add_command(label="Vent rafales à 10m", underline=3,
                               command=partial(self.DessinerCarteMonoParam,
                                               "AROME","0.01","Vent_Raf"))
        menu_export_arome_0001.add_command(label="Humidité relative à 2m", underline=3,
                               command=partial(self.DessinerCarteMonoParam,
                                               "AROME","0.01","Hu2m"))
#        menu_export_arome.add_command(label="Hauteur de neige", underline=3,
#                               accelerator="CTRL+N",
#                               command=partial(self.DessinerCarteMonoParam,
#                                               "AROME","0.01","Neige"))
        menu_export_arome_0001.add_command(label="Pression à la surface", underline=3,
                               command=partial(self.DessinerCarteMonoParam,
                                               "AROME","0.01","Psol"))
        menu_export_arome_0001.add_command(label="Précipitations", underline=3,
                               command=partial(self.DessinerCarteCumuls,
                                               "AROME","0.01","Total_Water_Precips"))
        menu_export_arome_0001.add_command(label="Nébulosité basse", underline=3,
                               command=partial(self.DessinerCarteMonoParam,
                                               "AROME","0.01","NebulBas"))
        menu_export_arome_0001.add_command(label="Nébulosité moyenne", underline=3,
                               command=partial(self.DessinerCarteMonoParam,
                                               "AROME","0.01","NebulMoy"))
        menu_export_arome_0001.add_command(label="Nébulosité haute", underline=3,
                               command=partial(self.DessinerCarteMonoParam,
                                               "AROME","0.01","NebulHaut"))
        menu_export_arome_0001.add_command(label="CAPE", underline=3,
                               command=partial(self.DessinerCarteMonoParam,
                                               "AROME","0.01","CAPE_INS"))
        menu_export_arome_0001.add_command(label="Température de brillance", underline=3,
                               command=partial(self.DessinerCarteMonoParam,
                                               "AROME","0.01","Temp_Brillance"))
        menu_export_arome_0001.add_command(label="Altitude surface modèle, constante échéance 0h", underline=3,
                               command=partial(self.DessinerCarteMonoParam,
                                               "AROME","0.01","Altitude_Surface"))
        menu_export_arome.add_cascade(label="AROME 0.01°",
                             underline=0,menu=menu_export_arome_0001)
        menu_bar.add_cascade(label="Export AROME", underline=0, menu=menu_export_arome)
        menu_obs = Menu(menu_bar, tearoff=0)
        menu_obs.add_command(label="SYNOP (surface)", underline=3,
                               command=partial(self.DessinerCarteObservations,None,None,"T2m"))
        menu_bar.add_cascade(label="Observations", underline=0, menu=menu_obs)
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
        menu_about = Menu(menu_bar,tearoff=0)
        menu_about.add_command(label="Aide",command=partial(self.AfficherAide))
        menu_about.add_command(label="À propos",command=partial(self.APropos))
        menu_bar.add_cascade(label="Aide",menu=menu_about)
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

        #self.chk = self.ck.get()
        self.chk = zone
        self.event_generate('<Control-Z>')

#    def ReglerNiveauIso(self,niveau):
#        """Réglage de la zone de zoom"""

#        #self.chk_iso = self.ck_iso.get()
#        self.chk_iso = niveau
#        print(self.chk_iso)
#        self.event_generate('<Control-Z>')

    def ReglerNiveauIso(self,event):
        self.chk_iso = self.niv_iso.get()
        print(self.chk_iso)

    def ReglerDateObs(self,event):
        self.chk_date_obs = self.date_obs.get()
        print(self.chk_date_obs)

    def ReglerEcheance(self,f):
        """Réglage de l’échéance d’intérêt"""

        self.echh = int(f)
        self.event_generate('<Control-Z>')

    def AfficherAide(self):
        """Afficher la documentation"""
        print("Voyons voir ce que donne cet essai de documentation…")

    def APropos(self):
        """Afficher un petit à propos"""
        print("Développé par Lucas GRIGIS, copyleft Lucas GRIGIS.\n" +\
              "L’intégralité du code est sous license GPL")

    def DessinerCarteMonoParam(self,modele,resolution,variable):
        """Ajout de cartes à un seul paramètre dans un canevas"""

        self.can.delete(ALL)
        self.c2 = CarteMonoParam(self,self.can,self.date_du_run,
                           modele,resolution,echeance=self.echh,
                           type_carte=variable,zoom = self.chk,
                           niveau_iso = self.chk_iso,
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

    def DessinerCarteObservations(self,modele,resolution,variable):
        """Ajout de cartes à un seul paramètre dans un canevas"""

        self.can.delete(ALL)
        self.Obs1 = CarteObservations(self,self.can,self.date_du_run,
                           self.chk_date_obs,
                           modele=None,resolution=None,echeance=None,
                           type_carte=variable,zoom = self.chk,
                           niveau_iso = None,
                           verification = 0)
        self.Obs1.envoyer_carte_vers_gui()
