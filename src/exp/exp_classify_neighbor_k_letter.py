# encoding=utf-8

from exp_classify import main, write_result

if __name__ == '__main__':
    filename = '../../dataset/classify/letter_error'
    filenames = {
        'origin': filename,
        'error': filename,
        'test': '../../dataset/classify/data_test_origin_k',
        'train': '../../dataset/classify/data_train_origin_k',
    }
    origin_schema = ['attr%d' % i for i in xrange(1, 17)] + ['class']
    used_attrs = ['attr%d' % i for i in xrange(1, 17)]

    epsilon_list = [3]
    neighbor_k_list = [14,16,18,20,22]
    result = main(epsilon_list, neighbor_k_list, [1,2,4,5,6], filenames, origin_schema, used_attrs)
    print result
    write_result(result, epsilon_list, neighbor_k_list, 'result/classification_accuracy_neighbor_letter_origin.dat')

