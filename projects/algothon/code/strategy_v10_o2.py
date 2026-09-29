"""Algothon 2026 final strategy for hidden days 1001--2000.

V10-O2 final: V9 with two validated, minimal changes.

* Pair assets retain V9's exact one-day weak-signal fallback.
* Orphan assets use a two-day recursive fallback only when both the current and
  previous lead-lag signals are weak.
* Malformed inputs and pathological sizing overflow fail flat.

Stable structure:
* ALGO is used as the market coordinate and remains flat.
* Thirteen disjoint log-ratio pairs are frozen from public days 1--1000.
* Pair moments and the residual lag-1 network use only visible history.
* The newest return is predictor-only and cannot select its own support.
* Weak lead-lag evidence receives bounded one-day inertia on pair assets and
  at most two-day recursive inertia on orphan assets.

Final-only plasticity:
* Expanding-history lead-lag is always the default.
* A recent-350 challenger is evaluated after the full decision pipeline,
  including inertia, pair routing, integer full-cap sizing and commissions.
* The selector acts separately on 26 pair assets and 24 orphan assets.
* Global and stricter group tests use only realised final-round data and
  revert automatically when the evidence disappears.

The strategy is a deterministic function of prcSoFar. Cache keys contain an
exact digest of the visible checkpoint prefix and affect runtime only.
"""
from __future__ import annotations

import hashlib
import numpy as np

LIMITS = np.array([100_000.0] + [10_000.0] * 50)
COMMISSIONS = np.array([0.00002] + [0.0001] * 50)

MIN_DAYS = 130
PUBLIC_FINAL_CUTOFF = 1000

PAIR_GATE = 0.60
SIGNIF_SE = 1.00
WEAK_BAND = 0.30

RECENT_LL_WINDOW = 350
SELECT_BLOCK = 100
SELECT_RECHECK = 25

GLOBAL_BLOCK_T = 2.0
GLOBAL_COMBINED_T = 3.5

# Slightly stricter because two group hypotheses are monitored in addition
# to the global hypothesis.
GROUP_BLOCK_T = 2.2
GROUP_COMBINED_T = 3.8

NAMES = (
    "ALGO", "AENO", "LSST", "SRNA", "ELLT", "AMRP", "OTCS", "HETT",
    "HUXZ", "DUCT", "SMAH", "NPCK", "MSDP", "EORC", "CUBO", "HRET",
    "ANSO", "DIHO", "RTTH", "SPLZ", "NWIG", "MMBT", "MDGI", "AGVF",
    "RRES", "CTGI", "ALUT", "ACAC", "SRTX", "GARI", "RCRI", "ACIX",
    "CCNS", "MTNS", "IHOZ", "NAYO", "FWWG", "EELT", "HRND", "AETS",
    "ULXY", "BLBT", "BENI", "ITPA", "HTRK", "NGTE", "ILVX", "FCSG",
    "FARS", "MHRM", "EAFC",
)
INDEX = {name: index for index, name in enumerate(NAMES)}

LOCKED_PAIRS = tuple(
    (INDEX[left], INDEX[right])
    for left, right in (
        ("AENO", "NWIG"),
        ("HETT", "ULXY"),
        ("HUXZ", "ACAC"),
        ("SMAH", "ILVX"),
        ("EORC", "NGTE"),
        ("RTTH", "NAYO"),
        ("CTGI", "EELT"),
        ("ALUT", "CCNS"),
        ("ACIX", "ITPA"),
        ("MTNS", "BENI"),
        ("FWWG", "BLBT"),
        ("MHRM", "EAFC"),
        ("HRET", "HTRK"),
    )
)

PAIR_ASSETS = frozenset(
    asset for pair in LOCKED_PAIRS for asset in pair
)
ORPHAN_ASSETS = frozenset(
    asset for asset in range(1, len(NAMES))
    if asset not in PAIR_ASSETS
)

PAIR_LL_INDICES = np.array(
    sorted(asset - 1 for asset in PAIR_ASSETS),
    dtype=int,
)
ORPHAN_LL_INDICES = np.array(
    sorted(asset - 1 for asset in ORPHAN_ASSETS),
    dtype=int,
)

# (use_recent_for_pair_assets, use_recent_for_orphan_assets)
_selector_cache: dict[tuple[int, bytes], tuple[bool, bool]] = {}


def reset() -> None:
    _selector_cache.clear()


