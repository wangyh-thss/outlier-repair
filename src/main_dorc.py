# encoding=utf-8

from database.Instance import Instance
from repair.DORCRepair import DORCRepair
from utils.UtilFunc import repair_accuracy, repair_accuracy_for_subspace, repair_accuracy_for_avg_attr


def repair_main(schema, sigma_k=1.0, outliers=None, epsilon=None, filenames=None, neighbor_k=3, data_size=None,
                used_attrs=None, comma=None):
    if filenames is None:
        filenames = {
            'error': '../dataset/restaurant/data_error',
            'origin': '../dataset/restaurant/data_origin',
        }
    DORCRepair.sigma_k = sigma_k
    instance = Instance(schema, filenames['error'], data_size=data_size, used_attrs=used_attrs)
    repair = DORCRepair(instance, neighbor_k, epsilon)
    print 'epsilon: %f' % repair.epsilon
    print outliers
    solutions = repair.repair()
    for record_id, solution_id in solutions:
        class_id = None
        try:
            class_id = instance.get(record_id).get('class')
        except:
            pass
        instance.data[record_id] = instance.get(solution_id).clone()
        if class_id is not None:
            instance.data[record_id].set('class', class_id)
    return instance

def repair_main_for_avg_attr(schema, sigma_k=1.0, outliers=None, epsilon=None, filenames=None, neighbor_k=3, data_size=None,
         used_attrs=None):
    if filenames is None:
        filenames = {
            'error': '../dataset/restaurant/data_error',
            'origin': '../dataset/restaurant/data_origin',
        }
    if used_attrs is not None:
        schema = used_attrs + ['class']
    DORCRepair.sigma_k = sigma_k
    instance = Instance(schema, filenames['error'], data_size=data_size, used_attrs=used_attrs)
    repair = DORCRepair(instance, neighbor_k, epsilon)
    repair.calculate_epsilon()
    outliers = repair.filter()
    print 'epsilon: %f' % repair.epsilon
    print outliers
    # repair.repair(outliers)
    solutions = repair.repair()
    for record_id, solution_id in solutions:
        # print '---------------'
        # print instance.get(record_id)
        # print solution
        # print '---------------'
        instance.data[record_id] = instance.get(solution_id)
    return instance, len(outliers)


def avg_num_main(schema, sigma_k=1.0, outliers=None, epsilon=None, filenames=None, neighbor_k=3, data_size=None,
         used_attrs=None, early_terminate=None, alpha = 0.2, trainRatio = 0.2, axis = 'epsilon'):
    instance = repair_main_for_avg_attr(schema, sigma_k=sigma_k, outliers=outliers, epsilon=epsilon, filenames=filenames,
                           neighbor_k=neighbor_k, data_size=data_size, used_attrs=used_attrs)
    ground_truth = Instance(schema, filenames['origin'], used_attrs=used_attrs)
    error_instance = Instance(schema, filenames['error'], used_attrs=used_attrs)
    jaccard, precision, recall, f1, accuracy, error_count = repair_accuracy_for_avg_attr(ground_truth, error_instance, instance)

def subspace_main(schema, sigma_k=1.0, outliers=None, epsilon=None, filenames=None, neighbor_k=3, data_size=None,
                  used_attrs=None, alpha=0.2, trainRatio=0.2, axis='epsilon'):
    instance = repair_main(schema, sigma_k=sigma_k, outliers=outliers, epsilon=epsilon, filenames=filenames,
                           neighbor_k=neighbor_k, data_size=data_size, used_attrs=used_attrs)
    ground_truth = Instance(schema, filenames['origin'], used_attrs=used_attrs)
    error_instance = Instance(schema, filenames['error'], used_attrs=used_attrs)
    jaccard, precision, recall, f1, accuracy, error_count = repair_accuracy_for_subspace(ground_truth, error_instance,
                                                                                         instance)
    return jaccard, precision, recall, f1, accuracy, error_count, instance.size()


def main(schema, sigma_k=1.0, outliers=None, epsilon=None, filenames=None, neighbor_k=3, data_size=None,
         used_attrs=None):
    instance = repair_main(schema, sigma_k=sigma_k, outliers=outliers, epsilon=epsilon, filenames=filenames,
                           neighbor_k=neighbor_k, data_size=data_size, used_attrs=used_attrs)
    ground_truth = Instance(schema, filenames['origin'], used_attrs=used_attrs)
    error_instance = Instance(schema, filenames['error'], used_attrs=used_attrs)
    rms, precision, recall, accuracy, repair_distance = repair_accuracy(ground_truth, error_instance, instance)
    return rms, precision, recall, accuracy, repair_distance, instance.size()
