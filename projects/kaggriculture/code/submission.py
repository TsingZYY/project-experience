"""Self-contained Kaggriculture agent: day-9 three-shop k=8 -> k=9 gate.

Generated from locally blind-validated frozen sources.  Upload this file
directly, or upload the companion ZIP whose top-level file is main.py.
"""

from __future__ import annotations

import math
from collections.abc import Callable, Iterable

ANIMALS = {
    "COW": {
        "cost": 400,
        "structure": "PASTURE",
        "first_yield_day": 8,
        "interval": 2,
        "max_held": 6,
        "product": "MILK",
    }
}


Agent = Callable[[dict], dict]
Coord = tuple[int, int]

ANIMAL = "COW"
PRODUCT = "MILK"
FERTILIZER = "FERTILIZER"
FEED = "WHEAT"
SEASON_DAYS = 30
LAST_REFRESH_DAY = SEASON_DAYS - 2

# A 5x5 path beginning at the NW shed-access tile.  Consecutive slots are
# adjacent and every coordinate remains in the initially unlocked quadrant.
# The factory rejects larger targets instead of silently buying land.
NW_SLOT_PATH: tuple[Coord, ...] = (
    (4, 4),
    (3, 4),
    (3, 3),
    (4, 3),
    (4, 2),
    (3, 2),
    (2, 2),
    (2, 3),
    (2, 4),
    (1, 4),
    (1, 3),
    (1, 2),
    (1, 1),
    (2, 1),
    (3, 1),
    (4, 1),
    (4, 0),
    (3, 0),
    (2, 0),
    (1, 0),
    (0, 0),
    (0, 1),
    (0, 2),
    (0, 3),
    (0, 4),
)

# Export the whole physical capacity of the free NW quadrant.  QA determines
# the economic/action frontier under the default 30-day configuration.
EXPORTED_SCALE_MAX = 25

NORMAL_COWS_PER_UNIT = 3
TERMINAL_COWS_PER_UNIT = 2


def _tile_at(farm: dict, coord: Coord) -> object:
    x, y = coord
    return farm["tiles"][y][x]


def _iter_tiles(farm: dict) -> Iterable[object]:
    for row in farm["tiles"]:
        yield from row


def _is_cow(tile: object) -> bool:
    return isinstance(tile, dict) and tile.get("animal") == ANIMAL


def _is_shed_access(coord: Coord, board_size: int) -> bool:
    half = board_size // 2
    return coord in {
        (half - 1, half - 1),
        (half, half - 1),
        (half - 1, half),
        (half, half),
    }


def _nearest_shed_access(coord: Coord, board_size: int) -> Coord:
    half = board_size // 2
    candidates = (
        (half - 1, half - 1),
        (half, half - 1),
        (half - 1, half),
        (half, half),
    )
    return min(
        candidates,
        key=lambda target: (
            abs(coord[0] - target[0]) + abs(coord[1] - target[1]),
            candidates.index(target),
        ),
    )


def _move_toward(current: Coord, target: Coord) -> list[str]:
    x, y = current
    tx, ty = target
    if x < tx:
        return ["EAST"]
    if x > tx:
        return ["WEST"]
    if y < ty:
        return ["SOUTH"]
    if y > ty:
        return ["NORTH"]
    return ["PASS"]


def _fib_hire_cost(number_of_hands: int) -> int:
    """Return the full one-day cost of ``number_of_hands`` hires."""

    a, b = 1, 1
    total = 0
    for _ in range(max(0, number_of_hands)):
        total += a
        a, b = b, a + b
    return total


