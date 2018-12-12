#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import cv
import math
import numbers
import numpy as np
import os
import sys
import time


def list_de_iplimage(image):
    "Renvoie la forme liste d'une image OpenCV"
    return [[cv.Get2D(image, i, j)[0] for j in xrange(image.width)]
             for i in xrange(image.height)]


class Tableau:
    def __add__(self, autre):
        "Additionne avec un Tableau ou un scalaire"
        if isinstance(autre, Tableau):
            return Tableau(self.tab + autre.tab)
        elif isinstance(autre, numbers.Number):
            return Tableau(self.tab + autre)
        else:
            raise TypeError("Tableau.__add__ : Tableau ou scalaire attendu")

    def __div__(self, autre):
        "Divise par un scalaire"
        return Tableau(self.tab / autre)

    def __getitem__(self, index):
        "Renvoie un coefficient du Tableau, pour pouvoir utiliser tableau[index]"
        if isinstance(index, int) and self.largeur != 1:
            return Tableau(self.tab[index])
        else:
            return self.tab[index]

    def __init__(self, source, nom=str(time.time())):
        """Constructeur d'un objet Tableau
        On peut lui passer:
        * une chaîne de caractère, qui sera le chemin de l'image à charger en Tableau
        * une image au format OpenCV à passer en Tableau
        * un array numpy à passer en Tableau
        """
        if isinstance(source, str):
            self.tab = np.array(list_de_iplimage(cv.LoadImage(source, cv.CV_LOAD_IMAGE_GRAYSCALE)))
        elif isinstance(source, cv.iplimage):
            self.tab = nb.array(list_de_iplimage(source))
        elif isinstance(source, (np.ndarray, list)):
            self.tab = np.array(source)
        else:
            raise TypeError("Tableau.__init__ : %s inattendu" % type(source))
        self.nom = nom
        self.calc_dimensions()

    def __len__(self):
        "Pour pouvoir utiliser len(tableau) au cas où"
        return len(self.tab)

    def __mul__(self, autre, element_par_element=False):
        """Multiplie : multiplication de matrice, ou par un scalaire
        Le flag element_par_element indique, s'il est vrai, qu'on n'utilise pas
        la multiplication de l'algèbre des matrices, mais une multiplication
        élément par élément de deux matrices de mêmes dimensions"""
        if isinstance(autre, Tableau):
            if element_par_element:
                return Tableau(self.tab * autre.tab)
            else:
                resultat = np.dot(self.tab, autre.tab)
                if isinstance(resultat, numbers.Number):
                    return resultat
                else:
                    return Tableau(resultat)
        elif isinstance(autre, numbers.Number):
            return Tableau(self * autre)
        else:
            raise TypeError("Tableau.__mul__ : Tableau ou scalaire attendu")

            
    def __setitem__(self, index, valeur):
        """Modifie un coefficient du Tableau :
        implémente tableau[index] = valeur"""
        self.tab[index] = valeur

    def __sub__(self, autre):
        "Additionne avec un Tableau ou un scalaire"
        if isinstance(autre, Tableau):
            return Tableau(self.tab - autre.tab)
        elif isinstance(autre, numbers.Number):
            return Tableau(self.tab - autre)
        else:
            raise TypeError("Tableau.__sub__ : Tableau ou scalaire attendu")


    def afficher(self, nom=None):
        """Affiche le Tableau, comme une image, dans une fenêtre
        Utilise OpenCV pour cela"""
        if nom is None:
            nom = self.nom
        cv.ShowImage(nom, self.vers_iplimage())
        

    def calc_dimensions(self):
        "Calcule les dimensions du Tableau"
        self.hauteur = len(self.tab)
        try:
            self.largeur = len(self.tab[0])
        except TypeError:
            self.largeur = 1

    def calc_elements_propres(self):
        "Calcule valeurs propres et vecteurs propres du tableau"
        valeurs, vecteurs = np.linalg.eig(self.tab)
        self.val_propres = list(valeurs)
        self.vect_propres = [Tableau(vect) for vect in vecteurs]
        
    def covariance(self):
        "Renvoie le Tableau de covariance du Tableau"
        return self * self.transposee()
    
    def dimensions(self):
        "Renvoie les dimensions - hauteur * largeur - du tableau"
        return self.hauteur, self.largeur

    def en_colonne(self):
        "Renvoie le Tableau comme un vecteur colonne"
        return self.redimensionnee(-1)

    def inverse(self):
        "Renvoie l'inverse du Tableau dans l'agèbre des matrices"
        return Tableau(np.linalg.inv(self.tab))

    def mahalanobis(self, autre, cov):
        "Calcule la distance de Mahalanobis entre deux Tableaux"
        a = (self - autre) * cov.inverse() * (self - autre)
        return math.sqrt(a)

    def mettre_en_colonne(self):
        "Met le Tableau en forme de vecteur colonne"
        self.redimensionner(-1)
    
    def redimensionnee(self, nouvelle_forme):
        """Renvoie le Tableau sous une nouvelle forme
        Le nombre total d'éléments doit rester le même"""
        tab = Tableau(np.reshape(self.tab, nouvelle_forme))
        tab.calc_dimensions()
        return tab

    def redimensionner(self, nouvelle_forme):
        """Change la forme du Tableau
        Le nombre total d'éléments reste le même"""
        self.tab = np.reshape(self.tab, nouvelle_forme)
        self.calc_dimensions()


    def transposee(self):
        "Renvoie la transposée du Tableau"
        return Tableau(np.transpose(self.tab))
    
    def transposer(self):
        "Transpose le Tableau"
        self.tab  = np.transpose(self.tab)

    def vers_iplimage(self, profondeur=cv.IPL_DEPTH_8U):
        "Renvoie l'iplimage équivalente (format OpenCV)"
        temp = cv.CreateImage((self.largeur, self.hauteur),
                              cv.IPL_DEPTH_64F, 1)
        for (i, ligne) in enumerate(self.tab):
            for (j, valeur) in enumerate(ligne):
                cv.Set2D(temp, i, j, valeur)
        img = cv.CreateImage((self.largeur, self.hauteur), profondeur, 1)
        cv.Convert(temp, img)
        return img

    


