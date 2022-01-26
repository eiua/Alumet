#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Oct 25 10:21:48 2021

@author: lucas

Téléchargement des données libres des modèles de prévision de Météo-France.
Code initial de François Pacull, voir:
https://www.architecture-performance.fr/ap_blog/
fetching-arome-weather-forecasts-and-plotting-temperatures/
"""
import os
import sys
import datetime
import subprocess
import numpy as np

from config import *

class TelechargerDonneesModeles():
    """Téléchargement des données modèles via requête sur le site des
    données publiques de Météo-France"""

    def __init__(self,modele,resolution,verification):
        """Téléchargement des données des modèles de prévision à courte
        échéance de Météo-France. AROME 0.01° et 0.025°, ARPEGE 0.1°
        """

        #self.date_du_run = date_du_run
        self.verification = verification
        self.modele = modele
        self.resolution = resolution
        
    def load_config(self):
        ho = YamYam(self.modele + "_" + self.resolution)
        self.t_fichiers = ho.load_config("t_fichiers")
        
    def donner_date_du_dernier_run(self,delay=4):
        """ Runs are updated at 0am, 3am, 6am, 0pm, 6pm UTC.
            Note that the delay must be adjusted.
        """
        utc_now = datetime.datetime.utcnow()
        candidate = datetime.datetime(utc_now.year, utc_now.month, utc_now.day, utc_now.hour) - \
            datetime.timedelta(hours=delay)
        run_time = datetime.datetime(candidate.year, candidate.month, candidate.day)
        
        if self.modele == "AROME":
            for hour in np.flip(np.sort([0, 3, 6, 12, 18,])):
                if candidate.hour >= hour:
                    run_time += datetime.timedelta(hours=int(hour))
                    break
        else:
            for hour in np.flip(np.sort([0, 6, 12, 18,])):
                if candidate.hour >= hour:
                    run_time += datetime.timedelta(hours=int(hour))
                    break
        return run_time.isoformat()

    def donner_intervalle_temps(self,batch_number=0):
        """ 7 different 6-hours long time ranges: 0-6H, 7-12H, ... , 37-42H.
        """
        if self.modele == "AROME" and self.resolution == "0.025":
            assert batch_number in range(7)
            end = 6 * (batch_number + 1)
            if batch_number == 0:
                start = 0
            else:
                start = end - 5
            time_range = str(start).zfill(2) + 'H' + str(end).zfill(2) +'H'
        elif self.modele == "AROME" and self.resolution == "0.01":
            assert batch_number in range(43)
            end = batch_number
            if batch_number == 0:
                start = 0
            else:
                start = end
            time_range = str(start).zfill(2) + 'H'
        elif self.modele == "ARPEGE" and self.resolution == "0.1":
            assert batch_number in range(9)
            end = 12 * (batch_number + 1)
            if batch_number == 0:
                start = 0
            else:
                start = end - 11
            time_range = str(start).zfill(2) + 'H' + str(end).zfill(2) +'H'
        elif self.modele == "ARPEGE" and self.resolution == "0.5":
            assert batch_number in range(9)
            end = 24 * (batch_number + 1)
            if batch_number == 0:
                start = 0
            else:
                start = end - 21
            time_range = str(start).zfill(2) + 'H' + str(end).zfill(2) +'H'
        return time_range

    def creer_url(self,run_time,time_range='00H06H',package='SP1',
                   token='__5yLVTdr-sGeHoPitnFc7TZ6MhBcJxuSsoZp6y0leVHU__'):
        """ Création de l’url sur le site de Météo-France.
        """
        assert package in ['HP1','HP2','HP3','IP1','IP2','IP3','IP4','IP5',
                           'SP1','SP2','SP3']
        url = "http://dcpc-nwp.meteo.fr/services/PS_GetCache_DCPCPreviNum\?" + \
            "token\=" + token + "\&model\=" + self.modele + "\&grid\=" + \
            self.resolution + "\&package\=" + package + "\&time\=" + time_range + \
            "\&referencetime\=" + run_time + "Z\&format\=grib2"
        return url

    def donner_date_du_run(self,delay=4):
        """ Runs are updated at 0am, 3am, 6am, 0pm, 6pm UTC.
            Note that the delay must be adjusted.
        """
        utc_now = datetime.datetime.utcnow()
        candidate = datetime.datetime(utc_now.year, utc_now.month, utc_now.day, utc_now.hour) - \
            datetime.timedelta(hours=delay)
        run_time = datetime.datetime(candidate.year, candidate.month, candidate.day)
        for hour in np.flip(np.sort([3, 6, 12, 18])):
            if candidate.hour >= hour:
                run_time += datetime.timedelta(hours=int(hour))
                break
        return run_time.strftime('%Y%m%d%H')

    def creer_nom_fichier(self,run_time, time_range='00H06H', package='SP1'):
        """Créer les noms de fichiers des gribs téléchargés"""
        dt = ''.join(run_time.split(':')[0:2]).replace('-', '').replace('T', '')
        #file_name = f'AROME_0.025_{package}_{time_range}_{dt}.grib2'
        file_name = self.modele + "_" + self.resolution + "_" + package + \
            "_" + time_range + "_" + dt + ".grib2"
        return file_name

    def telecharger_donnes_modeles(self,paquet="SP1"):#,modele,resolution):
        """Lancer la requête sur le site des données publiques M-F"""
        self.load_config()
        run_time = self.donner_date_du_dernier_run()
        print(run_time)
        time_range = self.donner_intervalle_temps(3)
        print(time_range)
        print("paquet:",paquet)

        time_ranges = []
        if self.modele == "AROME" and self.resolution == "0.025":
            for batch_number in range(7):
                time_ranges.append(self.donner_intervalle_temps(batch_number))
        elif self.modele == "AROME" and self.resolution == "0.01":
            for batch_number in range(43):
                time_ranges.append(self.donner_intervalle_temps(batch_number))
        else:
            for batch_number in range(9):
                time_ranges.append(self.donner_intervalle_temps(batch_number))
        print(time_ranges)

        files = []
        for time_range in time_ranges:
            url = self.creer_url(run_time, time_range,paquet)
            file_name = self.creer_nom_fichier(run_time, time_range,paquet)
            file_path = os.getcwd() + "/donnees/" + self.modele + \
                "_" + self.resolution + "/" + file_name
            cmd = f'wget --output-document {file_path} {url}'
            files.append({'url': url, 'file_name': file_name,
                          'file_path': file_path, 'cmd': cmd})
        print(files[0])  # let's display the first item from the list
        
        for cmd in [file['cmd'] for file in files]:
            subprocess.call(cmd, shell=True)


    # def telecharger_donnes_modeles(self):#,modele,resolution):
    #     """Lancer la requête sur le site des données publiques M-F"""
    #     run_time = self.donner_date_du_dernier_run()
    #     print(run_time)
    #     time_range = self.donner_intervalle_temps(3)
    #     print(time_range)

    #     time_ranges = []
    #     if self.modele == "AROME" and self.resolution == "0.025":
    #         for batch_number in range(7):
    #             time_ranges.append(self.donner_intervalle_temps(batch_number))
    #     elif self.modele == "AROME" and self.resolution == "0.01":
    #         for batch_number in range(43):
    #             time_ranges.append(self.donner_intervalle_temps(batch_number))
    #     else:
    #         for batch_number in range(9):
    #             time_ranges.append(self.donner_intervalle_temps(batch_number))
    #     print(time_ranges)

    #     files = []
    #     for time_range in time_ranges:
    #         url = self.creer_url(run_time, time_range)
    #         if (self.modele == "AROME" and self.resolution == "0.025"):
    #             url_sp1 = self.creer_url(run_time, time_range,"SP1")
    #             file_name_sp1 = self.creer_nom_fichier(run_time,
    #                                                    time_range,"SP1")
    #             file_path = os.getcwd() + "/donnees/" + self.modele + \
    #                 "_" + self.resolution + "/" + file_name_sp1
    #             cmd = f'wget --output-document {file_path} {url_sp1}'
    #             files.append({'url': url, 'file_name': file_name_sp1,
    #                           'file_path': file_path, 'cmd': cmd})

    #             url_ip5 = self.creer_url(run_time, time_range,"IP5")
    #             file_name_ip5 = self.creer_nom_fichier(run_time,
    #                                                    time_range,"IP5")
    #             file_path = os.getcwd() + "/donnees/" + self.modele + \
    #                 "_" + self.resolution + "/" + file_name_ip5
    #             cmd = f'wget --output-document {file_path} {url_ip5}'
    #             files.append({'url': url, 'file_name': file_name_ip5,
    #                           'file_path': file_path, 'cmd': cmd})
    #         else:
    #             url = self.creer_url(run_time, time_range,"SP1")
    #             file_name = self.creer_nom_fichier(run_time, time_range)
    #             file_path = os.getcwd() + "/donnees/" + self.modele + \
    #                 "_" + self.resolution + "/" + file_name
    #             cmd = f'wget --output-document {file_path} {url}'
    #             files.append({'url': url, 'file_name': file_name,
    #                           'file_path': file_path, 'cmd': cmd})
    #     print(files[0])  # let's display the first item from the list
        
    #     for cmd in [file['cmd'] for file in files]:
    #         subprocess.call(cmd, shell=True)