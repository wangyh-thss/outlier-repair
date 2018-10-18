# encoding=utf-8

import copy
from fastdc import FastDC
from table import Table


class HighErrorRateException(Exception):
    pass


class ConfilictHypergraph(object):
    def __init__(self):
        self.edge_count = 0
        self.edges = list()
        self.cells = dict()

    def edge_size(self):
        return self.edge_count

    def add_edge(self, edge):
        self.edges.append(edge)
        for cell in edge.cells:
            if cell not in self.cells:
                self.cells[cell] = list()
            self.cells[cell].append(self.edge_count)
        self.edge_count += 1

    def get_mvc(self):
        temp_cells = copy.deepcopy(self.cells)
        result = list()

        def _get_max_cell(cells):
            result = None
            max_len = 0
            for cell, edges in cells.items():
                if len(edges) > max_len:
                    max_len = len(edges)
                    result = cell
            for ori_cell in self.cells.keys():
                if ori_cell.__hash__() == result.__hash__():
                    return ori_cell

        removed_edges = set()
        while len(removed_edges) < len(self.edges):
            cell = _get_max_cell(temp_cells)
            result.append(cell)
            for edge_index in self.cells[cell]:
                removed_edges.add(edge_index)
                for edges in temp_cells.values():
                    try:
                        edges.remove(edge_index)
                    except:
                        continue
            del temp_cells[cell]
        return result

    def get_cells(self):
        return self.cells.keys()

    def get_edges(self, cell=None):
        if cell is None:
            return self.edges
        edge_index = self.cells.get(cell)
        if edge_index is None:
            return None
        result = list()
        for i in edge_index:
            result.append(self.edges[i])
        return result


class HyperEdge(object):
    def __init__(self, tid1, tuple1, tid2, tuple2, dc, table):
        self.tuples = {
            tid1: tuple1,
            tid2: tuple2
        }
        self.dc = dc
        self.cells = set()
        for attr in dc.get_attrs():
            self.cells.add(table.get_cell(tid1, attr))
            self.cells.add(table.get_cell(tid2, attr))
        self.repaired = False

    def add_cell(self, cell):
        self.cells.add(cell)

    def get_cell(self):
        return next(iter(self.cells))

    def build_re(self, cell=None):
        if cell is None:
            cells = self.cells
        else:
            cells = [cell]
        result = list()
        for single_cell in cells:
            tid = single_cell.tid
            for predicate in self.dc.predicates:
                for c in self.cells:
                    if c.tid == tid:
                        continue
                    if predicate.match(single_cell, c):
                        result.append(RepairExpression(left=single_cell, right=c,
                                                       operator=predicate.operator, edge=self))
        return result


class RepairExpression(object):
    def __init__(self, left=None, right=None, operator='', edge=None):
        self.left = left
        self.right = right
        self.operator = operator
        self.edge = edge
        self.value = right.value()

    def get_frontier(self):
        return self.right


class Violation(object):
    def __init__(self, tid1, tid2, dc):
        self.tid1 = tid1
        self.tid2 = tid2
        self.dc = dc


