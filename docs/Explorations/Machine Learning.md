Okay I want to explore this idea I have. The idea is to treat dropping set vectors  as embeddings. I'm not totally fluent in machine learning language, but the idea goes something like this.

We know that semantics can be extracted from vector embeddings - perhaps we could seed weights in such a way that we embed "pure" concepts as a vector in dset_k. And then we create some kind of distance metric between concepts.  And perhaps we generate some kind of metric to compare to the pure dropping sets, or between concepts in general.

As a simple example, let's say 

man = [3, 17, 6]

if we iterate collatz once, we get

[3 -> 10, 17 -> 52, 6 -> 3] -> [10, 52, 3]

There must be some relationship between them. I think it would be interesting to explore the properties here and if there's some way we could represent concepts this way. 


