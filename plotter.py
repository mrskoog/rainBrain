import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.neighbors import KNeighborsClassifier
from sklearn.linear_model import LogisticRegression

from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler

def moving_average(data_set, periods=3):
    weights = np.ones(periods) / periods
    return np.convolve(data_set, weights, mode='valid')

def dump_c_data(pressure, delta, rain):
    with open("dataset.h", "w") as f:
        test = len(pressure)
        f.write("#define SIZE_DATASET "+str(test)+"\n")
        f.write("const float dataset[SIZE_DATASET][2] = { \n")
        for i in range(0, len(pressure)-1):
            f.write("{ "+ str(pressure[i]) +", " + str(delta[i]) + "},\n")
        f.write("{ "+ str(pressure[i]) +", " + str(delta[i]) + "}\n")
        f.write("};\n")

        f.write("const byte data_tag[SIZE_DATASET] = { \n")
        for i in range(0, len(pressure)-1):
            f.write(str(rain[i])+",\n")
        f.write(str(rain[i])+"};\n")

def p(c,x):
    return c[0]*x**2 + c[1]*x

data = pd.read_csv('weather_data.csv', names = ['rain','temp','pressure','date'])

plt.plot(range(len(data.pressure)), data.pressure, range(len(data.rain)), (data.rain*1000) + 98000)

time_shifted_p = np.array(data.pressure[0:-2])
time_shifted_r = np.array(data.rain[2:])

delta = np.diff(time_shifted_p) / 2
delta = np.insert(delta,0,0)

data2 = {'pressure' :  time_shifted_p, 'delta' : delta }

X = pd.DataFrame(data2)

fig = plt.figure("scatter")
sc = plt.scatter(X.pressure, X.delta ,c = time_shifted_r)
plt.colorbar(sc)

y = time_shifted_r

dump_c_data(time_shifted_p,delta,time_shifted_r)

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=0)

# sc = StandardScaler()
# X_train = sc.fit_transform(X_train)
# X_test = sc.transform(X_test)

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

# LogisticRegression
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

plt.show()