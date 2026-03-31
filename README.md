# φ — From Zero to Calculus

**One recursive function. Six primitives. Thirteen layers. Zero imports from mathematics.**

This project builds a complete numerical analysis stack — from the bare Peano axioms all the way to partial derivatives, Newton's method, numerical integration, and ODE solvers — using a single universal evaluator `φ(e, x)` and the six μ-recursive primitives: **Z** (zero), **S** (successor), **P** (projection), **Cn** (composition), **Pr** (primitive recursion), **Mn** (μ-minimization).

Every number is crunched by the same 30-line interpreter. Calculus emerges from counting.

```
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
```

## Why I built this

While managing the computer vision algorithm team at General Motors Advanced Technology Center, I kept hitting the same wall: I couldn't explain to brilliant engineers *why functional programming matters*. Why pure functions. Why composition. Why treating programs as data. The arguments always sounded like aesthetic preference — "it's cleaner," "it's more testable" — never like a fundamental truth.

This project is my answer. Not an argument. A demonstration.

Six atoms — zero, successor, projection, composition, recursion, search — and nothing else. No state, no mutation, no objects. Just pure functions composed into other pure functions. And from that: arithmetic, algebra, calculus, differential equations, transcendental numbers, trigonometry, Fourier analysis, and the Mandelbrot set. Thirteen layers. The complexity isn't in the parts. It's in the depth of composition.

This is the same principle behind chemistry (~100 atoms, a few bonding rules, every molecule), genetics (4 bases, transcription machinery, every organism), and digital logic (NAND gates, wiring, every computer). Simple atoms composed deeply produce unbounded complexity. Functional programming isn't a style choice. It's what happens when you take this principle seriously in code.

By Layer 7, you cannot write the derivative without passing a function to a function. By Layer 10, you're solving differential equations by composing the same two operations (`fp_add`, `fp_mul`) that you built from successor in Layer 1. Nobody designed this. It falls out of the math. Higher-order functions, referential transparency, programs as data — these aren't features of a paradigm. They're consequences of composition.

This is a gift for my dear friends and colleagues **Lior Stein**, **Michael Michaeli**, **Yael Gefen**, **Yahav Zamari**, and the many others who worked alongside me at GM's Advanced Technology Center. I hope it settles the argument.

## The gap it fills

The computability theory people prove that the μ-recursive functions generate all computable functions — then stop at number theory. The numerical analysis people build derivatives and ODE solvers — starting from floats. Nobody walks the full staircase in one artifact.

This project connects them. One file. One evaluator. Thirteen layers. From `S(Z)` to `dy/dx = y(1−y)`.

## Quick start

```bash
python phi.py
```

No dependencies. No installs. Runs on any Python 3.6+.

## The thirteen layers

| Layer | What | How | Key insight |
|-------|------|-----|-------------|
| **1** | ℕ arithmetic | `Pr`, `Cn` over `Z`, `S`, `P` | Addition is repeated successor |
| **2** | Comparison & division | First `Mn` (μ-operator) | Division is a μ-search: "least n such that..." |
| **3** | Cantor pairing | `ℕ×ℕ ↔ ℕ` bijection | Two dimensions collapse into one |
| **4** | Signed integers | `(pos, neg)` pairs | ℤ emerges from ℕ by pairing |
| **5** | Fixed-point rationals | `ℤ / SCALE` | ℚ emerges from ℤ by division |
| **6** | Polynomials | Compositions of `fp_mul`, `fp_add` | Any polynomial is just nested counting |
| **7** | Partial derivatives | `[f(x+h) − f(x−h)] / 2h` | The derivative is a difference quotient |
| **8** | Newton's method | `x ← x − f(x)/f′(x)` | Equation solving from subtraction + division + derivative |
| **9** | Integration | Trapezoid & Simpson's rule | Area is a sum of products |
| **10** | ODE solvers | Euler & RK2 | `y ← y + h·f(x,y)` — physics falls out |
| **11** | Transcendentals | Taylor series, Newton | e, π, √2 — irrational numbers from counting |
| **12** | Trigonometry & Fourier | Taylor + harmonics | sin, cos, then square wave from sin series |
| **13** | Mandelbrot set | Complex iteration | z → z² + c — infinite fractal from S() |

## Sample output

