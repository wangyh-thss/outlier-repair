# encoding=utf-8

import editdistance
import ngram
import numpy as np
import pandas as pd
import sklearn

np.random.seed(4)
similarity_type = 'ed'
# similarity_type = 'ngram'


def convert_distances_to_weights(data, threshold):
    values = map(lambda x: x[0], data)
    distances = map(lambda x: x[1], data)
    weights = map(lambda x: 1.0 / (x + threshold) if x < threshold else 0, distances)
    return filter(lambda x: x[1] != 0, zip(values, weights))


def random_select(data):
    weights = map(lambda x: x[1], data)
    t = np.cumsum(weights)
    s = np.sum(weights)
    pick_index = np.searchsorted(t, np.random.rand(1) * s)
    return data[pick_index[0]][0]


def normalize(dis, scale_min, scale_max):
    return (dis - scale_min) / (scale_max - scale_min)


def string_similarity(value1, value2, scale_min=None, scale_max=None):
    try:
        num_value1 = float(value1)
        num_value2 = float(value2)
        dis = abs(num_value1 - num_value2)
        if scale_min is not None and scale_max is not None:
            return normalize(dis, scale_min, scale_max)
        return dis
    except:
        pass
    if similarity_type == 'ed':
        dis = editdistance.eval(value1, value2)
        if scale_min is not None and scale_max is not None:
            return normalize(dis, scale_min, scale_max)
        return dis
    elif similarity_type == 'ngram':
        return 1 - ngram.NGram.compare(value1, value2, N=3)


def ngram_similarity(value1, value2):
    return ngram.NGram.compare(value1, value2, N=3)

def repair_accuracy_for_avg_attr(origin, error, repaired, outlier_num):
    from database.Instance import Record
    assert origin.size() == repaired.size() == error.size()
    assert len(origin.schema) == len(error.schema) == len(repaired.schema)
    schema = origin.schema
    size = origin.size()
    width = len(origin.schema)
    total_cell_count = size * width
    rms_sum = 0.0
    repair_distance = 0.0
    error_count = 0
    repair_count = 0
    correct_error_repair_count = 0
    correct_repair_count = 0
    correct_checked_count = 0
    error_checked_count = 0
    error_labels = list()
    check_labels = list()
    for i in xrange(size):
        origin_record = origin.get(i)
        error_record = error.get(i)
        repaired_record = repaired.get(i)
        correct_value_count = 0
        is_error_or_repaired = False

        for attr in schema:
            origin_value = origin_record.get(attr)
            error_value = error_record.get(attr)
            repaired_value = repaired_record.get(attr)
            is_error = False
            value_correct = False
            if (not Record.value_equal(origin_value, repaired_value)):
                repair_count += 1
    print repair_count

    try:
        avg_num = repair_count / float(outlier_num)
    except:
        avg_num = 0
    print '<<<Error Count: %f' % avg_num
    return avg_num

