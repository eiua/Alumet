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
from tkinter import *
from math import floor

class AromeCartePourCanvas(Frame):
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
        self.conversion_unite = ha.load_config("conversion_unite")
        self.unite = ha.load_config("unite")
        self.unite_phy = ha.load_config("unite_phy")
        self.levels_colorbar = ha.load_config("levels_colorbar")
        self.levels_contours = ha.load_config("levels_contours")
        self.cmap_carte = ha.load_config("cmap_carte")
        self.paquet = ha.load_config("paquet_" + self.modele + \
                                     "_" + self.resolution)

    def construire_noms(self):
        """Renvoie les différentes chaines de caractères
        qui serviront de titre,
        nom de fichier à ouvrir et de figure à sauvegarder."""

        titre_00 = ""
        
        if self.type_de_carte == "T2m":
            #sp1_ip5 = "SP1"
            titre_00 = 'T2m (°C)'
            if self.zoom == 0:
                nom_00 = '/T2m'
            elif self.zoom == 1:
                nom_00 = '/T2m_zoom'

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
            t_fichier = str(self.echeance).zfill(2) + 'H'
            nom_fichier2 = self.nom_fichier_1 + t_fichier + self.nom_fichier_2

            print("t_fichier:",t_fichier)
            print("nom_fichier:",nom_fichier2)

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

        if self.type_de_carte == "DSW" or self.type_de_carte == "Precips":
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

        proj = ccrs.Stereographic(central_longitude=lon_0,
                                  central_latitude=lat_0)

        f = Figure()#figsize=(15,15), dpi=300)
        ax = f.add_subplot()#111)

        ax = plt.axes(projection=proj)

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

            if self.zoom == 1:
                ax.set_extent([lons.min(),lons.max(),lats.min(),lats.max()])
            else:
                ax.set_extent([lons.min(),lons.max(),lats.min(),lats.max()])

        elif self.modele == "ARPEGE":
            pays = cfeature.NaturalEarthFeature(category='cultural',
                                                name='admin_0_countries',
                                                scale='10m',facecolor='none')
            ax.add_feature(pays,edgecolor='black',linewidth=(0.4))

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


class CarteMonoParam(AromeCartePourCanvas):
    """Renvoie la carte de températures à deux mètre prévue
        par Arome 0.025° ou 0.01°."""
    def __init__(self,boss,canev,date_du_run,modele,resolution,echeance,
                 type_carte,zoom,verification):

        AromeCartePourCanvas.__init__(self,date_du_run,modele,resolution,
                                         echeance,type_carte,zoom)

        Frame.__init__(self)

        self.date_du_run = date_du_run
        self.verification = verification
        self.canev=canev

    def envoyer_carte_vers_gui(self):
        print("CarteMonoParam",self.type_de_carte)
        self.load_config()
        self.construire_noms()

        indice_echeance,nom_fichier = self.trouver_indice_echeance()

        if self.zoom >=1:
            coords = self.zones_zoom(self.zoom-1)

        grbs = pygrib.open(nom_fichier)
        
#        for g in grbs:
#            print(g.shortName,g)
        
        gt = grbs.select(shortName = self.shortName_grib)[indice_echeance]

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
        elif self.zoom >= 1:

            lat11 = coords[1][0]
            print(lat11)
            lat22 = coords[1][1]
            lon11 = coords[1][2]
            lon22 = coords[1][3]

            tt, lats, lons = gt.data(lat1=lat11,lat2=lat22,
                                     lon1=lon11,lon2=lon22)
            print(lats[0,0],lats[-1,-1])
            print(lons[0,0],lons[-1,-1])

        print("Champ: ", gt.shortName, "    Validité: ", gt.validityDate,
              " à ",gt.validityTime)

        del gt
        grbs.close()

        tt = (tt + self.conversion_unite)
        tt = tt.astype(int)

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

        bb = ax.pcolormesh(lons,lats,tt,vmin=ln,vmax=lx,
                           cmap=self.cmap_carte,
                           transform=ccrs.PlateCarree())

        csb = plt.colorbar(bb, shrink=0.9, pad=0, aspect=20)

        #csb.set_label("("+ self.unite +")")

        #csb.set_label("Module du Jet (m/s)")
        #ax.barbs(lons[::50],lats[::50], vent_zonal[::50], vent_meri[::50],
        #    transform=ccrs.PlateCarree(),length=5)

        lala_pvu = plt.clabel(cc, fontsize=8, fmt='%1.0f')

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
