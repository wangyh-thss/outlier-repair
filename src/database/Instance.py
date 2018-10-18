# encoding=utf-8

import numpy as np

from utils.UtilFunc import convert_distances_to_weights, random_select, string_similarity, normalize


class Record(object):
    equal_threshold = 1

    def __init__(self, attr_names=None, str_data=None, domains=None, used_attrs=None, comma='\",\"'):
        self.data = dict()
        self.schema = attr_names
        self.domains = domains
        if used_attrs is not None:
            used_attrs = set(used_attrs)
            self.schema = used_attrs
        if str_data is not None:
            attrs = str_data.split(comma)
            for i, attr_name in enumerate(attr_names):
                if used_attrs is not None and attr_name not in used_attrs:
                    continue
                self.set(attr_name, attrs[i].strip())

    def __hash__(self):
        try:
            str_record = '\2'.join(self.data.values())
            return str_record.__hash__()
        except:
            print self
            exit(-1)

    def __str__(self):
        return self.data.__str__()

    def get(self, attr_name):
        return self.data.get(attr_name)

    def set(self, attr_name, attr_value):
        self.data[attr_name] = attr_value

    def distance(self, record, attrs=None, normalization=False):
        dis = 0
        diff_attrs = 0
        if attrs is None:
            attrs = self.data.keys()
        for attr_name in attrs:
            if attr_name == 'class':
                continue
            attr_value = self.data[attr_name]
            if self.domains is None:
                attr_distance = string_similarity(attr_value, record.get(attr_name))
            else:
                attr_distance = self.domains[attr_name].distance(attr_value, record.get(attr_name),
                                                                 normalization=normalization)
            if attr_distance > 1e-2:
                diff_attrs += 1
            dis += attr_distance ** 2
        #print diff_attrs
        #print dis ** 0.5
        return dis ** 0.5 + diff_attrs

    def diff_attributes(self, record, max_dis=None):
        dis = 0
        for attr_name, attr_value in self.data.items():
            if not self.value_equal(attr_value, record.get(attr_name)):
                dis += 1
                if max_dis and dis > max_dis:
                    return dis
        return dis

    def clone(self):
        result = Record()
        result.domains = self.domains
        result.data = dict(self.data)
        return result

    @classmethod
    def set_equal_threshold(cls, threshold):
        cls.equal_threshold = threshold

    @classmethod
    def value_equal(cls, v1, v2):
        return string_similarity(v1, v2) <= cls.equal_threshold


class Domain(object):
    def __init__(self):
        self.hash_map = dict()
        self.values = list()
        self.distance_matrix = np.zeros((0, 0))
        self.min_distance = None
        self.max_distance = None
        self.normalized_distance_matrix = None

    def add(self, value):
        if value in self.hash_map:
            return self.hash_map[value]
        value_id = len(self.values)
        self.hash_map[value] = value_id
        self.extend_distance_matrix(value)
        self.values.append(value)
        return value_id

    def get_id(self, value):
        return self.hash_map.get(value)

    def get_value(self, value_id):
        if value_id < len(self.values):
            return self.values[value_id]

    def extend_distance_matrix(self, value):
        current_length = len(self.values)
        dis_vector = np.zeros((1, current_length))
        for i, existing_value in enumerate(self.values):
            dis = string_similarity(value, existing_value)
            if self.min_distance is None or dis < self.min_distance:
                self.min_distance = dis
            if self.max_distance is None or dis > self.max_distance:
                self.max_distance = dis
            dis_vector[0, i] = dis
        self.distance_matrix = np.concatenate((self.distance_matrix, dis_vector))
        dis_vector = np.insert(dis_vector, current_length, 0)
        dis_vector.shape = (1, current_length + 1)
        self.distance_matrix = np.concatenate((self.distance_matrix, dis_vector.T), axis=1)

    def normalize(self):
        shape = self.distance_matrix.shape
        self.normalized_distance_matrix = np.zeros(shape)
        for i in xrange(shape[0]):
            for j in xrange(shape[1]):
                self.normalized_distance_matrix[i, j] = normalize(self.distance_matrix[i, j],
                                                                  self.min_distance, self.max_distance)

    def distance(self, value1, value2, normalization=False):
        id_1 = self.get_id(value1)
        id_2 = self.get_id(value2)
        if not normalization:
            if id_1 is not None and id_2 is not None:
                return self.distance_matrix[self.get_id(value1), self.get_id(value2)]
            return string_similarity(value1, value2)
        if self.normalized_distance_matrix is not None and id_1 is not None and id_2 is not None:
            return self.normalized_distance_matrix[self.get_id(value1), self.get_id(value2)]
        elif id_1 is not None and id_2 is not None:
            return normalize(self.distance_matrix[self.get_id(value1), self.get_id(value2)],
                             self.min_distance, self.max_distance)
        else:
            return string_similarity(value1, value2, self.min_distance, self.max_distance)

    def get_distance_list(self, value, normalization=False):
        value_id = self.get_id(value)
        if value_id is None:
            return None
        if normalization and self.normalized_distance_matrix is not None:
            distances = list(self.normalized_distance_matrix[value_id, :])
        else:
            distances = list(self.distance_matrix[value_id, :])
        return zip(self.values, distances)


