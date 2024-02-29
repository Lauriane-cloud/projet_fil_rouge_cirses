import random
import os
from PIL import Image

# Fonction pour ajouter du bruit à une valeur
def add_noise(value, noise_factor=0.05):
    noise = random.uniform(-value * noise_factor, value * noise_factor)
    return value + noise


def add_noise_file(file_path,filename,nb_augmentation = 3):
    with open(os.path.join(file_path,filename), 'r') as file:
        lines = file.readlines()

    # Analyser les données pour les stocker dans une structure de liste ou tableau bidimensionnel
    data = [list(map(float, line.split())) for line in lines]

    # Ajouter des lignes avec du bruit
    #with open(f"{file_path}augmenter/{os.path.splitext(filename)[0]}_augmenter.txt", 'w') as file:
    with open(f"{os.path.join(file_path,os.path.splitext(filename)[0])}_augmenter.txt", 'w') as file:
        for line in data:
            for i in range (nb_augmentation) :
                new_line = [add_noise(value) if i!=0 else int(value) for i,value in enumerate(line)]
                file.write(' '.join(map(str, new_line)) + '\n')



# augmentation de données des tous les fichiers
chemin_dossier = "C:/Users/33783/OneDrive/Documents/AgroParisTech/3eme_annee/iodaa/Fil_rouge/image_bb/"

for nom_sous_dossier in os.listdir(chemin_dossier):
    chemin_sous_dossier = os.path.join(chemin_dossier, nom_sous_dossier)
    if os.path.isdir(chemin_sous_dossier):
        chemin_sous_dossier_label = f"{chemin_sous_dossier}/labels/"
        chemin_sous_dossier_images = f"{chemin_sous_dossier}/images/"
        
        # # Création des sous dossier augmenter
        # if not os.path.exists(f'{chemin_sous_dossier_label}augmenter/'):
        #         os.makedirs(f'{chemin_sous_dossier_label}augmenter/')
        # if not os.path.exists(f'{chemin_sous_dossier_images}augmenter/'):
        #         os.makedirs(f'{chemin_sous_dossier_images}augmenter/')


        # fichier txt à augmenter
        for filename in os.listdir(chemin_sous_dossier_label):
            if filename.endswith(".txt"):
                #print(filename)
                add_noise_file(chemin_sous_dossier_label,filename)

                # Dupliquer l'image
    
                original_image = Image.open(f'{os.path.join(chemin_sous_dossier_images,os.path.splitext(filename)[0])}.jpg')
                duplicated_image = original_image.copy()

                # Enregistrer l'image dupliquée avec le même nom de fichier, mais un nouveau chemin d'extension
                # duplicated_image.save(f'{chemin_sous_dossier_images}augmenter/{os.path.splitext(filename)[0]}_augmenter.jpg')
                duplicated_image.save(f'{os.path.join(chemin_sous_dossier_images,os.path.splitext(filename)[0])}_augmenter.jpg')



print("fin d'augmentation des données")