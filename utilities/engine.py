import streamlit as st
import numpy as np
from scipy.optimize import differential_evolution as dev
from scipy.optimize import Bounds, LinearConstraint, minimize

from mystic.coupler import and_
from mystic.solvers import diffev2, fmin_powell
from mystic.symbolic import generate_penalty, generate_constraint, generate_solvers, generate_conditions, replace_variables

from utilities.np_helper import shift

import json

# The evaluations are stochastic, so we can't cache for now.
# @st.cache(allow_output_mutation=True)
def evaluate(program):
    if "objective" in program:
        n = program["num_bins"]
        # pen_statements =  replace_variables(
        #     "\n".join([p["penalty"] for p in program["answers"]]),
        #     variables=[f"bin_{i}" for i in range(n)], markers="x"
        # )

        # pens =  generate_penalty(generate_conditions(pen_statements, nvars=n))
        # constraint_statements = replace_variables(
        #     "\n".join([p["constraint"] for p in program["constraints"]]),
        #     variables=[f"bin_{i}" for i in range(n)], markers="x"
        # )
        # cons = generate_constraint(generate_solvers(constraint_statements, nvars=n))

        # # results = fmin_powell(
        # #     cost=program["objective"], x0=[1.0/n] * n,
        # #     bounds=program["bounds"],
        # #     constraints=cons,
        # #     penalty=pens, disp=False,
        # #     full_output=True
        # # )
        # results = diffev2(
        #     cost=program["objective"], x0=[(0.0, 1.0/n)] * n,
        #     npop=10*n, bounds=program["bounds"],
        #     scale=0.7, cross=0.5,
        #     maxiter=300,
        #     constraints=cons,
        #     penalty=pens, disp=False,
        #     full_output=True
        # )
        # st.write(results)
        # return results
        obj = [
            lambda x: np.sum(x * np.ma.log(x).filled(0)),
            # lambda x: np.nansum((shift(x, -1) - x)**2) * .5*n + np.nansum((shift(x, -2) - x)**2) * .25*n
        ]
        pens = obj + [p['np_pen'] for p in program['answers']]
        def obj_fun(z, pens):
            return sum(f(z) for f in pens)
        import inspect
        return minimize(obj_fun, args=pens, x0=np.ones(n)/n, bounds=Bounds(np.zeros(n),np.ones(n)), constraints=LinearConstraint(np.ones(n), 1, 1))

    else:
        return ""
