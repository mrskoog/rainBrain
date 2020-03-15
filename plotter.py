import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.neighbors import KNeighborsClassifier
from sklearn import metrics
from sklearn.linear_model import LogisticRegression

from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
from mpl_toolkits import mplot3d

ALTITUDE_OF_SENSOR = 103

def dump_c_data(pressure,pressure1, delta, rain):
    with open("dataset.h", "w") as f:
        test = len(pressure)
        f.write("#define SIZE_DATASET "+str(test)+"\n")
        f.write("const float dataset[SIZE_DATASET][3] = { \n")
        for i in range(0, len(pressure)-1):
            f.write("{ "+ str(pressure[i]) +", "+ str(pressure1[i]) +", " +  str(delta[i]) + "},\n")
        f.write("{ "+ str(pressure[i]) +", "+ str(pressure1[i]) +", " + str(delta[i]) + "}\n")
        f.write("};\n")

        f.write("const byte data_tag[SIZE_DATASET] = { \n")
        for i in range(0, len(pressure)-1):
            f.write(str(int(rain[i]))+",\n")
        f.write(str(int(rain[i]))+"};\n")

data = pd.read_csv('weather_data.csv', names = ['rain','temp','pressure','date'])

time_shifted_p = np.array(data.pressure[0:-2])
time_shifted_p = time_shifted_p / pow(1.0 - ALTITUDE_OF_SENSOR/44330.0, 5.255) #make pressure sealevel
time_shifted_p1 = time_shifted_p[2:]
time_shifted_p = time_shifted_p[:-2]

time_shifted_r = np.array(data.rain[2:-2])

plt.plot(range(len(time_shifted_p)), time_shifted_p, range(len(time_shifted_r)), (time_shifted_r*1000) + 98000)

delta = np.diff(time_shifted_p) / 2
delta = np.insert(delta,0,0)

data2 = {'pressure' :  time_shifted_p,'pressure1' :  time_shifted_p1, 'delta' : delta }

X = pd.DataFrame(data2)

print(X)

fig = plt.figure("scatter, delta")
ax = fig.add_subplot(111, projection='3d')
sc = plt.scatter(X.pressure,X.pressure1, X.delta ,c = time_shifted_r)
plt.colorbar(sc)

y = time_shifted_r

dump_c_data(time_shifted_p, time_shifted_p1, delta, time_shifted_r)

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=0)

print(y_train.shape)
print(y_test.shape)

neighbors = np.arange(1, 25)
train_accuracy = np.empty(len(neighbors))
test_accuracy = np.empty(len(neighbors))

# Loop over K values
for i, k in enumerate(neighbors):
    knn = KNeighborsClassifier(n_neighbors=k, metric='euclidean')
    knn.fit(X_train, y_train)

    # Compute traning and test data accuracy
    train_accuracy[i] = knn.score(X_train, y_train)
    test_accuracy[i] = knn.score(X_test, y_test)

plt.figure("knn")
# Generate plot
plt.plot(neighbors, test_accuracy, label = 'Testing dataset Accuracy')
plt.plot(neighbors, train_accuracy, label = 'Training dataset Accuracy')

plt.legend()
plt.xlabel('n_neighbors')
plt.ylabel('Accuracy')

LogisticRegression
reg = LogisticRegression(solver='sag', max_iter=100)
reg.fit(X_train, y_train)
train_accuracy = reg.score(X_train, y_train)
test_accuracy = reg.score(X_test, y_test)
print("LR train_accuracy",train_accuracy)
print("LR test_accuracy",test_accuracy)

# Random Forest classifier
RF = RandomForestClassifier(n_estimators=100, random_state=0)
RF.fit(X_train, y_train)
train_accuracy = RF.score(X_train, y_train)
test_accuracy = RF.score(X_test, y_test)
print("RF train_accuracy",train_accuracy)
print("RF test_accuracy",test_accuracy)

knn = KNeighborsClassifier(n_neighbors=13, metric='euclidean',algorithm='brute')
knn.fit(X_train, y_train)

plt.figure("knn ROC curve")
y_pred_proba = knn.predict_proba(X_test)[::,1]
fpr, tpr, _ = metrics.roc_curve(y_test,  y_pred_proba)
auc = metrics.roc_auc_score(y_test, y_pred_proba)
plt.plot(fpr,tpr,label="data 1, auc="+str(auc))
plt.legend(loc=4)


plt.show()
