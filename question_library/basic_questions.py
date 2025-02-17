from collections.abc import Sequence
import numpy as np

from question_library.base_question import BaseQuestion, AnswerType
from utilities.np_helper import expr_gen

def bin_string(bin_or_list_of_bins):
    if isinstance(bin_or_list_of_bins, Sequence):
        return " + ".join([f"bin_{i}" for i in bin_or_list_of_bins])
    else:
        return f"bin_{bin_or_list_of_bins}"

class MoreLikely(BaseQuestion):
    q_type = 1
    def __init__(self, manager):
        super().__init__(manager)
        self.answer_type = AnswerType.COMPARATOR

    def set_question(self, a, b):
        self.question = f"In which interval does the outcome more likely lie?<ol type=\"a\"><li>{a}</li><li>{b}</li></ol>"

    def set_penalty(self):
        if self.answer == "a":
            operator =  ">"
        elif self.answer == "b":
            operator = "<"
        else:
            operator = "="
        lbs = bin_string(self.bins[0])
        rbs = bin_string(self.bins[1])
        self.penalty =  f"({lbs}) - ({rbs}) {operator} 0"

    def set_np_penalty(self):
        if self.answer == "a":
            self.np_pen = lambda x: np.clip(expr_gen(x, self.bins[0][0]) - expr_gen(x,self.bins[1][0]), 0, None) ** 2
        elif self.answer == "b":
            self.np_pen = lambda x: np.clip(expr_gen(x, self.bins[1][0]) - expr_gen(x,self.bins[0][0]), 0, None) ** 2
        else:
            self.np_pen = lambda x: (expr_gen(x, self.bins[0][0]) - expr_gen(x,self.bins[1][0])) ** 2

class MostLikely(BaseQuestion):
    q_type =  2
    def __init__(self, manager):
        super().__init__(manager)
        if self.manager.dtype == "Date":
            self.answer_type = AnswerType.DATE
        else:
            self.answer_type =  AnswerType.FLOAT
        self.invalid = self.q_type in self.manager.get_answer_types()

    def set_question(self, *args):
        self.question = "What is the single most likely outcome?"

    def set_penalty(self):
        best_bin = self.manager.get_bin_index_for_val(self.answer)
        other_bins = set(range(len(self.manager.bins))) - set([best_bin])
        pen = ""
        for a_bin in other_bins:
            pen += f"{bin_string(best_bin)} >= {bin_string(a_bin)}"
            pen += "\n"
        self.penalty = pen

    def set_np_penalty(self):
        best_bin = self.manager.get_bin_index_for_val(self.answer)
        self.np_pen = lambda x: np.sum(np.clip(x - x[best_bin], 0, None))**2

class TimesLikely(BaseQuestion):
    q_type = 3
    def __init__(self, manager):
        super().__init__(manager)
        self.default = 1.0
        self.answer_type = AnswerType.FLOAT

    def set_question(self, a, b):
        self.question = f"How many times more likely is it that the outcome is in the interval {a} than {b}?"

    def set_penalty(self):
        self.penalty = f"{bin_string(self.bins[0])} = {bin_string(self.bins[1])} * {self.answer}"

    def set_np_penalty(self):
        self.np_pen = lambda x: (expr_gen(x, self.bins[0][0]) - expr_gen(x,self.bins[1][0]) * self.answer)**2

class MultiBinPDF(BaseQuestion):
    q_type = 4
    def __init__(self, manager):
        super().__init__(manager)
        self.default = 0.0
        self.answer_type = AnswerType.FLOAT

    def set_question(self, range_str, *args):
        self.question = f"What is the probability that the outcome is between {range_str}?"

    def set_penalty(self):
        self.penalty = f"{bin_string(self.bins[0])} = {self.answer}"

    def set_np_penalty(self):
        self.np_pen = lambda x: (expr_gen(x, self.bins[0][0], self.bins[0][-1]) - self.answer) ** 2