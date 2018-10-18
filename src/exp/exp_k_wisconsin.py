# encoding=utf-8

import time

import sys

from artificial_error.add_errors_letter import begin_add_errors, set_error_config
from database.Instance import Record
from main_smr import main as run_single_exp_smr
from main_dorc import main as run_single_exp_dorc
from main_dc import main as run_single_exp_dc
from main_smr_approximate import main as run_single_exp_approximation
from utils import UtilFunc

random_seeds = [1, 2, 4, 5, 6]

if __name__ == '__main__':
    Record.set_equal_threshold(1)
    output_content_rms = 'RMS\tSMR\tDC\tDORC\tApproximation\r\n'
    output_content_accuracy = 'Accuracy\tSMR\tDC\tDORC\tApproximation\r\n'
    output_content_distance = 'RepairDistance\tSMR\tDC\tDORC\tApproximation\r\n'
    output_content_time = 'Time(s)\tSMR\tDC\tDORC\tApproximation\r\n'
    filenames = {
        'origin': '../../dataset/letter/data_origin_k',
        'error': '../../dataset/letter/data_error_k'
    }
    origin_attrs = ['attr%d' % i for i in xrange(1, 17)]
    modifiable_attrs = ['attr%d' % i for i in xrange(1, 5)]
    origin_schema = origin_attrs + ['class']
    origin_filename = '../../dataset/letter/data'
    used_attrs = ['attr%d' % i for i in xrange(1, 10)]
    schema = used_attrs + ['class']
    exp_methods = [
        ('SMR', run_single_exp_smr),
        ('DC', run_single_exp_dc),
        ('DORC', run_single_exp_dorc),
        ('Approximation', run_single_exp_approximation),
    ]
    for k in [2, 3, 4, 5, 6, 7, 8]:
        print k
        rms_lists = dict()
        precision_lists = dict()
        recall_lists = dict()
        accuracy_lists = dict()
        time_lists = dict()
        data_size_lists = dict()
        repair_distance_lists = dict()
        for seed in random_seeds:
            set_error_config('seed', seed)
            set_error_config('data_size', 1000)
            outliers = begin_add_errors(origin_schema, origin_filename, filenames, classes=100,
                                        modifiable_attrs=modifiable_attrs)
            print 'Outliers: %s' % outliers

            for method_name, exp_func in exp_methods:
                if method_name not in rms_lists:
                    rms_lists[method_name] = list()
                if method_name not in precision_lists:
                    precision_lists[method_name] = list()
                if method_name not in recall_lists:
                    recall_lists[method_name] = list()
                if method_name not in accuracy_lists:
                    accuracy_lists[method_name] = list()
                if method_name not in time_lists:
                    time_lists[method_name] = list()
                if method_name not in data_size_lists:
                    data_size_lists[method_name] = list()
                if method_name not in repair_distance_lists:
                    repair_distance_lists[method_name] = list()

                rms_list = rms_lists[method_name]
                precision_list = precision_lists[method_name]
                recall_list = recall_lists[method_name]
                accuracy_list = accuracy_lists[method_name]
                time_list = time_lists[method_name]
                data_size_list = data_size_lists[method_name]
                repair_distance_list = repair_distance_lists[method_name]

                time_begin = time.time()
                if exp_func is not None:
                    rms, precision, recall, accuracy, repair_distance, data_size = exp_func(
                        schema, outliers=None, filenames=filenames, neighbor_k=k,
                        used_attrs=used_attrs, epsilon=5)
                else:
                    rms, precision, recall, accuracy, repair_distance, data_size = (0.5, 0.5, 0.5, 1.0, 0.5, 200)
                time_end = time.time()
                sys.stdout.flush()

                outlier_size = float(len(outliers))
                time_used = (time_end - time_begin) / outlier_size
                rms_list.append((rms, data_size))
                precision_list.append((precision, data_size))
                recall_list.append((recall, data_size))
                accuracy_list.append((accuracy, data_size))
                time_list.append((time_used, outlier_size))
                data_size_list.append(data_size)
                repair_distance_list.append(repair_distance)

        rms = [UtilFunc.rms_average(rms_lists[name]) for name, _ in exp_methods]
        precision = [UtilFunc.plat_average(precision_lists[name]) for name, _ in exp_methods]
        recall = [UtilFunc.plat_average(recall_lists[name]) for name, _ in exp_methods]
        accuracy = [UtilFunc.plat_average(accuracy_lists[name]) for name, _ in exp_methods]
        time_used = [UtilFunc.plat_average(time_lists[name]) for name, _ in exp_methods]
        repair_distance = [sum(repair_distance_lists[name]) / float(len(random_seeds)) for name, _ in exp_methods]

        output_content_rms += str(k) + '\t%f\t%f\t%f\t%f\r\n' % tuple(rms)
        output_content_accuracy += str(k) + '\t%f\t%f\t%f\t%f\r\n' % tuple(accuracy)
        output_content_distance += str(k) + '\t%f\t%f\t%f\t%f\r\n' % tuple(repair_distance)
        output_content_time += str(k) + '\t%f\t%f\t%f\t%f\r\n' % tuple(time_used)

        print 'RMS: %s' % rms
        print 'Precision: %s' % precision
        print 'Recall: %s' % recall
        print 'Accuracy: %s' % accuracy
        print 'Average time(s): %s' % time_used
        print 'Repair distance: %s' % repair_distance
    print output_content_rms
    print output_content_accuracy
    print output_content_time
    print output_content_distance
    with open('result/k_rms_wisconsin.dat', 'w') as f:
        f.write(output_content_rms)
    with open('result/k_accuracy_wisconsin.dat', 'w') as f:
        f.write(output_content_accuracy)
    with open('result/k_repair_distance_wisconsin.dat', 'w') as f:
        f.write(output_content_distance)
    with open('result/k_time_wisconsin.dat', 'w') as f:
        f.write(output_content_time)

