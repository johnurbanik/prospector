import streamlit as st
import pandas as pd

def onboarding(state):
    st.title("20 Questions, Belief Distribution Edition")

    st.write("---")

    prompt = st.text_input("What is your Question?", state.q.prompt or "")
    state.q.set_prompt(prompt) # For Validation

    support_options = ['(-inf,inf)', '[a, inf)', '[a,b]']
    support = st.selectbox("What type of support does your question have?", support_options, support_options.index(state.q.get_support_type()))

    dtype_options = ['Numeric', 'Date']
    state.q.dtype = st.selectbox("Are the values of your forecast domain dates or numbers?", dtype_options, dtype_options.index(state.q.dtype))

    if support == support_options[0]:
        neg_inf = True
        bot_label = "What is the value you expect almost all results to be above"
    else:
        neg_inf = False
        bot_label =  "What is the minimum value that your question may occupy?"
    if state.q.dtype == 'Numeric':
        bottom  = st.number_input(bot_label, value=0)
    else:
        bottom = pd.to_datetime(
            st.date_input(
                bot_label,
                max_value=(pd.Timestamp.today() + pd.DateOffset(years=100)).to_pydatetime()
            )
        )
    if support_options.index(support) in [0, 1]:
        pos_inf = True
        top_label = "What is the value you expect almost all results to be below"
    else:
        pos_inf = False
        top_label =  "What is the maximum value that your question may occupy?"
    if state.q.dtype == 'Numeric':
        top  = st.number_input(top_label, value=100)
    else:
        top = pd.to_datetime(
            st.date_input(
                top_label,
                value=(pd.Timestamp.today() + pd.DateOffset(years=10)).to_pydatetime(),
                max_value=(pd.Timestamp.today() + pd.DateOffset(years=100)).to_pydatetime()
            )
        )

    state.q.set_domain(bottom, top, neg_inf, pos_inf)

    if st.button("Submit"):
        state.page = "Dashboard"
        state.q.initialize_program()