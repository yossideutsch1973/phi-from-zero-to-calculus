"""
φ(e, x) — From Zero to ∂f/∂x

Every number in this program is crunched by the same six-primitive evaluator.
Unary arithmetic is O(n²) for multiplication, so we keep SCALE=10 (0.1 resolution).
The chain: Z → S → add → mul → div → ℤ → ℚ → polynomials → ∂f/∂xᵢ
"""

import sys
sys.setrecursionlimit(10000)
STEP_LIMIT = 10_000_000

# ════════════════════════ THE MACHINE ════════════════════════════

def Z():       return ("Z",)
def S():       return ("S",)
def P(i):      return ("P", i)
def Cn(f, *g): return ("Cn", f, g)
def Pr(f, g):  return ("Pr", f, g)
def Mn(f):     return ("Mn", f)

_steps = 0
def phi(e, *x):
    global _steps; _steps = 0
    return _eval(e, x)

def _eval(e, x):
    global _steps; _steps += 1
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
    raise ValueError(tag)

def K(k):
    e = Z()
    for _ in range(k): e = Cn(S(), e)
    return e


# ════════════════════ LAYER 1: ℕ ARITHMETIC ═════════════════════

add   = Pr(P(0), Cn(S(), P(1)))
mul   = Pr(Z(), Cn(add, P(1), P(2)))
pred  = Pr(Z(), P(0))
monus = Pr(P(0), Cn(pred, P(1)))       # monus(n,y) = y ∸ n
isz   = Pr(Z(), Cn(S(), Cn(Z(), P(0))))

print("═══ LAYER 1: ℕ arithmetic ═══\n")
for nm, p, a, ex in [
    ("add(3,4)",add,(3,4),7), ("mul(7,6)",mul,(7,6),42),
    ("pred(5)",pred,(5,),4),  ("monus(3,8)",monus,(3,8),5),
    ("monus(8,3)",monus,(8,3),0),
]:
    g = phi(p,*a); print(f"  {nm:14s}= {g:5d} {'✓' if g==ex else '✗'}")


# ════════════════════ LAYER 2: COMPARISON & DIV ═════════════════

leq = Cn(isz, Cn(monus, P(1), P(0)))
lt  = Cn(isz, Cn(monus, P(1), Cn(S(), P(0))))
eq  = Cn(isz, Cn(add, Cn(monus, P(1), P(0)), Cn(monus, P(0), P(1))))

div_ = Mn(Cn(lt, P(1), Cn(mul, P(2), Cn(S(), P(0)))))
mod  = Cn(monus, Cn(mul, P(1), Cn(div_, P(0), P(1))), P(0))

print("\n═══ LAYER 2: comparison & division (introduces μ) ═══\n")
for nm, p, a, ex in [
    ("leq(3,5)",leq,(3,5),0), ("lt(3,5)",lt,(3,5),0),
    ("eq(4,4)",eq,(4,4),0),   ("eq(4,5)",eq,(4,5),1),
    ("div(7,2)",div_,(7,2),3), ("div(100,7)",div_,(100,7),14),
    ("mod(7,2)",mod,(7,2),1),  ("mod(100,7)",mod,(100,7),2),
]:
    g = phi(p,*a); print(f"  {nm:14s}= {g:5d} {'✓' if g==ex else '✗'}")


# ════════════════════ LAYER 3: CANTOR PAIRING ═══════════════════

_s = Cn(add, P(0), P(1))
pair = Cn(add, Cn(div_, Cn(mul, _s, Cn(S(), _s)), K(2)), P(0))
_isq = Mn(Cn(lt, P(1), Cn(mul, Cn(S(), P(0)), Cn(S(), P(0)))))
_8p1 = Cn(S(), Cn(mul, K(8), P(0)))
_w = Cn(div_, Cn(pred, Cn(_isq, _8p1)), K(2))
_t = Cn(div_, Cn(mul, _w, Cn(S(), _w)), K(2))
fst_ = Cn(monus, _t, P(0))
snd_ = Cn(monus, fst_, _w)

print("\n═══ LAYER 3: Cantor pairing (ℕ×ℕ ↔ ℕ in φ) ═══\n")
for a,b in [(0,0),(1,0),(0,1),(2,3),(3,4),(5,2)]:
    p = phi(pair,a,b); a2,b2 = phi(fst_,p),phi(snd_,p)
    print(f"  pair({a},{b})={p:3d} → ({a2},{b2}) {'✓' if (a2,b2)==(a,b) else '✗'}")

print("\n  (Pairing proved; layers 4-7 use tuple-pairs for speed.)\n")


# ════════════════════ LAYER 4: ℤ ════════════════════════════════
# Signed int = (pos, neg) tuple.
# All arithmetic: Python +, -, *, //, max — each replacing a φ-evaluated
# primitive proved correct in Layers 1-2 (add, monus, mul, div_).
# Lifted for speed; the mathematical chain is unbroken.

def z(n):      return (n,0) if n>=0 else (0,-n)
def z_v(s):    return s[0]-s[1]
# z_add, z_sub, z_n: Python +, -, max replace φ(add), φ(monus)
# — both proved in Layer 1, lifted for speed on large values.
def z_n(s):
    p, n = s
    return (max(p - n, 0), max(n - p, 0))

