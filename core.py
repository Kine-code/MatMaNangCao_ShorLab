"""Core mathematics for the ShorLab educational demo.

Nhóm thực hiện:
- Dương Công Kiên - B25CHKH072 (Nhóm trưởng)
- Nguyễn Cảnh Huỳnh - B25CHKH071
- Phạm Anh Tuấn - B25CHKH086

The Shor period-finding step is emulated classically so the project runs on
an ordinary computer. The post-processing (GCD, modular arithmetic, RSA key
recovery) is the same mathematics used after a quantum measurement.
"""
from __future__ import annotations

from dataclasses import dataclass, asdict
from math import gcd
from typing import Optional

Point = Optional[tuple[int, int]]


def egcd(a: int, b: int) -> tuple[int, int, int]:
    if b == 0:
        return a, 1, 0
    g, x1, y1 = egcd(b, a % b)
    return g, y1, x1 - (a // b) * y1


def mod_inverse(a: int, n: int) -> int:
    g, x, _ = egcd(a, n)
    if g != 1:
        raise ValueError(f"{a} has no inverse modulo {n}")
    return x % n


def is_prime(n: int) -> bool:
    if n < 2:
        return False
    if n % 2 == 0:
        return n == 2
    d = 3
    while d * d <= n:
        if n % d == 0:
            return False
        d += 2
    return True


def multiplicative_order(a: int, n: int, max_steps: int | None = None) -> tuple[int, list[int]]:
    if gcd(a, n) != 1:
        raise ValueError("a and N must be coprime to compute the order")
    limit = max_steps or (2 * n + 2)
    value = 1
    values = [1]
    for r in range(1, limit + 1):
        value = (value * a) % n
        values.append(value)
        if value == 1:
            return r, values
    raise ValueError("Order was not found within the safety limit")


@dataclass
class ShorResult:
    n: int
    a: int
    gcd_initial: int
    order_r: Optional[int]
    powers: list[int]
    x_half: Optional[int]
    factor_1: Optional[int]
    factor_2: Optional[int]
    success: bool
    note: str

    def to_dict(self) -> dict:
        return asdict(self)


def shor_factor_emulated(n: int, a: int) -> ShorResult:
    if n <= 3 or n % 2 == 0:
        if n % 2 == 0 and n > 2:
            return ShorResult(n, a, 2, None, [], None, 2, n // 2, True, "N is even; no period finding is needed.")
        return ShorResult(n, a, 1, None, [], None, None, None, False, "N must be an odd composite integer greater than 3.")
    if not 1 < a < n:
        return ShorResult(n, a, 1, None, [], None, None, None, False, "Choose a with 1 < a < N.")

    d = gcd(a, n)
    if d > 1:
        return ShorResult(n, a, d, None, [], None, d, n // d, True, "The initial GCD already gives a non-trivial factor.")

    r, powers = multiplicative_order(a, n)
    if r % 2 == 1:
        return ShorResult(n, a, 1, r, powers, None, None, None, False, "The order r is odd; choose another base a.")

    x = pow(a, r // 2, n)
    if x == n - 1:
        return ShorResult(n, a, 1, r, powers, x, None, None, False, "a^(r/2) = -1 mod N; choose another base a.")

    f1 = gcd(x - 1, n)
    f2 = gcd(x + 1, n)
    success = 1 < f1 < n and 1 < f2 < n and f1 * f2 == n
    note = "Non-trivial factors recovered from gcd(a^(r/2) +/- 1, N)." if success else "The GCD post-processing did not produce both non-trivial factors."
    return ShorResult(n, a, 1, r, powers, x, f1, f2, success, note)


@dataclass
class RSADemoResult:
    p: int
    q: int
    n: int
    phi: int
    e: int
    d: int
    message: int
    ciphertext: int
    decrypted: int
    attack_factor_1: Optional[int]
    attack_factor_2: Optional[int]
    recovered_d: Optional[int]
    recovered_message: Optional[int]
    attack_success: bool
    note: str

    def to_dict(self) -> dict:
        return asdict(self)


def rsa_demo(p: int, q: int, e: int, message: int, shor_base: int = 2) -> RSADemoResult:
    if not (is_prime(p) and is_prime(q) and p != q):
        raise ValueError("p and q must be distinct prime numbers")
    n = p * q
    phi = (p - 1) * (q - 1)
    if gcd(e, phi) != 1:
        raise ValueError("e must be coprime with phi(n)")
    if not 0 <= message < n:
        raise ValueError("message must satisfy 0 <= message < n")
    d = mod_inverse(e, phi)
    ciphertext = pow(message, e, n)
    decrypted = pow(ciphertext, d, n)

    attack = shor_factor_emulated(n, shor_base)
    recovered_d = None
    recovered_message = None
    attack_success = False
    if attack.success and attack.factor_1 and attack.factor_2:
        phi_attack = (attack.factor_1 - 1) * (attack.factor_2 - 1)
        if gcd(e, phi_attack) == 1:
            recovered_d = mod_inverse(e, phi_attack)
            recovered_message = pow(ciphertext, recovered_d, n)
            attack_success = recovered_message == message
    note = "RSA private exponent and plaintext were recovered after factoring n." if attack_success else "The selected Shor base did not complete the RSA attack; try another base."
    return RSADemoResult(
        p, q, n, phi, e, d, message, ciphertext, decrypted,
        attack.factor_1, attack.factor_2, recovered_d, recovered_message,
        attack_success, note,
    )


@dataclass(frozen=True)
class Curve:
    p: int
    a: int
    b: int

    def contains(self, point: Point) -> bool:
        if point is None:
            return True
        x, y = point
        return (y * y - (x * x * x + self.a * x + self.b)) % self.p == 0


def point_add(curve: Curve, p1: Point, p2: Point) -> Point:
    if p1 is None:
        return p2
    if p2 is None:
        return p1
    x1, y1 = p1
    x2, y2 = p2
    p = curve.p

    if x1 == x2 and (y1 + y2) % p == 0:
        return None

    if p1 == p2:
        if y1 % p == 0:
            return None
        slope = ((3 * x1 * x1 + curve.a) * mod_inverse(2 * y1 % p, p)) % p
    else:
        slope = ((y2 - y1) * mod_inverse((x2 - x1) % p, p)) % p

    x3 = (slope * slope - x1 - x2) % p
    y3 = (slope * (x1 - x3) - y1) % p
    result = (x3, y3)
    if not curve.contains(result):
        raise ArithmeticError("Point addition produced a point outside the curve")
    return result


def scalar_multiply(curve: Curve, k: int, point: Point) -> Point:
    if k < 0:
        raise ValueError("k must be non-negative")
    result: Point = None
    addend = point
    while k:
        if k & 1:
            result = point_add(curve, result, addend)
        addend = point_add(curve, addend, addend)
        k >>= 1
    return result


def point_order(curve: Curve, point: Point, limit: int = 10000) -> int:
    if point is None:
        return 1
    current: Point = None
    for k in range(1, limit + 1):
        current = point_add(curve, current, point)
        if current is None:
            return k
    raise ValueError("Point order exceeds the safety limit")


@dataclass
class ECCDemoResult:
    curve: dict
    base_point: tuple[int, int]
    private_k: int
    public_q: Point
    base_order: int
    recovered_k_classical: Optional[int]
    success: bool
    note: str

    def to_dict(self) -> dict:
        return asdict(self)


def recover_discrete_log_bruteforce(curve: Curve, base: Point, target: Point, order: int) -> Optional[int]:
    current: Point = None
    for k in range(order):
        if current == target:
            return k
        current = point_add(curve, current, base)
    return None


def ecc_demo(private_k: int) -> ECCDemoResult:
    curve = Curve(p=17, a=2, b=2)
    base = (5, 1)
    if not curve.contains(base):
        raise ArithmeticError("Configured base point is invalid")
    order = point_order(curve, base)
    k = private_k % order
    if k == 0:
        k = order - 1
    q = scalar_multiply(curve, k, base)
    recovered = recover_discrete_log_bruteforce(curve, base, q, order)
    success = recovered == k
    note = (
        "The toy key is recovered by classical exhaustive search. In the report, Shor's discrete-log algorithm is analyzed as the polynomial-time quantum threat to real ECC groups."
    )
    return ECCDemoResult(
        curve={"p": curve.p, "a": curve.a, "b": curve.b},
        base_point=base,
        private_k=k,
        public_q=q,
        base_order=order,
        recovered_k_classical=recovered,
        success=success,
        note=note,
    )


MLKEM_OPTIONS = [
    {"name": "ML-KEM-512", "category": 1, "public_key": 800, "secret_key": 1632, "ciphertext": 768},
    {"name": "ML-KEM-768", "category": 3, "public_key": 1184, "secret_key": 2400, "ciphertext": 1088},
    {"name": "ML-KEM-1024", "category": 5, "public_key": 1568, "secret_key": 3168, "ciphertext": 1568},
]


@dataclass
class OptimizationResult:
    required_category: int
    max_public_key: int
    max_ciphertext: int
    weights: dict
    candidates: list[dict]
    selected: Optional[dict]
    feasible: bool
    mathematical_model: str

    def to_dict(self) -> dict:
        return asdict(self)


def select_mlkem(
    required_category: int = 3,
    max_public_key: int = 1400,
    max_ciphertext: int = 1200,
    w_public_key: float = 0.35,
    w_secret_key: float = 0.15,
    w_ciphertext: float = 0.35,
    w_security: float = 0.15,
) -> OptimizationResult:
    weights = {
        "public_key": w_public_key,
        "secret_key": w_secret_key,
        "ciphertext": w_ciphertext,
        "security": w_security,
    }
    total = sum(weights.values())
    if total <= 0:
        raise ValueError("At least one optimization weight must be positive")
    weights = {k: v / total for k, v in weights.items()}

    max_pk = max(o["public_key"] for o in MLKEM_OPTIONS)
    max_sk = max(o["secret_key"] for o in MLKEM_OPTIONS)
    max_ct = max(o["ciphertext"] for o in MLKEM_OPTIONS)
    max_cat = max(o["category"] for o in MLKEM_OPTIONS)
    min_cat = min(o["category"] for o in MLKEM_OPTIONS)

    candidates: list[dict] = []
    for option in MLKEM_OPTIONS:
        feasible = (
            option["category"] >= required_category
            and option["public_key"] <= max_public_key
            and option["ciphertext"] <= max_ciphertext
        )
        security_cost = (max_cat - option["category"]) / max(1, (max_cat - min_cat))
        score = (
            weights["public_key"] * option["public_key"] / max_pk
            + weights["secret_key"] * option["secret_key"] / max_sk
            + weights["ciphertext"] * option["ciphertext"] / max_ct
            + weights["security"] * security_cost
        )
        row = dict(option)
        row.update({"feasible": feasible, "score": round(score, 4)})
        candidates.append(row)

    feasible_rows = [row for row in candidates if row["feasible"]]
    selected = min(feasible_rows, key=lambda row: row["score"]) if feasible_rows else None
    model = (
        "min sum_i c_i x_i; subject to sum_i x_i = 1, "
        "category_i x_i >= required, public_key_i x_i <= memory limit, "
        "ciphertext_i x_i <= network limit, x_i in {0,1}."
    )
    return OptimizationResult(
        required_category, max_public_key, max_ciphertext, weights,
        candidates, selected, selected is not None, model,
    )
