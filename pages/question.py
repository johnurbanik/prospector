import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from streamlit.hashing import _CodeHasher

from question_library.basic_questions import MoreLikely, MostLikely
from state_management.question_state import Support
from utilities.engine import evaluate
from app import _SessionState

QUESTION_TYPES = {
    MoreLikely.q_type: MoreLikely,
    MostLikely.q_type: MostLikely
}

RNG = np.random.default_rng()

@st.cache(allow_output_mutation=True)
def gen_question(question):
    valid_question_types = QUESTION_TYPES.copy()
    i = 0
    while valid_question_types and i < 100:
        i += 1
        q_type = RNG.choice(list(valid_question_types.keys()))
        question = valid_question_types[q_type](question)
        if question.invalid:
            valid_question_types.pop(q_type, None)
        else:
            break
    if i == 100 or not valid_question_types:
        raise Exception("Could not find a valid question.")
    return question

@st.cache
def cacheable_second_bin(bins, first_bin, q_id):
        return RNG.choice(list(set(range(bins)) - set([first_bin])))

def question(state):
    q =  state.q
    st.title("20 Questions, Belief Distribution Edition")
    st.write(f"## {q.get_prompt()}")

    question = gen_question(state.q)
    first_bin = q.best_bin_for_question()
    if question.is_range:
        raise NotImplementedError()
    elif question.q_type == MostLikely.q_type:
        second_bin = None
        first_label = q.bin_label(first_bin)
        question.set_question(first_label)
        question.set_bins([[first_bin]])
    else:
        # TODO: Avoid duplicate questions
        # used_bins = state.q.get_answer_types()[q_type]
        second_bin = int(cacheable_second_bin(state.q.num_bins, first_bin, id(question)))
        first_label, second_label = (q.bin_label(first_bin), q.bin_label(second_bin))
        question.set_question(first_label, second_label)
        question.set_bins([[first_bin], [second_bin]])
    fields =  question.answer_fields()
    if not question.is_range:
        field = fields[0]
        st.write(question.question, unsafe_allow_html=True)
        question.set_answer(field[0]("", **field[1]))
    if st.button("Submit"):
        q.add_answer(question.export())
        state.page = "Dashboard"