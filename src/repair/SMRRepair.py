# encoding=utf-8

import itertools
import numpy as np
from ErrorDetection import ErrorDetection


class SMRRepair(object):
    sigma_k = 3.0
    normalization = True

    def __init__(self, instance=None, k=2, epsilon=None):
        self.instance = instance
        self.k = k
        self.epsilon = epsilon
        self.k_distances = list()
        self.error_detector = ErrorDetection(instance, k, epsilon)
        self.processed_y = set()
        self.max_repaired_attrs = len(self.instance.schema) / 2
        self.current_solution_distance = None

    def set_k(self, k):
        self.k = k

    def set_epsilon(self, epsilon):
        self.epsilon = epsilon
        self.error_detector.set_epsilon(epsilon)

    def set_instance(self, instance):
        self.instance = instance

    def calculate_epsilon(self):
        length = self.instance.size()
        k_distances = []
        for i in xrange(length):
            k_distances.append([])

        def update_k_distance(index, dis, record_id):
            k_distance = k_distances[index]
            if len(k_distance) < self.k:
                k_distance.append((dis, record_id))
            elif k_distance[0][0] > dis:
                k_distance = k_distance[1:] + [(dis, record_id)]
            else:
                return
            k_distances[index] = sorted(k_distance, reverse=True)

        def update_k_distances(i, j, dis):
            update_k_distance(i, dis, j)
            update_k_distance(j, dis, i)

        for i in xrange(length):
            record1 = self.instance.get(i)
            for j in xrange(i + 1, length):
                record2 = self.instance.get(j)
                distance = self.instance.distance(record1, record2, normalization=self.normalization)
                update_k_distances(i, j, distance)

        k_distance_list = map(lambda x: x[0][0], k_distances)
        average = np.average(k_distance_list)
        sigma = np.std(k_distance_list)
        self.epsilon = average + SMRRepair.sigma_k * sigma
        self.k_distances = k_distances
        self.error_detector.set_epsilon(self.epsilon)

    def filter(self):
        result = list()
        for i in xrange(self.instance.size()):
            if self.k_distances[i][0][0] > self.epsilon:
                result.append(i)
        return result

    def check_processed(self, attrs):
        def _hash_set(names):
            names = sorted(list(names))
            return ('\2'.join(names)).__hash__()
        hash_code = _hash_set(attrs)
        processed = False
        if hash_code not in self.processed_y:
            self.processed_y.add(hash_code)
        else:
            processed = True
        return processed

    def repair_brute_force(self, outliers):
        solutions = dict()
        for record_id in outliers:
            record = self.instance.get(record_id)
            init_solution = self.instance.get(self.k_distances[record_id][-1][1])
            self.processed_y = set()
            self.current_solution_distance = record.distance(init_solution, normalization=self.normalization)
            solution = self.repair_record_brute_force(record, set(), record, init_solution)
            solutions[record_id] = solution
        return solutions

    def repair_record_brute_force(self, record, x_attrs, current_explanation, current_solution):
        if self.current_solution_distance is None:
            self.current_solution_distance = record.distance(current_solution)

        y_attrs = set(record.schema) - {'class'} - x_attrs
        if len(y_attrs) == 0:
            current_explanation_distance = record.distance(current_explanation)
            if current_explanation_distance >= self.current_solution_distance:
                return current_solution
            full_space_neighbors = self.error_detector.get_x_subspace_neighbors(current_explanation, None,
                                                                                normalization=self.normalization)
            if len(full_space_neighbors) > self.k:
                self.current_solution_distance = current_explanation_distance
                return current_explanation
            return current_solution

        attr = list(y_attrs)[0]
        candidate_values = self.instance.domains[attr].values
        for candidate_value in candidate_values:
            new_explanation = current_explanation.clone()
            new_explanation.set(attr, candidate_value)
            current_solution = self.repair_record_pruning(record, x_attrs | {attr},
                                                          new_explanation, current_solution)
        return current_solution

    def repair_pruning(self, outliers):
        solutions = dict()
        for record_id in outliers:
            record = self.instance.get(record_id)
            init_solution = self.instance.get(self.k_distances[record_id][-1][1])
            self.processed_y = set()
            self.current_solution_distance = record.distance(init_solution, normalization=self.normalization)
            solution = self.repair_record_pruning(record, set(), record, init_solution)
            solutions[record_id] = solution
        return solutions

    def repair_record_pruning(self, record, x_attrs,
                              current_explanation, current_solution,
                              subspace_id_list=None):
        if self.current_solution_distance is None:
            self.current_solution_distance = record.distance(current_solution)
        if self.check_processed(x_attrs):
            return current_solution
        current_explanation_distance = record.distance(current_explanation)
        if current_explanation_distance >= self.current_solution_distance:
            return current_solution
        subspace_neighbors = self.error_detector.get_x_subspace_neighbors(current_explanation, x_attrs, subspace_id_list)
        if len(subspace_neighbors) < self.k:
            return current_solution
        subspace_neighbors_id = [neighbor[0] for neighbor in subspace_neighbors]
        full_space_neighbors = self.error_detector.get_x_subspace_neighbors(current_explanation, None,
                                                                            id_list=subspace_neighbors_id,
                                                                            normalization=self.normalization)
        if len(full_space_neighbors) > self.k:
            self.current_solution_distance = current_explanation_distance
            return current_explanation
        subspace_neighbors = sorted(subspace_neighbors, cmp=lambda x, y: cmp(x[1], y[1]))
        k_neighbor = subspace_neighbors[self.k-1]
        if (k_neighbor[1] - self.epsilon) ** 2 + current_explanation_distance ** 2 >= self.current_solution_distance ** 2:
            return current_solution

        # upper bound
        r_2 = list()
        y_attrs = set(record.schema) - {'class'} - x_attrs
        for neighbor_id, sub_dis in subspace_neighbors:
            if self.k_distances[neighbor_id][0][0] <= self.epsilon - sub_dis:
                r_2.append(neighbor_id)
        if len(r_2) > 0:
            dis_y_list = [(neighbor_id, self.instance.distance(record, self.instance.get(neighbor_id), y_attrs))
                          for neighbor_id in r_2]
            candidate = min(dis_y_list, key=lambda x: x[1])
            solution = record.clone()
            t_2 = self.instance.get(candidate[0])
            for y_attr in y_attrs:
                solution.set(y_attr, t_2.get(y_attr))
            current_distance = record.distance(solution, normalization=self.normalization)
            if current_distance < self.current_solution_distance:
                current_solution = solution
                self.current_solution_distance = current_distance

        for attr in set(self.instance.schema) - x_attrs:
            new_x_attrs = x_attrs | {attr}
            current_solution = self.repair_record_pruning(
                record, new_x_attrs, current_explanation, current_solution,
                subspace_id_list=subspace_neighbors_id)
        return current_solution

