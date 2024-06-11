import pandas as pd 
import csv 
from ydata_profiling import ProfileReport
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import KBinsDiscretizer
from scorecardbundle.feature_discretization import ChiMerge as cm
from sklearn.preprocessing import LabelEncoder
from sklearn.preprocessing import PowerTransformer
import matplotlib.pyplot as plt
from sklearn.preprocessing import MinMaxScaler,StandardScaler,RobustScaler

raw_data=pd.read_csv('smoker.csv')
# report=ProfileReport(raw_data)
# report.to_file('smokerRep.html')

raw_data.drop_duplicates(inplace=True)

allCol=raw_data.columns

inputs=raw_data.iloc[:,:-1]
outputs=raw_data.iloc[:,-1]
in_col=inputs.columns
cat_col_indx=[1,3,4]

cat_col=[in_col[x] for x in cat_col_indx]
num_col=[x for x in in_col if x not in cat_col]

print(num_col)






step_one_inpts=inputs.copy()
for Num in num_col:
    calc_cv=step_one_inpts[Num].std()/step_one_inpts[Num].mean()
    if calc_cv<0.1:
        step_one_inpts.drop(Num,inplace=True)
    


varity=step_one_inpts[cat_col].dropna().nunique()
variety_indx=varity[varity[cat_col]>0.9].index
step_one_inpts.drop(variety_indx,axis=1)        

bias=step_one_inpts[cat_col].apply(lambda x: x.value_counts().max()/len(raw_data[cat_col]))
biased_indx=bias[bias>0.95].index
step_one_inpts.drop(biased_indx,axis=1)


#*************************************
def frequency_table(var):
    
    val,count=np.unique(var,return_counts=True)
    percent=count/len(var)
    df_rep=pd.DataFrame((val,count,percent),index=['values','counts','percent'])
    return df_rep
#*************************************

print(frequency_table(step_one_inpts['sex']))
    
normal_ranges={'age':(18,64),'bmi':(15,54),'children':(0,5),'charges':(1121,63800)}

for i,(j,k) in normal_ranges.items():
    raw_data[i]=raw_data[i].apply(lambda x: x if x<k and x>j else None)
    



x_train,x_test,y_train,y_test=train_test_split(inputs,outputs,test_size=0.3,random_state=42)

step_two_inputs=x_train
step_two_outputs=y_train

# for  p in in_col:
    
#     step_two_inputs['missing']=step_two_inputs[p].isnull().sum()

missing_series=step_two_inputs[in_col].apply(lambda x: x.isnull().sum())


median_needed_list=['charges']
mean_needed_list=['age','bmi']

for u in mean_needed_list:

    globals()[f"upper_of_{u}_outlier_mean"]=step_two_inputs[u].mean()+3*step_two_inputs[u].std()
    globals()[f"lower_of_{u}_outlier_mean"]=step_two_inputs[u].mean()-3*step_two_inputs[u].std()
    outliers_By_mean=step_two_inputs[u].apply(lambda x: x if (x>globals()[f"upper_of_{u}_outlier_mean"] or
                                                                  x<globals()[f"lower_of_{u}_outlier_mean"])else None)
    
    
    
    step_two_inputs[u]=step_two_inputs[u].apply(lambda  x: x if  x < globals()[f"upper_of_{u}_outlier_mean"] and 
                                                 x> globals()[f"lower_of_{u}_outlier_mean"] else
                                                 globals()[f"upper_of_{u}_outlier_mean"]
                                                 if x>globals()[f"upper_of_{u}_outlier_mean"] else
                                                 globals()[f"lower_of_{u}_outlier_mean"])
    
    