def _planned_feed_for_day(tile: dict, target_day: int) -> bool:
    """Pure scheduled-prebuy calendar for a placed cow."""

    animal_data = ANIMALS[ANIMAL]
    placed_day = int(tile["placed_day"])
    if target_day < placed_day:
        return False
    first_service_day = placed_day + int(animal_data["first_yield_day"]) - 1
    interval = int(animal_data["interval"])
    max_held = int(animal_data["max_held"])

    if target_day < first_service_day:
        available_days = max(0, first_service_day - placed_day)
        target_bonus = min(max_held - 1, available_days)
        skips = max(0, available_days - target_bonus)
        offset = target_day - placed_day
        return offset not in {2 * index for index in range(skips)}

    if first_service_day <= LAST_REFRESH_DAY:
        last_service_day = (
            first_service_day
            + ((LAST_REFRESH_DAY - first_service_day) // interval) * interval
        )
        if target_day <= last_service_day:
            return True
        return (
            target_day <= LAST_REFRESH_DAY
            and (target_day - last_service_day) % 2 == 0
        )

    return (
        target_day <= LAST_REFRESH_DAY
        and (target_day - placed_day) % 2 == 1
    )


def _service_schedule(tile: dict, day: int) -> tuple[bool, bool]:
    """Return ``(feed, care)`` without reducing useful cow output."""

    animal_data = ANIMALS[ANIMAL]
    placed_day = int(tile["placed_day"])
    first_service_day = placed_day + int(animal_data["first_yield_day"]) - 1
    interval = int(animal_data["interval"])
    max_held = int(animal_data["max_held"])

    if first_service_day <= LAST_REFRESH_DAY:
        last_service_day = (
            first_service_day
            + ((LAST_REFRESH_DAY - first_service_day) // interval) * interval
        )
    else:
        last_service_day = None

    if day < first_service_day:
        available_days = max(0, first_service_day - placed_day)
        target_bonus = min(max_held - 1, available_days)
        pending_bonus = int(tile.get("pending_care_bonus", 0))
        bonus_needed = max(0, target_bonus - pending_bonus)
        remaining_after_today = max(0, first_service_day - day - 1)
        feed_for_bonus = bonus_needed > remaining_after_today
        feed_for_survival = int(tile.get("consecutive_unfed", 0)) >= 1
        should_feed = feed_for_bonus or feed_for_survival
        return should_feed, should_feed and bonus_needed > 0

    if last_service_day is not None and day <= last_service_day:
        return True, day < last_service_day

    refresh_executes = day <= LAST_REFRESH_DAY
    should_feed = refresh_executes and int(tile.get("consecutive_unfed", 0)) >= 1
    return should_feed, False


def _owned_cows(farm: dict, private: dict) -> int:
    on_farm = sum(_is_cow(tile) for tile in _iter_tiles(farm))
    in_inventories = sum(
        int(inventory.get(ANIMAL, 0)) for inventory in private["inventories"]
    )
    return on_farm + int(private["shed"].get(ANIMAL, 0)) + in_inventories


def _all_inventory_units(private: dict, item: str) -> int:
    return int(private["shed"].get(item, 0)) + sum(
        int(inventory.get(item, 0)) for inventory in private["inventories"]
    )


def _feed_stock_target(farm: dict, day: int) -> int:
    """Count today's remaining feed plus tomorrow's scheduled feed."""

    today = 0
    tomorrow = 0
    for tile in _iter_tiles(farm):
        if not _is_cow(tile):
            continue
        should_feed, _ = _service_schedule(tile, day)
        today += int(should_feed and not tile["fed_today"])
        tomorrow += int(_planned_feed_for_day(tile, day + 1))
    return today + tomorrow


def _purchase_capacity(
    farm: dict,
    private: dict,
    target_count: int,
    current_wheat_price: int,
) -> int:
    """Conservative number of additional cows affordable this turn.

    A two-day feed buffer and the next day's full hire bill are reserved before
    expansion.  The market may still buy fewer animals if simultaneous orders
    change available cash; that is safe because the policy recounts ownership
    every turn.
    """

    owned = _owned_cows(farm, private)
    missing = max(0, target_count - owned)
    if missing == 0:
        return 0

    animal_cost = int(ANIMALS[ANIMAL]["cost"])
    affordable = 0
    # Test expansion incrementally.  Reserving for the full target would make
    # high-k policies deadlock at zero cows because the final operating reserve
    # is intentionally much larger than the starting cash.
    for addition in range(1, missing + 1):
        next_count = owned + addition
        hands = max(
            0,
            math.ceil(next_count / NORMAL_COWS_PER_UNIT) - 1,
        )
        reserve = (
            100
            + 2 * max(1, next_count) * max(1, current_wheat_price)
            + _fib_hire_cost(hands)
        )
        required = addition * animal_cost + reserve
        if float(farm["money"]) < required:
            break
        affordable = addition
    return affordable


def make_cow_scale_agent(target_count: int) -> Agent:
    """Build a stable, observation-only policy targeting ``target_count`` cows.

    The current implementation intentionally stays inside the free NW 5x5
    quadrant.  Larger values would require an explicit land-purchase policy and
    are rejected rather than silently producing a mislabeled strategy.
    """

    if not isinstance(target_count, int) or isinstance(target_count, bool):
        raise TypeError("target_count must be an integer")
    if not 1 <= target_count <= len(NW_SLOT_PATH):
        raise ValueError(
            f"target_count must be in 1..{len(NW_SLOT_PATH)} for the NW-only policy"
        )

    targets = NW_SLOT_PATH[:target_count]

    def cow_scale_agent(obs: dict) -> dict:
        player = int(obs["player"])
        farm = obs["farms"][player]
        private = obs["private"]
        shed = private["shed"]
        inventories = private["inventories"]
        board_size = len(farm["tiles"])
        day = int(obs["day"])

        owned = _owned_cows(farm, private)
        # A cow bought after day 20 cannot complete the full first-yield cycle;
        # keeping expansion bounded prevents a nominal high-k label from being
        # reached through economically dead terminal purchases.
        buy_count = (
            _purchase_capacity(
                farm,
                private,
                target_count,
                int(obs["market"]["prices"][FEED]),
            )
            if day <= 20
            else 0
        )
        prospective_slots = min(target_count, owned + buy_count)
        if prospective_slots == owned and owned < target_count and day <= 20:
            prospective_slots = min(target_count, owned + 1)

        assigned_slots = owned if day == SEASON_DAYS - 1 else prospective_slots
        if day == SEASON_DAYS - 1:
            # Pairs are action-safe near the shed.  Slots 18+ are at Manhattan
            # distance 6--8, where two cows plus the return/drop leg can exceed
            # the final 23 actionable turns.  Give each far cow its own hand.
            near_count = min(18, assigned_slots)
            assigned_groups = [
                targets[index:index + TERMINAL_COWS_PER_UNIT]
                for index in range(0, near_count, TERMINAL_COWS_PER_UNIT)
            ]
            assigned_groups.extend(
                targets[index:index + 1]
                for index in range(near_count, assigned_slots)
            )
        else:
            assigned_groups = [
                targets[index:index + NORMAL_COWS_PER_UNIT]
                for index in range(0, assigned_slots, NORMAL_COWS_PER_UNIT)
            ]
        desired_units = max(1, len(assigned_groups))
        desired_hands = max(0, desired_units - 1)
        missing_hands = max(0, desired_hands - len(farm["hands"]))

        market: list[list[object]] = []

        # Outputs already in any unit inventory can be DROPped before market
        # processing this turn, so include the corresponding sell order now.
        if _all_inventory_units(private, PRODUCT) > 0:
            market.append(["SELL", PRODUCT, 100])
        if _all_inventory_units(private, FERTILIZER) > 0:
            market.append(["SELL", FERTILIZER, 100])

        wheat_target = _feed_stock_target(farm, day)
        wheat_owned = _all_inventory_units(private, FEED)
        wheat_shortfall = max(0, wheat_target - wheat_owned)
        if wheat_shortfall > 0:
            market.append(["BUY_PRODUCT", FEED, wheat_shortfall])

        # Respect the default ten-order cap.  Additional hands are hired on the
        # next turn; existing units continue useful work meanwhile.
        hire_room = max(0, 10 - len(market))
        hires_now = min(missing_hands, hire_room)
        market.extend([["HIRE"] for _ in range(hires_now)])

        if buy_count > 0 and len(market) < 10:
            market.append(["BUY_ANIMAL", ANIMAL, buy_count])

        positions = [tuple(farm["farmer"])] + [
            tuple(position) for position in farm["hands"]
        ]

        def unit_action(unit_index: int, current: Coord) -> list[str]:
            inventory = inventories[unit_index]
            group_targets = (
                assigned_groups[unit_index]
                if unit_index < len(assigned_groups)
                else ()
            )

            if not group_targets:
                # A hand hired earlier in the day can become surplus if a
                # requested animal purchase could not clear.  Bring any cargo
                # home, then wait without interfering with active slots.
                if inventory:
                    if _is_shed_access(current, board_size):
                        return ["DROP"]
                    return _move_toward(
                        current, _nearest_shed_access(current, board_size)
                    )
                return ["PASS"]

            group_cows = [
                (coord, _tile_at(farm, coord))
                for coord in group_targets
                if _is_cow(_tile_at(farm, coord))
            ]

            def nearest(coords: list[Coord]) -> Coord:
                return min(
                    coords,
                    key=lambda coord: (
                        abs(coord[0] - current[0]) + abs(coord[1] - current[1]),
                        targets.index(coord),
                    ),
                )

            def travel_or(action: list[str], coords: list[Coord]) -> list[str]:
                target = nearest(coords)
                return action if current == target else _move_toward(current, target)

            saleable_cargo = (
                int(inventory.get(PRODUCT, 0))
                + int(inventory.get(FERTILIZER, 0))
            )
            if saleable_cargo and _is_shed_access(current, board_size):
                return ["DROP"]

            feed_targets = [
                coord
                for coord, tile in group_cows
                if _service_schedule(tile, day)[0] and not tile["fed_today"]
            ]
            wheat_needed = len(feed_targets)
            wheat_carried = int(inventory.get(FEED, 0))
            if wheat_needed > wheat_carried:
                shortage = wheat_needed - wheat_carried
                if _is_shed_access(current, board_size) and shed.get(FEED, 0) > 0:
                    return ["PICKUP", FEED, min(shortage, int(shed[FEED]))]
                shed_target = _nearest_shed_access(current, board_size)
                if current != shed_target:
                    return _move_toward(current, shed_target)
            if feed_targets and wheat_carried > 0:
                return travel_or(["FEED"], feed_targets)

            care_targets = [
                coord
                for coord, tile in group_cows
                if _service_schedule(tile, day)[1] and not tile["cared_today"]
            ]
            if care_targets:
                return travel_or(["CARE"], care_targets)

            # Expansion follows survival and useful CARE, but precedes the
            # replaceable daily fertilizer/harvest chores.  This prevents a
            # far group's purchased cows from remaining in worker inventory
            # for most of the season under a permanently busy service route.
            missing_targets = [
                coord for coord in group_targets
                if not _is_cow(_tile_at(farm, coord))
            ]
            if missing_targets:
                target = missing_targets[0]
                target_tile = _tile_at(farm, target)
                if inventory.get(ANIMAL, 0) > 0:
                    if current != target:
                        return _move_toward(current, target)
                    if target_tile is None:
                        return ["BUILD_PASTURE"]
                    if (
                        isinstance(target_tile, dict)
                        and target_tile.get("kind") == "PASTURE"
                        and "animal" not in target_tile
                    ):
                        return ["PLACE", ANIMAL]
                    if isinstance(target_tile, dict) and target_tile.get("kind") == "WEED":
                        return ["DIG"]
                    return ["PASS"]

                if shed.get(ANIMAL, 0) > 0:
                    if _is_shed_access(current, board_size):
                        amount = min(len(missing_targets), int(shed[ANIMAL]))
                        return ["PICKUP", ANIMAL, amount]
                    return _move_toward(
                        current, _nearest_shed_access(current, board_size)
                    )

                # Prepare one slot while waiting for the next affordable cow.
                if current != target:
                    return _move_toward(current, target)
                if target_tile is None:
                    return ["BUILD_PASTURE"]
                if isinstance(target_tile, dict) and target_tile.get("kind") == "WEED":
                    return ["DIG"]

            fertilizer_targets = [
                coord for coord, tile in group_cows
                if tile.get("fertilizer_available")
            ]
            if fertilizer_targets:
                return travel_or(["COLLECT_FERTILIZER"], fertilizer_targets)

            # Harvest at the six-unit holding cap, or harvest every remaining
            # unit on the terminal day.  This cuts recurring HARVEST actions
            # roughly in half while preventing any terminal milk.
            harvest_targets = [
                coord
                for coord, tile in group_cows
                if int(tile.get("yield_units", 0)) > 0
                and (
                    int(tile.get("yield_units", 0)) >= int(ANIMALS[ANIMAL]["max_held"])
                    or day == SEASON_DAYS - 1
                )
            ]
            if harvest_targets:
                return travel_or(["HARVEST"], harvest_targets)

            if inventory:
                if _is_shed_access(current, board_size):
                    return ["DROP"]
                return _move_toward(
                    current, _nearest_shed_access(current, board_size)
                )
            return ["PASS"]

        actions = [
            unit_action(unit_index, current)
            for unit_index, current in enumerate(positions)
        ]
        return {
            "farmer": actions[0],
            "hands": actions[1:],
            "market": market,
        }

    cow_scale_agent.__name__ = f"cow_scale_{target_count}_agent"
    return cow_scale_agent


SCALING_EXPERIMENTS: dict[str, Agent] = {
    f"cow_scale_{count}": make_cow_scale_agent(count)
    for count in range(1, EXPORTED_SCALE_MAX + 1)
}

# Module-level aliases are convenient for direct ``env.run`` calls and remain
# stable even before the central tournament resolver is allowed to import them.
globals().update(
    {
        f"cow_scale_{count}_agent": SCALING_EXPERIMENTS[f"cow_scale_{count}"]
        for count in range(1, EXPORTED_SCALE_MAX + 1)
    }
)


__all__ = [
    "EXPORTED_SCALE_MAX",
    "NW_SLOT_PATH",
    "SCALING_EXPERIMENTS",
    "make_cow_scale_agent",
    *[f"cow_scale_{count}_agent" for count in range(1, EXPORTED_SCALE_MAX + 1)],
]

MILK_SHOPS = frozenset({"PIZZA_SHOP", "ICE_CREAM_SHOP", "SMOOTHIE_SHOP"})


def _milk_shop_count(obs: dict) -> int:
    shops = obs.get("town", {}).get("unlocked_shops", [])
    return sum(shop in MILK_SHOPS for shop in shops)


def agent(obs: dict) -> dict:
    """Return one legal action for the current public/private observation."""

    player = int(obs["player"])
    farm = obs["farms"][player]
    private = obs["private"]
    trigger = int(obs["day"]) == 9 and _milk_shop_count(obs) >= 3
    already_expanded = _owned_cows(farm, private) > 8
    policy = "cow_scale_9" if trigger or already_expanded else "cow_scale_8"
    return SCALING_EXPERIMENTS[policy](obs)
