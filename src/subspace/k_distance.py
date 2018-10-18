import pandas as pd
import numpy as np
class KDistance(object):

    def __init__(self, dataSet, k):
        self.dataSet = self.TransformToList(dataSet)
        self.k = k

    def TransformToList(self, instance):
        resList = []
        for i in xrange(instance.size()):
            strIns = instance.get(i).data
            df = pd.DataFrame(strIns, index=[0])
            ls = np.array(df.values.tolist())
            resList.append(ls.astype('float64')[0].tolist())
        return np.array(resList)

    def get_k_distance(self):
        data_len = len(self.dataSet)
        knn = []
        k_dis = []
        for i in xrange(0, data_len):
            testData = self.dataSet[i]
            distSquareMat = (self.dataSet - testData) ** 2
            distSquareSums = distSquareMat.sum(axis=1)
            distances = distSquareSums ** 0.5
            sortedIndices = distances.argsort()
            distances.sort()

            temp_k_dis = distances[self.k - 1]
            indices = []
            for j in xrange(0, data_len):
                if (distances[j] <= temp_k_dis):
                    indices.append(sortedIndices[j])
            knn.append(indices)
            k_dis.append(temp_k_dis)

        return k_dis, knn

    def get_knn(self, k_distance):
        data_len = len(self.dataSet)
        knn = []
        for i in xrange(0, data_len):
            testData = self.dataSet[i]
            distSquareMat = (self.dataSet - testData) ** 2
            distSquareSums = distSquareMat.sum(axis=1)
            distances = distSquareSums ** 0.5
            sortedIndices = distances.argsort()
            distances.sort()

            indices = []
            for j in xrange(0, data_len):
                if (distances[j] <= k_distance):
                    indices.append(sortedIndices[j])
            knn.append(indices)
        return knn
