
import argparse 
from dataLoader.dataLoader import data_loader
from preprocessing.preprocessor import image_resizer
from imutils import paths
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split
from sklearn.neighbors import KNeighborsClassifier
from sklearn.metrics import classification_report



ap=argparse.ArgumentParser()

ap.add_argument("-d","--dataset",required=True,help="dataset")
ap.add_argument("-k","--neighbor",default=1,type=int,help="neighbor")
ap.add_argument("-j","--jobs",default=-1,type=int,help="jobs")
args=vars(ap.parse_args())

proc=image_resizer(32,32)
pathOfImagees=list(paths.list_images(args["dataset"]))
dl=data_loader([proc])
(data,label)=dl.dataLoader(pathOfImagees)
data=data.reshape(data.shape[0],3072)



print("[INFO] evaluating k-NN classifier...")
le=LabelEncoder()
label=le.fit_transform(label)
model=KNeighborsClassifier(n_neighbors=args["neighbor"],n_jobs=args["jobs"])
(X_train,X_test,Y_train,Y_test)=train_test_split(data,label,test_size=0.25,random_state=42)
model.fit(X_train,Y_train)
print(classification_report(Y_test,model.predict(X_test),target_names=le.classes_))