def _lead_lag_signal(
    alpha_returns: np.ndarray,
    observed_days: int,
    recent_window: int | None,
) -> np.ndarray:
    """Cross-fitted marginal LL signal for one visible prefix."""
    fit_count = observed_days - 2
    if fit_count < 3:
        return np.zeros(alpha_returns.shape[0])

    start = 0 if recent_window is None else max(0, fit_count - recent_window)
    fit = alpha_returns[:, start:fit_count]

    mean = fit.mean(axis=1, keepdims=True)
    standard_deviation = np.maximum(
        fit.std(axis=1, keepdims=True),
        1e-12,
    )
    z_fit = (fit - mean) / standard_deviation
    z_now = (
        alpha_returns[:, observed_days - 2] - mean[:, 0]
    ) / standard_deviation[:, 0]

    today = z_fit[:, :-1]
    tomorrow = z_fit[:, 1:]
    transition_count = today.shape[1]

    lead_lag = (today @ tomorrow.T) / transition_count
    np.fill_diagonal(lead_lag, 0.0)
    standard_error = SIGNIF_SE / np.sqrt(transition_count)
    lead_lag = np.sign(lead_lag) * np.maximum(
        np.abs(lead_lag) - standard_error, 0.0
    )

    signal = lead_lag.T @ z_now
    signal -= signal.mean()
    return signal


def _one_day_direction(
    alpha_returns: np.ndarray,
    observed_days: int,
    recent_window: int | None,
) -> np.ndarray:
    """Pair assets use one-day inertia; orphan assets use two-day recursion."""
    current = _lead_lag_signal(
        alpha_returns,
        observed_days,
        recent_window,
    )
    direction = np.sign(current)

    scale = float(np.mean(np.abs(current)))
    weak = (
        np.abs(current) < WEAK_BAND * scale
        if scale > 0.0
        else np.ones(current.shape, dtype=bool)
    )
    if observed_days > MIN_DAYS:
        previous = _lead_lag_signal(
            alpha_returns,
            observed_days - 1,
            recent_window,
        )
        one_day_direction = np.sign(previous)
        carry_direction = one_day_direction.copy()

        if observed_days > MIN_DAYS + 1:
            previous_scale = float(np.mean(np.abs(previous)))
            previous_weak = (
                np.abs(previous) < WEAK_BAND * previous_scale
                if previous_scale > 0.0
                else np.ones(previous.shape, dtype=bool)
            )
            two_days_ago = _lead_lag_signal(
                alpha_returns,
                observed_days - 2,
                recent_window,
            )
            orphan_previous_weak = previous_weak[ORPHAN_LL_INDICES]
            carry_direction[ORPHAN_LL_INDICES] = np.where(
                orphan_previous_weak,
                np.sign(two_days_ago[ORPHAN_LL_INDICES]),
                one_day_direction[ORPHAN_LL_INDICES],
            )

        # Pair assets retain V9's exact one-day fallback.  Only orphan assets
        # may inherit the recursively reconstructed previous decision.
        fallback = one_day_direction.copy()
        fallback[ORPHAN_LL_INDICES] = carry_direction[ORPHAN_LL_INDICES]
        direction = np.where(weak, fallback, direction)

    return direction.astype(float)


def _two_ll_directions(
    alpha_returns: np.ndarray,
    observed_days: int,
) -> tuple[np.ndarray, np.ndarray]:
    expanding = _one_day_direction(
        alpha_returns,
        observed_days,
        None,
    )
    recent = _one_day_direction(
        alpha_returns,
        observed_days,
        RECENT_LL_WINDOW,
    )
    return expanding, recent


