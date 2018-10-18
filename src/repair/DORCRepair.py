# encoding=utf-8

from gurobipy import Model, GurobiError, GRB, quicksum
import numpy as np
from ErrorDetection import ErrorDetection


class DORCRepair(object):
    sigma_k = 3.0
    normalization = True

    def __init__(self, instance, k, epsilon):
        self.instance = instance
        self.k = k
        self.k_distances = list()
        self.error_detector = ErrorDetection(instance, k, epsilon)
        if epsilon is None:
            self.calculate_epsilon()
        else:
            self.epsilon = epsilon
        self.neighbor_map = self.error_detector.neighbor_map

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
        # print k_distance_list
        average = np.average(k_distance_list)
        sigma = np.std(k_distance_list)
        self.epsilon = average + DORCRepair.sigma_k * sigma
        self.k_distances = k_distances
        self.error_detector.set_epsilon(self.epsilon)

    def filter(self):
        result = list()
        for i in xrange(self.instance.size()):
            if self.k_distances[i][0][0] > self.epsilon:
                result.append(i)
        return result

    def repair(self):
        this = self
        data_size = self.instance.size()

        def get_cj(j, x_vars):
            x_list = [x_vars[i][j] for i in xrange(data_size)]
            multi_list = list()
            for k in xrange(data_size):
                if k not in self.neighbor_map[j]:
                    continue
                for i in xrange(data_size):
                    multi_list.append(x_vars[i][k])
            return quicksum(x_list) + quicksum(multi_list)

        def build_objective(x_vars):
            result = list()
            for i, record1 in enumerate(this.instance.data):
                for j, record2 in enumerate(this.instance.data):
                    result.append(record1.distance(record2) * x_vars[i][j])
            return result

        try:
            m = Model('mip1')
            x = list()
            y = list()
            for i, record in enumerate(self.instance.data):
                variables = [m.addVar(vtype=GRB.BINARY, name='x_%d_%d' % (i, j)) for j in xrange(data_size)]
                x.append(variables)
                y.append(m.addVar(vtype=GRB.BINARY, name='y_%d' % i))
                m.addConstr(quicksum(x[i]) == 1, name='sum_%d' % i)
            for j, record in enumerate(self.instance.data):
                c_j = get_cj(j, x)
                m.addConstr(c_j - self.k * y[j] >= 0, name='constr_1_%d' % j)
                m.addConstr(y[j] * data_size - c_j >= 1 - self.k, name='constr_2_%d' % j)
                m.addConstr(y[j] +
                            quicksum([y[i] if i in self.neighbor_map[j] else 0 for i in xrange(data_size)]) -
                            quicksum([x[k][j] for k in xrange(data_size)]) / float(data_size)
                            >= 0, name='constr_3_%d' % j)
            m.setObjective(quicksum(build_objective(x)))

            print '---- Begin to solve the ILP ----'
            m.optimize()
            repair_result = list()
            for v in m.getVars():
                if v.varName.startswith('x') and v.x == 1:
                    _, record_id, candidate_id = v.varName.split('_')
                    repair_result.append((int(record_id), int(candidate_id)))
            print('Obj: %g' % m.objVal)
            return repair_result

        except GurobiError as e:
            print('Error code ' + str(e.errno) + ": " + str(e))

        except AttributeError:
            import traceback;
            traceback.print_exc()
            print('Encountered an attribute error')
