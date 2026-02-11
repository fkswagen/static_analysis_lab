def calc(a, b):
    if a <= 0 or b <= 0:
        return 0
    if a > b:
        return a - b
    return b - a