```
═══ LAYER 7: PARTIAL DERIVATIVES ═══

  d/dx [x²] = 2x
    x=3:  φ →    6.000   exact    6.000

═══ LAYER 8: NEWTON'S METHOD ═══

  x² − x − 1 = 0   (root: φ = 1.618...)
    x₀= 2.000 →   1.670  (1 iters, err=0.052) ✓

═══ LAYER 11: TRANSCENDENTALS ═══

  e = Σ 1/n!       φ → 2.700   exact  2.718
  π via Nilakantha  φ → 3.140   exact  3.14159...

═══ LAYER 12: TRIGONOMETRY ═══

  sin(π/2) = 1.000  cos(π/2) = 0.000  sin²+cos² = 1.000

═══ LAYER 13: MANDELBROT ═══

  .........···::::::::::::::::::;;;;;;;;;++***%#@@@@@@@@%*++++;;;::::::···
  ........···::::::::::::::::::;;;;;;;++***%%%#@@@@@@@@@#%****++;;::::::··
  ........··::::::::::::::::;;;;;;++++*#@@@@@@@@@@@@@@@@@@@##%@@*;;:::::::
  .......··:::::::::::::::;;;+++++++**%#@@@@@@@@@@@@@@@@@@@@@@@@#+;;::::::
```

## Transparency

**What genuinely goes through φ (the evaluator):**
- Layers 1–3: pure tuple-programs, every step evaluated by `_eval()`
- All programs (`add`, `mul`, `pred`, `monus`, `div_`, `mod`, `pair`, `fst`, `snd`) are verified correct by the evaluator with checked test cases

**What uses Python shortcuts (proved correct in Layers 1–2, lifted for speed):**
- `z_add`, `z_sub`: Python `+` replaces `φ(add)`
- `z_n`: Python `max(a-b, 0)` replaces `φ(monus)`
- `z_mul`: Python `*`, `+` replace `φ(mul)`, `φ(add)`
- `z_dn`: Python `//` replaces `φ(div_)`
- `fp_div`: Python `abs()`, `<` replace `φ`-built equivalents

The shortcuts are necessary because unary arithmetic is O(n²) for multiplication — `φ(mul, 300, 500)` would need 150,000 primitive recursion steps, and the Mandelbrot set would take weeks. The mathematical chain is unbroken; only the execution is lifted.

## The punchline

```
The Mandelbrot set is complex iteration.
Complex multiply is two multiplications and a subtraction.
Multiplication is repeated addition.
Addition is repeated successor.

Infinite fractal complexity emerged from S.
```

Layer 10 closes the calculus circle:
- Layer 7: `d/dx[x²] = 2x` (differentiation)
- Layer 10: `dy/dx = 2x → y = x²` (integration recovers the polynomial)

Layer 11 pulls transcendentals from counting:
- e = 2.700 (from Σ 1/n!)
- π = 3.140 (from Nilakantha series)
- ζ(2) ≈ π²/6 — two independent paths to the same transcendental

Layer 13 generates infinite complexity: the Mandelbrot set — the most famous image in mathematics — rendered as ASCII art from six primitives.

## Prior art

I couldn't find that someone built the complete staircase in one runnable artifact before. The pieces have deep roots:

- **Kleene (1936)** — defined φ(e, x) and the six primitives. Stopped at number theory.
- **Gödel (1931)** — encoded arithmetic in primitive recursive functions. For incompleteness, not calculus.
- **Markov (1954)** — constructivist analysis from algorithms on naturals. Axiomatic, not runnable.
- **Bishop (1967)** — constructive analysis, but started from integers as given.
- **Weihrauch (2000)** — proved differentiation is computable. Used infinite sequences, not unary arithmetic.

The gap: computability theorists stop at ℕ, numerical analysts start from ℚ. This walks across.

## Extensions

Still one or two layers away, composing what already exists:

- **Second derivatives / Hessians** — `D(lambda x: D(f, x), x₀)`
- **Taylor approximation** — `f(a) + f'(a)(x−a) + f''(a)(x−a)²/2 + ...`
- **Gradient descent** — `x ← x − α·∂f/∂x` (we have Dx, Dy)
- **Systems of ODEs** — vector state, same Euler/RK2
- **Fourier analysis** (DFT) — compute Σ x[n]·e^(-2πikn/N) using sin/cos from Layer 12
- **Chaos** — logistic map x → rx(1−x), period doubling from deterministic counting
- **RSA** — modular exponentiation from `mul` and `mod` (Layer 2)

## License

MIT. See [LICENSE](LICENSE).

## Author

**Yossi Deutsch** — [github.com/yossideutsch1973](https://github.com/yossideutsch1973)

Research assistants are Claude (Anthropic) and Gemini (Google). March 2026.
