# encoding=utf-8

import itertools
import numpy as np


class ErrorDetection(object):

    def __init__(self, instance, neighbor_k, epsilon=None):
        self.instance = instance
        self.neighbor_k = neighbor_k
        self.epsilon = epsilon
        self.thresholds = dict()
        if self.epsilon is not None:
            self.neighbor_map = self.get_neighbors()

    def set_epsilon(self, epsilon):
        self.epsilon = epsilon
        self.neighbor_map = self.get_neighbors()

    @staticmethod
    def get_candidate_y(schema, attr_num):
        return itertools.combinations(schema, attr_num)

    def get_neighbors(self):
        print '----- Building neighbors map -----'
        result = dict()
        for record_id1 in xrange(self.instance.size()):
            for record_id2 in xrange(record_id1 + 1, self.instance.size()):
                record1 = self.instance.get(record_id1)
                record2 = self.instance.get(record_id2)
                if record_id1 not in result:
                    result[record_id1] = set()
                if record_id2 not in result:
                    result[record_id2] = set()
                if self.instance.distance(record1, record2) > self.epsilon:
                    continue
                result[record_id1].add(record_id2)
                result[record_id2].add(record_id1)
        return result

    @staticmethod
    def construct_attrs_key(attrs):
        sorted_attrs = sorted(attrs)
        return '\2'.join(sorted_attrs).__hash__()

    def attrs_dis_threshold(self, attrs):
        key = self.construct_attrs_key(attrs)
        if key in self.thresholds:
            return self.thresholds[key]
        distance_list = list()
        for record_id1, neighbors in self.neighbor_map.items():
            for record_id2 in neighbors:
                record1 = self.instance.get(record_id1)
                record2 = self.instance.get(record_id2)
                distance_list.append(record1.distance(record2, attrs))
        average = np.average(distance_list)
        sigma = np.average(distance_list)
        self.thresholds[key] = {
            'avg': average,
            'sigma': sigma
        }
        return self.thresholds[key]

    def get_subspace_neighbors(self, record, schema, y, id_list=None):
        neighbors = list()
        attrs_x = list(set(schema) - set(y))
        if id_list is None:
            id_list = xrange(self.instance.size())
        for record_id in id_list:
            data_record = self.instance.get(record_id)
            dis = self.instance.distance(record, data_record, attrs_x)
            if dis <= self.epsilon:
                neighbors.append((record_id, dis))
        return neighbors

    def get_x_subspace_neighbors(self, record, x_attrs, normalization=False, id_list=None):
        neighbors = list()
        if id_list is None:
            id_list = xrange(self.instance.size())
        for record_id in id_list:
            data_record = self.instance.get(record_id)
            dis = self.instance.distance(record, data_record, x_attrs, normalization=normalization)
            if dis <= self.epsilon:
                neighbors.append((record_id, dis))
        return neighbors

    # check whether the remaining has k neighbors for each candidate
    def filter_candidate(self, record, schema, candidates):
        result = list()
        for candidate in candidates:
            neighbors = self.get_subspace_neighbors(record, schema, candidate)
            neighbor_count = len(neighbors)
            if neighbor_count > self.neighbor_k:
                result.append((candidate, neighbor_count))
        result = sorted(result, cmp=lambda x, y: cmp(x[1], y[1]), reverse=True)
        return [el[0] for el in result]

    def detect(self, record, min_attr_num=None):
        schema = self.instance.schema
        valid_y = None
        if min_attr_num is None:
            min_attr_num = 1
        for attr_num in xrange(min_attr_num, len(schema) + 1):
            candidates = self.get_candidate_y(schema, attr_num)
            valid_y = self.filter_candidate(record, schema, candidates)
            if len(valid_y) > 0:
                break
        if valid_y and len(valid_y) == 0:
            valid_y = None
        return valid_y

