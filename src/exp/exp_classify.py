# encoding=utf-8
import sys

import numpy as np
from sklearn.metrics import accuracy_score
from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeClassifier
from main_dc import repair_main as repair_dc
from main_dorc import repair_main as repair_dorc
from main_smr import repair_main as repair_smr

exp_methods = [
    ('SMR', repair_smr),
    ('DC', repair_dc),
    ('DORC', repair_dorc),
]


def read_dataset(filename, comma='\",\"', used_attrs_num=None):
    with open(filename) as f:
        lines = f.readlines()

    def _convert_line_to_data(line):
        line_data = line.strip().split(comma)
        try:
            x_data = map(lambda x: float(x), line_data[:-1])
        except:
            print line_data
        if used_attrs_num is not None:
            x_data = x_data[:used_attrs_num]
        label = float(line_data[-1])
        return x_data, label

    data = map(_convert_line_to_data, lines)
    X = list()
    y = list()
    for point in data:
        X.append(point[0])
        y.append(point[1])
    return np.array(X), np.array(y)


def write_dataset(filename, X, y, comma='\",\"'):
    content = ''
    size = len(X)
    assert len(y) == size
    for i in xrange(size):
        X_data = list(X[i])
        y_data = y[i]
        line_data = comma.join(map(str, X_data + [y_data]))
        content += line_data + '\r\n'
    with open(filename, 'w') as f:
        f.write(content)

def split_dataset(filename, output_files, random_seed=None, test_size=0.7, used_attrs_num=None, comma=','):
    train_filename = output_files['train']
    test_filename = output_files['test']
    X, y = read_dataset(filename, comma=comma, used_attrs_num=used_attrs_num)
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=test_size, random_state=random_seed)
    write_dataset(train_filename, X_train, y_train)
    write_dataset(test_filename, X_test, y_test)


def train_model(filename, used_attrs_num=None):
    data_X, data_y = read_dataset(filename, used_attrs_num=used_attrs_num)
    model = DecisionTreeClassifier()
    model.fit(data_X, data_y)
    return model


def classify(model, data_X, data_y, outliers):
    used_X = list()
    used_y = list()
    if outliers is None:
        used_X = data_X
        used_y = data_y
    else:
        for tid in outliers:
            used_X.append(data_X[tid])
            used_y.append(data_y[tid])
    result_y = model.predict(used_X)
    return accuracy_score(used_y, result_y)


def build_key(error_distance, error_attrs_num):
    return '%s/%s' % (error_distance, error_attrs_num)


def build_classify_data(instance, data_attrs, class_attr):
    data_X = list()
    data_y = list()
    attrs = list(data_attrs)
    if 'class' in attrs:
        attrs.remove('class')
    for record in instance.data:
        data_X.append([float(record.get(attr)) for attr in attrs])
        data_y.append(float(record.get(class_attr)))
    return np.array(data_X), np.array(data_y)


def main(epsilon_list, neighbor_k_list, random_seeds, filenames, origin_schema, used_attrs):
    global exp_methods
    schema = used_attrs + ['class']

    result_dict = {
        'origin': list(),
        'SMR': dict(),
        'DC': dict(),
        'DORC': dict(),
    }
    for random_seed in random_seeds:

        split_dataset(filenames['origin'], filenames, random_seed=random_seed, test_size=0.5, comma='\",\"',
                      used_attrs_num=10)
        model = train_model(filenames['train'])
        test_X, test_y = read_dataset(filenames['test'])
        origin_acc = classify(model, test_X, test_y, None)
        result_dict['origin'].append(origin_acc)
        print 'Origin accuracy: %s' % origin_acc

        for epsilon in epsilon_list:
            for neighbor_k in neighbor_k_list:
                key = build_key(epsilon, neighbor_k)
                print key

                for method_name, run_func in exp_methods:
                    if run_func is None:
                        pass
                    else:
                        instance = run_func(origin_schema, filenames=filenames, neighbor_k=neighbor_k, epsilon=epsilon,
                                            used_attrs=schema, comma='\",\"', sigma_k=0)
                        print 'Building classify data'
                        X, y = build_classify_data(instance, used_attrs, 'class')
                        X_train, X_test, y_train, y_test = train_test_split(
                            X, y, test_size=0.5, random_state=random_seed)
                        model_clean = DecisionTreeClassifier()
                        model_clean.fit(X_train, y_train)
                        repair_acc = classify(model_clean, X_test, y_test, None)
                        print 'Repair accuracy: %s' % repair_acc
                        if key not in result_dict[method_name]:
                            result_dict[method_name][key] = list()
                        result_dict[method_name][key].append(repair_acc)
                        sys.stdout.flush()
    return result_dict


def write_result(result, epsilon_list, neighbor_k_list, output_filename):
    if len(epsilon_list) == 1:
        fixed_factor = epsilon_list[0]
        changed_factor = neighbor_k_list
        is_fixed_in_front = True
    elif len(neighbor_k_list) == 1:
        fixed_factor = neighbor_k_list[0]
        changed_factor = epsilon_list
        is_fixed_in_front = False
    else:
        raise Exception()
    content = 'Accuracy\tSMR\tDC\tDORC\tORIGIN\r\n'
    for factor in changed_factor:
        line_data = list()
        if is_fixed_in_front:
            key = build_key(fixed_factor, factor)
        else:
            key = build_key(factor, fixed_factor)

        for method_name, _ in exp_methods:
            acc_data = result[method_name].get(key, [])
            if len(acc_data) == 0:
                line_data.append(1.0)
            else:
                line_data.append(np.average(acc_data))
        line_data.append(np.average(result['origin']))
        print line_data
        content += str(factor) + "\t%s\t%s\t%s\t%s\r\n" % tuple(line_data)
    with open(output_filename, 'w') as f:
        f.write(content)