for u in median_needed_list:
    iqr=step_two_inputs[u].quantile(0.75)-step_two_inputs[u].quantile(0.25)
    upper_bound=step_two_inputs[u].quantile(0.75)+2*iqr
    lower_bound=step_two_inputs[u].quantile(0.25)-2*iqr
    globals()[f"upper_of_{u}_outlier_sigma"]=upper_bound
    globals()[f"lower_of_{u}_outlier_sigma"]=lower_bound
    
    outliers_By_sigma=[x for x in step_two_inputs[u] if (x>upper_bound or x<lower_bound )]
    
    print(len(outliers_By_sigma))
    step_two_inputs[u]=step_two_inputs[u].apply(lambda x:globals()[f"upper_of_{u}_outlier_sigma"] if x>globals()[f"upper_of_{u}_outlier_sigma"]
                                                else globals()[f"lower_of_{u}_outlier_sigma"] if x< globals()[f"lower_of_{u}_outlier_sigma"] else x )

    
for coll in in_col:
    step_two_inputs['nullRecCount']=step_two_inputs.isnull().sum(axis=1)
    missedRec=(step_two_inputs[step_two_inputs['nullRecCount']>=3]).index
    step_two_inputs.drop(missedRec)
    step_two_outputs.drop(missedRec)
    
print(step_two_inputs)


for coll in in_col:
    print(step_two_inputs[coll].isnull().sum())

lastFile=(pd.concat((step_two_inputs,step_two_outputs),axis=1)).to_csv('resultStepTwo.csv')






#discritization:

raw_data2=pd.read_csv('resultStepTwo.csv')
le=LabelEncoder()
label_neede=['smoker','sex','region']
for i in label_neede:
    raw_data2[i]=le.fit_transform(raw_data2[i])
raw_data2.drop(columns=raw_data2.columns[[0,7]],axis=1,inplace=True)
print(raw_data2)

step_three_inputs=raw_data2.copy().iloc[:,:-1]
step_three_outputs=raw_data2.copy().iloc[:,-1]
#kammi ha vahed nadashte bashand
for u in num_col:
    mean_of_nums=step_three_inputs[u].mean()
    step_three_inputs[u]=step_three_inputs[u].apply(lambda x:x/mean_of_nums)



#charges:boxcox      age :discritization by chimerge
chimerge_dicritizer=cm.ChiMerge(max_intervals=5,min_intervals=2,output_dataframe=True)

discsOfAge=chimerge_dicritizer.fit_transform(step_three_inputs[['age']],step_three_outputs.astype(int))


temp_dict=np.insert(chimerge_dicritizer.boundaries_['age'],[0,len(chimerge_dicritizer.boundaries_['age'])]
                                                 ,[step_three_inputs['age'].min(),step_three_inputs['age'].max()+1])
temp_dict=np.delete(temp_dict,-2)
chimerge_dicritizer.boundaries_['age']=temp_dict



step_three_inputs['age_disc']=pd.cut(step_three_inputs['age'],bins=temp_dict,right=False,labels=[1,2,3,4,5])
step_three_inputs=step_three_inputs.drop(columns='age')
print(step_three_inputs)



# charges: normal nist + hast yani  - ndare pas boxCox

method_ofNomalization=PowerTransformer(method='box-cox',standardize=False)
step_three_inputs['charges_normaled']=method_ofNomalization.fit_transform(step_three_inputs[['charges']])
#print(method_ofNomalization.lambdas_)
step_three_inputs.drop(columns='charges')

plt.subplot(1,2,1)
plt.hist(step_three_inputs['charges_normaled'])
plt.subplot(1,2,2)
plt.hist(step_two_inputs['charges'])
plt.show()



step_three_inputs['age_disc']=step_three_inputs['age_disc'].astype(int)
print(step_three_inputs.info())

col_Scaling=step_three_inputs.columns
scaling_method=['min_max']
for y in col_Scaling:
    scaler=MinMaxScaler()
    step_three_inputs[y]=scaler.fit_transform(step_three_inputs[[y]])


lastData=pd.concat((step_three_inputs,step_three_outputs),axis=1)
lastData.to_csv('Lastsmoker.csv')