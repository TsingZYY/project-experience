import re
import sys
from collections import defaultdict
from random import seed, shuffle


if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')


def card_to_unicode(card):
    suit = card // 13
    rank = card % 13
    base = [0x1F0B0, 0x1F0C0, 0x1F0D0, 0x1F0A0][suit]
    value = rank + 1
    if value >= 12:
        value += 1
    return chr(base + value)


def get_target_stack(card, inc_tops, dec_tops):
    suit = card // 13
    rank = card % 13

    if rank == 0 and inc_tops[suit] is None:
        return 'inc', suit
    if rank == 12 and dec_tops[suit] is None:
        return 'dec', suit
    if inc_tops[suit] is not None and card == inc_tops[suit] + 1:
        return 'inc', suit
    if dec_tops[suit] is not None and card == dec_tops[suit] - 1:
        return 'dec', suit
    return None


def ordinal(n):
    if 10 <= n % 100 <= 20:
        suffix = 'th'
    else:
        suffix = {1: 'st', 2: 'nd', 3: 'rd'}.get(n % 10, 'th')
    return f'{n}{suffix}'


def stack_token(top_card, increasing):
    if top_card is None:
        return ''
    hidden = top_card % 13 if increasing else 12 - top_card % 13
    return '[' * hidden + card_to_unicode(top_card)


def render_stack_line(tops, increasing):
    tokens = [stack_token(top, increasing) for top in tops]
    if not any(tokens):
        return ''

    pieces = [' '] * 64
    for i, token in enumerate(tokens):
        start = 4 + 15 * i
        for j, char in enumerate(token):
            pieces[start + j] = char
    return ''.join(pieces).rstrip()


def render_face_up(face_up):
    if not face_up:
        return ''
    return '[' * (len(face_up) - 1) + card_to_unicode(face_up[-1])


def snapshot_lines(deck, face_up, inc_tops, dec_tops):
    return [
        ']' * len(deck),
        render_face_up(face_up),
        render_stack_line(inc_tops, True),
        render_stack_line(dec_tops, False),
    ]


def placement_message(card, stack_type, inc_tops, dec_tops):
    suit = card // 13
    rank = card % 13
    if stack_type == 'inc' and rank == 0 and inc_tops[suit] is None:
        return 'Starting a stack.'
    if stack_type == 'dec' and rank == 12 and dec_tops[suit] is None:
        return 'Starting a stack.'
    if stack_type == 'inc':
        return 'Extending an increasing stack.'
    return 'Extending a decreasing stack.'


def play_game(seed_value):
    deck = list(range(52))
    seed(seed_value)
    shuffle(deck)
    face_up = []
    inc_tops = [None] * 4
    dec_tops = [None] * 4
    collected_output = ['Deck shuffled. Ready to start!', ']' * 52]
    last_block_snapshot = False

    def append_block(lines, is_snapshot=False):
        nonlocal last_block_snapshot
        collected_output.extend(lines)
        last_block_snapshot = is_snapshot

    placed_total = 0
    round_number = 1

    while True:
        placed_this_round = 0
        append_block(['', f'Starting the {ordinal(round_number)} round...', ''])

        while deck:
            drawn = []
            for _ in range(3):
                if not deck:
                    break
                drawn.append(deck.pop())
            face_up.extend(drawn)
            if last_block_snapshot:
                collected_output.append('')
            append_block(snapshot_lines(deck, face_up, inc_tops, dec_tops), is_snapshot=True)

            while face_up:
                target = get_target_stack(face_up[-1], inc_tops, dec_tops)
                if target is None:
                    break

                stack_type, suit = target
                card = face_up.pop()
                if last_block_snapshot:
                    collected_output.append('')
                append_block([placement_message(card, stack_type, inc_tops, dec_tops)])
                if stack_type == 'inc':
                    inc_tops[suit] = card
                else:
                    dec_tops[suit] = card

                placed_this_round += 1
                placed_total += 1
                append_block(snapshot_lines(deck, face_up, inc_tops, dec_tops), is_snapshot=True)

        if placed_total == 52:
            return True, 0, collected_output
        if placed_this_round == 0:
            return False, len(face_up), collected_output

        deck = face_up[::-1]
        face_up = []
        round_number += 1


def parse_request(user_input, total_lines):
    stripped = user_input.strip()
    if stripped == 'q':
        return 'quit', None

    if re.fullmatch(r'0*[1-9]\d*', stripped):
        value = int(stripped)
        if value <= total_lines:
            return 'last', value
        return None, None

    if re.fullmatch(r'-0*[1-9]\d*', stripped):
        value = int(stripped)
        if -total_lines <= value <= -1:
            return 'first', -value
        return None, None

    match = re.fullmatch(r'\s*(\d+)\s*--\s*(\d+)\s*', user_input)
    if match:
        start = int(match.group(1))
        end = int(match.group(2))
        if 1 <= start <= end <= total_lines:
            return 'range', (start, end)
    return None, None


def display_requested_lines(collected_output, request_type, payload):
    if request_type == 'last':
        lines = collected_output[:payload]
    elif request_type == 'first':
        lines = collected_output[-payload:]
    else:
        start, end = payload
        lines = collected_output[start - 1:end]

    for line in lines:
        print(line)
    return lines


def simulate_one_game(seed_value):
    won, remaining, _ = play_game(seed_value)
    return 0 if won else remaining


def simulate(n, i):
    frequencies = defaultdict(int)
    for g in range(n):
        cards_left = simulate_one_game(i + g)
        frequencies[cards_left] += 1

    print('Number of cards left | Relative frequency')
    print('-----------------------------------------')
    for cards_left in sorted(frequencies, reverse=True):
        percentage = frequencies[cards_left] / n * 100
        print(f'{cards_left:>20} | {percentage:>17.2f}%')


def print_options(total_lines):
    print('Enter: q to quit')
    print(f'       a last line number (between 1 and {total_lines})')
    print(f'       a first line number (between -1 and -{total_lines})')
    print(f'       a range of line numbers (of the form m--n with 1 <= m <= n <= {total_lines})')


def main():
    seed_value = int(input('Enter an integer to pass to the seed() function: '))
    won, remaining, collected_output = play_game(seed_value)

    print()
    if won:
        print('You placed all cards. You won! \U0001F60A')
    else:
        print(f'You could not place {remaining} cards. You lost! \U0001F61E')

    total_lines = len(collected_output)
    print()
    print(f'There are {total_lines} lines of output. What do you want me to do?')
    print()
    print_options(total_lines)

    while True:
        user_input = input('       ')
        request_type, payload = parse_request(user_input, total_lines)
        if request_type == 'quit':
            return

        if request_type is not None:
            print()
            display_requested_lines(collected_output, request_type, payload)
            print()
            print_options(total_lines)
        else:
            print()
            print_options(total_lines)


if __name__ == '__main__':
    main()
