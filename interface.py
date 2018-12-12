#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import cv
import json
import os
import sys
from PySide.QtCore import *
from PySide.QtGui import *

class Bouton(QPushButton):
    """Classe utilisée pour changer le pointeur
    quand on passe la souris sur un bouton"""
    def __init__(self, texte, parent=None):
        super(Bouton, self).__init__(texte, parent)
        self.setCursor(Qt.PointingHandCursor)
        
class Fenetre(QWidget):
    def __init__(self, parent=None):
        super(Fenetre, self).__init__(parent)
        
        # Création des éléments
        self.setWindowTitle("Thira")
        self.liste_modules = QComboBox() # liste déroulante
        self.recharger_modules = Bouton("Recharger les modules")
        self.description = QLabel()
        self.action = Bouton("Action !")
        
        # Placement des éléments
        layout = QGridLayout()
        layout.addWidget(self.liste_modules, 0, 0)
        layout.addWidget(self.recharger_modules, 0, 1)
        layout.addWidget(self.description, 1, 0, 1, 2)
        layout.addWidget(self.action, 2, 0, 1, 2)
        self.setLayout(layout)
        
        # Création des slots
        self.liste_modules.currentIndexChanged.connect(self.changer_module)
        self.recharger_modules.clicked.connect(self.charger_modules)
        self.action.clicked.connect(self.reconnaitre)
       
        # Autoriser le passage à la ligne dans la description
        # Sinon elle est en une ligne et on ne peut pas réduire la taille
        self.description.setWordWrap(True)
        
        # On charge les modules disponibles à la création de la fenêtre
        self.charger_modules()

    def reconnaitre(self):
        "Utilisée lorsqu'on demande à reconnaître le visage pris en photo"
        commande = self.modules[self.liste_modules.currentIndex()]["commande"]
        # La commande est sous la forme :
        # nom_du_programme_a_executer {0}
        # on a "c{0}d".format("bla") == "cblad"        
        
        # Le moteur répond sur la sortie standard
        # Actuellement on se contente de le laisser l'afficher,
        # on pourrait le rediriger vers une variable pour l'exploiter
        # par exemple en l'affichant dans une fenêtre
        os.system(commande.format("visage.bmp"))
        

    def changer_module(self, texte):
        """Lorsqu'on change de module à l'aide de la liste déroulante,
        on actualise l'affichage de la description"""
        self.description.setText(
            self.modules[self.liste_modules.currentIndex()]["description"])
        
    def charger_modules(self):
        """Pour recharger la liste des modules si on a modifié le fichier
        modules.js qui contient leur description sous format json"""
        self.liste_modules.clear()
        self.modules = json.loads(open("modules.js").read())
        for module in self.modules:
            self.liste_modules.addItem(module["nom"])
            
if __name__ == "__main__":
    # Ce code ne s'exécute que si on exécute directement le module (pas en cas d'import)
    webcam = cv.CaptureFromCAM(0)
    print "Appuyez sur S pour prendre la photo"
    while True:
        image = cv.GetSubRect(cv.QueryFrame(webcam), (281, 191, 80, 100))
        cv.ShowImage("webcam", image)
        key = cv.WaitKey(1)
        # La touche pour prendre la photo est la touche s
        # Sous le linux utilisé pour tester, la valeur correspondante
        # était 1048691.
        # Sous Windows, la valeur était ord("s"), soit 115.
        # Sous certaines machine, cette valeur peut être "s".
        if key in [1048691, ord("s"), "s"]:
            cv.SaveImage("visage.bmp", image)
            break
    # thira = THIbault RAlph
    # sys.argv = les arguments de la commande exécutée, 
    # par exemple ["interface.py", "-o3", "visage.bmp"]
    # Inutile pour nous mais demandé dans le constructeur de QApplication
    thira = QApplication(sys.argv)
    fenetre = Fenetre()
    fenetre.show()
    sys.exit(thira.exec_())
