# coding: utf-8

import yaml

class YamYam():
    
    def __init__(self,field):
       self.fifi = field
 
    def yaml_loader(self,filepath):
        with open(filepath,"r") as filedescriptor:
            data = yaml.safe_load(filedescriptor)
        return(data)


    def load_config(self,key):

        filepath = "parametres_cartes.yml"
        data = self.yaml_loader(filepath)
        return(data[self.fifi][key]) 


#    def load_config(self):
#        instant = config[self.field]['instant']
        

 #       about_wind: config[self.field]['about_wind']
  #      na: config[self.field]['na']
   #     short_var: config[self.field]['short_var']
    #    anomalies_units: config[self.field]['anomalies_units']
     #   term: config[self.field]['term']
      #  nb_lats: config[self.field]['nb_lats']
       # nb_lons: config[self.field]['nb_lons']
        #nb_mb_f: config[self.field]['nb_mb_f']