def _target_position_from_directions(
    prices: np.ndarray,
    log_prices: np.ndarray,
    observed_days: int,
    expanding_direction: np.ndarray,
    recent_direction: np.ndarray,
    use_recent_pair: bool,
    use_recent_orphan: bool,
) -> np.ndarray:
    """Complete routed portfolio for one structural-group expert choice."""
    ll_direction = expanding_direction.copy()

    if use_recent_pair:
        ll_direction[PAIR_LL_INDICES] = recent_direction[PAIR_LL_INDICES]

    if use_recent_orphan:
        ll_direction[ORPHAN_LL_INDICES] = recent_direction[ORPHAN_LL_INDICES]

    direction = np.zeros(prices.shape[0])
    direction[1:] = ll_direction

    for left, right in LOCKED_PAIRS:
        spread = (
            log_prices[left, :observed_days]
            - log_prices[right, :observed_days]
        )
        spread_z = (
            spread[-1] - spread.mean()
        ) / (spread.std() + 1e-12)

        for asset, pair_direction in (
            (left, -np.sign(spread_z)),
            (right, np.sign(spread_z)),
        ):
            network_direction = ll_direction[asset - 1]
            if (
                pair_direction == network_direction
                or abs(spread_z) >= PAIR_GATE
            ):
                direction[asset] = pair_direction

    direction[0] = 0.0
    current_prices = prices[:, observed_days - 1]
    with np.errstate(over="ignore", divide="ignore", invalid="ignore"):
        raw_position = LIMITS[:prices.shape[0]] * direction / current_prices

    # Fail flat rather than allowing a float-to-int overflow on pathological
    # positive subnormal inputs.  This branch is unreachable on official data.
    # float64 rounds int64 max up to 2**63; step one representable float
    # toward zero so every value admitted here is safely castable to int64.
    int64_safe_bound = np.nextafter(
        np.float64(np.iinfo(np.int64).max),
        np.float64(0.0),
    )
    if (
        not np.isfinite(raw_position).all()
        or np.any(np.abs(raw_position) > int64_safe_bound)
    ):
        return np.zeros(len(NAMES), dtype=int)

    return raw_position.astype(int)


def _target_position(
    prices: np.ndarray,
    log_prices: np.ndarray,
    alpha_returns: np.ndarray,
    observed_days: int,
    use_recent_pair: bool,
    use_recent_orphan: bool,
) -> np.ndarray:
    expanding, recent = _two_ll_directions(
        alpha_returns,
        observed_days,
    )
    return _target_position_from_directions(
        prices,
        log_prices,
        observed_days,
        expanding,
        recent,
        use_recent_pair,
        use_recent_orphan,
    )


def _t_statistic(values: np.ndarray) -> float:
    if values.size < 20:
        return -np.inf
    standard_deviation = float(values.std())
    return float(
        values.mean()
        / (standard_deviation / np.sqrt(values.size) + 1e-12)
    )


def _daily_pnl(
    current_position: np.ndarray,
    previous_position: np.ndarray,
    current_prices: np.ndarray,
    next_prices: np.ndarray,
) -> float:
    fee = float(
        (
            current_prices
            * np.abs(current_position - previous_position)
            * COMMISSIONS
        ).sum()
    )
    return float(
        current_position @ (next_prices - current_prices) - fee
    )


