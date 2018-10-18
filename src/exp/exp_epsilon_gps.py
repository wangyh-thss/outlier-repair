# encoding=utf-8

import time

from database.Instance import Record
from main_dc import main as run_single_exp_dc
from main_dorc import main as run_single_exp_dorc
from main_smr import main as run_single_exp

if __name__ == '__main__':
    Record.set_equal_threshold(5e-5)
    output_content_rms = 'RMS\tSMR\tDC\tDORC\r\n'
    output_content_accuracy = 'Accuracy\tSMR\tDC\tDORC\r\n'
    output_content_distance = 'RepairDistance\tSMR\tDC\tDORC\r\n'
    output_content_time = 'Time(s)\tSMR\tDC\tDORC\r\n'
    filenames = {
        'origin': '../../dataset/gps/gps_label',
        'error': '../../dataset/gps/gps_obs'
    }
    schema = ['ts', 'x', 'y']
    exp_methods = [
        ('SMR', run_single_exp),
        ('DC', run_single_exp_dc),
        ('DORC', run_single_exp_dorc),
    ]
    for epsilon in [0.5, 1, 1.5, 2, 2.5]:
        print epsilon
        rms_list = list()
        precision_list = list()
        recall_list = list()
        accuracy_list = list()
        time_list = list()
        data_size_list = list()
        repair_distance_list = list()

        for method_name, exp_func in exp_methods:
            time_begin = time.time()
            if exp_func is not None:
                rms, precision, recall, accuracy, repair_distance, data_size = exp_func(
                    schema, epsilon=epsilon, filenames=filenames, neighbor_k=6)
            else:
                rms, precision, recall, accuracy, repair_distance, data_size = (0.5, 0.5, 0.5, 1.0, 0.5, 200)
            time_end = time.time()

            outlier_size = float(data_size)
            time_used = (time_end - time_begin) / outlier_size
            rms_list.append(rms)
            precision_list.append(precision)
            recall_list.append(recall)
            accuracy_list.append(accuracy)
            time_list.append(time_used)
            data_size_list.append(data_size)
            repair_distance_list.append(repair_distance)

            print 'RMS: %s' % rms
            print 'Precision: %s' % precision
            print 'Recall: %s' % recall
            print 'Accuracy: %s' % accuracy
            print 'Average time(s): %s' % time_used
            print 'Repair distance: %s' % repair_distance

        output_content_rms += str(epsilon) + '\t%f\t%f\t%f\r\n' % tuple(rms_list)
        output_content_accuracy += str(epsilon) + '\t%f\t%f\t%f\r\n' % tuple(accuracy_list)
        output_content_distance += str(epsilon) + '\t%f\t%f\t%f\r\n' % tuple(repair_distance_list)
        output_content_time += str(epsilon) + '\t%f\t%f\t%f\r\n' % tuple(time_list)

    print output_content_rms
    print output_content_accuracy
    print output_content_time
    print output_content_distance
    with open('result/epsilon_rms_gps.dat', 'w') as f:
        f.write(output_content_rms)
    with open('result/epsilon_accuracy_gps.dat', 'w') as f:
        f.write(output_content_accuracy)
    with open('result/epsilon_repair_distance_gps.dat', 'w') as f:
        f.write(output_content_distance)
    with open('result/epsilon_time_gps.dat', 'w') as f:
        f.write(output_content_time)
