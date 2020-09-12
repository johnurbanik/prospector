import streamlit as st
import pandas as pd

from utilities.logic_engine import evaluate, compile_program_string

def dashboard(state):
    st.title(state.q.get_prompt())
    st.write()
    display_state_values(state)
    st.write(compile_program_string(state.q.get_program()))
    st.write(str(evaluate(compile_program_string(state.q.get_program()))))

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
        bottom = pd.to_datetime(st.date_input(bot_label))
    if support_options.index(support) in [0, 1]:
        pos_inf = True
        top_label = "What is the value you expect almost all results to be below"
    else:
        pos_inf = False
        top_label =  "What is the maximum value that your question may occupy?"
    if state.q.dtype == 'Numeric':
        top  = st.number_input(top_label, value=0)
    else:
        top = pd.to_datetime(st.date_input(top_label))

    state.q.set_domain(bottom, top, neg_inf, pos_inf)

    if st.button("Submit"):
        state.page = "Dashboard"
        state.q.initialize_program()
        st.write(state.page)


def display_state_values(state):
    st.write("Input state:", state.q.get_prompt() or "")
    # st.write("Slider state:", state.slider)
    # st.write("Radio state:", state.radio)
    # st.write("Checkbox state:", state.checkbox)
    # st.write("Selectbox state:", state.selectbox)
    # st.write("Multiselect state:", state.multiselect)

    # for i in range(3):
    #     st.write(f"Value {i}:", state[f"State value {i}"])

    # if st.button("Clear state"):
    #     state.clear()