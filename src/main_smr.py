# encoding=utf-8

from database.Instance import Instance
from repair.SMRRepair import SMRRepair
from utils.UtilFunc import repair_accuracy, repair_accuracy_for_subspace, repair_accuracy_for_avg_attr


def repair_main(schema, sigma_k=1.0, outliers=None, epsilon=None, filenames=None, neighbor_k=3,
                data_size=None, used_attrs=None, comma='\",\"'):
    if filenames is None:
        filenames = {
            'error': '../dataset/restaurant/data_error',
            'origin': '../dataset/restaurant/data_origin',
        }
    SMRRepair.sigma_k = sigma_k
    instance = Instance(schema, filenames['error'], data_size=data_size, used_attrs=used_attrs, comma=comma)
    repair = SMRRepair(instance)
    repair.set_k(neighbor_k)
    repair.calculate_epsilon()

    if epsilon is not None:
        repair.set_epsilon(epsilon)
    print 'epsilon: %f' % repair.epsilon
    if outliers is None:
        outliers = repair.filter()
        print 'Detected outliers: %s' % outliers
    solutions = repair.repair_brute_force(outliers)

    for record_id, solution in solutions.items():
        instance.data[record_id] = solution
    return instance

def repair_main_for_avg_attr(schema, sigma_k=1.0, outliers=None, epsilon=None, filenames=None, neighbor_k=3,
                data_size=None, used_attrs=None, comma='\",\"'):
    if filenames is None:
        filenames = {
            'error': '../dataset/restaurant/data_error',
            'origin': '../dataset/restaurant/data_origin',
        }
    SMRRepair.sigma_k = sigma_k
    instance = Instance(schema, filenames['origin'], data_size=data_size, used_attrs=used_attrs, comma=comma)
    repair = SMRRepair(instance)
    repair.set_k(neighbor_k)
    repair.calculate_epsilon()
    if epsilon is not None:
        repair.set_epsilon(epsilon)
        print 'epsilon: %f' % repair.epsilon
    if outliers is None:
        outliers = repair.filter()
        print 'Detected outliers: %s' % outliers
        print 'Detected outliers len: %s' % len(outliers)
    solutions = repair.repair_pruning(outliers)
    #solutions = repair.repair_approximation(outliers)
    # solutions = repair.repair_brute_force(outliers)
    for record_id, solution in solutions.items():
        # print '---------------'
        # print instance.get(record_id)
        # print solution
        # print '---------------'
        instance.data[record_id] = solution
    return instance, len(outliers)

def avg_attr_main(schema, sigma_k=1.0, outliers=None, epsilon=4, filenames=None, neighbor_k=20, data_size=None,
         used_attrs=None, early_terminate=None, alpha = 0.2, trainRatio = 0.2, axis = 'epsilon'):
    instance, outlier_num = repair_main_for_avg_attr(schema, sigma_k=sigma_k, outliers=outliers, epsilon=epsilon, filenames=filenames,
                           neighbor_k=neighbor_k, data_size=data_size, used_attrs=used_attrs)
    ground_truth = Instance(schema, filenames['origin'], used_attrs=used_attrs)
    error_instance = Instance(schema, filenames['error'], used_attrs=used_attrs)
    error_count = repair_accuracy_for_avg_attr(ground_truth, error_instance, instance, outlier_num)
    return error_count, instance.size()

def subspace_main(schema, sigma_k=1.0, outliers=None, epsilon=4, filenames=None, neighbor_k=20, data_size=None,
                  used_attrs=None, alpha=0.2, trainRatio=0.2, axis='epsilon'):
    instance = repair_main(schema, sigma_k=sigma_k, outliers=outliers, epsilon=epsilon, filenames=filenames,
                           neighbor_k=neighbor_k, data_size=data_size, used_attrs=used_attrs)
    ground_truth = Instance(schema, filenames['origin'], used_attrs=used_attrs)
    error_instance = Instance(schema, filenames['error'], used_attrs=used_attrs)
    jaccard, precision, recall, f1, accuracy, error_count = repair_accuracy_for_subspace(ground_truth, error_instance, instance)
    return jaccard, precision, recall, f1, accuracy, error_count, instance.size()


def main(schema, sigma_k=0, outliers=None, epsilon=None, filenames=None, neighbor_k=3, data_size=None,
         used_attrs=None):
    instance = repair_main(schema, sigma_k=sigma_k, outliers=outliers, epsilon=epsilon, filenames=filenames,
                           neighbor_k=neighbor_k, data_size=data_size, used_attrs=used_attrs)
    ground_truth = Instance(schema, filenames['origin'], used_attrs=used_attrs)
    error_instance = Instance(schema, filenames['error'], used_attrs=used_attrs)
    rms, precision, recall, accuracy, repair_distance = repair_accuracy(ground_truth, error_instance, instance)
    return rms, precision, recall, accuracy, repair_distance, instance.size()
