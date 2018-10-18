# encoding=utf-8

import copy
import itertools

from rule import DC, Predicate


class FastDC(object):
    # instance: list[dict({attr: value})]
    # schema: dict({name: type})
    def __init__(self, table, epsilon=0):
        self.num_operators = ['>', '<', '>=', '<=']
        self.eq_operators = ['==', '!=']
        self.table = table
        self.predicates = list()
        self.instance = table.instance
        self.schema = table.schema
        self.evidence_set = list()
        self.evidence_set_size = 0
        self.epsilon = epsilon
        self.dcs = list()
        self.count = 0
        self.last_len = 0
        self.empty_count = 0

    def build_predicate_space(self):
        self.predicates = []
        attrs = self.schema.keys()
        for i, attr1 in enumerate(attrs):
            for j in xrange(i, len(attrs)):
                attr2 = attrs[j]
                if self.schema[attr1] != self.schema[attr2]:
                    continue
                for op in self.eq_operators:
                    self.predicates.append(Predicate(attr1, attr2, op))
                    if attr1 != attr2:
                        self.predicates.append(Predicate(attr2, attr1, op))
                if self.schema[attr1] == float or self.schema[attr1] == int:
                    for op in self.num_operators:
                        self.predicates.append(Predicate(attr1, attr2, op))
                        if attr1 != attr2:
                            self.predicates.append(Predicate(attr2, attr1, op))
        print 'Predicates:', len(self.predicates)
        for i, pred in enumerate(self.predicates):
            print i, pred

    def build_evidence_set(self):
        self.evidence_set = []
        for i, tuple1 in enumerate(self.instance):
            for j in xrange(0, len(self.instance)):
                tuple2 = self.instance[j]
                if i == j:
                    continue
                evi = []
                for predicate in self.predicates:
                    if predicate.satisfied(tuple1, tuple2):
                        evi.append(predicate)
                self.evidence_set.append(evi)
        self.evidence_set_size = len(self.evidence_set)

    def get_ordering(self, preds, evi_current):
        copy_preds = copy.deepcopy(preds)
        coverages = dict()
        for pred in preds:
            coverages[pred] = len(filter(lambda evi: pred in evi, evi_current))

        def pred_cmp(a, b):
            return cmp(coverages[a], coverages[b])

        copy_preds.sort(cmp=pred_cmp, reverse=True)
        return copy_preds

    def cover_evidence_set(self, preds):
        not_cover_num = 0
        for e in self.evidence_set:
            flag = False
            for p in preds:
                if p in e:
                    flag = True
                    break
            if not flag:
                not_cover_num += 1
                if not_cover_num > self.epsilon * self.evidence_set_size:
                    return False
        return True

    def search_minimal_covers(self, evi_current=None, path=None, ordering=None):
        self.count += 1
        if not hasattr(self, 'minimal_covers'):
            self.minimal_covers = []
        if evi_current is None:
            evi_current = copy.deepcopy(self.evidence_set)
        if path is None:
            path = set()
        if ordering is None:
            ordering = self.get_ordering(self.predicates, evi_current)
        # Branch pruning
        for mc in self.minimal_covers:
            if mc.issubset(path):
                return
        for dc in self.dcs:
            if dc.is_subset(path):
                return
        # Base cases
        threshold = self.epsilon * self.evidence_set_size
        if ordering == [] and len(evi_current) > threshold:
            return
        if len(evi_current) <= threshold:
            for p1 in path:
                for p2 in path:
                    if not p1 == p2 and p1.conflict(p2):
                        return
            for subset in itertools.combinations(path, len(path) - 1):
                if self.cover_evidence_set(subset):
                    path_copy = copy.deepcopy(subset)
                    self.minimal_covers.append(set(path_copy))
                    new_dc = DC(path_copy)
                    self.dcs.append(new_dc)
                    print new_dc
                    return
            path_copy = copy.deepcopy(path)
            self.minimal_covers.append(path_copy)
            new_dc = DC(path_copy)
            self.dcs.append(new_dc)
            print new_dc
            print len(self.dcs)
            return
        # Recursive cases
        if len(path) > 2:
            return
        for i, pred in enumerate(ordering):
            if len(path) == 0:
                dc_size = len(self.dcs)
                if dc_size == self.last_len:
                    self.empty_count += 1
                    if self.empty_count > 4:
                        return
                else:
                    self.empty_count = 0
                    self.last_len = dc_size
            path.add(pred)
            evi_next = filter(lambda evi: pred not in evi, evi_current)
            ordering_next = self.get_ordering(ordering[i + 1:], evi_next)
            self.search_minimal_covers(evi_next, path, ordering_next)
            path.remove(pred)

    def build_dc(self):
        self.dcs = []
        for mc in self.minimal_covers:
            self.dcs.append(DC(mc))

    def discover(self):
        self.build_predicate_space()
        print 'build_evidence_set...'
        self.build_evidence_set()
        print len(self.evidence_set)
        print 'search_minimal_covers...'
        self.last_len = 0
        self.empty_count = 0
        self.search_minimal_covers()
        for i, mc in enumerate(self.minimal_covers):
            print '---- Minimal cover %s' % i
            for pred in mc:
                print pred
        print self.count
