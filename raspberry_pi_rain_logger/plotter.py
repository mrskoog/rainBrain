import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.neighbors import KNeighborsClassifier

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

data = pd.read_csv('weather_data.csv', names = ['rain','temp','pressure','date'])

plt.plot(range(len(data.pressure)), data.pressure, range(len(data.rain)), (data.rain*1000) + 98000)

# shift arrays so class (rain) is 1 hour in the future
time_shifted_p = np.array(data.pressure[0:-2])
time_shifted_r = np.array(data.rain[2:])

# Calculate derivitive of samples
delta = np.diff(time_shifted_p) / 2
delta = np.insert(delta,0,0)

X = pd.DataFrame({'pressure' :  time_shifted_p, 'delta' : delta })
y = time_shifted_r

# generate data for c code
dump_c_data(time_shifted_p,delta,time_shifted_r)

# refernce KNN 
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

neighbors = np.range(1, 20)
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
plt.plot(neighbors, test_accuracy, label = 'Testing dataset Accuracy')
plt.plot(neighbors, train_accuracy, label = 'Training dataset Accuracy')

plt.legend()
plt.xlabel('n_neighbors')
plt.ylabel('Accuracy')

plt.show()
