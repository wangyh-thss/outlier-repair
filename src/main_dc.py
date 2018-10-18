# encoding=utf-8
import pickle

from database.Instance import Instance
from repair.DCRepair import HolisticRepair
from repair.DCRepair import Table

from utils.UtilFunc import repair_accuracy, repair_accuracy_for_subspace, repair_accuracy_for_avg_attr
from artificial_error.add_errors_letter import begin_add_errors as begin_add_errors_pen
from artificial_error.add_errors_letter import set_error_config as set_error_config_pen
import sys
sys.path.append('..')


def read_table(filename, attrs, comma='\",\"'):
    instance = list()
    schema = dict()
    for attr in attrs:
        schema[attr] = str
    with open(filename, 'r') as f:
        lines = f.readlines()
    for line in lines:
        line_data = line.strip().split(comma)
        record = dict()
        for (attr, value) in zip(attrs, line_data):
            record[attr] = value
        instance.append(record)
    return Table(instance, schema, attrs)

def repair_main(schema, sigma_k=1.0, outliers=None, epsilon=None, filenames=None, neighbor_k=3, data_size=None,
                used_attrs=None, comma=None):
    with open('result/DCs.pkl', 'r') as f:
        dcs = pickle.load(f)
    if used_attrs is not None:
        schema = used_attrs + ['class']
    error_table_filename = filenames.get('error', '../dataset/wisconsin/data_error')
    error_table = read_table(error_table_filename, schema)
    error_instance = Instance(schema)
    error_instance.data = error_table.instance
    repair = HolisticRepair(error_table, dcs, threshold=float('inf'))
    try:
        repair.repair()
    except Exception:
        import traceback;
        traceback.print_exc()
    repaired_instance = Instance(schema)
    repaired_instance.data = error_table.get_data()
    return repaired_instance

def avg_num_main(schema, sigma_k=1.0, outliers=None, epsilon=None, filenames=None, neighbor_k=3, data_size=None,
         used_attrs=None, early_terminate=None, alpha = 0.2, trainRatio = 0.2, axis = 'epsilon'):
    with open('result/DCs2.pkl', 'r') as f:
        dcs = pickle.load(f)
    if used_attrs is not None:
        schema = used_attrs + ['class']
    error_table_filename = filenames.get('error', '../dataset/magic/magic_origin')
    error_table = read_table(error_table_filename, schema)
    error_instance = Instance(schema)
    error_instance.data = error_table.instance
    repair = HolisticRepair(error_table, dcs, threshold=float('inf'))
    try:
        repair.repair()
    except Exception:
        import traceback; traceback.print_exc()
    repaired_instance = Instance(schema)
    repaired_instance.data = error_table.get_data()

    origin_table_filename = filenames.get('origin', '../dataset/magic/magic_origin')
    origin_table = read_table(origin_table_filename, schema)
    origin_instance = Instance(schema)
    origin_instance.data = origin_table.instance

    violated_tuples = set()
    for i in xrange(len(repair.violations)):
        violated_tuples.add(repair.violations[i].tid1)
    print len(violated_tuples)

    error_count = repair_accuracy_for_avg_attr(origin_instance, error_instance, repaired_instance, len(violated_tuples))
    return error_count, len(violated_tuples)

def subspace_main(schema, sigma_k=1.0, outliers=None, epsilon=None, filenames=None, neighbor_k=3, data_size=None,
                  used_attrs=None, alpha=0.2, trainRatio=0.2, axis='epsilon'):
    with open('result/DCs.pkl', 'r') as f:
        dcs = pickle.load(f)
    if used_attrs is not None:
        schema = used_attrs + ['class']
    error_table_filename = filenames.get('error', '../dataset/letter/data_error')
    error_table = read_table(error_table_filename, schema)
    error_instance = Instance(schema)
    error_instance.data = error_table.instance
    repair = HolisticRepair(error_table, dcs, threshold=float('inf'))
    try:
        repair.repair()
    except Exception:
        import traceback;
        traceback.print_exc()
    repaired_instance = Instance(schema)
    repaired_instance.data = error_table.get_data()

    origin_table_filename = filenames.get('origin', '../dataset/letter/data_origin')
    origin_table = read_table(origin_table_filename, schema)
    origin_instance = Instance(schema)
    origin_instance.data = origin_table.instance

    violated_tuples = set()
    for i in xrange(len(repair.violations)):
        violated_tuples.add(repair.violations[i].tid1)
    print len(violated_tuples)

    jaccard, precision, recall, f1, accuracy, error_count = repair_accuracy_for_subspace(origin_instance, error_instance,
                                                                                        repaired_instance)
    return jaccard, precision, recall, f1, accuracy, error_count, origin_instance.size()


def main(schema, sigma_k=1.0, outliers=None, epsilon=None, filenames=None, neighbor_k=3, data_size=None,
         used_attrs=None):
    with open('result/DCs-gps.pkl', 'r') as f:
        dcs = pickle.load(f)
    if used_attrs is not None:
        schema = used_attrs + ['class']
    error_table_filename = filenames.get('error', '../dataset/wisconsin/data_error')
    error_table = read_table(error_table_filename, schema)
    error_instance = Instance(schema)
    error_instance.data = error_table.instance
    repair = HolisticRepair(error_table, dcs, threshold=float('inf'))
    try:
        repair.repair()
    except Exception:
        import traceback
        traceback.print_exc()
    repaired_instance = Instance(schema)
    repaired_instance.data = error_table.get_data()

    origin_table_filename = filenames.get('origin', '../dataset/wisconsin/data_origin')
    origin_table = read_table(origin_table_filename, schema)
    origin_instance = Instance(schema)
    origin_instance.data = origin_table.instance

    rms, precision, recall, accuracy, repair_distance = repair_accuracy(origin_instance,
                                                                        error_instance, repaired_instance)
    return rms, precision, recall, accuracy, repair_distance, repaired_instance.size()

