import cv2

class image_resizer():
    
    def __init__(self,width,height,inter=cv2.INTER_AREA):
        self.width=width
        self.height=height
        self.inter=inter
    def prepro(self,img):
        return cv2.resize(img,(self.width,self.height),interpolation=self.inter)