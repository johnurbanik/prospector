import streamlit as st
import numpy as np

from mystic.coupler import and_
from mystic.solvers import diffev2, fmin_powell
from mystic.symbolic import generate_penalty, generate_constraint, generate_solvers, generate_conditions, replace_variables

import json

# The evaluations are stochastic, so we can't cache for now.
# @st.cache(allow_output_mutation=True)
def evaluate(program):
    if "objective" in program:
        n = program["num_bins"]
        pen_statements =  replace_variables(
            "\n".join([p["penalty"] for p in program["answers"]]),
            variables=[f"bin_{i}" for i in range(n)], markers="x"
        )

        pens =  generate_penalty(generate_conditions(pen_statements, nvars=n))
        constraint_statements = replace_variables(
            "\n".join([p["constraint"] for p in program["constraints"]]),
            variables=[f"bin_{i}" for i in range(n)], markers="x"
        )
        cons = generate_constraint(generate_solvers(constraint_statements, nvars=n))
        results = fmin_powell(
            cost=program["objective"], x0=[1.0/n] * n,
            bounds=program["bounds"],
            constraints=cons,
            penalty=pens, disp=False,
            full_output=True
        )
        return results
    else:
        return ""
