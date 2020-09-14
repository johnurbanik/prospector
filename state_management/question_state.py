from collections import defaultdict
from enum import Enum, auto
from numbers import Number
from typing import Any, Dict, List, Optional, TypeVar, Tuple

import numpy as np
import pandas as pd

import streamlit as st

class Support(Enum):
    BOUNDED = auto()
    SEMI = auto() # We assume that it is (0, inf) unless overwritten
    INFINITE = auto()

class QuestionManager:
    # NB: In the future, I'd like to use the Python ProbLog API to build terms and keep data more structured.
    def __init__(self,
                 prompt: Optional[str] = None,
                 support_type: Enum = Support.BOUNDED,
                 num_bins: int = 20,
                 program: Dict[str, Any] = {}
                ) -> None:
        self.prompt = prompt
        self.support_type = support_type
        self._init_domain()
        self.dtype = "Numeric"
        self.num_bins = num_bins
        self.bins =  pd.DataFrame()
        self.program = program

    def _init_domain(self) -> None:
        if self.support_type == Support.INFINITE:
            self.domain = (float("-inf"), float("inf"))
        if self.support_type == Support.SEMI:
            self.domain = (0.0, float("inf"))
        if self.support_type == Support.BOUNDED:
            self.domain = (0.0, 100.0)  # TODO: Dumb initialization!

    def set_domain(self, bottom: Any, top: Any, neg_inf: bool = False, pos_inf: bool = False) -> None:
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
            labels =  pd.date_range(bottom, top, periods=num_bins + 2).round(freq='D')
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
        self.domain = (labels[0], labels[-1])
        df = pd.DataFrame([
            {
                "from": labels[bin_num],
                "to": labels[bin_num + 1],
                "rel_answer_count": 0
            } for bin_num in range(self.num_bins)
        ])
        self.bins = df

    def get_domain_str(self) -> str:
        a, b = self.domain
        return self.format_range(a, b)

    def format_range(self, a, b):
        if isinstance(a, pd.Timestamp):
            a = a.strftime("%Y-%m-%d")
            b = b.strftime("%Y-%m-%d")
        if a == -np.Inf:
            a = "-∞"
        if b == np.Inf:
            b = "∞"
        return f"{a} - {b}"

    def get_bin_index_for_val(self, val: Any, start: int = 0) -> int:
        df =  self.bins
        if self.dtype == "Date":
            val =  pd.Timestamp(val)
            st.write(val)
        try:
            bin_num = df.loc[(df['from'] <= val) & (df['to'] > val)].index[0]
            return bin_num
        except:
            raise ValueError("Value was out of range as compared to %s" % self.domain)

    def increment_answer_count(self, bin_idxs: List[int], amount: int = 1) -> None:
        # TODO: make this one pass on bins
        self.bins.loc[bin_idxs, ["rel_answer_count"]] += amount

    def best_bin_for_question(self) -> int:
        idx = self.bins["rel_answer_count"].idxmin()
        return idx

    def bin_label(self, index: int, how: str = "both") -> Any:
        if how == "both":
            return self.get_bin_labels()[index]
        elif how == "center":
            if self.dtype == "Date":
                temp = self.bins.iloc[index]
                val =  temp["from"] + (temp["to"] - temp["from"]) / 2
                return val.strftime("%Y-%m-%d")
            else:
                return self.bins.iloc[index][["from", "to"]].mean()
        elif how == "left":
            val = self.bins["from"][index]
        else:
            val = self.bins["to"][index]
        if self.dtype == "Date":
            val = val.strftime("%Y-%m-%d")
        return val

    def set_prompt(self, prompt: str) -> None:
        if isinstance(prompt, str):
            self.prompt = prompt
        else:
            raise TypeError("Prompt must be a string, representing the question being forecasted.")

    def get_prompt(self) -> str:
        return self.prompt

    def add_answer(self, answer_dict: Dict[Any, Any]) -> None:
        self.program["answers"].append(answer_dict)
        self.increment_answer_count(np.unique(np.concatenate(answer_dict["bins"], axis=0)))


    def remove_answer(self, index: int) -> None:
        ans = self.program["answers"].pop(index)
        self.increment_answer_count(np.unique(np.concatenate(ans["bins"], axis=0)), amount=-1)

    def get_program(self) -> Dict[str, Any]:
        return self.program

    def get_support_type(self) -> str:
        if self.support_type == Support.INFINITE:
            return "(-inf,inf)"
        elif self.support_type == Support.SEMI:
            return "[a, inf)"
        else:
            return "[a,b]"

    def initialize_program(self) -> None:
        p = {}
        p["objective"] = lambda x: np.sum(x) - 1
        p["num_bins"] = self.num_bins
        p["bounds"] = [(0.0, 1.0)] * self.num_bins
        p["answers"] = [
            # Examples:
            # {
            #     "type": 7,
            #     "question": "How far forward in time would you need to go from 2022-08-11 to have an equal likelihood as the period from 2020-09-14 - 2022-08-11?",
            #     "answer": "2025-06-01",
            #     "bins": [[0, 1, 2, 3], [4, 5, 6, 7, 8, 9]],
            #     "penalty": "(bin_0 + bin_1 + bin_2 + bin_3) - (bin_4 + bin_5 + bin_6 + bin_7 + bin_8 + bin_9) = 0"
            # },
            # {
            #     "type": 5,
            #     "question": "How many times more likely is it that the outcome occurs between 2020-09-14 and 2021-03-07 than between 2021-08-28 and 2022-08-11",
            #     "answer": 5,
            #     "bins": [[0], [2]],
            #     "penalty": "bin_0 - bin_2 * 5 = 0"
            # }
        ]
        self.program = p

    def get_bin_labels(self) -> List[str]:
        def bin_label(bin):
            a = bin["from"]
            b = bin["to"]
            if a == -np.Inf:
                a = "-∞"
            if b == np.Inf:
                b = "∞"
            return f"({a}, {b})"

        def signif(x, p):
            x = np.asarray(x)
            x_positive = np.where(np.isfinite(x) & (x != 0), np.abs(x), 10**(p-1))
            mags = 10 ** (p - 1 - np.floor(np.log10(x_positive)))
            return np.round(x * mags) / mags

        if np.issubdtype(self.bins["from"], np.datetime64):
            bins = self.bins[['from','to']].apply(lambda x: x.dt.strftime("%Y-%m-%d"))
        else:
            bins  = self.bins[['from','to']].apply(lambda x: signif(x, 3))
        return bins.apply(bin_label, axis=1)

    def get_answer_types(self) -> Dict[int, List[int]]:
        res = defaultdict(set)
        for a in self.program["answers"]:
            flat = set(tuple(x) for x in a)
            res[a["type"]]|flat
        return res