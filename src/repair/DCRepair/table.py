# encoding=utf-8

import copy

import xlsxwriter


class Cell(object):
    def __init__(self, table, tid, attr):
        self.table = table
        self.tid = tid
        self.attr = attr

    def __str__(self):
        return str(self.tid) + '.' + self.attr

    def __hash__(self):
        attr = self.attr.encode('utf-8') if isinstance(self.attr, unicode) else self.attr
        return (str(self.tid) + str(attr)).__hash__()

    def __cmp__(self, other):
        return self.tid == other.tid and self.attr == other.attr

    def __eq__(self, other):
        return self.tid == other.tid and self.attr == other.attr

    def value(self):
        return self.table.get_value(self.tid, self.attr)

    def repair(self, value):
        self.table.repair_value(self.tid, self.attr, value)


class Table(object):
    def __init__(self, instance, schema, ordered_attr=None):
        self.instance = instance
        self.schema = schema
        self.ordered_attr = ordered_attr if ordered_attr is not None else schema.keys()
        self.repair_log = dict()
        self.conflict_cells = list()

    def size(self):
        return len(self.instance) * len(self.ordered_attr)

    def get_cell(self, tid, attr):
        return Cell(self, tid, attr)

    def get_value(self, tid, attr):
        return self.instance[tid].get(attr)

    def get_key(self, tid, attr):
        return '%d.%s' % (tid, attr)

    def repair_value(self, tid, attr, value):
        origin_value = self.get_value(tid, attr)
        self.repair_log[self.get_key(tid, attr)] = RepairLog(tid, attr, origin_value, value)

    def get_repaired_value(self, tid, attr):
        log = self.repair_log.get(self.get_key(tid, attr))
        if log is None:
            return None
        return log.repaired_value

    def write_excel(self, filename, sheet_name='Sheet1'):
        workbook = xlsxwriter.Workbook(filename)
        worksheet = workbook.add_worksheet(sheet_name)
        for i, attr in enumerate(self.ordered_attr):
            worksheet.write(0, i, attr)
        for tid, t in enumerate(self.instance):
            for attr_id, attr in enumerate(self.ordered_attr):
                worksheet.write(tid + 1, attr_id, t[attr])
        style_conflict = workbook.add_format()
        style_conflict.set_pattern(1)
        style_conflict.set_bg_color('gray')
        for cell in self.conflict_cells:
            worksheet.write(cell.tid + 1, self.ordered_attr.index(cell.attr), cell.value(), style_conflict)
        style = workbook.add_format()
        style.set_pattern(1)
        style.set_bg_color('green')
        for log in self.repair_log.values():
            worksheet.write(log.tid + 1, self.ordered_attr.index(log.attr), log.repaired_value, style)

    def get_data(self):
        data = copy.deepcopy(self.instance)
        for cell in self.conflict_cells:
            data[cell.tid][cell.attr] = cell.value()
        for log in self.repair_log.values():
            data[log.tid][log.attr] = log.repaired_value
        return data

    def mark_conflicts(self, tid_1, tid_2, dc):
        for attr in dc.get_attrs():
            self.conflict_cells.append(self.get_cell(tid_1, attr))
            self.conflict_cells.append(self.get_cell(tid_2, attr))


class RepairLog(object):
    def __init__(self, tid, attr, origin_value, repaired_value):
        self.tid = tid
        self.attr = attr
        self.origin_value = origin_value
        self.repaired_value = repaired_value

    def __str__(self):
        return '%s\t%s\t%s->%s' % (self.tid, self.attr, self.origin_value, self.repaired_value)
