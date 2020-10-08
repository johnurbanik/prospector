# Prospector
## A system to elicit information about a user's belief in the the probability distribution of a future event

Prospector is like a game of [Twenty Questions](https://en.wikipedia.org/wiki/Twenty_Questions), but where the "answer" is the probability distribution corresponding to the _answerer's_ belief about a future event. The system is inspired by a challenge posted by [Andreas Stuhlmüller](https://gist.github.com/stuhlmueller/2e3d6a5af0e4b9dec74d2f2c1f6c8a2d) of [Ought.org](https://ought.org/) and is similar to Ought's system, [Elicit](http://elicit.ought.org/).

The system asks a sequence of questions to try to *quickly* ascertain information about the shape, local extrema, and critical regions of the distribution's PDF. The system aims to utilize a combination of randomness and "intelligent" questions to fill in areas of the domain that are missing information and to 

### Installation / Running

Assuming you have [poetry](https://python-poetry.org/) installed, the package can be run by
```bash
poetry install
poetry shell
streamlit run app.py --server.port 3030
```



### Motivation / Design Overview

Succinctly, the goal of this repository is to develop an end to end application that allows a user to unpack their own implicit belief distribution about a given 'forecast question.'

These forecast questions can have any type of support, but for now are assumed to be univariate and continuous domain. Currently, questions asked are explicitly about the 'overall distribution' rather than asking about 'underlying factors' or trying to decompose the question.

The user is "onboarded" with questions that directly give information about support and domain, as opposed to trying to use "automated" methods of understanding the question. This helps with alignment and prevents the system from wandering down paths that are not salient to the user.

The system design is motivated more-so by work in [Decision Support Systems](https://dspace.mit.edu/handle/1721.1/47172) and [Knowledge-Based Systems](https://www.reidgsmith.com/Knowledge-Based_Systems_-_Concepts_Techniques_Examples_08-May-1985.pdf) than modern machine learning.



#### Sources:

StreamLit Session State code credit goes to [Ghasel](https://gist.github.com/Ghasel/0aba4869ba6fdc8d49132e6974e2e662).
