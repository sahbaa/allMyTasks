import cv2
from imutils import paths
import os
import numpy as np
import preprocessing.preprocessor 

class data_loader():
    
    def __init__(self,mypreprocessor=None):
        
        self.mypreprocessor=mypreprocessor
        if self.mypreprocessor is None:
            self.mypreprocessor=[]
        
        
    def dataLoader(self,imgpthlist):
        
        data=[]
        labels=[]
        cnt=1
        for i,imagePath in enumerate(imgpthlist):
            
            image=cv2.imread(imagePath)
            label=imagePath.split(os.path.sep)[-2]
            if self.mypreprocessor is not None:
                for p in self.mypreprocessor:
                    image=p.resizer(image)
            
                print("{}/{} of images have been loaded please Wait...".format(i,len(imgpthlist)))    
            data.append(image)
            labels.append(label)
            cnt+=1
        return np.array(data),np.array(labels)
        