import streamlit as st
from streamlit.hashing import _CodeHasher

from streamlit import _get_report_ctx as get_report_ctx
from streamlit.server.server import Server

from pages import *
from state_management import QuestionManager


def main():
    state = _get_state()
    pages = {
        "Dashboard": dashboard,
        "Initial Questions": onboarding,
        "New Question": question,
    }
    if not state.q:
        state.q = QuestionManager()

    st.sidebar.title("20Q")
    for title in pages.keys():
        if st.sidebar.button(title):
            state.page = title
    if not state.page:
        state.page =  "Initial Questions"
    # state.page = st.sidebar.radio("Select your page", tuple(pages.keys()), index=1)

    # Display the selected page with the session state
    pages[state.page](state)

    # Mandatory to avoid rollbacks with widgets, must be called at the end of your app
    state.sync()


# This class and the following two functions are directly lifted from [Ghasel's gist](https://gist.github.com/Ghasel/0aba4869ba6fdc8d49132e6974e2e662)
class _SessionState:

    def __init__(self, session, hash_funcs):
        """Initialize SessionState instance."""
        self.__dict__["_state"] = {
            "data": {},
            "hash": None,
            "hasher": _CodeHasher(hash_funcs),
            "is_rerun": False,
            "session": session,
        }

    def __call__(self, **kwargs):
        """Initialize state data once."""
        for item, value in kwargs.items():
            if item not in self._state["data"]:
                self._state["data"][item] = value

    def __getitem__(self, item):
        """Return a saved state value, None if item is undefined."""
        return self._state["data"].get(item, None)

    def __getattr__(self, item):
        """Return a saved state value, None if item is undefined."""
        return self._state["data"].get(item, None)

    def __setitem__(self, item, value):
        """Set state value."""
        self._state["data"][item] = value

    def __setattr__(self, item, value):
        """Set state value."""
        self._state["data"][item] = value

    def clear(self):
        """Clear session state and request a rerun."""
        self._state["data"].clear()
        self._state["session"].request_rerun()

    def sync(self):
        """Rerun the app with all state values up to date from the beginning to fix rollbacks."""

        # Ensure to rerun only once to avoid infinite loops
        # caused by a constantly changing state value at each run.
        #
        # Example: state.value += 1
        if self._state["is_rerun"]:
            self._state["is_rerun"] = False

        elif self._state["hash"] is not None:
            if self._state["hash"] != self._state["hasher"].to_bytes(self._state["data"], None):
                self._state["is_rerun"] = True
                self._state["session"].request_rerun()

        self._state["hash"] = self._state["hasher"].to_bytes(self._state["data"], None)


def _get_session():
    session_id = get_report_ctx().session_id
    session_info = Server.get_current()._get_session_info(session_id)

    if session_info is None:
        raise RuntimeError("Couldn't get your Streamlit Session object.")

    return session_info.session


def _get_state(hash_funcs=None):
    session = _get_session()

    if not hasattr(session, "_custom_session_state"):
        session._custom_session_state = _SessionState(session, hash_funcs)

    return session._custom_session_state


if __name__ == "__main__":
    main()