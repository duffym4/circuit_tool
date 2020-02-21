''' Converts Minus/Plus Value to a One/Zero Value
    Useful when sign must be converted to a boolean or multiplier
'''
def mp2oz(v):
    return .5*(-v + 1)