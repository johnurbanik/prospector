# twenty-q-dist
## Ought.org Take Home: 20Q on Belief Distributions
## Implemented by [John Urbanik](https://github.com/johnurbanik) solely on 9/11/20.

Assuming you have poetry, the package can be run by
```bash
poetry install
poetry shell
streamlit run app.py --server.port 3030
```


### Motivation / Design Overview

This repository is my 1-day attempt at building a baseline solution for the problem posed by [Andreas Stuhlmüller](https://gist.github.com/stuhlmueller/2e3d6a5af0e4b9dec74d2f2c1f6c8a2d).

Succinctly, the goal is to develop an application that allows a user to unpack their own implicit belief distribution about a given 'forecast question.'

Based on additional conversations with Andreas, these forecast questions can have any type of support, but can safely be assumed to be univariate and continuous domain. Questions asked should be explicitly about the 'overall distribution' rather than asking about 'underlying factors' or trying to decompose the question.

In order to keep this system open and general purpose, I have chosen to include questions that directly give information about support and domain, as opposed to trying to use 'automated' methods of understanding the question. This helps with alignment and prevents the system from wandering down paths that are not salient to the user.

The system design is motivated moreso by work in [Decision Support Systems](https://dspace.mit.edu/handle/1721.1/47172) and [Knowledge-Based Systems](https://www.reidgsmith.com/Knowledge-Based_Systems_-_Concepts_Techniques_Examples_08-May-1985.pdf) than modern machine learning.

Further, I leverage [Mystic](https://mystic.readthedocs.io/), a non-convex optimization and uncertainty quantification package that allows for relatively easy specification of constraints for an optimization problem. Mystic has the nice ability to specify 'penalties' in addition to constraints, unlike scipy.optimize. This means that the answers provided by the user can be violated, without having to engineer a very awkward objective function.

I intended to implement an additional pass which allows the user to modify a histogram of the empirical distribution that the 20q section finds most likely (via sliders for each bin), but I did not have time. This could be done relatively easily with streamlit, but I spent a long time thinking about how one could make this type of interaction interact with mystic and did not come up with a great way of translating the changes on the histogram to mystic penalties or constraints.



#### Caveats / Limitations:
- Wasted time on ProbLog
    - I spent about 2-3 hours digging into ProbLog thinking that there might be a way to express continuous distributions or probabilistic 'evidence,' as I had wanted to use ProbLog fro a project and on first glance this seemed like a good project to use it on.

- Lack of familiarity:
    - This was my first time using mystic at all, and my first time using Streamlit outside of a toy context. I may not be following best practices. I chose to use mystic instead of a convex optimization package because it seems likely that adding enough penalties will result in a non-convex problem, and uncertainty estimation is a nice additional feature.

- Fixed bins:
    - For now, I use fixed bins for the distribution; it seems unlikely that human reasoning would have intuition that holds well beyond 100 bins. However, in the future I would try to modify the optimization problem to be more dynamic.


#### Sources:

StreamLit Session State code credit goes to [Ghasel](https://gist.github.com/Ghasel/0aba4869ba6fdc8d49132e6974e2e662).