# Function definitions for terrain generation

def clamp(d, i, j, v, offsets):
    n = d.shape[0]
    res, k = 0, 0
    for p, q in offsets:
        pp, qq = i + p * v, j + q * v
        # Clamp coordinates to the nearest edge
        pp = max(0, min(n - 1, pp))
        qq = max(0, min(n - 1, qq))
        res += d[pp, qq]
        k += 1.0
    return res / k

def fixed(d, i, j, v, offsets):
    n = d.shape[0]
    res, k = 0, 0
    for p, q in offsets:
        pp, qq = i + p * v, j + q * v
        if 0 <= pp < n and 0 <= qq < n:
            res += d[pp, qq]
            k += 1.0
    return res / k

def mirror(d, i, j, v, offsets):
    n = d.shape[0]
    res, k = 0, 0
    for p, q in offsets:
        pp, qq = i + p * v, j + q * v
        if pp < 0 or pp >= n:
            pp = abs(pp) if pp < 0 else 2 * (n - 1) - pp
        if qq < 0 or qq >= n:
            qq = abs(qq) if qq < 0 else 2 * (n - 1) - qq
        res += d[pp, qq]
        k += 1.0
    return res / k

def periodic(d, i, j, v, offsets):
    n = d.shape[0] - 1
    res = 0
    for p, q in offsets:
        res += d[(i + p * v) % n, (j + q * v) % n]
    return res / 4.0

def reflective(d, i, j, v, offsets):
    n = d.shape[0]
    res, k = 0, 0
    for p, q in offsets:
        pp, qq = i + p * v, j + q * v
        if pp < 0:
            pp = -pp
        elif pp >= n:
            pp = 2 * (n - 1) - pp
        if qq < 0:
            qq = -qq
        elif qq >= n:
            qq = 2 * (n - 1) - qq
        res += d[pp, qq]
        k += 1.0
    return res / k

def wrap_around(d, i, j, v, offsets):
    n = d.shape[0]
    res = 0
    for p, q in offsets:
        res += d[(i + p * v) % n, (j + q * v) % n]
    return res / len(offsets)