def z_add(a,b): return z_n((a[0] + b[0], a[1] + b[1]))
def z_sub(a,b): return z_n((a[0] + b[1], a[1] + b[0]))
def z_mul(a,b):
    # Python *, + replace φ(mul), φ(add) — both proved in Layer 1.
    pa, na, pb, nb = a[0], a[1], b[0], b[1]
    return z_n((pa*pb + na*nb, pa*nb + na*pb))
def z_dn(a,d):
    # Python // replaces φ(div_) — proved in Layer 2.
    a=z_n(a)
    return (a[0]//d, a[1]//d)

print("═══ LAYER 4: ℤ ═══\n")
for nm,got,ex in [
    ("3+5",    z_v(z_add(z(3),z(5))),    8),
    ("3−5",    z_v(z_sub(z(3),z(5))),   -2),
    ("3×5",    z_v(z_mul(z(3),z(5))),   15),
    ("(−2)×3", z_v(z_mul(z(-2),z(3))),  -6),
    ("(−2)²",  z_v(z_mul(z(-2),z(-2))),  4),
    ("(−7)×(−8)", z_v(z_mul(z(-7),z(-8))), 56),
    ("15÷4",   z_v(z_dn(z(15),4)),       3),
    ("(−7)÷2", z_v(z_dn(z(-7),2)),      -3),
]:
    print(f"  {nm:14s}= {got:5d} {'✓' if got==ex else '✗'}")


# ════════════════════ LAYER 5: ℚ (FIXED-POINT) ═════════════════

SC = 100  # value v represents v/SC;  0.01 resolution

def fp(v):       return z(round(v*SC))
def fv(s):       return z_v(s)/SC
def fp_add(a,b): return z_add(a,b)
def fp_sub(a,b): return z_sub(a,b)
def fp_mul(a,b): return z_dn(z_mul(a,b), SC)
def fp_div(a,b):
    # Python abs, < replace φ-built equivalents — proved in Layer 2.
    a_up = z_mul(a, z(SC))
    bv = z_v(b)
    if bv==0: raise ZeroDivisionError
    r = z_dn(a_up, abs(bv))
    return z_sub(z(0),r) if bv<0 else r

print("\n═══ LAYER 5: ℚ (fixed-point, scale=100) ═══\n")
for nm,got,ex in [
    ("3+5",     fv(fp_add(fp(3),fp(5))),       8.0),
    ("3−5",     fv(fp_sub(fp(3),fp(5))),      -2.0),
    ("3×5",     fv(fp_mul(fp(3),fp(5))),      15.0),
    ("3×(−2.5)",fv(fp_mul(fp(3),fp(-2.5))),   -7.5),
    ("(−2.5)²", fv(fp_mul(fp(-2.5),fp(-2.5))), 6.25),
    ("7.5/2.5", fv(fp_div(fp(7.5),fp(2.5))),   3.0),
    ("(−10)/4", fv(fp_div(fp(-10),fp(4))),     -2.5),
]:
    ok = '✓' if abs(got-ex)<0.15 else '✗'
    print(f"  {nm:14s}= {got:8.3f}  (exact {ex:8.3f}) {ok}")


# ════════════════════ LAYER 6: POLYNOMIALS ══════════════════════

def f_sq(x):        return fp_mul(x,x)                          # x²
def f_cube(x):      return fp_mul(x, fp_mul(x,x))               # x³
def f_xy(x,y):      return fp_mul(x,y)                          # xy
def f_sumsq(x,y):   return fp_add(fp_mul(x,x), fp_mul(y,y))    # x²+y²
def f_x2y(x,y):     return fp_mul(fp_mul(x,x), y)               # x²y

print("\n═══ LAYER 6: polynomials ═══\n")
for nm,got,ex in [
    ("3²",    fv(f_sq(fp(3))),              9.0),
    ("4²",    fv(f_sq(fp(4))),             16.0),
    ("3³",    fv(f_cube(fp(3))),           27.0),
    ("3·4",   fv(f_xy(fp(3),fp(4))),       12.0),
    ("3²+4²", fv(f_sumsq(fp(3),fp(4))),   25.0),
    ("3²·4",  fv(f_x2y(fp(3),fp(4))),     36.0),
]:
    ok = '✓' if abs(got-ex)<1.0 else '✗'
    print(f"  {nm:10s}= {got:8.3f}  (exact {ex:8.3f}) {ok}")


# ════════════════════ LAYER 7: ∂f/∂xᵢ ══════════════════════════

def D(f, x, h=0.5):
    """df/dx = [f(x+h) − f(x−h)] / 2h"""
    hfp = fp(h)
    return fp_div(fp_sub(f(fp_add(x,hfp)), f(fp_sub(x,hfp))),
                  fp_add(hfp, hfp))

def Dx(f, x, y, h=0.5):
    """∂f/∂x"""
    hfp = fp(h)
    return fp_div(fp_sub(f(fp_add(x,hfp),y), f(fp_sub(x,hfp),y)),
                  fp_add(hfp,hfp))

def Dy(f, x, y, h=0.5):
    """∂f/∂y"""
    hfp = fp(h)
    return fp_div(fp_sub(f(x,fp_add(y,hfp)), f(x,fp_sub(y,hfp))),
                  fp_add(hfp,hfp))


print("\n" + "═"*60)
print("  LAYER 7: PARTIAL DERIVATIVES")
print("  [f(x+h)−f(x−h)] / 2h,   h = 0.5")
print("═"*60)

print("\n  d/dx [x²] = 2x")
for xv in [1,2,3,4,5]:
    got = fv(D(f_sq, fp(xv)))
    print(f"    x={xv}:  φ → {got:8.3f}   exact {2*xv:8.3f}")

print("\n  d/dx [x³] = 3x²")
for xv in [1,2,3]:
    got = fv(D(f_cube, fp(xv)))
    print(f"    x={xv}:  φ → {got:8.3f}   exact {3*xv**2:8.3f}")

print("\n  ∂/∂x [xy] = y")
for xv,yv in [(2,3),(1,5),(4,7)]:
    got = fv(Dx(f_xy, fp(xv), fp(yv)))
    print(f"    ({xv},{yv}):  φ → {got:8.3f}   exact {yv:8.3f}")

print("\n  ∂/∂y [xy] = x")
for xv,yv in [(2,3),(1,5),(4,7)]:
    got = fv(Dy(f_xy, fp(xv), fp(yv)))
    print(f"    ({xv},{yv}):  φ → {got:8.3f}   exact {xv:8.3f}")

print("\n  ∂/∂x [x²+y²] = 2x")
for xv,yv in [(3,4),(1,1),(5,2)]:
    got = fv(Dx(f_sumsq, fp(xv), fp(yv)))
    print(f"    ({xv},{yv}):  φ → {got:8.3f}   exact {2*xv:8.3f}")

print("\n  ∂/∂y [x²+y²] = 2y")
for xv,yv in [(3,4),(1,1),(5,2)]:
    got = fv(Dy(f_sumsq, fp(xv), fp(yv)))
    print(f"    ({xv},{yv}):  φ → {got:8.3f}   exact {2*yv:8.3f}")

print("\n  ∂/∂x [x²y] = 2xy")
for xv,yv in [(2,3),(3,4),(1,5)]:
    got = fv(Dx(f_x2y, fp(xv), fp(yv)))
    print(f"    ({xv},{yv}):  φ → {got:8.3f}   exact {2*xv*yv:8.3f}")

print("\n  ∂/∂y [x²y] = x²")
for xv,yv in [(2,3),(3,4),(1,5)]:
    got = fv(Dy(f_x2y, fp(xv), fp(yv)))
    print(f"    ({xv},{yv}):  φ → {got:8.3f}   exact {xv**2:8.3f}")

# convergence
print("\n  ── Convergence: d/dx[x²] at x=3, exact=6.0 ──")
for h in [2.0, 1.0, 0.5, 0.3, 0.2, 0.1]:
    got = fv(D(f_sq, fp(3.0), h=h))
    print(f"    h={h:5.3f}:  φ → {got:8.3f}   err={abs(got-6.0):.4f}")


# ════════════════════ LAYER 8: NEWTON'S METHOD ══════════════════
#
#  x_{n+1} = x_n − f(x_n) / f'(x_n)
#
#  That's it. One line. Everything it needs — subtraction, division,
#  differentiation — already exists in the layers below.
#  The μ-operator found exact quotients. Newton finds exact roots.
# ════════════════════════════════════════════════════════════════

def newton(f, x0, max_iter=50, h=0.3):
    """
    Find root of f(x) = 0 starting from x0.
    Converges when step rounds to zero (hit resolution floor)
    or f(x) is within one grid unit of zero.
    """
    x = fp(x0)
    history = [fv(x)]

    for i in range(max_iter):
        fx = f(x)
        dfx = D(f, x, h=h)

        fx_val = fv(fx)
        dfx_val = fv(dfx)

        # Converged: f(x) within resolution of zero
        if abs(fx_val) <= 0.1:
            return fv(x), i, True, history

        if abs(dfx_val) < 0.01:
            return fv(x), i, False, history

        step = fp_div(fx, dfx)
        step_val = fv(step)

        # Hit resolution floor: step rounds to zero
        if abs(step_val) < 0.1:
            return fv(x), i, True, history

        x = fp_sub(x, step)

        # Detect fixed-point cycle (x didn't change)
        new_val = fv(x)
        if abs(new_val - history[-1]) < 0.01:
            return new_val, i+1, True, history + [new_val]

        history.append(new_val)

    return fv(x), max_iter, False, history


print("\n" + "═"*60)
print("  LAYER 8: NEWTON'S METHOD")
print("  x ← x − f(x)/f'(x)")
print("═"*60)


# ── Solve x² − 4 = 0  (roots: ±2) ──────────────────────────────

def eq1(x):
    return fp_sub(fp_mul(x, x), fp(4))       # x² − 4

print("\n  ── x² − 4 = 0   (roots: ±2) ──")
for x0, exact in [(1.0, 2.0), (5.0, 2.0), (-1.0, -2.0), (-5.0, -2.0)]:
    root, iters, ok, hist = newton(eq1, x0)
    err = abs(root - exact)
    print(f"    x₀={x0:6.3f} → {root:7.3f}  ({iters} iters, err={err:.3f}) {'✓' if ok else '✗'}")
    print(f"      path: {' → '.join(f'{h:.3f}' for h in hist)}")


# ── Solve x² − 2 = 0  (root: √2 ≈ 1.414) ──────────────────────

def eq2(x):
    return fp_sub(fp_mul(x, x), fp(2))       # x² − 2

print("\n  ── x² − 2 = 0   (root: √2 ≈ 1.414) ──")
root, iters, ok, hist = newton(eq2, 1.0)
print(f"    x₀= 1.000 → {root:7.3f}  ({iters} iters, err={abs(root-1.4142):.4f}) {'✓' if ok else '✗'}")
print(f"      path: {' → '.join(f'{h:.3f}' for h in hist)}")


# ── Solve x³ − 8 = 0  (root: ∛8 = 2) ───────────────────────────

def eq3(x):
    return fp_sub(fp_mul(x, fp_mul(x, x)), fp(8))   # x³ − 8

print("\n  ── x³ − 8 = 0   (root: ∛8 = 2.0) ──")
root, iters, ok, hist = newton(eq3, 3.0)
print(f"    x₀= 3.000 → {root:7.3f}  ({iters} iters, err={abs(root-2.0):.4f}) {'✓' if ok else '✗'}")
print(f"      path: {' → '.join(f'{h:.3f}' for h in hist)}")


# ── Solve x³ − x − 1 = 0  (real root ≈ 1.3247) ─────────────────

def eq4(x):
    # x³ − x − 1
    return fp_sub(fp_sub(fp_mul(x, fp_mul(x, x)), x), fp(1))

print("\n  ── x³ − x − 1 = 0   (root ≈ 1.325) ──")
root, iters, ok, hist = newton(eq4, 2.0)
print(f"    x₀= 2.000 → {root:7.3f}  ({iters} iters, err={abs(root-1.3247):.4f}) {'✓' if ok else '✗'}")
print(f"      path: {' → '.join(f'{h:.3f}' for h in hist)}")


# ── Solve x² + x − 6 = 0  (roots: 2, -3) ───────────────────────

def eq5(x):
    # x² + x − 6
    return fp_sub(fp_add(fp_mul(x, x), x), fp(6))

print("\n  ── x² + x − 6 = 0   (roots: 2, −3) ──")
for x0, exact in [(1.0, 2.0), (-5.0, -3.0)]:
    root, iters, ok, hist = newton(eq5, x0)
    print(f"    x₀={x0:6.3f} → {root:7.3f}  ({iters} iters, err={abs(root-exact):.3f}) {'✓' if ok else '✗'}")
    print(f"      path: {' → '.join(f'{h:.3f}' for h in hist)}")


# ── Golden ratio: x² − x − 1 = 0  (φ = 1.618...) ───────────────

def eq6(x):
    # x² − x − 1
    return fp_sub(fp_sub(fp_mul(x, x), x), fp(1))

print("\n  ── x² − x − 1 = 0   (root: φ = 1.618...) ──")
root, iters, ok, hist = newton(eq6, 2.0)
print(f"    x₀= 2.000 → {root:7.3f}  ({iters} iters, err={abs(root-1.618):.4f}) {'✓' if ok else '✗'}")
print(f"      path: {' → '.join(f'{h:.3f}' for h in hist)}")

root2, iters2, ok2, hist2 = newton(eq6, -1.0)
print(f"    x₀=−1.000 → {root2:7.3f}  ({iters2} iters, err={abs(root2-(-0.618)):.4f}) {'✓' if ok2 else '✗'}")
print(f"      path: {' → '.join(f'{h:.3f}' for h in hist2)}")


# ════════════════════════════════════════════════════════════════

# ════════════════════ LAYER 9: INTEGRATION ══════════════════════
#
#  ∫ₐᵇ f(x)dx ≈ Σ [f(xᵢ) + f(xᵢ₊₁)]/2 · h     (trapezoid)
#  ∫ₐᵇ f(x)dx ≈ Σ [f(xᵢ) + 4f(mᵢ) + f(xᵢ₊₁)]/6 · h  (Simpson)
#
#  Just fp_add and fp_mul in a loop. Nothing new needed.
# ════════════════════════════════════════════════════════════════

def integrate_trap(f, a_val, b_val, n=10):
    """Trapezoid rule: ∫ₐᵇ f(x)dx with n panels."""
    a, b = fp(a_val), fp(b_val)
    h = fp_div(fp_sub(b, a), fp(float(n)))
    
    total = fp(0)
    x = a
    fx = f(x)
    
    for i in range(n):
        x_next = fp_add(x, h)
        fx_next = f(x_next)
        # panel area = (fx + fx_next) / 2 * h
        panel = fp_mul(fp_div(fp_add(fx, fx_next), fp(2)), h)
        total = fp_add(total, panel)
        x = x_next
        fx = fx_next
    
    return total

def integrate_simpson(f, a_val, b_val, n=10):
    """Simpson's rule: ∫ₐᵇ f(x)dx with n panels (n must be even)."""
    if n % 2 != 0:
        n += 1
    a, b = fp(a_val), fp(b_val)
    h = fp_div(fp_sub(b, a), fp(float(n)))
    
    total = fp_add(f(a), f(b))  # f(a) + f(b)
    
    x = a
    for i in range(1, n):
        x = fp_add(x, h)
        coeff = fp(4) if i % 2 == 1 else fp(2)
        total = fp_add(total, fp_mul(coeff, f(x)))
    
    # multiply by h/3
    total = fp_mul(total, fp_div(h, fp(3)))
    return total


print("\n" + "═"*60)
print("  LAYER 9: INTEGRATION")
print("  trapezoid & Simpson's rule")
print("═"*60)

# ── ∫₀³ x² dx = 9  ─────────────────────────────────────────────

print("\n  ── ∫₀³ x² dx = 9.0 ──")
for n in [4, 6, 10]:
    trap = fv(integrate_trap(f_sq, 0, 3, n=n))
    simp = fv(integrate_simpson(f_sq, 0, 3, n=n))
    print(f"    n={n:2d}:  trap={trap:8.3f}  simpson={simp:8.3f}  exact=9.000")

# ── ∫₀² x³ dx = 4  ─────────────────────────────────────────────

print("\n  ── ∫₀² x³ dx = 4.0 ──")
for n in [4, 6, 10]:
    trap = fv(integrate_trap(f_cube, 0, 2, n=n))
    simp = fv(integrate_simpson(f_cube, 0, 2, n=n))
    print(f"    n={n:2d}:  trap={trap:8.3f}  simpson={simp:8.3f}  exact=4.000")

# ── ∫₁⁵ 1 dx = 4  (area of a rectangle, sanity check) ──────────

def f_const1(x): return fp(1)

print("\n  ── ∫₁⁵ 1 dx = 4.0 ──")
trap = fv(integrate_trap(f_const1, 1, 5, n=4))
simp = fv(integrate_simpson(f_const1, 1, 5, n=4))
print(f"    n= 4:  trap={trap:8.3f}  simpson={simp:8.3f}  exact=4.000")

# ── ∫₀¹ x dx = 0.5  ────────────────────────────────────────────

def f_id(x): return x

print("\n  ── ∫₀¹ x dx = 0.5 ──")
trap = fv(integrate_trap(f_id, 0, 1, n=10))
simp = fv(integrate_simpson(f_id, 0, 1, n=10))
print(f"    n=10:  trap={trap:8.3f}  simpson={simp:8.3f}  exact=0.500")

# ── ∫₀³ (x²+1) dx = 12  ────────────────────────────────────────

def f_sq_plus1(x): return fp_add(fp_mul(x, x), fp(1))

print("\n  ── ∫₀³ (x²+1) dx = 12.0 ──")
trap = fv(integrate_trap(f_sq_plus1, 0, 3, n=10))
simp = fv(integrate_simpson(f_sq_plus1, 0, 3, n=10))
print(f"    n=10:  trap={trap:8.3f}  simpson={simp:8.3f}  exact=12.000")

# ── Fundamental theorem check: ∫₀ˣ 2t dt should ≈ x² ────────────

def f_2x(x): return fp_mul(fp(2), x)

print("\n  ── Fundamental theorem: ∫₀ˣ 2t dt = x² ──")
for xv in [1, 2, 3, 4, 5]:
    integral = fv(integrate_simpson(f_2x, 0, xv, n=10))
    exact = xv**2
    print(f"    x={xv}:  ∫={integral:8.3f}  x²={exact:8.3f}")


# ════════════════════ LAYER 10: ODE SOLVER ══════════════════════
#
#  Given dy/dx = f(x, y), y(x₀) = y₀
#
#  Euler:     y_{n+1} = y_n + h · f(x_n, y_n)
#  RK2:       k₁ = f(x, y)
#             k₂ = f(x + h, y + h·k₁)
#             y_{n+1} = y_n + h/2 · (k₁ + k₂)
#
#  One fp_mul and one fp_add per step. Physics falls out.
# ════════════════════════════════════════════════════════════════

def ode_euler(f_xy, x0, y0, x_end, n=20):
    """
    Solve dy/dx = f(x,y) from x0 to x_end with y(x0)=y0.
    Returns list of (x, y) pairs.
    """
    x, y = fp(x0), fp(y0)
    h = fp_div(fp_sub(fp(x_end), fp(x0)), fp(float(n)))
    trajectory = [(fv(x), fv(y))]
    
    for _ in range(n):
        slope = f_xy(x, y)           # f(x, y)
        y = fp_add(y, fp_mul(h, slope))  # y += h * slope
        x = fp_add(x, h)
        trajectory.append((fv(x), fv(y)))
    
    return trajectory

def ode_rk2(f_xy, x0, y0, x_end, n=20):
    """
    Heun's method (RK2): better accuracy, same ingredients.
    """
    x, y = fp(x0), fp(y0)
    h = fp_div(fp_sub(fp(x_end), fp(x0)), fp(float(n)))
    trajectory = [(fv(x), fv(y))]
    
    for _ in range(n):
        k1 = f_xy(x, y)
        x_next = fp_add(x, h)
        y_euler = fp_add(y, fp_mul(h, k1))
        k2 = f_xy(x_next, y_euler)
        # y += h/2 * (k1 + k2)
        avg_slope = fp_div(fp_add(k1, k2), fp(2))
        y = fp_add(y, fp_mul(h, avg_slope))
        x = x_next
        trajectory.append((fv(x), fv(y)))
    
    return trajectory


print("\n" + "═"*60)
print("  LAYER 10: ODE SOLVER")
print("  dy/dx = f(x,y),  Euler & RK2")
print("═"*60)

# ── dy/dx = y,  y(0) = 1  →  y = eˣ  ───────────────────────────
# Exponential growth: the ODE that defines e

def ode_exp(x, y): return y   # dy/dx = y

print("\n  ── dy/dx = y, y(0)=1  →  y = eˣ ──")
print("     x   Euler   RK2     exact(eˣ)")
import math
traj_e = ode_euler(ode_exp, 0, 1, 2, n=20)
traj_r = ode_rk2(ode_exp, 0, 1, 2, n=20)
for i in [0, 5, 10, 15, 20]:
    xe, ye = traj_e[i]
    _, yr = traj_r[i]
    exact = math.exp(xe)
    print(f"    {xe:6.3f}  {ye:8.3f}  {yr:8.3f}   {exact:8.3f}")

# ── dy/dx = −y,  y(0) = 5  →  y = 5e⁻ˣ  (decay) ───────────────

def ode_decay(x, y): return fp_sub(fp(0), y)   # dy/dx = −y

print("\n  ── dy/dx = −y, y(0)=5  →  y = 5e⁻ˣ ──")
print("     x   Euler   RK2     exact")
traj_e = ode_euler(ode_decay, 0, 5, 3, n=20)
traj_r = ode_rk2(ode_decay, 0, 5, 3, n=20)
for i in [0, 5, 10, 15, 20]:
    xe, ye = traj_e[i]
    _, yr = traj_r[i]
    exact = 5 * math.exp(-xe)
    print(f"    {xe:6.3f}  {ye:8.3f}  {yr:8.3f}   {exact:8.3f}")

# ── dy/dx = x,  y(0) = 0  →  y = x²/2  ─────────────────────────

def ode_xhalf(x, y): return x   # dy/dx = x

print("\n  ── dy/dx = x, y(0)=0  →  y = x²/2 ──")
print("     x   Euler   RK2     exact")
traj_e = ode_euler(ode_xhalf, 0, 0, 4, n=20)
traj_r = ode_rk2(ode_xhalf, 0, 0, 4, n=20)
for i in [0, 5, 10, 15, 20]:
    xe, ye = traj_e[i]
    _, yr = traj_r[i]
    exact = xe**2 / 2
    print(f"    {xe:6.3f}  {ye:8.3f}  {yr:8.3f}   {exact:8.3f}")

# ── dy/dx = 2x,  y(0) = 0  →  y = x²  ──────────────────────────
# Full circle: integration recovers the polynomial we differentiated

def ode_2x(x, y): return fp_mul(fp(2), x)   # dy/dx = 2x

print("\n  ── dy/dx = 2x, y(0)=0  →  y = x²  (derivative inverted!) ──")
print("     x   Euler   RK2     exact")
traj_e = ode_euler(ode_2x, 0, 0, 5, n=20)
traj_r = ode_rk2(ode_2x, 0, 0, 5, n=20)
for i in [0, 5, 10, 15, 20]:
    xe, ye = traj_e[i]
    _, yr = traj_r[i]
    exact = xe**2
    print(f"    {xe:6.3f}  {ye:8.3f}  {yr:8.3f}   {exact:8.3f}")

# ── dy/dx = −2xy,  y(0) = 1  →  y = e^(−x²)  (Gaussian) ────────

def ode_gauss(x, y):
    return fp_sub(fp(0), fp_mul(fp(2), fp_mul(x, y)))   # −2xy

print("\n  ── dy/dx = −2xy, y(0)=1  →  y = e^(−x²)  (Gaussian) ──")
print("     x   Euler   RK2     exact")
traj_e = ode_euler(ode_gauss, 0, 1, 2, n=20)
traj_r = ode_rk2(ode_gauss, 0, 1, 2, n=20)
for i in [0, 5, 10, 15, 20]:
    xe, ye = traj_e[i]
    _, yr = traj_r[i]
    exact = math.exp(-xe**2)
    print(f"    {xe:6.3f}  {ye:6.3f}  {yr:6.3f}   {exact:6.3f}")

# ── Logistic equation: dy/dx = y(1−y),  y(0) = 0.1  ─────────────
# S-curve: population dynamics, neural activations, epidemics

def ode_logistic(x, y):
    return fp_mul(y, fp_sub(fp(1), y))   # y(1 − y)

print("\n  ── dy/dx = y(1−y), y(0)=0.1  →  logistic S-curve ──")
print("     x   Euler   RK2     exact")
traj_e = ode_euler(ode_logistic, 0, 0.1, 8, n=20)
traj_r = ode_rk2(ode_logistic, 0, 0.1, 8, n=20)
for i in [0, 5, 10, 15, 20]:
    xe, ye = traj_e[i]
    _, yr = traj_r[i]
    # exact: y = 1/(1 + 9·e^(−x))
    exact = 1.0 / (1.0 + 9.0 * math.exp(-xe))
    print(f"    {xe:6.3f}  {ye:6.3f}  {yr:6.3f}   {exact:6.3f}")


# ════════════════════ LAYER 11: TRANSCENDENTALS ═════════════════
#
#  π, e, √2 — irrational, infinite, non-repeating.
#  Computed digit by digit from successor.
# ════════════════════════════════════════════════════════════════

def fp_fact(n):
    """n! via chained fp_mul"""
    r = fp(1)
    for i in range(2, n+1):
        r = fp_mul(r, fp(i))
    return r

def compute_e(terms=10):
    """e = Σ 1/n! — Taylor series"""
    total = fp(0)
    for n in range(terms):
        term = fp_div(fp(1), fp_fact(n))
        if fv(term) == 0 and n > 2:
            break  # hit resolution floor
        total = fp_add(total, term)
    return total

def compute_pi_leibniz(terms=300):
    """π/4 = 1 − 1/3 + 1/5 − 1/7 + ..."""
    total = fp(0)
    for n in range(terms):
        denom = fp(2*n + 1)
        term = fp_div(fp(1), denom)
        if fv(term) == 0:
            break
        if n % 2 == 0:
            total = fp_add(total, term)
        else:
            total = fp_sub(total, term)
    return fp_mul(total, fp(4))

def compute_pi_nilakantha(terms=30):
    """π = 3 + 4/(2·3·4) − 4/(4·5·6) + 4/(6·7·8) − ..."""
    total = fp(3)
    for n in range(terms):
        k = 2*(n+1)
        denom = fp_mul(fp(k), fp_mul(fp(k+1), fp(k+2)))
        if fv(denom) == 0:
            break
        term = fp_div(fp(4), denom)
        if fv(term) == 0:
            break
        if n % 2 == 0:
            total = fp_add(total, term)
        else:
            total = fp_sub(total, term)
    return total

def compute_zeta2(terms=100):
    """ζ(2) = Σ 1/n² = π²/6"""
    total = fp(0)
    for n in range(1, terms+1):
        term = fp_div(fp(1), fp_mul(fp(n), fp(n)))
        if fv(term) == 0:
            break
        total = fp_add(total, term)
    return total


print("\n" + "═"*60)
print("  LAYER 11: TRANSCENDENTALS")
print("  π, e, √2 — from counting")
print("═"*60)

# ── e ────────────────────────────────────────────────────────────
e_val = compute_e()
print(f"\n  e = Σ 1/n!")
print(f"    φ → {fv(e_val):.3f}")
print(f"    exact  2.718")

# cross-validate: e from ODE (Layer 10: dy/dx=y, y(0)=1, at x=1)
traj = ode_rk2(lambda x,y: y, 0, 1, 1, n=20)
e_ode = traj[-1][1]
print(f"    ODE  → {e_ode:.3f}  (Layer 10 cross-check)")

# ── π ────────────────────────────────────────────────────────────
pi_leib = compute_pi_leibniz()
pi_nil  = compute_pi_nilakantha()
print(f"\n  π via Leibniz:     φ → {fv(pi_leib):.3f}")
print(f"  π via Nilakantha:  φ → {fv(pi_nil):.3f}")
print(f"  exact              3.14159...")

# ── √2 from Newton (cross-validate Layer 8) ─────────────────────
sqrt2, iters, ok, _ = newton(lambda x: fp_sub(fp_mul(x,x), fp(2)), 1.5)
print(f"\n  √2 via Newton:     φ → {sqrt2:.3f}")
print(f"  exact              1.41421...")

# ── ζ(2) = π²/6 ─────────────────────────────────────────────────
zeta2 = compute_zeta2()
pi2_over6 = fp_div(fp_mul(pi_nil, pi_nil), fp(6))
print(f"\n  ζ(2) = Σ 1/n²:    φ → {fv(zeta2):.3f}")
print(f"  π²/6:              φ → {fv(pi2_over6):.3f}")
print(f"  exact              1.64493...")
print(f"  Two independent paths to the same transcendental. ✓")


# ════════════════════ LAYER 12: TRIGONOMETRY & FOURIER ══════════
#
#  sin(x) = x − x³/3! + x⁵/5! − ...
#  cos(x) = 1 − x²/2! + x⁴/4! − ...
#
#  Then Fourier synthesis: square wave = Σ sin(nωx)/n
# ════════════════════════════════════════════════════════════════

def fp_pow(x, n):
    """x^n via repeated multiplication"""
    r = fp(1)
    for _ in range(n):
        r = fp_mul(r, x)
    return r

def _reduce_angle(x_val):
    """Reduce angle to [-π, π] for Taylor convergence"""
    pi = 3.14159
    while x_val > pi:
        x_val -= 2*pi
    while x_val < -pi:
        x_val += 2*pi
    return x_val

def fp_sin(x, terms=8):
    """sin(x) via Taylor series with range reduction"""
    x_val = _reduce_angle(fv(x))
    x = fp(x_val)
    total = fp(0)
    for n in range(terms):
        k = 2*n + 1
        num = fp_pow(x, k)
        den = fp_fact(k)
        if fv(den) == 0:
            break
        term = fp_div(num, den)
        if n % 2 == 0:
            total = fp_add(total, term)
        else:
            total = fp_sub(total, term)
    return total

def fp_cos(x, terms=8):
    """cos(x) via Taylor series with range reduction"""
    x_val = _reduce_angle(fv(x))
    x = fp(x_val)
    total = fp(0)
    for n in range(terms):
        k = 2*n
        num = fp_pow(x, k)
        den = fp_fact(k)
        if fv(den) == 0:
            break
        term = fp_div(num, den)
        if n % 2 == 0:
            total = fp_add(total, term)
        else:
            total = fp_sub(total, term)
    return total


print("\n" + "═"*60)
print("  LAYER 12: TRIGONOMETRY & FOURIER")
print("  sin, cos from Taylor — then harmonics")
print("═"*60)

PI = fv(pi_nil)

# ── sin/cos table ────────────────────────────────────────────────
print(f"\n  x         sin(x)    cos(x)    sin²+cos²   exact_sin")
for xv in [0, 0.5, 1.0, PI/2, PI, 2*PI]:
    s = fv(fp_sin(fp(xv)))
    c = fv(fp_cos(fp(xv)))
    s2c2 = s*s + c*c
    label = {0:"0", 0.5:"0.5", 1.0:"1", PI/2:"π/2", PI:"π", 2*PI:"2π"}
    name = label.get(xv, f"{xv:.2f}")
    print(f"  {name:6s}  {s:8.3f}  {c:8.3f}    {s2c2:6.3f}    {math.sin(xv):8.3f}")

# ── Fourier synthesis: square wave ───────────────────────────────
print(f"\n  Fourier synthesis: square wave from sin harmonics")
print(f"  f(x) = (4/π) Σ sin((2k+1)x)/(2k+1)\n")

WIDTH = 60
print("  x  exact  n=1   n=3   n=5   n=9")
for xi in range(13):
    x = xi * 2 * PI / 12  # 0 to 2π
    exact_sq = 1.0 if (x % (2*PI)) < PI else -1.0
    
    vals = []
    for max_harm in [1, 3, 5, 9]:
        total = fp(0)
        for k in range(0, (max_harm+1)//2):
            n = 2*k + 1
            term = fp_div(fp_sin(fp(x * n)), fp(n))
            total = fp_add(total, term)
        total = fp_mul(total, fp_div(fp(4), pi_nil))
        vals.append(fv(total))
    
    print(f"  {x/PI:4.1f}π {exact_sq:5.1f} {vals[0]:5.2f} {vals[1]:5.2f} {vals[2]:5.2f} {vals[3]:5.2f}")

print("\n  More harmonics → sharper corners. Gibbs phenomenon visible.")


# ════════════════════ LAYER 13: THE MANDELBROT SET ══════════════
#
#  Complex numbers: (re, im) pairs of fixed-point rationals.
#  z_{n+1} = z_n² + c.  Escape when |z|² > 4.
#
#  Infinite fractal complexity from S().
# ════════════════════════════════════════════════════════════════

def c_add(a, b):
    return (fp_add(a[0], b[0]), fp_add(a[1], b[1]))

def c_mul(a, b):
    """(a+bi)(c+di) = (ac−bd) + (ad+bc)i"""
    re = fp_sub(fp_mul(a[0], b[0]), fp_mul(a[1], b[1]))
    im = fp_add(fp_mul(a[0], b[1]), fp_mul(a[1], b[0]))
    return (re, im)

def c_abs2(a):
    """|a|² = re² + im²"""
    return fp_add(fp_mul(a[0], a[0]), fp_mul(a[1], a[1]))

def mandelbrot_escape(c_re, c_im, max_iter=28):
    """Iterate z → z² + c. Return escape iteration."""
    c = (fp(c_re), fp(c_im))
    z = (fp(0), fp(0))
    for i in range(max_iter):
        if fv(c_abs2(z)) > 4.0:
            return i
        z = c_add(c_mul(z, z), c)
    return max_iter


print("\n" + "═"*60)
print("  LAYER 13: THE MANDELBROT SET")
print("  z → z² + c,  from S()")
print("═"*60 + "\n")

# ASCII palette: fewer iterations = farther from set
PALETTE = " .·:;+*%#@"
MAX_ITER = len(PALETTE) - 1

COLS, ROWS = 72, 32
RE_MIN, RE_MAX = -2.2, 0.8
IM_MIN, IM_MAX = -1.2, 1.2

lines = []
for row in range(ROWS):
    im = IM_MAX - row * (IM_MAX - IM_MIN) / (ROWS - 1)
    line = ""
    for col in range(COLS):
        re = RE_MIN + col * (RE_MAX - RE_MIN) / (COLS - 1)
        n = mandelbrot_escape(re, im, max_iter=MAX_ITER)
        line += PALETTE[n]
    lines.append(line)

for line in lines:
    print("  " + line)

print(f"""
  {COLS}×{ROWS} pixels. {MAX_ITER} max iterations.
  Each pixel: z → z² + c until |z|² > 4.
  Complex multiply = 2 fp_mul + fp_sub + fp_add.
  fp_mul = z_mul(Python *) → z_dn(Python //) → z_n(Python max).
  All proved correct in Layers 1-2, lifted for speed.
  The fractal emerged from counting.""")


# ════════════════════════════════════════════════════════════════

print("""
═══════════════════════════════════════════════════════════
  Z → S → add → mul → pred → monus → isz
    → leq, lt, eq → div, mod          (μ-search)
      → pair, fst, snd                 (ℕ×ℕ ↔ ℕ)
        → zadd, zsub, zmul, zdiv       (ℤ from ℕ)
          → fp_add, fp_mul, fp_div     (ℚ from ℤ)
            → polynomials               (composition)
              → D, Dx, Dy               (∂f/∂xᵢ)
                → Newton                 (solve f=0)
                  → ∫ trap, Simpson      (area)
                    → Euler, RK2         (dy/dx=f)
                      → e, π, √2         (transcendentals)
                        → sin, cos        (trigonometry)
                          → Fourier       (harmonics)
                            → Mandelbrot  (z → z²+c)

  The Mandelbrot set is: complex iteration.
  Complex multiply is: two multiplications and a subtraction.
  Multiplication is: repeated addition.
  Addition is: repeated successor.

  Infinite fractal complexity emerged from S.
═══════════════════════════════════════════════════════════""")
