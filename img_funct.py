from PIL import Image


class img_class():
    @staticmethod
    def save_img(img, path):
        """Function to save img in delivered path"""
        pil_img = Image.fromarray(img)
        pil_img.save(path)
