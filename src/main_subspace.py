from sklearn import linear_model
from utils.UtilFunc import subspace_precision, avg_num_precision
from repair.SMRRepair import SMRRepair
import sklearn
from database.Instance import Instance
from subspace.build_classification_set import ClassificationSetBuilder
from subspace.k_distance import KDistance
from utils.UtilFunc import subspace_precision

def main_for_avg_num(schema, sigma_k=1.0, outliers=None, epsilon=4, filenames=None, neighbor_k=80, data_size=None,
         used_attrs=None, early_terminate=None, alpha = 0.2, trainRatio = 0.2, axis = 'epsilon'):
    # Get k-distance points set of each point p

    # Build classification set
    # Train with lars lasso
    # Important feature selection as explanation
    if filenames is None:
        filenames = {
            'error': '../dataset/restaurant/data_error',
            'origin': '../dataset/restaurant/data_origin',
        }

    # Get k-distance points set of each point p
    ground_truth = Instance(schema, filenames['origin'], data_size=data_size, used_attrs=used_attrs)
    error_instance = Instance(schema, filenames['error'], data_size=data_size, used_attrs=used_attrs)

    dis_calculator = KDistance(error_instance, neighbor_k)

    knn = dis_calculator.get_knn(epsilon)
    SMRRepair.sigma_k = sigma_k
    instance = Instance(schema, filenames['origin'], data_size=data_size, used_attrs=used_attrs, comma='\",\"')
    repair = SMRRepair(instance)
    repair.set_k(neighbor_k)
    repair.calculate_epsilon()

    k_dis = []
    for i in range(instance.size()):
        k_dis.append(repair.k_distances[i][0][0])

    # Build classification set
    classification_set = ClassificationSetBuilder(error_instance, alpha, k_dis, trainRatio)
    classification_set.BuildInSet()
    classification_set.BuildOutSet()
    train_data, train_labels, test_data, test_labels = classification_set.build()

    # Train with random forest
    data_len = len(train_data)
    subspace_explanation = []
    outlierness = []
    for i in xrange(0, data_len):
        train_data_by_point = train_data[i]
        train_labels_by_point = train_labels[i]
        test_data_by_point = test_data[i]
        test_labels_by_point = test_labels[i]
        reg = linear_model.LassoLars(alpha=0.005)
        reg.fit(train_data_by_point, train_labels_by_point)
        reg_pre = reg.predict(test_data_by_point)
        outlierness.append(sklearn.metrics.mean_squared_error(test_labels_by_point, reg_pre))

        exp_by_point = []
        for j in range(len(reg.coef_)):
            if reg.coef_[j] != 0:
                exp_by_point.append(1)
            else:
                exp_by_point.append(0)
        subspace_explanation.append(exp_by_point)

    #print outlierness
    error_count = avg_num_precision(ground_truth, error_instance, subspace_explanation,
                                    k_dis, knn, epsilon = epsilon, neighbor_k = neighbor_k, axis = axis)
    print "Error Count: " + str(error_count)

    return error_count, error_instance.size()

def main(schema, sigma_k=1.0, outliers=None, epsilon=4, filenames=None, neighbor_k=80, data_size=None,
         used_attrs=None, alpha=0.2, trainRatio=0.2, axis='epsilon'):
    # Get k-distance points set of each point p

    # Build classification set
    # Train with lars lasso
    # Important feature selection as explanation
    if filenames is None:
        filenames = {
            'error': '../dataset/restaurant/data_error',
            'origin': '../dataset/restaurant/data_origin',
        }

    # Get k-distance points set of each point p
    ground_truth = Instance(schema, filenames['origin'], data_size=data_size, used_attrs=used_attrs)
    error_instance = Instance(schema, filenames['error'], data_size=data_size, used_attrs=used_attrs)

    dis_calculator = KDistance(error_instance, neighbor_k)

    knn = dis_calculator.get_knn(epsilon)
    SMRRepair.sigma_k = sigma_k
    instance = Instance(schema, filenames['error'], data_size=data_size, used_attrs=used_attrs, comma='\",\"')
    repair = SMRRepair(instance)
    repair.set_k(neighbor_k)
    repair.calculate_epsilon()

    k_dis = []
    for i in range(instance.size()):
        k_dis.append(repair.k_distances[i][0][0])

    # Build classification set
    classification_set = ClassificationSetBuilder(error_instance, alpha, k_dis, trainRatio)
    classification_set.BuildInSet()
    classification_set.BuildOutSet()
    train_data, train_labels, test_data, test_labels = classification_set.build()

    # Train with random forest
    data_len = len(train_data)
    subspace_explanation = []
    outlierness = []
    for i in xrange(0, data_len):
        train_data_by_point = train_data[i]
        train_labels_by_point = train_labels[i]
        test_data_by_point = test_data[i]
        test_labels_by_point = test_labels[i]
        reg = linear_model.LassoLars(alpha=0.005)
        reg.fit(train_data_by_point, train_labels_by_point)
        reg_pre = reg.predict(test_data_by_point)
        outlierness.append(sklearn.metrics.mean_squared_error(test_labels_by_point, reg_pre))

        exp_by_point = []
        for j in range(len(reg.coef_)):
            if reg.coef_[j] != 0:
                exp_by_point.append(1)
            else:
                exp_by_point.append(0)
        subspace_explanation.append(exp_by_point)

    jaccard, precision, recall, f1, accuracy, error_count = subspace_precision(ground_truth, error_instance,
                                                                               subspace_explanation,
                                                                               k_dis, knn, epsilon=epsilon,
                                                                               neighbor_k=neighbor_k, axis=axis)

    print 'Jaccard: %s' % jaccard
    print 'Precision: %s' % precision
    print 'Recall: %s' % recall
    print 'F1-Score: %s' % f1
    print 'Accuracy: %s' % accuracy

    return jaccard, precision, recall, f1, accuracy, error_count, error_instance.size()
