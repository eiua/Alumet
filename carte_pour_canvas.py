#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""@author: lucas
 classes et méthode pour afficher une seule carte
à une échéance et à un zoom donné
 le tout dans une fenêtre de lumet.
"""
import matplotlib
matplotlib.use("TkAgg")
import pygrib
import numpy as np
import time
from config import *
#from matplotlib.animation import ArtistAnimation
from datetime import datetime
from datetime import timedelta
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cfeature
import matplotlib.dates as mdates
import matplotlib.colors as mcolors
from matplotlib.backends.backend_tkagg import FigureCanvasTk
from matplotlib.backends.backend_tkagg import NavigationToolbar2Tk
from matplotlib.figure import Figure
import matplotlib.ticker as mticker
from cartopy.mpl.gridliner import LONGITUDE_FORMATTER, LATITUDE_FORMATTER
from tkinter import *
from math import floor
import subprocess
import pandas as pd
#from metpy.calc import *
from metpy.calc import wind_components
#from metpy.calc import get_wind_components
from metpy.cbook import get_test_data
from metpy.io import metar
from metpy.plots.declarative import (BarbPlot, ContourPlot, FilledContourPlot, MapPanel,
                                     PanelContainer, PlotObs)
from metpy.units import (units, pandas_dataframe_to_unit_arrays)
from metpy.plots import StationPlot
from metpy.plots.wx_symbols import sky_cover, current_weather

class CartePourCanvas(Frame):
    """Exploiter les fichiers Arome 0.025°,
    dessin de cartes usuelles en météo.
    """
#self,jour,mois,annee,run,type_carte,zoom
    def __init__(self,date_du_run,modele,resolution,echeance,type_carte,zoom):

        Frame.__init__(self)

        self.date_du_run = date_du_run
        self.zoom = zoom
        self.modele = modele
        self.resolution = resolution
        self.echeance = echeance
        self.type_de_carte = type_carte
        self.nom_fichier_1 = ""
        self.nom_fichier_2 = ""
        self.titre_0 = ""
        self.titre_10 = ""
        self.nom_0 = ""
        self.nom_10 = ""

    def load_config(self):
        ho = YamYam(self.modele + "_" + self.resolution)
        self.t_fichiers = ho.load_config("t_fichiers")
        ha = YamYam(self.type_de_carte)
        #output forecasts files naming:
        #self.category = ha.load_config("category")
        self.shortName_grib = ha.load_config("shortName_grib")
        print("self.shortName_grib:",self.shortName_grib)
        self.instant = ha.load_config("instant")
        self.conversion_unite = ha.load_config("conversion_unite")
        self.unite = ha.load_config("unite")
        self.unite_phy = ha.load_config("unite_phy")
        self.levels_colorbar = ha.load_config("levels_colorbar")
        self.levels_contours = ha.load_config("levels_contours")
        self.cmap_carte = ha.load_config("cmap_carte")
        self.paquet = ha.load_config("paquet_" + self.modele + \
                                     "_" + self.resolution)
        self.nws_precip_colors = ha.load_config("nws_precip_colors")
        self.levels = ha.load_config("levels")
        # Pour le vent, ajout de la composante meridienne
        if self.type_de_carte[0:4] == "Vent": #"Vent_Moy" or self.type_de_carte == "Vent_Raf" or self.type_de_carte == "Vent_Moy_100m":
            self.shortName_grib_2 = ha.load_config("shortName_grib_2")
#        if self.paquet[0] == "I" or self.paquet == "H": # si niveaux isobares ou hauteur, on charge les niveaux
#            self.niveaux = ha.load_config("niveaux")

    def construire_noms(self):
        """Renvoie les différentes chaines de caractères
        qui serviront de titre,
        nom de fichier à ouvrir et de figure à sauvegarder."""

        titre_00 = ""
        
#        if self.type_de_carte == "T2m":
 #           titre_00 = self.type_de_carte + " " + self.unite
  #          if self.zoom == 0:
   #             nom_00 = "/" + self.type_de_carte
    #        elif self.zoom == 1:
     #           nom_00 = "/" + "_zoom"

        titre_00 = self.type_de_carte + " " + self.unite
        if self.zoom == 0:
            nom_00 = "/" + self.type_de_carte
        elif self.zoom == 1:
            nom_00 = "/" + "_zoom"

        self.nom_fichier_1 = "./donnees/" + self.modele +\
            "_"+ self.resolution+"/" + self.modele + "_"+ self.resolution +\
            "_" + self.paquet +"_"

        self.nom_fichier_2 = "_" + self.date_du_run + "00.grib2"

        self.titre_0 = titre_00 + " " + self.modele +\
            " " + self.resolution +"° run " + self.date_du_run[-2:] +\
            "h " + self.date_du_run[6:8] +'/'+self.date_du_run[4:6]+\
            "/"+self.date_du_run[0:4] +'0'

        self.titre_10 = titre_00 + " " + self.modele + \
            " " + self.resolution + "° run " + self.date_du_run[-2:] +\
            "h " + self.date_du_run[6:8] +'/'+self.date_du_run[4:6]+\
            "/"+self.date_du_run[0:4]

        self.nom_0 = "./figures/" + self.modele + "_" + self.resolution +\
            "_J_run_" + self.date_du_run[-2:] + "_0"
        self.nom_10 = "./figures/" + self.modele + "_" + self.resolution+\
            "_J_run_" + self.date_du_run[-2:] + "_"

    def trouver_indice_echeance(self):
        """
        Méthode qui ouvre le bon fichier au bon indice
        à partir d'une valeur d'échéance.
        Renvoie un fichier ouvert via pygrib et un indice d'échéance
        (deux de chaque dans le cas de champs à cumul
         comme les précips et le DSW).
        Les fichiers bruts sont organisés par échéances,
        de +00h à +6h, soit 7 échéances, pour le premier fichier grib2.
        Ensuite chaque fichier contient 6 échéances comme suit : +7h à +12h.
        Pour accéder au données à la bonne échéance, il faut donc:
        1 charger le bon fichier
        2 trouver l'indice dans ce fichier qui
        correspond à notre échéances donnée.
        On traduit donc: je veux l'échéance +15h
        par: voici dans le fichier 13-18h.grib2, ce sera l'indice numéro 3.
        """

        if self.resolution == "0.01":

            indice_echeance_2 = 0
            indice_echeance_1 = 0
            t_fichier = str(self.echeance).zfill(2) + 'H'
            t_fichier1 = 0
            nom_fichier2 = self.nom_fichier_1 + t_fichier + self.nom_fichier_2
            nom_fichier1 = self.nom_fichier_1 + t_fichier + self.nom_fichier_2
            # Pour les paramètres météos cumulés
            if self.echeance == 0:
                indice_echeance_1 == indice_echeance_2
                nom_fichier1 = nom_fichier2
            else:
                indice_echeance_1 = indice_echeance_2 - 1
                t_fichier1 = str(self.echeance-1).zfill(2) + 'H'
                nom_fichier1 = self.nom_fichier_1 + t_fichier1 + self.nom_fichier_2

            print("t_fichier:",t_fichier)
            print("nom_fichier:",nom_fichier2)
            print("t_fichier:",t_fichier1)
            print("nom_fichier:",nom_fichier1)

        else:
            for i in range(len(self.t_fichiers)):
                t_fichier2 = self.t_fichiers[i]
                if ((self.echeance >= int(t_fichier2[0:2])) and 
                    (self.echeance <= int(t_fichier2[3:5]))):
                    print("int(t_fichier[3:5])",int(t_fichier2[3:5]))
                    print("échéance:",self.echeance)
                    print("i:",i)
                    print("t_fichier2",t_fichier2)
                    # t_fichier = self.t_fichiers[i]
                    indice_echeance_2 = self.echeance - int(t_fichier2[0:2])
                    print("indice_echeance_2",indice_echeance_2)
                    if indice_echeance_2 == 0:
                        if self.echeance >0:
                            t_fichier1 = self.t_fichiers[i-1]
                            indice_echeance_1 = (self.echeance - 
                                                 int(self.t_fichiers[i-1][0:2]))
                        elif self.echeance ==0:
                            t_fichier1 = t_fichier2
                            indice_echeance_1 = indice_echeance_2
                    else:
                        indice_echeance_1 = indice_echeance_2 - 1
                        t_fichier1 = t_fichier2
                    break
                else:
                    del(t_fichier2)

            print("t_fichier2:",t_fichier2)
            nom_fichier2 = self.nom_fichier_1 + t_fichier2 + \
                self.nom_fichier_2
            print("nom_fichier:",nom_fichier2)
            print("t_fichier1:",t_fichier1)
            nom_fichier1 = self.nom_fichier_1 + t_fichier1 + \
                self.nom_fichier_2
            print("nom_fichier1:",nom_fichier1)

#        if self.type_de_carte == "DSW" or self.type_de_carte == "Flux_Chaleur_latente_Surface" or self.type_de_carte == "Flux_Chaleur_sensible_Surface" or self.type_de_carte == "Rayonnement_Thermique_Descendant_Surface" or self.type_de_carte == "Rayonnement_Solaire_Net_Surface" or self.type_de_carte == "Rayonnement_Solaire_Net_Surface_Ciel_Clair" or self.type_de_carte == "Rayonnement_Thermique_Net_Surface" or self.type_de_carte == "Rayonnement_Thermique_Net_Surface_Ciel_Clair" or self.type_de_carte == "Precips" or self.type_de_carte == "Total_Water_Precips" or self.type_de_carte == "Precips_Eau" or self.type_de_carte == "Neige_Precips":
        if self.instant == "cumul":
            print("coucoucouou")
            return (indice_echeance_1,indice_echeance_2,
                   nom_fichier1,nom_fichier2)
        else:
            return (indice_echeance_2,nom_fichier2)

    def dessiner_fond_carte(self,lons,lats):
        """
        Renvoie un fond de carte géographique sur lequel
        on tracera le ou les champs météo.
        """
        lon_0 = lons.mean()
        lat_0 = lats.mean()

        if self.resolution == "0.5":
            proj = ccrs.Robinson()
        else:
            proj = ccrs.Stereographic(central_longitude=lon_0, central_latitude=lat_0)
        #Robinson(central_longitude=0,globe=None)
        #InterruptedGoodeHomolosine(central_longitude=0)
        #Mollweide()
        #Stereographic(central_longitude=lon_0,central_latitude=lat_0)

        f = Figure()#figsize=(15,15), dpi=300)
        ax = f.add_subplot()#111)

        ax = plt.axes(projection=proj)
        ax.set_global()

        if self.modele == "AROME":
            pays = cfeature.NaturalEarthFeature(category='cultural',
                                                name='admin_0_countries',
                                                scale='10m',facecolor='none')
            ax.add_feature(pays,edgecolor='black',linewidth=(0.7))

            fleuves = cfeature.NaturalEarthFeature(category='physical',
                                                   name='rivers_lake_centerlines',
                                                   scale='10m',
                                                   facecolor='none')

            ax.add_feature(fleuves,edgecolor='blue',linewidth=(0.3))
            rivieres = cfeature.NaturalEarthFeature(category='physical',
                                                    name='rivers_europe',
                                                    scale='10m',
                                                    facecolor='none')
            ax.add_feature(rivieres,edgecolor='blue',linewidth=(0.3))
        elif self.modele == "ARPEGE":
            pays = cfeature.NaturalEarthFeature(category='cultural',
                                                name='admin_0_countries',
                                                scale='10m',facecolor='none')
            ax.add_feature(pays,edgecolor='black',linewidth=(0.4))

        if self.resolution != "0.5":
            if self.zoom == 1:
                ax.set_extent([lons.min(),lons.max(),lats.min(),lats.max()])
            else:
                ax.set_extent([lons.min(),lons.max(),lats.min(),lats.max()])

        return f,ax

    def zones_zoom(self,num_zone):

        zones_zoom=((("Sud-Est"),(43,47,2.25,7.5)),
                    (("Toulouse_Garonne_Ariege"),(42.4,43.7,0.37,1.88)),
                    (("Grand_S_France"),(41.07,46.22,-3.61,9.55)),
                    (("Lus_Geneve_Charlieu"),(44.64,46.2,4.15,6.66)),
                    (("Grand_Mont_Blanc"),(45.59,46.24,6.27,7.24)),
                    (("Savoie"),(45.16,45.68,6.19,7.22)),
                    (("Ecrins"),(44.61,45.11,5.94,6.62)),)

        return zones_zoom[num_zone]

class CarteMonoParam(CartePourCanvas):
    """Renvoie une carte à un seul paramètre météo."""

    def __init__(self,boss,canev,date_du_run,modele,resolution,echeance,
                 type_carte,zoom, niveau_iso, verification):

        CartePourCanvas.__init__(self,date_du_run,modele,resolution,
                                         echeance,type_carte,zoom)

        Frame.__init__(self)

        self.date_du_run = date_du_run
        self.verification = verification
        self.canev=canev
        self.niveau_iso = niveau_iso

    def arrondir(self,x, val=4):
        return val * np.round(x/val)

    def envoyer_carte_vers_gui(self):
        print("CarteMonoParam",self.type_de_carte)
        self.load_config()
        self.construire_noms()

        indice_echeance,nom_fichier = self.trouver_indice_echeance()

        if self.zoom >=1:
            coords = self.zones_zoom(self.zoom-1)

        grbs = pygrib.open(nom_fichier)
        
        for g in grbs:
            print(g.shortName,g)
#            print(g.level,g)

        if self.paquet[0] == "I": # si niveaux isobares ou hauteur, on charge les niveaux
            print("self.shortName_grib: ",self.shortName_grib)
            print("self.niveau_iso: ",self.niveau_iso)
            print("self.type_de_carte[0:4]: ", self.type_de_carte[0:4])
            gt = grbs.select(shortName = self.shortName_grib, level = self.niveau_iso)[indice_echeance]

            if self.type_de_carte[0:4] == "Vent":
                gt2 = grbs.select(shortName = self.shortName_grib_2, level = self.niveau_iso)[indice_echeance]
        elif self.paquet[0] == "H":
            gt = grbs.select(shortName = self.shortName_grib, level = self.niveau_iso)[indice_echeance]
            if self.type_de_carte[0:4] == "Vent":
                gt2 = grbs.select(shortName = self.shortName_grib_2, level = self.niveau_iso)[indice_echeance]
        else:
            gt = grbs.select(shortName = self.shortName_grib)[indice_echeance]
            if self.type_de_carte[0:4] == "Vent":
                gt2 = grbs.select(shortName = self.shortName_grib_2)[indice_echeance]

        print("Échéance: ",self.echeance)
        print("indice échéance 1: ",indice_echeance)

        ech_mois = str(gt.validityDate)[4:6]
        ech_jour = str(gt.validityDate)[6:8]

        if gt.validityTime<1000:
            ech_heure = str(gt.validityTime)[0]
        else:
            ech_heure = str(gt.validityTime)[0:2]

        validite ="Prévision pour le " + ech_jour + "/" + ech_mois+ \
            " " + ech_heure + "H"

        if self.zoom == 0:
            tt, lats, lons = gt.data()#(lat1=43,lat2=47,lon1=2.25,lon2=7.5)
            if self.type_de_carte[0:4] == "Vent":
                tt2, lats,lons = gt2.data()
        elif self.zoom >= 1:

            lat11 = coords[1][0]
            print(lat11)
            lat22 = coords[1][1]
            lon11 = coords[1][2]
            lon22 = coords[1][3]

            tt, lats, lons = gt.data(lat1=lat11,lat2=lat22,
                                     lon1=lon11,lon2=lon22)
            if self.type_de_carte[0:4] == "Vent":
                tt2, lats, lons = gt2.data(lat1=lat11,lat2=lat22,
                                         lon1=lon11,lon2=lon22)
            print(lats[0,0],lats[-1,-1])
            print(lons[0,0],lons[-1,-1])

        print("Champ: ", gt.shortName, "    Validité: ", gt.validityDate,
              " à ",gt.validityTime)

        del gt
        grbs.close()
        if self.type_de_carte[0:4] == "Vent":
            tt = np.sqrt(tt**2 + tt2**2)*3.6 # fusion des composante et passage de m/s vers km/h

        tt = (tt + self.conversion_unite)
        tt = tt.astype(int)
        #tt = arrondir(tt,4)

        f,ax = self.dessiner_fond_carte(lons,lats)

        origin='lower'

        print(self.levels_colorbar)
        print(self.levels_colorbar[0])
        ln = int(self.levels_colorbar[0])
        lx = int(self.levels_colorbar[1])
        lst = float(self.levels_colorbar[2])
        levels = np.arange(ln,lx,lst)

        lln = int(self.levels_contours[0])
        llx = int(self.levels_contours[1])
        llst = float(self.levels_contours[2])
        levels_contour_2 = np.arange(lln,llx,llst)

        cc = ax.contour(lons, lats, tt, levels_contour_2,
                      colors=('k'),
                      linewidths=(0.15),
                      origin=origin,transform=ccrs.PlateCarree())

        if self.verification == 1:
            print("fin contour")

        if self.type_de_carte == "Neige_Cumul" or self.type_de_carte[0:4] == "Vent":
            nws_precip_colors = self.nws_precip_colors
            precip_colormap = mcolors.ListedColormap(nws_precip_colors)
            levels = self.levels
            norm = mcolors.BoundaryNorm(levels, len(levels))

            bb=plt.pcolormesh(lons, lats, tt, norm=norm, cmap=precip_colormap,
                          transform=ccrs.PlateCarree())
        else:
            bb = ax.pcolormesh(lons,lats,tt,vmin=ln,vmax=lx,
                               cmap=self.cmap_carte,
                               transform=ccrs.PlateCarree())

        csb = plt.colorbar(bb, shrink=0.9, pad=0, aspect=20)

        #csb.set_label("("+ self.unite +")")

        #csb.set_label("Module du Jet (m/s)")
        #ax.barbs(lons[::50],lats[::50], vent_zonal[::50], vent_meri[::50],
        #    transform=ccrs.PlateCarree(),length=5)

        lala_pvu = plt.clabel(cc, fontsize=8, fmt='%1.0f')

        gl = ax.gridlines(crs=ccrs.PlateCarree(), draw_labels=True,
                          linewidth=0.2, color='k', alpha=1, linestyle='--')
        gl.xlabels_top = False
        gl.ylabels_left = False
        gl.xlines = True
        gl.xlocator = mticker.FixedLocator([-180, -135, -90, -45, 0, 45, 90, 135, 180])
        gl.ylocator = mticker.FixedLocator([-66.33, -45, -23.26, 0, 23.26, 45, 66.33])
        gl.xformatter = LONGITUDE_FORMATTER
        gl.yformatter = LATITUDE_FORMATTER
        gl.xlabel_style = {'size': 7, 'color': 'k'}
        gl.ylabel_style = {'size': 7, 'color': 'k'}

        if self.verification == 1:
            print("fin contourf")

        if self.echeance < 10:
            titre = self.titre_0 + "\n" + validite
            nom = self.nom_0 + str(self.echeance)+'H.png'
        else:
            titre = self.titre_10 + "\n" + validite
            nom = self.nom_10 + str(self.echeance)+'H.png'
        plt.text(0.5,0.97,titre,horizontalalignment='center',
                 verticalalignment='center', transform = ax.transAxes)
        print(titre)
        print(nom)

        #plt.title(titre)
        plt.subplots_adjust(left=0, right=1, top=1, bottom=0)
        plt.show()
        self.canev = FigureCanvasTk(f, self.master)
        self.canev.show()

        self.canev.get_tk_widget().pack(expand=True)

        toolbar = NavigationToolbar2Tk(self.canev, self.master)
        toolbar.update()
        self.canev._tkcanvas.pack(expand=True)

        plt.close()

        del tt
        del titre
        del nom

class CarteCumuls(CartePourCanvas):
    """Renvoie une carte pour un paramètre à cumul, comme les précipitations
    ou le rayonnement visible descendant (DSW)."""

    def __init__(self,boss,canev,date_du_run,modele,resolution,echeance,
                 type_carte,zoom,verification):

        CartePourCanvas.__init__(self,date_du_run,modele,resolution,
                                         echeance,type_carte,zoom)

        Frame.__init__(self)

        self.date_du_run = date_du_run
        self.verification = verification
        self.canev=canev
        self.echeance = echeance

    def envoyer_carte_vers_gui(self):
        print("CarteCumuls: ",self.type_de_carte)
        self.load_config()
        self.construire_noms()

        if self.zoom >=1:
            coords = self.zones_zoom(self.zoom-1)

        print(self.trouver_indice_echeance())

        indice_echeance_1,indice_echeance_2,nom_fichier1,nom_fichier2 = self.\
            trouver_indice_echeance()

        if self.echeance > 0:
            grbs_1 = pygrib.open(nom_fichier1)

#            for gg in grbs_1.select(shortName = self.shortName_grib):
#                print(gg)
            gt_1 = grbs_1.select(shortName = self.shortName_grib)[indice_echeance_1]

        grbs_2 = pygrib.open(nom_fichier2)
        gt_2 = grbs_2.select(shortName = self.shortName_grib)[indice_echeance_2]

        ech_mois = str(gt_2.validityDate)[4:6]
        ech_jour = str(gt_2.validityDate)[6:8]

        if gt_2.validityTime<1000:
            ech_heure = str(gt_2.validityTime)[0]
        else:
            ech_heure = str(gt_2.validityTime)[0:2]

        print("Champ: ",gt_2.shortName,"  Validité: ",gt_2.validityDate,
              " à ",gt_2.validityTime)

        validite ="Prévision pour le " + ech_jour + "/" + ech_mois+ \
            " " + ech_heure + "H"

        if self.verification == 1:
            print(gt_1)
            print(gt_2)

        if self.echeance == 0:
            if self.zoom == 0:
                tt2, lats, lons = gt_2.data()
                grbs_2.close()
            elif self.zoom >= 1:

                lat11 = coords[1][0]
                print(lat11)
                lat22 = coords[1][1]
                lon11 = coords[1][2]
                lon22 = coords[1][3]
                tt2, lats, lons = gt_2.data(lat1=lat11,lat2=lat22,
                                            lon1=lon11,lon2=lon22)
                grbs_2.close()

            tt1 = 0

        else:
            if self.zoom == 0:
                tt1, lats, lons = gt_1.data()
                tt2, lats, lons = gt_2.data()
                grbs_1.close()
                grbs_2.close()
            elif self.zoom >= 1:
                lat11 = coords[1][0]
                print(lat11)
                lat22 = coords[1][1]
                lon11 = coords[1][2]
                lon22 = coords[1][3]
                tt1, lats, lons = gt_1.data(lat1=lat11,lat2=lat22,
                                            lon1=lon11,lon2=lon22)
                tt2, lats, lons = gt_2.data(lat1=lat11,lat2=lat22,
                                            lon1=lon11,lon2=lon22)
                grbs_1.close()
                grbs_2.close()

        if self.echeance > 0:
            del gt_1
        del gt_2

        tete = tt2 - tt1

        del tt1
        del tt2

        if self.type_de_carte == "DSW" or self.type_de_carte == "Precips" or self.type_de_carte == "Total_Water_Precips" or self.type_de_carte == "Precips_Eau":
            tt = np.ma.masked_less(tete, 0.1)
        else:
            tt = tete
        del tete

        f,ax = self.dessiner_fond_carte(lons,lats)

        origin='lower'

        print(self.levels_colorbar)
        print(self.levels_colorbar[0])
        ln = int(self.levels_colorbar[0])
        lx = int(self.levels_colorbar[1])
        lst = float(self.levels_colorbar[2])
        levels = np.arange(ln,lx,lst)

        lln = int(self.levels_contours[0])
        llx = int(self.levels_contours[1])
        llst = float(self.levels_contours[2])
        levels_contour_2 = np.arange(lln,llx,llst)

        cc = ax.contour(lons, lats, tt, levels_contour_2,
                      colors=('k'),
                      linewidths=(0.15),
                      origin=origin,transform=ccrs.PlateCarree())
        if self.type_de_carte == "DSW" or self.type_de_carte == "Flux_Chaleur_latente_Surface" or self.type_de_carte == "Flux_Chaleur_sensible_Surface" or self.type_de_carte == "Rayonnement_Thermique_Descendant_Surface" or self.type_de_carte == "Rayonnement_Solaire_Net_Surface" or self.type_de_carte == "Rayonnement_Solaire_Net_Surface_Ciel_Clair" or self.type_de_carte == "Rayonnement_Thermique_Net_Surface" or self.type_de_carte == "Rayonnement_Thermique_Net_Surface_Ciel_Clair":
            cs=plt.pcolormesh(lons, lats, tt, vmin=ln, vmax=lx, cmap=self.cmap_carte,
                          transform=ccrs.PlateCarree())
        else:
            nws_precip_colors = self.nws_precip_colors
            precip_colormap = mcolors.ListedColormap(nws_precip_colors)
            levels = self.levels
            norm = mcolors.BoundaryNorm(levels, len(levels))

            cs=plt.pcolormesh(lons, lats, tt, norm=norm, cmap=precip_colormap,
                          transform=ccrs.PlateCarree())

        csb = plt.colorbar(cs, shrink=0.9, pad=0, aspect=20)
        #csb.set_label("mm")

        lala_pvu = plt.clabel(cc, fontsize=8, fmt='%1.0f')

        gl = ax.gridlines(crs=ccrs.PlateCarree(), draw_labels=True,
                          linewidth=0.2, color='k', alpha=1, linestyle='--')
        gl.xlabels_top = False
        gl.ylabels_left = False
        gl.xlines = True
        gl.xlocator = mticker.FixedLocator([-180, -135, -90, -45, 0, 45, 90, 135, 180])
        gl.ylocator = mticker.FixedLocator([-66.33, -45, -23.26, 0, 23.26, 45, 66.33])
        gl.xformatter = LONGITUDE_FORMATTER
        gl.yformatter = LATITUDE_FORMATTER
        gl.xlabel_style = {'size': 7, 'color': 'k'}
        gl.ylabel_style = {'size': 7, 'color': 'k'}

        if self.echeance < 10:
            titre = self.titre_0 + "\n" + validite
            nom = self.nom_0 + str(self.echeance)+'H.png'
        else:
            titre = self.titre_10 + "\n" + validite
            nom = self.nom_10 + str(self.echeance)+'H.png'

        if self.verification == 1:
            print(titre)
            print(nom)
        plt.text(0.5,0.97,titre,horizontalalignment='center',
                 verticalalignment='center', transform = ax.transAxes)
        #plt.title(titre)
        plt.subplots_adjust(left=0, right=1, top=1, bottom=0)
        plt.show()

        #self.canev.get_tk_widget().destroy()
        self.canev = FigureCanvasTk(f, self.master)
        self.canev.show()
        self.canev.get_tk_widget().pack(expand=True)

        toolbar = NavigationToolbar2Tk(self.canev, self.master)
        toolbar.update()
        self.canev._tkcanvas.pack(expand=True)

        plt.close()
        del tt
        del titre
        del nom

        print("coucou")

class CarteObservations(CartePourCanvas):
    """Renvoie une carte des observations de surface in-situ essentielles SYNOP."""

    def __init__(self,boss,canev,date_du_run,date_des_obs,modele,resolution,echeance,
                 type_carte,zoom, niveau_iso, verification):

        CartePourCanvas.__init__(self,date_du_run,modele,resolution,
                                         echeance,type_carte,zoom)

        Frame.__init__(self)

        self.date_des_obs = date_des_obs
        self.canev=canev
        self.niveau_iso = niveau_iso

    def envoyer_carte_vers_gui(self):
        print("CarteMonoParam",self.type_de_carte)

        if self.zoom >=1:
            coords = self.zones_zoom(self.zoom-1)

        print(int(datetime.strptime(self.date_des_obs, '%Y-%m-%d %H').strftime("%Y%m%d%H%M%S")))

        #Décompresser une archive d’obs synop au format .gz
        subprocess.run(["gzip","-dfk","./donnees/SYNOP/synop." + datetime.strptime(self.date_des_obs, '%Y-%m-%d %H').strftime("%Y%m") + ".csv.gz"])
        subprocess.run(["gzip","-dfk","./donnees/SYNOP/marine." + datetime.strptime(self.date_des_obs, '%Y-%m-%d %H').strftime("%Y%m") + ".csv.gz"])

        df_sy= pd.read_csv("./donnees/SYNOP/synop." + datetime.strptime(self.date_des_obs, '%Y-%m-%d %H').strftime("%Y%m")+ ".csv",sep=';', na_values="mq")
        df_sy.rename(columns={'numer_sta': 'station_id'}, inplace=True)

        print(datetime.strptime(self.date_des_obs, '%Y-%m-%d %H').timestamp())

        df_sy = df_sy[df_sy.values==int(datetime.strptime(self.date_des_obs, '%Y-%m-%d %H').strftime("%Y%m%d%H%M%S"))]

        df_loc= pd.read_csv("./donnees/SYNOP/postesSynop.csv",sep=';', na_values="mq")
        df_loc.rename(columns={'ID': 'station_id', "Latitude": "latitude", "Longitude": "longitude"}, inplace=True)

        df_syn = pd.merge(df_sy, df_loc, on="station_id", how="left")

        df_mar= pd.read_csv("./donnees/SYNOP/marine." + datetime.strptime(self.date_des_obs, '%Y-%m-%d %H').strftime("%Y%m")+ ".csv",sep=';', na_values="mq")
        df_mar.rename(columns={'numer_sta': 'station_id', "lat": "latitude", "lon": "longitude"}, inplace=True)
        df_mar = df_mar[df_mar.values==int(datetime.strptime(self.date_des_obs, '%Y-%m-%d %H').strftime("%Y%m%d%H%M%S"))]

        df_synop = pd.concat([df_syn, df_mar]) 

        print(df_synop["n"])
        u, v = wind_components((df_synop['ff'].values * units('m/s')).to('knots'),
                                    df_synop['dd'].values * units.degree)

        nebul_tot = df_synop["n"].fillna(130).values
        nebul_tot = (8 * nebul_tot/100).astype(int)
        print(nebul_tot)

        lons = df_synop['longitude'].values 
        lats = df_synop['latitude'].values

        proj = ccrs.Robinson(central_longitude=0,globe=None)

        f = Figure()#figsize=(15,15), dpi=300)
        ax = f.add_subplot()#111)

        ax = plt.axes(projection=proj)
        ax.set_global()

        pays = cfeature.NaturalEarthFeature(category='cultural',
                                            name='admin_0_countries',
                                            scale='50m',facecolor='none')
        ax.add_feature(pays,edgecolor='black',linewidth=(0.7))

        fleuves = cfeature.NaturalEarthFeature(category='physical',
                                               name='rivers_lake_centerlines',
                                               scale='50m',
                                               facecolor='none')

        ax.add_feature(fleuves,edgecolor='blue',linewidth=(0.3))

        stationplot = StationPlot(ax, lons, lats, transform=ccrs.PlateCarree(),
                          fontsize=8)

        stationplot.plot_symbol('C', nebul_tot, sky_cover)
        stationplot.plot_barb(u, v,linewidth=(0.3))
        stationplot.plot_parameter('NW', df_synop["t"].values-273.15, color='black')
        stationplot.plot_parameter('SW', df_synop["td"].values-273.15, color='red')
        stationplot.plot_parameter('NE', df_synop["pmer"].values, formatter=lambda v: format(v, '.0f')[-4:-1], color='black')
        stationplot.plot_parameter('E', df_synop["tend"].values, formatter=lambda v: format(v, '.0f')[:-1], color='black')
        stationplot.plot_symbol('W', df_synop["ww"].fillna(0).values.astype(int), current_weather)

        titre = "Observations à la surface SYNOP\n" + self.date_des_obs + "H"

        plt.text(0.5,0.97,titre,horizontalalignment='center',
                 verticalalignment='center', transform = ax.transAxes)
        plt.subplots_adjust(left=0, right=1, top=1, bottom=0)
        plt.show()


        # supprimer le fichier décompressé, on ne garde que les fichiers compressés (10x plus légers)
        subprocess.run(["rm","./donnees/SYNOP/synop." + datetime.strptime(self.date_des_obs, '%Y-%m-%d %H').strftime("%Y%m") + ".csv"])
        subprocess.run(["rm","./donnees/SYNOP/marine." + datetime.strptime(self.date_des_obs, '%Y-%m-%d %H').strftime("%Y%m") + ".csv"])

        self.canev = FigureCanvasTk(f, self.master)
        self.canev.show()
        self.canev.get_tk_widget().pack(expand=True)

        toolbar = NavigationToolbar2Tk(self.canev, self.master)
        toolbar.update()
        self.canev._tkcanvas.pack(expand=True)
