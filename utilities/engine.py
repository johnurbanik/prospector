
import streamlit as st


from mystic.solvers import diffev2
from mystic.symbolic import generate_penalty, generate_conditions, replace_variables

import json

# @st.cache(allow_output_mutation=True)
def evaluate(program):
    if 'objective' in program:
        n = program["num_bins"]
        pen_statements =  replace_variables(
            "\n".join([p["penalty"] for p in program["penalties"]]),
            variables=[f"bin_{i}" for i in range(n)], markers="x"
        )
        pens =  generate_penalty(generate_conditions(pen_statements, nvars=n), k=1e12)
        results = diffev2(
            cost=program["objective"], x0=[(0.0, 1.0/n)] * n,
            npop=10, bounds=program["bounds"],
            penalty=pens, disp=False,
            full_output=True, gtol=10  #, retall = True
        )
        return results
    else:
        return ''