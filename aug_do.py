import os
import cv2


# Définir le répertoire contenant les images
input_directory_p = "../photo_cirses/Cirses.v1i.folder/Positive"
#input_directory_n = "../Cirses.v1i.folder/Negative"
output_directory = "../photo_cirses/Cirses.v1i.folder/output"

# Assurez-vous que le répertoire de sortie existe, sinon le créer
if not os.path.exists(output_directory):
    os.makedirs(output_directory)

# Liste les fichiers dans le répertoire d'entrée
image_files = os.listdir(input_directory_p)

# Parcours des fichiers et augmentation des données
for filename in image_files:
    if filename.endswith(".jpg") or filename.endswith(".jpeg"):
        # Charger l'image
        image = cv2.imread(os.path.join(input_directory_p, filename))
        
    # Effectuer les 3 rotations
    
        rotated_image = cv2.rotate(image, cv2.ROTATE_90_CLOCKWISE)
        output_name = f"{os.path.splitext(filename)[0]}_rotated_90.jpg"
        cv2.imwrite(os.path.join(output_directory, output_name), rotated_image)

        # Effet miroir
        mirrored_image = cv2.flip(rotated_image, 1)
        output_name = f"{os.path.splitext(filename)[0]}_rotated_90_mirrored.jpg"
        cv2.imwrite(os.path.join(output_directory, output_name), mirrored_image)

        rotated_image = cv2.rotate(image, cv2.ROTATE_180)
        output_name = f"{os.path.splitext(filename)[0]}_rotated_180.jpg"
        cv2.imwrite(os.path.join(output_directory, output_name), rotated_image)

        # Effet miroir
        mirrored_image = cv2.flip(rotated_image, 1)
        output_name = f"{os.path.splitext(filename)[0]}_rotated_180_mirrored.jpg"
        cv2.imwrite(os.path.join(output_directory, output_name), mirrored_image)

        rotated_image = cv2.rotate(image, cv2.ROTATE_90_COUNTERCLOCKWISE)
        output_name = f"{os.path.splitext(filename)[0]}_rotated_270.jpg"
        cv2.imwrite(os.path.join(output_directory, output_name), rotated_image)

        # Effet miroir
        mirrored_image = cv2.flip(rotated_image, 1)
        output_name = f"{os.path.splitext(filename)[0]}_rotated_270_mirrored.jpg"
        cv2.imwrite(os.path.join(output_directory, output_name), mirrored_image)
        
        # Effet miroir
        mirrored_image = cv2.flip(image, 1)
        output_name = f"{os.path.splitext(filename)[0]}_mirrored.jpg"
        cv2.imwrite(os.path.join(output_directory, output_name), mirrored_image)

print("Augmentation des données terminée.")