class HolisticRepair(object):
    def __init__(self, table, dcs, threshold=1.0):
        self.table = table
        self.dcs, self.unusable_dc = self.split_dcs(dcs)
        self.ch = ConfilictHypergraph()
        self.threshold = threshold
        self.violations = list()

    def split_dcs(self, dcs):
        usable_dc = list()
        unusable_dc = list()
        for dc in dcs:
            if dc.is_usable():
                usable_dc.append(dc)
            else:
                unusable_dc.append(dc)
        return usable_dc, unusable_dc

    def detect(self):
        instance = self.table.instance
        instance_length = len(instance)
        for i, tuple1 in enumerate(instance):
            for j in xrange(i + 1, instance_length):
                tuple2 = instance[j]
                for dc in self.dcs:
                    if dc.violate(tuple1, tuple2):
                        self.violations.append(Violation(i, j, dc))
                        edge = HyperEdge(i, tuple1, j, tuple2, dc, self.table)
                        self.ch.add_edge(edge)

    def mark_conflicts(self):
        instance = self.table.instance
        instance_length = len(instance)
        for i, tuple1 in enumerate(instance):
            for j in xrange(i + 1, instance_length):
                tuple2 = instance[j]
                for dc in self.unusable_dc:
                    if dc.violate(tuple1, tuple2):
                        self.table.mark_conflicts(i, j, dc)

    def get_conflict_hypergraph(self):
        instance = self.table.instance
        for violation in self.violations:
            if violation.dc not in self.dcs:
                continue
            i = violation.tid1
            j = violation.tid2
            tuple1 = instance[i]
            tuple2 = instance[j]
            edge = HyperEdge(i, tuple1, j, tuple2, violation.dc, self.table)
            self.ch.add_edge(edge)

    def get_mvc(self):
        self.mvc = self.ch.get_mvc()

    def look_up(self, cell):
        edges = self.ch.get_edges(cell)
        exps = list()
        for edge in edges:
            if edge.repaired:
                continue
            edge.repaired = True
            exp = edge.build_re()
            if exp is not None:
                exps += exp
        return exps

    def determination(self, init_cell, exps):
        assigns = dict()
        invalid_assigns = dict()
        for exp in exps:
            if exp.left not in assigns:
                assigns[exp.left] = dict()
            if exp.left not in invalid_assigns:
                invalid_assigns[exp.left] = set()
            if exp.operator == '==':
                if exp.value not in assigns[exp.left]:
                    assigns[exp.left][exp.value] = 0
                assigns[exp.left][exp.value] += 1
            elif exp.operator == '!=':
                invalid_assigns[exp.left].add(exp.value)
        max_count = 0
        target_cell = init_cell
        target_value = 'new_value'
        for cell in assigns:
            sorted_assigns = sorted(assigns[cell].keys(), reverse=True,
                                    cmp=lambda x, y: cmp(assigns[cell][x], assigns[cell][y]))
            for assign in sorted_assigns:
                if assign not in invalid_assigns:
                    if assigns[cell][assign] > max_count or cell == init_cell:
                        max_count = assigns[cell][assign]
                        target_cell = cell
                        target_value = assign
                        if cell == init_cell:
                            return target_cell, target_value
        return target_cell, target_value

    def single_repair(self):
        for cell in self.mvc:
            self.cell_queue = [cell]
            look_up_cell = self.cell_queue.pop()
            exps = self.look_up(look_up_cell)
            if len(exps) > 0:
                repaired_cell, repaired_value = self.determination(cell, exps)
                repaired_cell.repair(repaired_value)

    def repair(self):
        self.detect()
        self.get_conflict_hypergraph()
        self.get_mvc()
        if len(self.mvc) / float(self.table.size()) > self.threshold:
            raise HighErrorRateException
        processed_cells = set()
        for cell in self.ch.get_cells():
            processed_cells.add(cell)
        while True:
            size_before = len(processed_cells)
            self.single_repair()
            self.detect()
            self.get_conflict_hypergraph()
            if self.ch.edge_size() == 0:
                break
            self.get_mvc()
            for cell in self.ch.get_cells():
                processed_cells.add(cell)
            size_after = len(processed_cells)
            if size_before >= size_after:
                break
        self.mark_conflicts()


if __name__ == '__main__':
    a = FastDC(Table([
        {'I': 'A1', 'M': 'A1', 'S': 50},
        {'I': 'A2', 'M': 'A1', 'S': 40},
        {'I': 'A3', 'M': 'A1', 'S': 40},
    ], {
        'I': str,
        'M': str,
        'S': float
    }))

    a.discover()
    dcs = a.dcs
    for dc in dcs:
        print dc
    table = Table([
        {'I': 'A1', 'M': 'A1', 'S': 50},
        {'I': 'A2', 'M': 'A3', 'S': 40},
        {'I': 'A3', 'M': 'A1', 'S': 40},
    ], {
        'I': str,
        'M': str,
        'S': float
    })
    r = HolisticRepair(table, dcs, threshold=0.1)
    r.repair()
    for log in table.repair_log.values():
        print log
    table.write_excel('output.xlsx')
