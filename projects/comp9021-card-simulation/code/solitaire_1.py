import sys
from itertools import chain
from random import seed, shuffle
from collections import defaultdict

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

deck = list(range(52))


def is_picture(card):
    return card % 13 in {10, 11, 12}


def card_to_unicode(card):
    suit = card // 13
    rank = card % 13

    base = [0x1F0B0, 0x1F0C0, 0x1F0D0, 0x1F0A0][suit]
    value = rank + 1
    if value >= 12:
        value += 1

    return chr(base + value)


def print_layout(layout):
    for row in range(4):
        pieces = []
        for col in range(4):
            index = row * 4 + col
            if layout[index] is None:
                pieces.append('')
            else:
                pieces.append(card_to_unicode(layout[index]))
        print('\t' + '\t'.join(pieces).rstrip())


def simulate_one_round(deck, total_removed_so_far):
    layout = []
    for _ in range(16):
        layout.append(deck.pop())
    removed = 0

    while True:
        picture_positions = [i for i, card in enumerate(layout) if card is not None and is_picture(card)]
        n = len(picture_positions)

        if n == 0:
            break

        removed += n

        for i in picture_positions:
            layout[i] = None

        if total_removed_so_far + removed == 12:
            break

        for i in range(len(layout)):
            if layout[i] is None and deck:
                layout[i] = deck.pop()

    return layout, deck, removed


def count_removed_pictures(seed_value):
    deck = list(range(52))
    total_removed = 0

    for _ in range(4):
        deck = sorted(deck)
        seed(seed_value)
        shuffle(deck)

        layout, deck, removed = simulate_one_round(deck, total_removed)
        total_removed += removed

        if total_removed == 12:
            return total_removed

        deck.extend(card for card in layout if card is not None)
        seed_value += 1

    return total_removed



def play_one_round(deck, total_removed_so_far):
    layout = []
    for _ in range(16):
        layout.append(deck.pop())
    removed = 0
    drawn = 16

    while True:
        print()
        print(f'Drawing {drawn} card:' if drawn == 1 else f'Drawing {drawn} cards:')
        print(']' * len(deck))
        print_layout(layout)


        picture_positions = [i for i, card in enumerate(layout) if card is not None and is_picture(card)]
        n = len(picture_positions)

        if n == 0:
            break

        removed += n
        

        for i in picture_positions:
            layout[i] = None

        print()
        print(f'Removing {n} picture card:' if n == 1 else f'Removing {n} picture cards:')
        print_layout(layout)
        
        if total_removed_so_far + removed == 12:
            break

        drawn = 0
        for i in range(len(layout)):
            if layout[i] is None and deck:
                layout[i] = deck.pop()
                drawn += 1

    return layout, deck, removed


def play_game(seed_value):
    deck = list(range(52))
    total_removed = 0

    print()
    print('Deck shuffled. Ready to start!')
    print(']' * 52)

    for round_number in range(4):
        deck = sorted(deck)
        seed(seed_value)
        shuffle(deck)

        print()
        if round_number == 0:
            print('Starting the first round...')
        elif round_number ==1:
            print('After shuffling, starting the second round...')
        elif round_number == 2:
            print('After shuffling, starting the third round...')
        else:
            print('After shuffling, starting the fourth round...')

        layout, deck, removed = play_one_round(deck,total_removed)
        total_removed += removed

        if total_removed == 12:
            print()
            print('You removed all picture cards. You won! 😀')
            return

        deck.extend(card for card in layout if card is not None)
        seed_value += 1

    print()
    if total_removed == 0:
        print('You removed no picture cards. You lost! 😞')
    elif total_removed == 1:
        print('You removed only 1 picture card. You lost! 😞')
    else:
        print(f'You removed only {total_removed} picture cards. You lost! 😞')
def simulate(n, i):
    frequencies = defaultdict(int)

    for g in range(n):
        removed = count_removed_pictures(i + g)
        frequencies[removed] += 1

    print('Number of picture cards removed | Relative frequency')
    print('----------------------------------------------------')
    for removed in sorted(frequencies):
        percentage = frequencies[removed] / n * 100
        print(f'{removed:>31} | {percentage:>17.2f}%')


def main():
    seed_value = int(input('Enter an integer to pass to the seed() function: '))
    play_game(seed_value)


if __name__ == '__main__':
    main()
