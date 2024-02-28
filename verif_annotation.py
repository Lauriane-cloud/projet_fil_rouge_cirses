
import re
import numpy as np
from change_hue import change_hue
#from annotation import move_positive_image,move_negative_image,move_cirse_et_autre_image,move_a_verifier

import os
import cv2
from pathlib import Path

import tkinter as tk
from PIL import Image, ImageTk


def charger_imagettes(chemin_dossier):
    sous_images = []
    nom_images = []
    classe = []

    cpt =0
    
    # Vérifier si le chemin est un dossier
    if os.path.isdir(chemin_dossier):
        # Parcourir tous les sous-dossiers du dossier
        for nom_sous_dossier in os.listdir(chemin_dossier):
            chemin_sous_dossier = os.path.join(chemin_dossier, nom_sous_dossier)
            cpt += 1
            
            # Charger l'image de chaque sous-dossier
            for nom_fichier in os.listdir(chemin_sous_dossier):
                # chemin_image = os.path.join(nom_sous_dossier, nom_fichier)
                chemin_image = os.path.join(chemin_sous_dossier, nom_fichier)  # lequel choisir ?

                sous_images.append(chemin_image)
                nom_images += re.findall(r'DJI_\d{4}',chemin_image)
                classe.append(cpt)

    return [sous_images, nom_images], classe

def rebuild_verif(path, image_select, sous_images,classe_list, prefix: str = ""): #from subimage_creation import SubimageCreator
    """Rebuilds the image from the subimages that were created with the cut method.
    Can optionnally add a prefix to the name of the subimages

    Args:
        prefix (str, optional): prefix that must be added before. Defaults to "".

    Returns:
        matrix_image: ndarray of the rebuilt image

    """
    # on prends la liste des images
    path_list= [x for x,image in zip(sous_images[0], sous_images[1]) if image == image_select]
    class_list= [classe for classe,image in zip(classe_list, sous_images[1]) if image == image_select]
    print(len(path_list))
    
    length_image = 3000 
    height_image = 4000 
    # Empty matrix of size (length_image,height_image,3)
    matrix_image = np.zeros(
        (length_image, height_image, 3), dtype=np.uint8)
    print(matrix_image.shape)

    # Filling the matrix with the subimages

    for file,classe in zip(path_list,class_list):
        #print(file)
        subimage = cv2.imread(file)
        subimage_name = os.path.splitext(os.path.basename(file))[0]
        xstart = int(subimage_name.split('_')[-1])
        ystart = int(subimage_name.split('_')[-2])
        xend = xstart+100
        yend = ystart+100

        # attribution des couleurs selon les classes /!\ si on prend que positif négatif chager les valeur des conditions
        if classe == 1:#cirse et autre (rose)
            subimage_colored= change_hue(subimage,160)
        elif classe ==2:#Negatif (vert)
            subimage_colored = change_hue(subimage,60)
        elif classe == 3:#Positif (rouge)
            subimage_colored = change_hue(subimage,110)
        else : #indeterminiser (bleu ?)
            #print("indeterminer")
            subimage_colored = subimage
        

        matrix_image[ystart:yend, xstart:xend] = subimage_colored

    cv2.imwrite(
        f"Images/{image_select}_{prefix}reconstruction.jpg", matrix_image)
    print(
        f"Rebuilt an image of size {matrix_image.shape} from an image of size {4000,3000} and subimages of size {100,100}")
    return matrix_image, path_list


########################################################


