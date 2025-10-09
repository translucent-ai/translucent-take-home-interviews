# Fill me in with your design considerations

I considered changing the embedding implementation over to sentence transformers,
but this did not help with accuracy on the eval.py script.

What did help was changing the selection criteria from top three most similar to those
with above average similarity, and adding a call to Open AI to generate the final answer
based on per-department denial reason counts.
