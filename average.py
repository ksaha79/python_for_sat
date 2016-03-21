from __future__ import division
def average(seq_in):
    if isinstance(seq_in, (list, tuple)):
        return sum(seq_in) / len(seq_in)
    else:
        return 'Input can only be list or tuple'
