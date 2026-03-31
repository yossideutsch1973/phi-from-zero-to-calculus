"""
φ(e, x) — The Universal Partial Recursive Function (minimal version)

Six primitives. One evaluator. Import this to build anything computable.

    from phi_core import phi, Z, S, P, Cn, Pr, Mn, add, mul, pred, monus, div_

Usage:
    >>> phi(add, 3, 4)
    7
    >>> phi(mul, 7, 6)
    42
    >>> phi(div_, 100, 7)
    14
"""

STEP_LIMIT = 10_000_000

# ── The six primitives ────────────────────────────────────────────

def Z():       return ("Z",)          # zero:       λx. 0
def S():       return ("S",)          # successor:  λx. x + 1
def P(i):      return ("P", i)        # projection: λx̄. xᵢ
def Cn(f, *g): return ("Cn", f, g)    # compose:    λx̄. f(g₁(x̄), …, gₖ(x̄))
def Pr(f, g):  return ("Pr", f, g)    # prim. rec:  h(0,x̄)=f(x̄), h(n+1,x̄)=g(n,h(n,x̄),x̄)
def Mn(f):     return ("Mn", f)       # μ-search:   least n s.t. f(n,x̄)=0

# ── The evaluator ─────────────────────────────────────────────────

_steps = 0

def phi(e, *x):
    """Evaluate program e on inputs x."""
    global _steps
    _steps = 0
    return _eval(e, x)

def _eval(e, x):
    global _steps
    _steps += 1
    if _steps > STEP_LIMIT:
        raise RecursionError("φ diverged")
    tag = e[0]
    if   tag == "Z":  return 0
    elif tag == "S":  return x[0] + 1
    elif tag == "P":  return x[e[1]]
    elif tag == "Cn": return _eval(e[1], tuple(_eval(g, x) for g in e[2]))
    elif tag == "Pr":
        n, rest = x[0], x[1:]
        acc = _eval(e[1], rest)
        for i in range(n):
            acc = _eval(e[2], (i, acc) + rest)
        return acc
    elif tag == "Mn":
        n = 0
        while True:
            _steps += 1
            if _steps > STEP_LIMIT:
                raise RecursionError("μ diverged")
            if _eval(e[1], (n,) + x) == 0:
                return n
            n += 1
    raise ValueError(f"unknown: {tag}")

def K(k):
    """Constant function: λx̄. k"""
    e = Z()
    for _ in range(k):
        e = Cn(S(), e)
    return e

# ── Layer 1: ℕ arithmetic ────────────────────────────────────────

add   = Pr(P(0), Cn(S(), P(1)))           # add(n, y) = y + n
mul   = Pr(Z(), Cn(add, P(1), P(2)))      # mul(n, y) = y × n
pred  = Pr(Z(), P(0))                     # pred(0) = 0, pred(n+1) = n
monus = Pr(P(0), Cn(pred, P(1)))          # monus(n, y) = y ∸ n
isz   = Pr(Z(), Cn(S(), Cn(Z(), P(0))))   # 0 if n=0, else 1

# ── Layer 2: comparison & division ────────────────────────────────

leq  = Cn(isz, Cn(monus, P(1), P(0)))                          # 0 if a ≤ b
lt   = Cn(isz, Cn(monus, P(1), Cn(S(), P(0))))                 # 0 if a < b
eq   = Cn(isz, Cn(add, Cn(monus, P(1), P(0)), Cn(monus, P(0), P(1))))
div_ = Mn(Cn(lt, P(1), Cn(mul, P(2), Cn(S(), P(0)))))         # ⌊a/b⌋
mod  = Cn(monus, Cn(mul, P(1), Cn(div_, P(0), P(1))), P(0))   # a mod b


if __name__ == "__main__":
    print("φ(e, x) — The Universal Partial Recursive Function\n")

    for name, prog, args, expect in [
        ("add(3, 4)",   add,  (3, 4),   7),
        ("mul(7, 6)",   mul,  (7, 6),   42),
        ("pred(5)",     pred, (5,),     4),
        ("monus(3, 8)", monus,(3, 8),   5),
        ("div(100, 7)", div_, (100, 7), 14),
        ("mod(100, 7)", mod,  (100, 7), 2),
    ]:
        got = phi(prog, *args)
        print(f"  {name:16s} = {got:5d}  {'✓' if got == expect else '✗'}")

    print("\nSix primitives. One evaluator. Every computable function.")
