import streamlit as st
import pandas as pd
import plotly.graph_objects as go

from utilities.engine import evaluate
from state_management.question_state import Support

def dashboard(state):
    st.title("20 Questions, Belief Distribution Edition")
    st.write(f"## {state.q.get_prompt()}")
    if st.button("Answer a question"):
        state.page = "New Question"
    if st.button("Generate potential PDF"):
        display_belief_hist(state)
    st.write("----------------")
    st.write(f"**Domain:** {state.q.get_domain_str()}")
    display_answered_questions(state)

def display_answered_questions(state):
    answers = state.q.get_program()['answers']
    st.markdown("------------------------")
    for i, answer in enumerate(answers):
        # Currently no way in streamlit to do grid layout.
        st.write("**Question:**")
        st.write(f"{answer['question']}", unsafe_allow_html=True)
        st.write(f"**Answer:** {answer['answer']}")
        if st.button("Remove", key=f"remove_{i}"):
            state.q.remove_answer(i)
        st.write("----------------")
    pass

def display_belief_hist(state):
    # Single run
    res  = evaluate(state.q.get_program())
    results = res.x
    s = pd.Series(results, index=state.q.get_bin_labels())
    fig = go.Figure()
    fig.add_trace(go.Bar(
        name='Expected Probability',
        x=s.index, y=s,
    ))
    # In the case that you want multiple runs, use this instead.
    # runs = []
    # for _ in range(10):
    #     results, _, _, _, warn_flag  = evaluate(state.q.get_program())
    #     if warn_flag != 0:
    #         st.warning("The computation was too expensive and may not have converged to a good optimization of the constraints and penalties.")
    #     s = pd.Series(results, index=state.q.get_bin_labels())
    #     runs.append(s)
    # df = pd.concat(runs, axis=1)
    # stats = pd.concat([df.mean(axis=1), df.quantile([0.10, 0.90], axis=1).T], axis=1)
    # st.write(stats)
    # st.write(df.sum(axis=0))
    # fig = go.Figure()
    # fig.add_trace(go.Bar(
    #     name='Expected Probability',
    #     x=stats.index, y=stats.iloc[:, 0],
    #     error_y=dict(
    #         type='data',
    #         array=stats.iloc[:, 2] - stats.iloc[:, 0],
    #         arrayminus=stats.iloc[:, 0] - stats.iloc[:, 1]
    #     )
    # ))
    fig.update_layout(xaxis_tickangle=45)
    st.plotly_chart(fig)

    pass

