from enum import Enum, auto
from numbers import Number
from typing import Dict, List, Optional, TypeVar, Tuple

import numpy as np
import pandas as pd

import streamlit as st

T = TypeVar('T')

class Support(Enum):
    BOUNDED = auto()
    SEMI = auto() # We assume that it is (0, inf) unless overwritten
    INFINITE = auto()

class QuestionManager:
    # NB: In the future, I'd like to use the Python ProbLog API to build terms and keep data more structured.
    def __init__(self,
                 prompt: Optional[str] = None,
                 support_type: Enum = Support.SEMI,
                 num_bins: int = 20,
                 program: List[Dict[str, T]] = []
                ) -> None:
        self.prompt = prompt
        self.support_type = support_type
        self._init_domain()
        self.dtype = "Numeric"
        self.num_bins = num_bins
        self.bins =  []
        self.program = program

    def _init_domain(self) -> None:
        if self.support_type == Support.INFINITE:
            self.domain = (float(-inf), float("inf"))
        if self.support_type == Support.SEMI:
            self.domain = (0.0, float("inf"))
        if self.support_type == Support.BOUNDED:
            self.domain = (0.0, 100.0)  # TODO: Dumb initialization!


    def set_domain(self, bottom: T, top: T, neg_inf: bool = False, pos_inf: bool = False) -> None:
        num_bins =  self.num_bins
        if pos_inf:
            self.support_type = Support.SEMI
            num_bins = num_bins - 1
        if neg_inf:
            self.support_type = Support.INFINITE
            num_bins = num_bins - 1
        else:
            self.support_type = Support.BOUNDED
        if self.dtype == "Date":
            labels =  pd.date_range(bottom, top, periods=num_bins + 2)
            if neg_inf:
                raise ValueError("Infinite time ranges not allowed")
        elif self.dtype == "Numeric":
            labels =  list(np.linspace(bottom, top, num=num_bins + 1, endpoint=True))
            if neg_inf:
                labels = [float("-inf")] + labels
            if pos_inf:
                labels = labels + [float("inf")]

        else:
            raise TypeError("Only dates and numbers are supported at this time.")
        self.labels = labels
        print(len(self.labels), self.num_bins)
        self.bins = pd.DataFrame([
            {
                "from": labels[bin_num],
                "to": labels[bin_num + 1],
                "rel_question_count": 0
            } for bin_num in range(self.num_bins)
        ])

    def get_bin_index_for_val(self, val: T, start: int = 0) -> int:
        df =  self.bins
        bin_num = df.loc[(df['from'] > val) & (df['to'] <= val)].index[0]
        if bin_num:
            return bin_num
        else:
            raise ValueError("Value was out of range as compared to %s" % self.domain)

    def increment_question_count(self, bin_idxs: List[int]) -> None:
        # TODO: make this one pass on bins
        self.bins.loc[bin_idxs, ["rel_question_count"]] += 1

    def best_bin_for_question(self) -> int:
        return self.bins["rel_question_count"].idx_min()

    def set_prompt(self, prompt: str) -> None:
        if isinstance(prompt, str):
            self.prompt = prompt
        else:
            raise TypeError("Prompt must be a string, representing the question being forecasted.")

    @st.cache
    def get_prompt(self) -> str:
        return self.prompt

    def add_answer_to_program(self, question: str, answer: T, problog_code: str) -> None:
        self.program.append({
            "question": question,
            "answer": answer,
            "problog": problog_code
        })

    def add_special_clause_to_program(self, rep_dict: Dict[str, T]) -> None:
        self.program.append(rep_dict)

    @st.cache
    def get_program(self) -> List[Dict[str, T]]:
        return self.program

    @st.cache
    def get_support_type(self) -> str:
        if self.support_type == Support.INFINITE:
            return "(-inf,inf)"
        elif self.support_type == Support.SEMI:
            return "[a, inf)"
        else:
            return "[a,b]"

    def initialize_program(self) -> None:
        # Set up libraries, outcome, and
        problog = """
        :- use_module(library(apply)).
        :- use_module(library(lists)).
        P::make_bin(J, P).
        get_prob(B, Out) :- make_bin(B, 1.0).
        histogram(L) :-
            findall(X, between(1, %s, X), L),
            maplist(get_prob, L, S).
        query(histogram(_)).
        """ % (self.num_bins)
        self.add_special_clause_to_program({
            "function": "setup",
            "problog": problog
        })