def repair_accuracy_for_subspace(origin, error, repaired):
    from database.Instance import Record
    assert origin.size() == repaired.size() == error.size()
    assert len(origin.schema) == len(error.schema) == len(repaired.schema)
    schema = origin.schema
    size = origin.size()
    width = len(origin.schema)
    total_cell_count = size * width
    rms_sum = 0.0
    repair_distance = 0.0
    error_count = 0
    repair_count = 0
    correct_error_repair_count = 0
    correct_repair_count = 0
    correct_checked_count = 0
    error_checked_count = 0
    error_labels = list()
    check_labels = list()
    for i in xrange(size):
        origin_record = origin.get(i)
        error_record = error.get(i)
        repaired_record = repaired.get(i)
        correct_value_count = 0
        is_error_or_repaired = False

        for attr in schema:
            origin_value = origin_record.get(attr)
            error_value = error_record.get(attr)
            repaired_value = repaired_record.get(attr)
            is_error = False
            value_correct = False
            if ((not Record.value_equal(origin_value, error_value)) and
                    (not Record.value_equal(error_value, repaired_value))):
                correct_checked_count += 1

            '''if Record.value_equal(origin_value, repaired_value):
                correct_value_count += 1
                value_correct = True
            if origin_value != error_value:
                error_count += 1
                is_error_or_repaired = True'''
            if not Record.value_equal(origin_value, error_value):
                error_count += 1
                error_labels.append(1)
            else:
                error_labels.append(0)

            if not Record.value_equal(error_value, repaired_value):
                repair_count += 1
                check_labels.append(1)
            else:
                check_labels.append(0)
    print correct_checked_count
    print repair_count
    print error_count

    try:
        jaccard = correct_checked_count / float(repair_count + error_count - correct_checked_count)
    except:
        jaccard = 0
    try:
        precision = correct_checked_count / float(repair_count)
    except:
        precision = 0
    try:
        recall = correct_checked_count / float(error_count)
    except:
        recall = 0
    try:
        f1 = 2 * precision * recall / (precision + recall)
    except:
        f1 = 0
    try:
        accuracy = sklearn.metrics.accuracy_score(error_labels, check_labels)
    except:
        accuracy = 0

    print '<<<Jaccard: %f' % jaccard
    print '<<<Precision: %f' % precision
    print '<<<Recall: %f' % recall
    print '<<<F1-score: %f' % f1
    print '<<<Error Count: %f' % repair_count
    return jaccard, precision, recall, f1, accuracy, repair_count


def repair_accuracy(origin, error, repaired):
    from database.Instance import Record
    assert origin.size() == repaired.size() == error.size()
    assert len(origin.schema) == len(error.schema) == len(repaired.schema)
    schema = origin.schema
    size = origin.size()
    width = len(origin.schema)
    total_cell_count = size * width
    rms_sum = 0.0
    repair_distance = 0.0
    error_count = 0
    repair_count = 0
    correct_error_repair_count = 0
    correct_repair_count = 0
    accuracies = list()
    for i in xrange(size):
        origin_record = origin.get(i)
        error_record = error.get(i)
        repaired_record = repaired.get(i)
        correct_value_count = 0
        is_error_or_repaired = False

        for attr in schema:
            origin_value = origin_record.get(attr)
            error_value = error_record.get(attr)
            repaired_value = repaired_record.get(attr)
            is_error = False
            value_correct = False
            if Record.value_equal(origin_value, repaired_value):
                correct_value_count += 1
                value_correct = True
            if origin_value != error_value:
                is_error = True
                error_count += 1
                is_error_or_repaired = True
            if error_value != repaired_value:
                is_error_or_repaired = True
                if not Record.value_equal(error_value, repaired_value):
                    repair_count += 1
                    if value_correct:
                        correct_repair_count += 1
                        if is_error:
                            correct_error_repair_count += 1
                if string_similarity(origin_value, repaired_value) < 2:
                    repair_distance += string_similarity(origin_value, repaired_value)
            if origin_value != repaired_value:
                if string_similarity(origin_value, repaired_value) < 2:
                    rms_sum += string_similarity(origin_value, repaired_value) ** 2
        if is_error_or_repaired:
            accuracies.append(float(correct_value_count) / len(schema))
    rms = (rms_sum / float(total_cell_count)) ** 0.5
    if len(accuracies) != 0:
        accuracy = sum(accuracies) / len(accuracies)
    else:
        accuracy = 0
    print '<<<Accuracy: %f' % accuracy
    try:
        precision = correct_repair_count / float(repair_count)
    except:
        precision = 0
    try:
        recall = correct_error_repair_count / float(error_count)
    except:
        recall = 0
    if precision + recall == 0:
        fscore = 0.0
    else:
        fscore = (2 * precision * recall) / (precision + recall)
    print '<<<RMS: %f' % rms
    print '<<<Precision: %f' % precision
    print '<<<Recall: %f' % recall
    print '<<<F-score: %f' % fscore
    print '<<<Repair distance: %f'
    return rms, precision, recall, accuracy, repair_distance


