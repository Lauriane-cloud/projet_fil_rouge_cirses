import os
import cv2
import numpy as np


class SubimageCreator:
    """Class that governs the creation of subimages from an image of a field

    Args: 
    image_path (str): path to the image
    size (tuple): size of the subimage
    """

    def __init__(self, image_path: str, size: tuple = (100, 100)):
        """Initializes a SubimageCreator object

        Args:
            image_path (str): path to the image that you want to create subimages from
            size (tuple, optional): Size of the subimages. Defaults to (100, 100).
        """
        image = cv2.imread(image_path)
        self.original_image_size = image.shape
        self.image_path = image_path
        self.output_dir = "C:/Users/Lauriane/Documents/Scolaire/IODAA/IODAA/fil_rouge/PFR_Cirses_2022/Images/Subimages"
        self.size = size
        self.image_name = os.path.splitext(os.path.basename(image_path))[0]
        self.subimages = []

    def cut(self):
        """Method that cuts the image into subimages"""
        # loading the image

        image = cv2.imread(self.image_path)

        # getting the name of the image without the extension

        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)

        # We iterate over the rows and columns the image and for each self.size pixel we create a subimage

        for i in range(0, image.shape[0], self.size[0]):
            for j in range(0, image.shape[1], self.size[1]):
                # we extract the subimage
                subimage = image[i:i+self.size[0], j:j+self.size[1]]
                # if the subimage is smaller than the size, we pad it with zeros
                if subimage.shape[0] < image.shape[0] or subimage.shape[1] < image.shape[1]:
                    subimage = cv2.copyMakeBorder(
                        subimage, 0, self.size[0]-subimage.shape[0], 0, self.size[1]-subimage.shape[1], cv2.BORDER_CONSTANT, value=0)
                # We generate the name of the subimage, adding the coordinates of the subimage in the image
                subimage_name = f"{self.image_name}_{i}_{j}.jpg"
                self.subimages.append(subimage_name)

                # Saving the subimage
                cv2.imwrite(os.path.join(
                    self.output_dir, subimage_name), subimage)

    def rebuild(self, prefix: str = ""):
        """Rebuilds the image from the subimages that were created with the cut method.
        Can optionnally add a prefix to the name of the subimages

        Args:
            prefix (str, optional): prefix that must be added before. Defaults to "".

        Returns:
            matrix_image: ndarray of the rebuilt image

        """
        # on prends la liste des images
        path_list = self.subimages
        path_list = [prefix+x for x in path_list]
        print(len(path_list))
        # getting the dimensions of the image to be rebuilt (can be different
        # from the original image's because of the padding)
        number_of_subimage_x = int(self.original_image_size[0]/self.size[0]) if self.original_image_size[0] % self.size[0] == 0 else int(
            self.original_image_size[0]/self.size[0])+1
        number_of_subimage_y = int(self.original_image_size[1]/self.size[1]) if self.original_image_size[1] % self.size[1] == 0 else int(
            self.original_image_size[1]/self.size[1])+1
        length_image = number_of_subimage_x*(self.size[0])
        height_image = number_of_subimage_y*(self.size[1])
        # Empty matrix of size (length_image,height_image,3)
        matrix_image = np.zeros(
            (length_image, height_image, 3), dtype=np.uint8)
        print(matrix_image.shape)

        # Filling the matrix with the subimages

        for file in path_list:
            subimage = cv2.imread(self.output_dir+"/"+file)
            subimage_name = os.path.splitext(os.path.basename(file))[0]
            xstart = int(subimage_name.split('_')[-1])
            ystart = int(subimage_name.split('_')[-2])
            xend = xstart+self.size[0]
            yend = ystart+self.size[1]
            matrix_image[ystart:yend, xstart:xend] = subimage
        cv2.imwrite(
            f"Images/{self.image_name}_{prefix}reconstruction.jpg", matrix_image)
        print(
            f"Rebuilt an image of size {matrix_image.shape} from an image of size {self.original_image_size} and subimages of size {self.size}")
        return matrix_image


if __name__ == "__main__":
    image_path = "C:/Users/Lauriane/Documents/Scolaire/IODAA/IODAA/fil_rouge/PFR_Cirses_2022/Images/Subimages/DJI_0181.JPG"  # to be adapted to your path and image name
    sushi = SubimageCreator(image_path, size=(100, 100))
    sushi.cut()
    sushi.rebuild()