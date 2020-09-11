# twenty-q-dist
## Ought.org Take Home: 20Q on Belief Distributions
## Implemented by [John Urbanik](https://github.com/johnurbanik) solely on 9/11/20.

<br><br>

### Motivation / Design Overview

This repository is my 1-day attempt at building a baseline solution for the problem posed by [Andreas Stuhlmüller](https://gist.github.com/stuhlmueller/2e3d6a5af0e4b9dec74d2f2c1f6c8a2d).

Succinctly, the goal is to develop an application that allows a user to unpack their own implicit belief distribution about a given 'forecast question.'

Based additional conversations with Andreas, these forecast questions can have any type of support, but can safely be assumed to be univariate and continuous domain. Questions asked should be explicitly about the 'overall distribution' rather than asking about 'underlying factors' or trying to decompose the question.

In order to keep this system open and general purpose, I have chosen to include questions that directly give information about support and domain, as opposed to trying to use 'automated' methods of understanding the question. This helps with alignment and prevents the system from wandering down paths that are not salient to the user.

The system design is motivated moreso by work in [Decision Support Systems](https://dspace.mit.edu/handle/1721.1/47172) and [Knowledge-Based Systems](https://www.reidgsmith.com/Knowledge-Based_Systems_-_Concepts_Techniques_Examples_08-May-1985.pdf) than modern machine learning.

Further, I leverage [Problog](https://problog.readthedocs.io/), which includes 'evidence' that allows for constraint definition as well as probabilistic statements. While Prolog (and by extension Problog) does not do 'smart' theorem proving, it is sufficient for this application; future iterations might do a better job of isolating the source of `InconsistentEvidenceError`s to give user feedback. Further, the use of probabilities allows the user to specify confidence of various facts; we also include a slider for baseline confidence.

I intended to implement an additional pass which allows the user to modify a histogram of the empirical distribution that the 20q section finds most likely (via sliders for each bin), but I did not have time. This could be done relatively easily with streamlit, but I spent a long time thinking about how one could make this type of interaction interact with Problog and did not come up with a great way of translating the changes on the histogram to Problog clauses.


#### Caveats / Limitations:

This was my first time using both Streamlit and Problog outside of a toy context. I believe strongly in using the right tool for the job, but ended up spending a large percentage of my time on this task just getting up to speed on syntax for both libraries.

For now, I use fixed bins for the distribution; it seems unlikely that human reasoning would have intuition that holds well beyond 100 bins. However, in the future I would try to modify the predicate list to


#### Sources:

StreamLit Session State code credit goes to [Ghasel](https://gist.github.com/Ghasel/0aba4869ba6fdc8d49132e6974e2e662)