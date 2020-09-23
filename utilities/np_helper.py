import streamlit as st
import numpy as np

def expr_gen(x, *idx):
    if len(idx)>1:
        if idx[1]:
            idxer = slice(idx[0],idx[1]+1)
        else:
            idxer = slice(idx[0], None)
    else:
        idxer = slice(idx[0],idx[0]+1)
    return np.sum(x[idxer])

def shift(xs, n):
    e = np.empty_like(xs)
    if n >= 0:
        e[:n] = np.nan
        e[n:] = xs[:-n]
    else:
        e[n:] = np.nan
        e[:n] = xs[-n:]
    return e