def _counterfactual_differences(
    prices: np.ndarray,
    log_prices: np.ndarray,
    alpha_returns: np.ndarray,
    first_decision: int,
    checkpoint: int,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Recent-minus-expanding P&L for global, pair and orphan choices."""
    modes = (
        (False, False),  # expanding baseline
        (True, True),    # recent globally
        (True, False),   # recent for pair assets only
        (False, True),   # recent for orphan assets only
    )

    previous_positions: list[np.ndarray] = []
    if first_decision == PUBLIC_FINAL_CUTOFF:
        previous_positions = [
            np.zeros(prices.shape[0], dtype=int)
            for _ in modes
        ]
    else:
        for use_pair, use_orphan in modes:
            previous_positions.append(
                _target_position(
                    prices,
                    log_prices,
                    alpha_returns,
                    first_decision - 1,
                    use_pair,
                    use_orphan,
                )
            )

    length = checkpoint - first_decision
    global_difference = np.empty(length, dtype=float)
    pair_difference = np.empty(length, dtype=float)
    orphan_difference = np.empty(length, dtype=float)

    for offset, decision_day in enumerate(
        range(first_decision, checkpoint)
    ):
        expanding_direction, recent_direction = _two_ll_directions(
            alpha_returns,
            decision_day,
        )

        positions: list[np.ndarray] = []
        for use_pair, use_orphan in modes:
            positions.append(
                _target_position_from_directions(
                    prices,
                    log_prices,
                    decision_day,
                    expanding_direction,
                    recent_direction,
                    use_pair,
                    use_orphan,
                )
            )

        current_prices = prices[:, decision_day - 1]
        next_prices = prices[:, decision_day]

        pnl = np.empty(4, dtype=float)
        for index in range(4):
            pnl[index] = _daily_pnl(
                positions[index],
                previous_positions[index],
                current_prices,
                next_prices,
            )

        global_difference[offset] = pnl[1] - pnl[0]
        pair_difference[offset] = pnl[2] - pnl[0]
        orphan_difference[offset] = pnl[3] - pnl[0]

        previous_positions = positions

    return (
        global_difference,
        pair_difference,
        orphan_difference,
    )


def _block_evidence(
    values: np.ndarray,
) -> tuple[np.ndarray, np.ndarray]:
    earlier = values[:SELECT_BLOCK]
    current = values[SELECT_BLOCK:]
    return earlier, current


def _passes(
    values: np.ndarray,
    block_threshold: float,
    combined_threshold: float,
) -> bool:
    earlier, current = _block_evidence(values)
    return bool(
        _t_statistic(earlier) > block_threshold
        and _t_statistic(current) > block_threshold
        and _t_statistic(values) > combined_threshold
    )


def _positive_in_both_blocks(values: np.ndarray) -> bool:
    """A global change may not drag a structurally losing group along."""
    earlier, current = _block_evidence(values)
    return bool(earlier.mean() > 0.0 and current.mean() > 0.0)


def _expert_flags(
    prices: np.ndarray,
    log_prices: np.ndarray,
    alpha_returns: np.ndarray,
) -> tuple[bool, bool]:
    """Return whether pair/orphan asset groups should use recent-350 LL."""
    observed_days = prices.shape[1]
    final_days_seen = observed_days - PUBLIC_FINAL_CUTOFF

    if final_days_seen < 2 * SELECT_BLOCK:
        return False, False

    checkpoint = (
        PUBLIC_FINAL_CUTOFF
        + (final_days_seen // SELECT_RECHECK) * SELECT_RECHECK
    )
    if checkpoint - PUBLIC_FINAL_CUTOFF < 2 * SELECT_BLOCK:
        return False, False

    checkpoint_prices = np.ascontiguousarray(
        prices[:, :checkpoint]
    )
    digest = hashlib.blake2b(
        checkpoint_prices.view(np.uint8),
        digest_size=16,
    ).digest()
    key = (checkpoint, digest)

    cached = _selector_cache.get(key)
    if cached is not None:
        return cached

    first_decision = checkpoint - 2 * SELECT_BLOCK
    global_difference, pair_difference, orphan_difference = (
        _counterfactual_differences(
            prices,
            log_prices,
            alpha_returns,
            first_decision,
            checkpoint,
        )
    )

    global_selected = _passes(
        global_difference,
        GLOBAL_BLOCK_T,
        GLOBAL_COMBINED_T,
    )

    pair_selected = _passes(
        pair_difference,
        GROUP_BLOCK_T,
        GROUP_COMBINED_T,
    )
    orphan_selected = _passes(
        orphan_difference,
        GROUP_BLOCK_T,
        GROUP_COMBINED_T,
    )

    # A diffuse global change retains power, but it may only switch a structural
    # action group whose own realised advantage was positive in both blocks.
    # Strict group evidence can always select that group independently.
    flags = (
        pair_selected
        or (
            global_selected
            and _positive_in_both_blocks(pair_difference)
        ),
        orphan_selected
        or (
            global_selected
            and _positive_in_both_blocks(orphan_difference)
        ),
    )

    _selector_cache[key] = flags
    return flags


def getMyPosition(prcSoFar: np.ndarray) -> np.ndarray:
    prices = np.asarray(prcSoFar, dtype=float)
    if prices.ndim != 2:
        return np.zeros(len(NAMES), dtype=int)

    instrument_count, day_count = prices.shape

    # The competition contract always has 51 instruments.  Return the fixed
    # contract shape even for malformed inputs so downstream clipping is safe.
    if instrument_count != len(NAMES) or day_count < MIN_DAYS:
        return np.zeros(len(NAMES), dtype=int)

    if not np.isfinite(prices).all() or np.any(prices <= 0.0):
        return np.zeros(len(NAMES), dtype=int)

    safe_prices = prices
    log_prices = np.log(safe_prices)
    returns = np.diff(log_prices, axis=1)
    residual_returns = returns - returns[0]
    alpha_returns = residual_returns[1:]

    use_recent_pair, use_recent_orphan = _expert_flags(
        safe_prices,
        log_prices,
        alpha_returns,
    )

    return _target_position(
        safe_prices,
        log_prices,
        alpha_returns,
        day_count,
        use_recent_pair,
        use_recent_orphan,
    )


