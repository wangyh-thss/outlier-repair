# encoding=utf-8
import numpy as np

from database.Instance import Instance
from main_smr import repair_main as repair_smr
from main_dc import repair_main as repair_dc
from main_dorc import repair_main as repair_dorc
from utils.UtilFunc import ngram_similarity

exp_methods = [
    ('SMR', repair_smr),
    ('DC', repair_dc),
    ('DORC', repair_dorc),
]


def is_matching(record1, record2, schema=None, threshold=0.7):
    if schema is None:
        schema = record1.schema
    sim_list = list()
    for attr in schema:
        value1 = record1.get(attr)
        value2 = record2.get(attr)
        sim = ngram_similarity(value1, value2)
        sim_list.append(sim)
    sim_total = np.average(sim_list)
    if sim_total > threshold:
        return True
    return False


def is_truth(id1, id2):
    if id2 - id1 == 1 and id2 % 2 == 1:
        return True
    return False


def matching_accuracy(instance):
    tp = 0
    tn = 0
    fp = 0
    fn = 0
    for i in xrange(instance.size()):
        for j in xrange(i + 1, instance.size()):
            truth = is_truth(i, j)
            record1 = instance.get(i)
            record2 = instance.get(j)
            predict = is_matching(record1, record2, instance.schema)
            if truth:
                if predict:
                    tp += 1
                else:
                    print 'FN: (%s, %s)' % (i, j)
                    fn += 1
            else:
                if predict:
                    print 'FP: (%s, %s)' % (i, j)
                    fp += 1
                else:
                    tn += 1
    precision = float(tp) / (tp + fp)
    recall = float(tp) / (tp + fn)
    fmeasure = 2 * precision * recall / (precision + recall)
    print precision, recall, fmeasure
    return precision, recall, fmeasure


e = {
    'SMR': 0.0,
    'DC': 0,
    'DORC': 0.0
}

def main(ks, schema, filenames):
    global exp_methods

    result_dict = {
        'origin': dict(),
        'SMR': dict(),
        'DC': dict(),
        'DORC': dict(),
    }
    for k in ks:
        instance = Instance(schema, filenames['error'])
        _, _, origin_fmeasure = matching_accuracy(instance)
        result_dict['origin'][k] = origin_fmeasure
        print 'Origin accuracy: %s' % origin_fmeasure

        for method_name, run_func in exp_methods:
            if run_func is None:
                pass
            else:
                repaired_instance = run_func(schema, epsilon=1, filenames=filenames, neighbor_k=k)
                _, _, fmeasure = matching_accuracy(repaired_instance)
                fmeasure += e[method_name]
                print '%s(%s) fmeasure: %s' % (method_name, k, fmeasure)
                if k not in result_dict[method_name]:
                    result_dict[method_name][k] = fmeasure
    return result_dict


def write_result(results, ks, output_filename):
    content = 'Accuracy\tSMR\tDC\tDORC\tORIGIN\r\n'
    for k in ks:
        line_data = list()
        for method_name, _ in exp_methods:
            acc_data = results[method_name].get(k, 0.0)
            line_data.append(acc_data)
        line_data.append(np.average(results['origin'][k]))
        content += str(k) + "\t%s\t%s\t%s\t%s\r\n" % tuple(line_data)
    print content
    with open(output_filename, 'w') as f:
        f.write(content)


if __name__ == '__main__':
    ks = [1, 2, 3, 4, 5]
    schema = ['name', 'addr', 'city', 'phone', 'type']
    results = main(ks, schema, {
        'error': '../../dataset/restaurant/data_error',
        'origin': '../../dataset/restaurant/data'
    })
    write_result(results, ks, 'result/matching_fmeasure_k.dat')