class Collection:
    def __init__(self, chemin="faces/"):
        "Constructeur d'un objet Collection"
        self.liste_faces = [Tableau(chemin + fichier)
                            for fichier in os.listdir(chemin)]
        self.nb_faces = len(self.liste_faces)
        # On prépare la Collection pour la reconnaissance"
        self.calc_moyenne()
        self.calc_ecarts()
        self.calc_covariance()
        self.calc_faces_propres()
        self.calc_coeff_faces()

    def calc_covariance(self):
        "Calcule la covariance des faces normalisées de la Collection"
        self.covariance = self.ecarts.transposee().covariance()
        
    def calc_moyenne(self):
        "Calcule la moyenne des faces de la Collection"
        self.moyenne = reduce(Tableau.__add__, self.liste_faces) / self.nb_faces


    def calc_coeff_faces(self):
        """Calcule les coefficients des faces de la collection,
        dans la base des faces propres"""
        self.coeff_faces = Tableau([self.coeff(face)
                            for face in self.ecarts.transposee()])
        self.covar_coeff = self.coeff_faces.transposee().covariance()
        
    def calc_ecarts(self):
        "Calcule le Tableau des écarts à la moyenne"
        self.ecarts = Tableau([(face - self.moyenne).en_colonne().tab
                               for face in self.liste_faces]).transposee()

    def calc_faces_propres(self):
        "Calcule les faces propres de la collection"
        self.covariance.calc_elements_propres()
        self.faces_propres = [self.ecarts * vect
                              for vect in self.covariance.vect_propres]
        #Pour un affichage, redimensionner en (100, 80)

    def coeff(self, tableau):
        "Renvoie les coefficients d'un tableau sur la base des faces propres"
        return [face * tableau.en_colonne() for face in self.faces_propres]


    def reconnaitre(self, image):
        """Reconnait ou non une image.
        Sauvegarde la face connue la plus proche dans le fichier resultat.bmp,
        et renvoie la distance entre le visage à reconnaître et cette face"""
        coeff = Tableau(self.coeff(image - self.moyenne))
        distances = [coeff.mahalanobis(coeff_face, self.covar_coeff)
                     for coeff_face in self.coeff_faces]
        distance_min = min(distances)
        i = distances.index(distance_min)
        cv.SaveImage("resultat.bmp", self.liste_faces[i].vers_iplimage())
        return distance_min
        
if __name__ == "__main__":
    collection = Collection()
    # On passe en argument le visage à reconnaître
    visage = Tableau(sys.argv[1])
    # On utilise la méthode reconnaissance et on affiche le résultat en sortie standard
    # L'interface s'occupe du reste
    print collection.reconnaitre(visage)
