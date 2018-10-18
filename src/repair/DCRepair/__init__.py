#encoding=utf-8

import os
import sys
import xlrd
import pickle
from fastdc import FastDC
from utils import strQ2B
from table import Table
from holistic_repair import HolisticRepair, HighErrorRateException

reload(sys)
sys.setdefaultencoding('utf-8')


def build_table(filename):
    try:
        workbook = xlrd.open_workbook(filename)
        table = workbook.sheets()[0]
    except:
        return None
    attrs = table.row_values(0)
    attrs = map(lambda x: strQ2B(x), attrs)
    attrs = map(lambda x: x.encode('utf-8') if isinstance(x, unicode) else x, attrs)
    schema = dict()
    instance = list()
    for i in xrange(1, table.nrows):
        row_data = table.row_values(i)
        map(lambda x: strQ2B(x), row_data)
        row_dict = dict()
        for (k, v) in zip(attrs, row_data):
            if v == '':
                v = None
            if v is not None and k not in schema:
                t = type(v)
                if t == int:
                    t = float
                schema[k] = t
            row_dict[k] = v
        instance.append(row_dict)
    return Table(instance, schema, attrs)


def dc_discover(filename, output_filename):
    table = build_table(filename)
    discover = FastDC(table)
    discover.discover()
    dcs = discover.dcs
    with open(output_filename, 'w') as f:
        pickle.dump(dcs, f)
    dc_str = ''
    for dc in dcs:
        dc_str += dc.__str__() + '\n'
    if not os.path.isdir('log'):
        os.mkdir('log')
    with open('log/DCRules.log', 'w') as f:
        f.write(dc_str)


def dc_repair(filename, dc_model_path, output_filename, train_filename=None, epsilon=0.2):
    with open(dc_model_path, 'r') as f:
        dcs = pickle.load(f)
    table = build_table(filename)
    train_table = build_table(train_filename)
    repair = HolisticRepair(table, dcs)
    try:
        repair.repair()
    except HighErrorRateException:
        if train_table is not None and table.schema == train_table:
            merge_table = Table(table.instance + train_table.instance,
                                table.schema, table.ordered_attr)
        else:
            merge_table = table
        discover = FastDC(merge_table, epsilon=epsilon)
        discover.discover()
        new_dcs = dc_discover.dcs
        repair = HolisticRepair(table, new_dcs)
        repair.repair()
    table.write_excel(output_filename)