class Verif_classif:
    def __init__(self, master, matrice_image,image_choisi, path_list):
        self.master = master
        self.nom_image = image_choisi
        self.path_list = path_list
        self.matrice_image = matrice_image
        self.master.title("Vérification annotation image : "+self.nom_image)

        # Charger l'image
        self.original_image = Image.fromarray(self.matrice_image)
        self.photo = ImageTk.PhotoImage(self.original_image.resize((800,600),Image.LANCZOS)) #redimentioné 1/5ème
        # self.photo = ImageTk.PhotoImage(self.original_image)

        # Créer le canvas pour afficher l'image
        self.canvas = tk.Canvas(self.master, width=900, height=600)
        # self.canvas = tk.Canvas(self.master, width=self.original_image.width, height=self.original_image.height)
        self.canvas.pack()

        # Afficher l'image sur le canevas
        self.image_item = self.canvas.create_image(0, 0, anchor="nw", image=self.photo)

        # Gérer l'événement de passage de la souris
        self.canvas.bind("<Motion>", self.on_mouse_motion)
        
        # Gérer l'événement de clic gauche
        self.canvas.bind("<Button-1>", self.on_left_click)

        # Définir les zones à encadrer
        self.x1 = None
        self.y1 = None

    def on_mouse_motion(self, event):
        # Récupérer les coordonnées de la souris
        # x, y = event.x, event.y #dimension echelle 1/1
        x, y = event.x*5, event.y*5 # echelle 1/5

        x_t = x//100*100
        y_t = y//100*100


        if x_t != self.x1 or y_t != self.y1 :

            self.x1 = x_t
            self.y1 = y_t

            # Encadrer la zone spécifiée
            # x2 = self.x1 + 100
            # y2 = self.y1 + 100
            x2 = self.x1//5 + 20
            y2 = self.y1//5 + 20
            self.remove_highlight()  # Supprimer les encadrements existants
            
            self.highlight_rectangle = self.canvas.create_rectangle(self.x1//5, self.y1//5, x2, y2, outline="red", width=2)

    def remove_highlight(self):
        # Supprimer les encadrements existants
        if hasattr(self, 'highlight_rectangle'):
            self.canvas.delete(self.highlight_rectangle)
    
    def on_left_click(self, event):
        # Arret du déplacement de la souris sur la première tre
        self.canvas.unbind("<Motion>")

        # Extraire la zone de l'image correspondant sur laquelle zoomé
        cropped_image = self.original_image.crop((self.x1 - 100, self.y1 - 100, self.x1 + 200, self.y1 + 200))
        
        # Créer une nouvelle fenêtre pour le zoom avec des boutons
        zoom_window = tk.Toplevel(self.master)
        zoom_window.title("Rectification de classification")
        
        #Extraire le nom de l'imagette réévaluer
        pattern = '_{}_{}.jpg'.format(self.y1,self.x1)
        
        for element in self.path_list: # si un element est modifier une fois il faudrat relancer le script pour le remodifier car self.path_list n'est pas modifier
            if re.search(pattern,element):  
                zoom_window.path_image = element
                zoom_window.nom_imagette = element.split('\\')[-1]
                break
                
        label = tk.Label(zoom_window, text = 'Imagette : '+zoom_window.nom_imagette)
        label.pack()

        # Afficher la zone zoomée sur la nouvelle fenêtre
        zoom_window.photo = ImageTk.PhotoImage(cropped_image)
        zoomed_canvas = tk.Canvas(zoom_window, width=cropped_image.width, height=cropped_image.height)
        zoomed_canvas.pack()
        zoomed_canvas.create_image(0, 0, anchor="nw", image=zoom_window.photo)

        # Ajouter des boutons de reclassification
        button_negative = tk.Button(zoom_window, text="Negative", command = lambda: self.negative_image(zoom_window))
        button_negative.pack(side="right")

        button_positive = tk.Button(zoom_window, text="Positive", command = lambda: self.positive_image(zoom_window))
        button_positive.pack(side="left")

        button_autre = tk.Button(zoom_window, text="CirseAutre", command = lambda: self.cirse_et_autre_image(zoom_window))
        button_autre.pack(side="right")

        button_verif = tk.Button(zoom_window, text="Verifier", command = lambda: self.a_verifier(zoom_window))
        button_verif.pack(side="left")

    def negative_image(self,zoom_window):
        # Changement de couleur lié au changement de classe
        subimage = cv2.imread(zoom_window.path_image)
        self.matrice_image [self.y1:self.y1+100, self.x1:self.x1+100] = change_hue(subimage,60)
        self.original_image = Image.fromarray(self.matrice_image)
        image_modifiee = ImageTk.PhotoImage(self.original_image.resize((800,600),Image.LANCZOS))
        self.canvas.itemconfig(self.image_item, image=image_modifiee)
        self.photo = image_modifiee
        
        # Modification de l'emplacement de l'imagette
        Path(zoom_window.path_image).rename(f"C:/Users/33783/OneDrive/Documents/AgroParisTech/3eme_annee/iodaa/Fil_rouge/images/annotee_bis/Negative/{zoom_window.nom_imagette}")
        
        # Fermeture de la tre
        zoom_window.destroy()

        # Réactivation de la fonction motion
        self.canvas.bind("<Motion>", self.on_mouse_motion)
        

    def positive_image(self,zoom_window):
        # Changement de couleur lié au changement de classe
        subimage = cv2.imread(zoom_window.path_image)
        self.matrice_image [self.y1:self.y1+100, self.x1:self.x1+100] = change_hue(subimage,110)
        self.original_image = Image.fromarray(self.matrice_image)
        image_modifiee = ImageTk.PhotoImage(self.original_image.resize((800,600),Image.LANCZOS))
        self.canvas.itemconfig(self.image_item, image=image_modifiee)
        self.photo = image_modifiee

        # Modification de l'emplacement de l'imagette
        Path(zoom_window.path_image).rename(f"C:/Users/33783/OneDrive/Documents/AgroParisTech/3eme_annee/iodaa/Fil_rouge/images/annotee_bis/Positive/{zoom_window.nom_imagette}")
        
        # Fermeture de la tre
        zoom_window.destroy()

        # Réactivation de la fonction motion
        self.canvas.bind("<Motion>", self.on_mouse_motion)
        

    def cirse_et_autre_image(self,zoom_window):
        # Changement de couleur lié au changement de classe
        subimage = cv2.imread(zoom_window.path_image)
        self.matrice_image [self.y1:self.y1+100, self.x1:self.x1+100] = change_hue(subimage,160)
        self.original_image = Image.fromarray(self.matrice_image)
        image_modifiee = ImageTk.PhotoImage(self.original_image.resize((800,600),Image.LANCZOS))
        self.canvas.itemconfig(self.image_item, image=image_modifiee)
        self.photo = image_modifiee 
        
        # Modification de l'emplacement de l'imagette
        Path(zoom_window.path_image).rename(f"C:/Users/33783/OneDrive/Documents/AgroParisTech/3eme_annee/iodaa/Fil_rouge/images/annotee_bis/CirseAutre/{zoom_window.nom_imagette}")
        
        # Fermeture de la tre
        zoom_window.destroy()
        
        # Réactivation de la fonction motion
        self.canvas.bind("<Motion>", self.on_mouse_motion)
        

    def a_verifier(self,zoom_window):
        # Changement de couleur lié au changement de classe
        subimage = cv2.imread(zoom_window.path_image)
        self.matrice_image [self.y1:self.y1+100, self.x1:self.x1+100] = subimage
        self.original_image = Image.fromarray(self.matrice_image)
        image_modifiee = ImageTk.PhotoImage(self.original_image.resize((800,600),Image.LANCZOS))
        self.canvas.itemconfig(self.image_item, image=image_modifiee)
        self.photo = image_modifiee
        
        # Modification de l'emplacement de l'imagette
        Path(zoom_window.path_image).rename(f"C:/Users/33783/OneDrive/Documents/AgroParisTech/3eme_annee/iodaa/Fil_rouge/images/annotee_bis/Verifier/{zoom_window.nom_imagette}")
    
        # Fermeture de la tre
        zoom_window.destroy()

        # Réactivation de la fonction motion
        self.canvas.bind("<Motion>", self.on_mouse_motion)

def choix_image (list_images):# Choix de l'image à vérifier
    def valider():
        # Enregistrer la réponse
        selected_option_index = listbox.curselection()

        root.selected_option = listbox.get(selected_option_index[0])
        root.destroy()
        # return selected_option
        
    # Créer la fenêtre du questionnaire        
    root = tk.Tk()
    root.title("Choix de l'image à vérifier")
    label = tk.Label(root, text="Voici les images qui ont été annotée. Laquelle souhaitez-vous vérifier ?")
    label.pack(pady=10)

    # Liste des options
    var = tk.Variable(value=list_images)

    listbox = tk.Listbox(root, listvariable=var, selectmode=tk.SINGLE)
    listbox.pack()

    # Validation du choix
    button = tk.Button(root, text="Valider", command= valider)
    button.pack(pady=10)
        
    root.mainloop()

    # selected_option = button.invoke()
    # print(selected_option)
    # print('test0')
    return root.selected_option

def main():    

    #Création liste des chemins d'accès, noms et classes des imagettes
    dossier_principal = "C:/Users/33783/OneDrive/Documents/AgroParisTech/3eme_annee/iodaa/Fil_rouge/images/annotee_bis/"
    
    sous_images,classe_list = charger_imagettes(dossier_principal)
    list_images = list(set(sous_images[1]))

    # Affichage permettant de choisir l'image à vérifier
    selected_image = choix_image(list_images)
    print('test1 ')
    print(selected_image)
    
    # construction de la matrice de l'images colorée selon les classes
    image_reconstruite, path_list = rebuild_verif(dossier_principal,selected_image,sous_images,classe_list)
    
    # Créer la fenêtre principale
    root = tk.Tk()

    # Créer l'application
    app = Verif_classif(root, image_reconstruite , selected_image, path_list)

    # Démarrer la boucle principale
    root.mainloop()


# ###############################################################################
# #                              IMAGE RECONSTRUCTION                           #
# ###############################################################################


# dossier_principal = "C:/Users/33783/OneDrive/Documents/AgroParisTech/3eme_annee/iodaa/Fil_rouge/images/Annotee/"
# sous_images,classe_list = charger_imagettes(dossier_principal)
# list_images = list(set(sous_images[1]))

# print(list_images)
# # print(sous_images)
# # print(classe_list)

# image_reconstruite,path_list = rebuild_verif(dossier_principal,list_images[2],sous_images,classe_list)


# ###############################################################################
# #                              WINDOW DEFINITION                              #
# ###############################################################################

# root = tk.Tk()
# root.configure(background='white')
# root.title("Vérification annotation image : "+list_images[2])

# image_tk = Image.fromarray(image_reconstruite)
# image_redimensionnee = ImageTk.PhotoImage(image_tk.resize((800,600),Image.LANCZOS))


# root_geometry = (800, 600)
# root.geometry(f"{root_geometry[0]}x{root_geometry[1]}")
# root.resizable(0, 0)

# root.grid()

# ###############################################################################
# #                              FRAMES DEFINITION                              #
# ###############################################################################


# frame = tk.Frame(root, width=800, height=600)
# frame.pack()
# frame.place(anchor='center', relx=0.5, rely=0.5)

# label = tk.Label(frame)
# label.pack()
# label.config(image=image_redimensionnee)

# canvas = tk.Canvas(frame, width = 800, height = 600)

###############################################################################
#                                  WINDOW LOOP                                #
###############################################################################

if __name__ == '__main__' :
    main()
