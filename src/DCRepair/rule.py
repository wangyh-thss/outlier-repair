#encoding=utf-8


class DC(object):

    def __init__(self, predicates):
        self.predicates = predicates

    def __str__(self):
        return 'not(%s)' % ' & '.join(map(lambda x: x.inverse_str(), self.predicates))

    def size(self):
        return len(self.predicates)

    def violate(self, tuple1, tuple2):
        for predicate in self.predicates:
            if predicate.satisfied(tuple1, tuple2):
                return False
        return True

    def get_attrs(self):
        result = set()
        for predicate in self.predicates:
            result.add(predicate.attr1)
            result.add(predicate.attr2)
        return result

    def is_usable(self):
        for predicate in self.predicates:
            if predicate.operator not in ['==', '!=']:
                return False
        return True

    def is_subset(self, path):
        for pred in self.predicates:
            if pred not in path:
                return False
        return True


class Predicate(object):
    inverse_map = {
        '==': '!=',
        '!=': '==',
        '>': '<=',
        '<': '>=',
        '<=': '>',
        '>=': '<'
    }

    opposite_map = {
        '==': '==',
        '!=': '!=',
        '>': '<',
        '<': '>',
        '<=': '>=',
        '>=': '<='
    }

    def __init__(self, attr1, attr2, operator):
        self.attr1 = attr1
        self.attr2 = attr2
        self.operator = operator

    def __str__(self):
        attr1 = self.attr1.encode('utf-8') if isinstance(self.attr1, unicode) else self.attr1
        attr2 = self.attr2.encode('utf-8') if isinstance(self.attr2, unicode) else self.attr2
        return 't1.%s %s t2.%s' % (attr1, self.operator, attr2)

    def __hash__(self):
        return hash(self.attr1 + self.operator + self.attr2)

    def __cmp__(self, other):
        return self.attr1 == other.attr1 and self.attr2 == other.attr2 and self.operator == other.operator

    def __eq__(self, other):
        return self.attr1 == other.attr1 and self.attr2 == other.attr2 and self.operator == other.operator

    def conflict(self, other):
        return self.attr1 == other.attr1 and self.attr2 == other.attr2

    def inverse_str(self):
        attr1 = self.attr1.encode('utf-8') if isinstance(self.attr1, unicode) else self.attr1
        attr2 = self.attr2.encode('utf-8') if isinstance(self.attr2, unicode) else self.attr2
        return 't1.%s %s t2.%s' % (attr1, Predicate.inverse_map[self.operator], attr2)

    def satisfied(self, tuple1, tuple2):
        value1 = tuple1.get(self.attr1)
        value2 = tuple2.get(self.attr2)
        if value1 == '' or value2 == '':
            return True
        return eval('value1 %s value2' % self.operator)

    def match(self, cell1, cell2):
        if cell1.attr == self.attr1 and cell2.attr == self.attr2:
            return True
        if cell1.attr == self.attr2 and cell2.attr == self.attr1:
            return True
        return False

