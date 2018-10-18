# encoding=utf-8

from database.Instance import Instance
from repair.SMRRepair import SMRRepair
from utils.UtilFunc import repair_accuracy


def repair_main(schema, sigma_k=1.0, outliers=None, tau=None, filenames=None, neighbor_k=3, data_size=None,
                used_attrs=None, comma=None):
    if filenames is None:
        filenames = {
            'error': '../dataset/restaurant/data_error',
            'origin': '../dataset/restaurant/data_origin',
        }
    SMRRepair.sigma_k = sigma_k
    instance = Instance(schema, filenames['error'], data_size=data_size, used_attrs=used_attrs)
    repair = SMRRepair(instance)
    repair.set_k(neighbor_k)
    repair.calculate_epsilon()
    if tau is not None:
        repair.set_epsilon(tau)
    print 'tau: %f' % repair.epsilon
    print outliers
    print repair.filter()
    if outliers is None:
        outliers = repair.filter()
        print 'Detected outliers: %s' % outliers
    solutions = repair.repair_pruning(outliers)
    for record_id, solution in solutions.items():
        instance.data[record_id] = solution
    return instance


def main(schema, sigma_k=0, outliers=None, tau=None, filenames=None, neighbor_k=3, data_size=None,
         used_attrs=None):
    instance = repair_main(schema, sigma_k=sigma_k, outliers=outliers, tau=tau, filenames=filenames,
                           neighbor_k=neighbor_k,
                           data_size=data_size, used_attrs=used_attrs)
    ground_truth = Instance(schema, filenames['origin'], used_attrs=used_attrs)
    error_instance = Instance(schema, filenames['error'], used_attrs=used_attrs)
    rms, precision, recall, accuracy, repair_distance = repair_accuracy(ground_truth, error_instance, instance)
    return rms, precision, recall, accuracy, repair_distance, instance.size()
