# encoding=utf-8

import time

from artificial_error.add_errors_letter import begin_add_errors as begin_add_errors_pen
from artificial_error.add_errors_letter import set_error_config as set_error_config_pen
from database.Instance import Record
from main_smr import subspace_main as run_single_exp
from main_dorc import subspace_main as run_single_exp_dorc
from main_dc import subspace_main as run_single_exp_dc
from main_subspace import main as run_single_exp_subspace
from utils import UtilFunc

random_seeds = [1, 2, 4, 5, 6]

if __name__ == '__main__':
    Record.set_equal_threshold(2)
    output_content_jaccard = 'Jaccard\tKNN\tDC\tDORC\tERACER\tSUBSPACE\r\n'
    output_content_precision = 'Precision\tKNN\tDC\tDORC\tERACER\tSUBSPACE\r\n'
    output_content_recall = 'Recall\tKNN\tDC\tDORC\tERACER\tSUBSPACE\r\n'
    output_content_f1 = 'F1-Score\tKNN\tDC\tDORC\tERACER\tSUBSPACE\r\n'
    output_content_accuracy = 'Accuracy\tKNN\tDC\tDORC\tERACER\tSUBSPACE\r\n'
    output_content_error_count = 'ErrorCount\tKNN\tDC\tDORC\tERACER\tSUBSPACE\r\n'
    output_content_time = 'Time(s)\tKNN\tDC\tDORC\tERACER\tSUBSPACE\r\n'
    output_content_datasize = 'DataSize\tKNN\tDC\tDORC\tERACER\tSUBSPACE\r\n'

    filenames = {
        'origin': '../../dataset/letter/data_origin',
        'error': '../../dataset/letter/data_error'
    }
    '''filenames = {
        'origin': '../../dataset/restaurant/data_origin_dis',
        'error': '../../dataset/restaurant/data_error_dis'
    }
    schema = ['name', 'addr', 'city', 'phone', 'type']
    origin_schema = schema + ['id']
    origin_filename = '../../dataset/restaurant/data'
    modifiable_attrs = ['city', 'type']'''
    exp_methods = [
        ('KNN', run_single_exp),
        ('DC', run_single_exp_dc),
        ('DORC', run_single_exp_dorc),
        ('ERACER', None),
        ('SUBSPACE', run_single_exp_subspace)
    ]
    epsilon = 3
    for k in [14, 16, 18, 20, 22]:
        print k
        jaccard_lists = dict()
        precision_lists = dict()
        recall_lists = dict()
        f1_lists = dict()
        accuracy_lists = dict()
        errorcount_lists = dict()
        time_lists = dict()
        datasize_lists = dict()
        for seed in random_seeds:
            set_error_config_pen('seed', seed)
            attrs = ['attr%d' % i for i in xrange(1, 17)]
            schema = attrs + ['class']
            outliers = begin_add_errors_pen(schema, '../../dataset/letter/data.dat', filenames, classes=10)
            '''set_error_config('seed', seed)
            set_error_config('error_distance_threshold', error_distance)
            set_error_config('error_distance_max_threshold', error_distance + 2)
            outliers = begin_add_errors(origin_schema, origin_filename, filenames, modifiable_attrs=modifiable_attrs)'''
            print 'Outliers: %s' % outliers

            for method_name, exp_func in exp_methods:
                if method_name not in jaccard_lists:
                    jaccard_lists[method_name] = list()
                if method_name not in precision_lists:
                    precision_lists[method_name] = list()
                if method_name not in recall_lists:
                    recall_lists[method_name] = list()
                if method_name not in f1_lists:
                    f1_lists[method_name] = list()
                if method_name not in accuracy_lists:
                    accuracy_lists[method_name] = list()
                if method_name not in errorcount_lists:
                    errorcount_lists[method_name] = list()
                if method_name not in time_lists:
                    time_lists[method_name] = list()
                if method_name not in datasize_lists:
                    datasize_lists[method_name] = list()

                jaccard_list = jaccard_lists[method_name]
                precision_list = precision_lists[method_name]
                recall_list = recall_lists[method_name]
                f1_list = f1_lists[method_name]
                accuracy_list = accuracy_lists[method_name]
                errorcount_list = errorcount_lists[method_name]
                time_list = time_lists[method_name]
                datasize_list = datasize_lists[method_name]

                time_begin = time.time()
                if exp_func is not None:
                    jaccard, precision, recall, f1, accuracy, errorcount, data_size = exp_func(
                        schema, epsilon=epsilon, neighbor_k=k, filenames=filenames, axis='neighbor_k')
                else:
                    jaccard, precision, recall, f1, accuracy, errorcount, data_size = (0.5, 0.5, 0.5, 0.5, 0.5, 0, 200)
                time_end = time.time()

                outlier_size = float(len(outliers))
                time_used = (time_end - time_begin) / outlier_size
                jaccard_list.append((jaccard, data_size))
                precision_list.append((precision, data_size))
                recall_list.append((recall, data_size))
                f1_list.append((f1, data_size))
                accuracy_list.append((accuracy, data_size))
                errorcount_list.append((errorcount, data_size))
                time_list.append((time_used, outlier_size))
                datasize_list.append(data_size)

        jaccard = [UtilFunc.plat_average(jaccard_lists[name]) for name, _ in exp_methods]
        precision = [UtilFunc.plat_average(precision_lists[name]) for name, _ in exp_methods]
        recall = [UtilFunc.plat_average(recall_lists[name]) for name, _ in exp_methods]
        f1 = [UtilFunc.plat_average(f1_lists[name]) for name, _ in exp_methods]
        accuracy = [UtilFunc.plat_average(accuracy_lists[name]) for name, _ in exp_methods]
        errorcount = [UtilFunc.plat_average(errorcount_lists[name]) for name, _ in exp_methods]
        time_used = [UtilFunc.plat_average(time_lists[name]) for name, _ in exp_methods]

        output_content_jaccard += str(k) + '\t%f\t%f\t%f\t%f\t%f\r\n' % tuple(jaccard)
        output_content_precision += str(k) + '\t%f\t%f\t%f\t%f\t%f\r\n' % tuple(precision)
        output_content_recall += str(k) + '\t%f\t%f\t%f\t%f\t%f\r\n' % tuple(recall)
        output_content_f1 += str(k) + '\t%f\t%f\t%f\t%f\t%f\r\n' % tuple(f1)
        output_content_accuracy += str(k) + '\t%f\t%f\t%f\t%f\t%f\r\n' % tuple(accuracy)
        output_content_error_count += str(k) + '\t%f\t%f\t%f\t%f\t%f\r\n' % tuple(errorcount)
        output_content_time += str(k) + '\t%f\t%f\t%f\t%f\t%f\r\n' % tuple(time_used)

        print 'Jaccard: %s' % jaccard
        print 'Precision: %s' % precision
        print 'Recall: %s' % recall
        print 'F1-Score: %s' % f1
        print 'Accuracy: %s' % accuracy
        print 'Average time(s): %s' % time_used
        print 'Error Count: %s' % errorcount
    print output_content_jaccard
    print output_content_f1
    print output_content_error_count
    print output_content_time
    with open('result/subspace_k_jaccard_letter.dat', 'w') as f:
        f.write(output_content_jaccard)
    with open('result/subspace_k_f1_letter.dat', 'w') as f:
        f.write(output_content_f1)
    with open('result/subspace_k_error_count_letter.dat', 'w') as f:
        f.write(output_content_error_count)
    with open('result/subspace_k_time_letter.dat', 'w') as f:
        f.write(output_content_time)
