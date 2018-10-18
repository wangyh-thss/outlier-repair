import numpy as np
import pandas as pd
import math
class ClassificationSetBuilder(object):

    def __init__(self, dataSet, alpha, k_distance, trainRatio):
        self.dataSet = self.TransformToList(dataSet)
        self.inset = []
        self.outset = []
        self.train_data = []
        self.test_data = []
        self.train_labels = []
        self.test_labels = []
        self.alpha = alpha
        self.k_distance = k_distance
        self.dim = len(self.dataSet[0])
        self.trainRatio = trainRatio

    def TransformToList(self, instance):
        resList = []
        for i in xrange(instance.size()):
            strIns = instance.get(i).data
            df = pd.DataFrame(strIns, index=[0])
            ls = np.array(df.values.tolist())
            resList.append(ls.astype('float64')[0].tolist())
        return np.array(resList)

    def BuildInSet(self):
        data_len = len(self.dataSet)
        for i in xrange(data_len):
            self.inset.append(np.delete(self.dataSet, (i), axis=0))
        return self.inset

    def BuildOutSet(self):
        data_len = len(self.dataSet)
        for i in xrange(0, data_len):
            mean = self.dataSet[i]
            lamda = self.alpha * (1 / math.sqrt(self.dim)) * self.k_distance[i]
            cov = (lamda ** 2) * np.eye(self.dim)
            x = np.random.multivariate_normal(mean, cov, data_len - 2)
            tempSet = x.tolist()
            tempSet.append(self.dataSet[i].tolist())
            self.outset.append(tempSet)
        return self.outset


    def build(self):
        data_len = len(self.dataSet)
        for i in xrange(0, data_len):
            tempInSet = self.inset[i]
            np.random.shuffle(tempInSet)
            temp_train_data = tempInSet[0 : (int)(len(tempInSet) * self.trainRatio)]
            temp_train_labels = np.zeros((int)(len(tempInSet) * self.trainRatio))

            tempOutSet = self.outset[i]
            np.random.shuffle(tempOutSet)
            temp_train_data = np.concatenate((temp_train_data, tempOutSet[0 : (int)(len(tempInSet) * self.trainRatio)]), axis=0)
            temp_train_labels = np.concatenate((temp_train_labels, temp_train_labels + np.ones((int)(len(tempInSet) * self.trainRatio))), axis=0)

            self.train_data.append(temp_train_data)
            self.train_labels.append(temp_train_labels)


            temp_test_data = tempInSet[(int)(len(tempInSet) * self.trainRatio):]
            temp_test_labels = np.zeros(len(tempInSet) - (int)(len(tempInSet) * self.trainRatio))

            temp1 = tempOutSet[(int)(len(tempInSet) * self.trainRatio):]
            temp_test_data = np.concatenate((temp_test_data, tempOutSet[(int)(len(tempInSet) * self.trainRatio):]), axis=0)
            temp_test_labels = np.concatenate((temp_test_labels, np.ones(len(tempOutSet) - (int)(len(tempOutSet) * self.trainRatio))), axis=0)

            self.test_data.append(temp_test_data)
            self.test_labels.append(temp_test_labels)

        return self.train_data, self.train_labels, self.test_data, self.test_labels