def instance_distance(origin, repaired, error=None, outliers=None):
    assert origin.size() == repaired.size()
    if error is not None:
        assert origin.size() == error.size()
    dis_square = 0
    size = origin.size()
    outlier_size = len(outliers) if outliers is not None else 0
    correct_repair = 0
    for i in xrange(size):
        origin_record = origin.get(i)
        repaired_record = repaired.get(i)
        dis_square += repaired_record.distance(origin_record) ** 2
        if outliers and i in outliers:
            correct = repaired_record.diff_attributes(origin_record, 1) == 0
            print '++++++++++++++++++++++'
            print i
            print origin_record
            print repaired_record
            print correct
            print '++++++++++++++++++++++'
            if not correct:
                continue
            correct_repair += 1
    rms = (dis_square / size) ** 0.5
    accuracy = correct_repair / float(outlier_size)
    return rms, accuracy


def rms_average(rms_list):
    summation = 0.0
    total_count = 0
    for rms, count in rms_list:
        summation += rms ** 2 * count
        total_count += count
    return (summation / total_count) ** 0.5


def plat_average(data_list):
    print data_list
    summation = 0.0
    total_count = 0
    for data, count in data_list:
        summation += data * count
        total_count += count
    print total_count
    if (total_count > 0):
        return summation / total_count
    else:
        return 0
def avg_num_precision(ground_truth, error_instance, subspace_explanation, k_dis, knn, epsilon = None, neighbor_k = None, axis = 'epsilon'):
    size = ground_truth.size()
    exp_true = []
    exp_pred = []
    correct_checked_count = 0
    error_count = 0
    checked_count = 0
    outlier_num = 0
    for i in xrange(size):
        ori = ground_truth.get(i).data
        err = error_instance.get(i).data

        df = pd.DataFrame(ori, index=[0])
        ori = np.array(df.values.tolist())
        ori = ori.astype('float64')[0].tolist()

        df = pd.DataFrame(err, index=[0])
        err = np.array(df.values.tolist())
        err = err.astype('float64')[0].tolist()

        if (k_dis[i] <= epsilon):
            continue

        outlier_num += 1
        ground_exp = []
        ground_exp_attr = []
        subspace_exp_attr = []
        for j in xrange(len(ori)):
            if (subspace_explanation[i][j] == 1):
                checked_count += 1
    try:
        avg_num = checked_count / float(outlier_num)
    except:
        avg_num = 0

    return avg_num


def subspace_precision(ground_truth, error_instance, subspace_explanation, k_dis, knn, epsilon=None, neighbor_k=None,
                       axis='epsilon'):
    size = ground_truth.size()
    exp_true = []
    exp_pred = []
    correct_checked_count = 0
    error_count = 0
    checked_count = 0
    outlier_num = 0
    for i in xrange(size):
        ori = ground_truth.get(i).data
        err = error_instance.get(i).data

        df = pd.DataFrame(ori, index=[0])
        ori = np.array(df.values.tolist())
        ori = ori.astype('float64')[0].tolist()

        df = pd.DataFrame(err, index=[0])
        err = np.array(df.values.tolist())
        err = err.astype('float64')[0].tolist()

        for j in xrange(len(ori)):
            if (ori[j] != err[j]):
                error_count += 1

        if (k_dis[i] <= epsilon):
            continue

        outlier_num += 1
        ground_exp = []
        ground_exp_attr = []
        subspace_exp_attr = []
        for j in xrange(len(ori)):
            if (ori[j] != err[j]):
                ground_exp.append(1)
                if (subspace_explanation[i][j] == 1):
                    correct_checked_count += 1
            else:
                ground_exp.append(0)
            if (subspace_explanation[i][j] == 1):
                checked_count += 1

        exp_true = exp_true + ground_exp
        exp_pred = exp_pred + subspace_explanation[i]

    try:
        jaccard = correct_checked_count / float(error_count + checked_count - correct_checked_count)
    except:
        jaccard = 0.0
    try:
        precision = correct_checked_count / float(checked_count)
    except:
        precision = 0.0
    try:
        recall = correct_checked_count / float(error_count)
    except:
        recall = 0.0
    try:
        f1 = 2 * precision * recall / (precision + recall)
    except:
        f1 = 0.0
    try:
        accuracy = sklearn.metrics.accuracy_score(exp_true, exp_pred)
    except:
        accuracy = 0.0

    return jaccard, precision, recall, f1, accuracy, checked_count