class Instance(object):
    def __init__(self, schema, filename=None, data_size=None, used_attrs=None, comma='\",\"'):
        self.data = list()
        self.schema = schema
        self.distance_map = dict()
        self.domains = dict()
        self.candidates = list()
        for attr in schema:
            self.domains[attr] = Domain()
        if filename is not None:
            self.read(filename, data_size=data_size, used_attrs=used_attrs, comma=comma)
        if used_attrs is not None:
            self.schema = used_attrs

    def read(self, filename, data_size=None, used_attrs=None, comma='\",\"'):
        with open(filename, 'r') as f:
            lines = f.readlines()
        count = 0
        for line in lines:
            if data_size is not None and count > data_size:
                break
            record = Record(self.schema, line, self.domains, used_attrs=used_attrs, comma=comma)
            self.data.append(record)
            for attr in self.schema:
                value = record.get(attr)
                self.domains[attr].add(value)
            count += 1

    def distance(self, record1, record2, attrs=None, normalization=False):
        if record1.__hash__() > record2.__hash__():
            record1, record2 = record2, record1
        if attrs is None and record1 in self.distance_map and record2 in self.distance_map[record1]:
            return self.distance_map[record1][record2]
        dis = record1.distance(record2, attrs, normalization=normalization)
        if attrs is None and record1 not in self.distance_map:
            self.distance_map[record1] = dict()
            self.distance_map[record1][record2] = dis
        return dis

    def size(self):
        return len(self.data)

    def candidates_size(self):
        return len(self.candidates)

    def get(self, index):
        try:
            return self.data[index]
        except IndexError:
            return None

    def generate_candidates(self, distance_threshold, num=10):
        self.candidates = set()
        for record in self.data:
            self.candidates.add(record)
            attr_candidates = dict()
            for attr in self.schema:
                distance_list = self.domains[attr].get_distance_list(record.get(attr))
                attr_candidates[attr] = convert_distances_to_weights(distance_list, distance_threshold)
            count = 0
            for _ in xrange(num * 2):
                candidate = Record()
                for attr in self.schema:
                    candidate.set(attr, random_select(attr_candidates[attr]))
                if candidate in self.candidates:
                    continue
                self.candidates.add(candidate)
                count += 1
                if count >= num:
                    break
        self.candidates = list(self.candidates)
        print 'Candidates Size: %d' % len(self.candidates)

    def build_candidate_weights(self):
        print 'Building weights'
        for count, candidate in enumerate(self.candidates):
            for tuple_record in self.data:
                _ = self.distance(tuple_record, candidate)

    def write(self, filename):
        content = ''
        for record in self.data:
            content += ','.join([record.get(attr) for attr in self.schema]) + '\r\n'
        with open(filename, 'w') as f:
            f.write(content)
