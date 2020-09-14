from abc import ABC
from enum import Enum, auto
from itertools import count
from typing import Any, Dict, List, Optional, TypeVar, Tuple

import pandas as pd
import streamlit as st

from state_management.question_state import QuestionManager

class AnswerType(Enum):
    COMPARATOR =  auto()
    FLOAT =  auto()
    FLOAT_RANGE = auto()
    INT = auto()
    INT_RANGE = auto()
    DATE = auto()
    DATE_RANGE = auto()

class BaseQuestion(ABC):
    q_type = 0

    def __init__(self, manager: QuestionManager) -> None:
        self.manager = manager
        self.question = None
        self.answer_type = AnswerType.FLOAT
        self.answer = None
        self.default = None
        self.bins = []
        self.penalty = ""
        self.is_range = False
        self.invalid = False

    def __str__(self) -> None:
        return self.__class__.__name__

    def export(self) -> Dict[str, Any]:
        return {
            "type": self.__class__.q_type,
            "question": self.question,
            "answer": self.answer,
            "bins": self.bins,
            "penalty": self.penalty,
        }

    def answer_fields(self) -> List[Tuple[Any, Dict[str, Any]]]:
        if self.answer_type == AnswerType.COMPARATOR:
            return [(
                st.selectbox,
                {
                    "options": ("a", "b", "a and b are equal"),
                    "index": 0,
                }
            )]
        elif self.answer_type == AnswerType.FLOAT:
            return [(st.number_input, {"value": self.default or 0.0})]
        elif self.answer_type == AnswerType.FLOAT_RANGE:
            return [(st.number_input, {"value": 0.0}), (st.number_input, {"value": 100.0})]
        elif self.answer_type == AnswerType.INT:
            return [(st.number_input, {"value": self.default or 1})]
        elif self.answer_type == AnswerType.INT_RANGE:
            return [(st.number_input, {"value": 0}), (st.number_input, {"value": 1})]
        elif self.answer_type == AnswerType.DATE:
            return [(st.date_input, {})]
        elif self.answer_type == AnswerType.DATE_RANGE:
            return [(
                st.date_input,
                {
                    "value": [
                        pd.Timestamp.today().to_pydatetime(),
                        (pd.Timestamp.today() + pd.DateOffset(years=10)).to_pydatetime()
                    ]
                })]
        else:
            raise ValueError("Unknown answer type")

    def set_question(self, a, b) -> None:
        pass

    def set_bins(self, bins: List[Any]) -> None:
        self.bins = bins

    def set_answer(self, answer: Any) -> None:
        self.answer = answer
        self.set_penalty()

    def set_penalty(self) -> None:
        pass


