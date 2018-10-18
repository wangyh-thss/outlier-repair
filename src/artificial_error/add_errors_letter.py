# encoding=utf-8

import random

error_config = {
    'exact_error_rate': 10,
    'error_distance_threshold': 3,
    'error_distance_max_threshold': 6,
    'seed': 0,
    'modify_attrs_num': 2,
    'data_size': 1000,
}


def set_error_config(key, value):
    global error_config
    error_config[key] = value


def read(filename, schema, classes, comma=','):
    global error_config
    with open(filename) as f:
        lines = f.readlines()
    instance = list()
    count = 0
    for line in lines:
        if error_config['data_size'] is not None and count > error_config['data_size']:
            break
        record = dict()
        values = line.split(comma)
        for key, value in zip(schema, values):
            value = value.strip()
            record[key] = float(value)
        if int(record['class']) >= classes:
            continue
        instance.append(record)
        count += 1
    return instance


def write_data(data, schema, filename, used_attrs=None):
    content = ''
    if used_attrs is not None:
        schema = used_attrs
    for record in data:
        content += '\",\"'.join([str(record[attr]) for attr in schema]) + '\r\n'
    with open(filename, 'w') as f:
        f.write(content)


def generate_error(record, modifiable_attrs):
    global error_config
    result = dict(record)
    for attr in modifiable_attrs:
        dis = random.randint(error_config['error_distance_threshold'], error_config['error_distance_max_threshold'])
        result[attr] += dis
        if result[attr] > 15:
            result[attr] -= 2 * dis
        if result[attr] <= 0:
            result[attr] += dis
    return result


def filter_attrs(record, used_attrs):
    if used_attrs is None:
        return record
    result = dict()
    for attr in used_attrs:
        result[attr] = record[attr]
    result['class'] = record['class']
    return result


def begin_add_errors(schema, filename, output_files, modifiable_attrs=None, classes=100, comma=',', used_attrs=None):
    global error_config
    random.seed(error_config['seed'])
    instance = read(filename, schema, classes, comma=comma)
    origin_data = list()
    error_data = list()
    outliers = list()
    if modifiable_attrs is None:
        modifiable_attrs = list(set(schema) - {'class'})
    for i, record in enumerate(instance):
        if random.randint(1, 100) <= error_config['exact_error_rate']:
            outliers.append(i)
            new_record = generate_error(record, random.sample(modifiable_attrs, error_config['modify_attrs_num']))
        else:
            new_record = record
        origin_data.append(filter_attrs(record, used_attrs))
        error_data.append(filter_attrs(new_record, used_attrs))
    write_data(origin_data, schema, output_files['origin'], used_attrs)
    write_data(error_data, schema, output_files['error'], used_attrs)
    return outliers


if __name__ == '__main__':
    attrs = ['attr%d' % i for i in xrange(1, 17)]
    schema = attrs + ['class']
    set_error_config('exact_error_rate', 40)
    set_error_config('data_size', 200)
    set_error_config('modify_attrs_num', 5)
    outliers = begin_add_errors(schema, '../../dataset/letter/data', {
        'origin': '../../dataset/classify/letter_origin',
        'error': '../../dataset/classify/letter_error'
    }, classes=4)
    print 'Outliers: %s' % outliers
