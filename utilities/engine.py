
import streamlit as st

from problog.program import PrologString
from problog import get_evaluatable

import json

@st.cache(allow_output_mutation=True)
def evaluate(program_string):
    program = PrologString(program_string)
    return get_evaluatable().create_from(program).evaluate()

def compile_program_string(question_program):
    return "\n".join([statement["problog"] for statement in question_program])
