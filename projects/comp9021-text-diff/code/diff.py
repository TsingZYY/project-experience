import re
import sys

sys.setrecursionlimit(10000)


ERROR_MSG = "Cannot possibly be the commands for the diff of two files"

CMD_RE = re.compile(r'^(\d+)(?:,(\d+))?([acd])(\d+)(?:,(\d+))?$')


class DiffCommandsError(Exception):
    pass


class DiffCommands:
    def __init__(self, filename):
        with open(filename) as f:
            raw = f.read()

        lines = raw.splitlines()
        if not lines:
            self._cmds = []
            return

        self._cmds = [self._parse_line(line) for line in lines]
        self._check_consistency()

    @classmethod
    def _from_list(cls, cmds):
        obj = cls.__new__(cls)
        obj._cmds = cmds
        return obj

    @staticmethod
    def _parse_line(line):
        if ' ' in line:
            raise DiffCommandsError(ERROR_MSG)
        m = CMD_RE.match(line)
        if m is None:
            raise DiffCommandsError(ERROR_MSG)

        a, b, op, c, d = m.groups()
        a = int(a)
        b = int(b) if b is not None else None
        c = int(c)
        d = int(d) if d is not None else None

        if op == 'a':
            if b is not None:
                raise DiffCommandsError(ERROR_MSG)
            if c < 1:
                raise DiffCommandsError(ERROR_MSG)
            if d is not None and d <= c:
                raise DiffCommandsError(ERROR_MSG)
        elif op == 'd':
            if d is not None:
                raise DiffCommandsError(ERROR_MSG)
            if a < 1:
                raise DiffCommandsError(ERROR_MSG)
            if b is not None and b <= a:
                raise DiffCommandsError(ERROR_MSG)
        else:
            if a < 1 or c < 1:
                raise DiffCommandsError(ERROR_MSG)
            if b is not None and b <= a:
                raise DiffCommandsError(ERROR_MSG)
            if d is not None and d <= c:
                raise DiffCommandsError(ERROR_MSG)

        return (a, b, op, c, d)

    def _check_consistency(self):
        last_o, last_n = 0, 0
        for i, (a, b, op, c, d) in enumerate(self._cmds):
            if op == 'a':
                gap_o = a - last_o
                gap_n = c - 1 - last_n
            elif op == 'd':
                gap_o = a - 1 - last_o
                gap_n = c - last_n
            else:
                gap_o = a - 1 - last_o
                gap_n = c - 1 - last_n

            if gap_o < 0 or gap_n < 0 or gap_o != gap_n:
                raise DiffCommandsError(ERROR_MSG)
            if i > 0 and gap_o == 0:
                raise DiffCommandsError(ERROR_MSG)

            if op == 'a':
                last_o = a
                last_n = d if d is not None else c
            elif op == 'd':
                last_o = b if b is not None else a
                last_n = c
            else:
                last_o = b if b is not None else a
                last_n = d if d is not None else c

    def __str__(self):
        out = []
        for a, b, op, c, d in self._cmds:
            left = f'{a},{b}' if b is not None else str(a)
            right = f'{c},{d}' if d is not None else str(c)
            out.append(f'{left}{op}{right}')
        return '\n'.join(out)


class OriginalNewFiles:
    def __init__(self, original_filename, new_filename):
        with open(original_filename) as f:
            self.original = f.read().splitlines()
        with open(new_filename) as f:
            self.new = f.read().splitlines()
        self._dp = None

    def _build_dp(self):
        if self._dp is not None:
            return
        a, b = self.original, self.new
        m, n = len(a), len(b)
        dp = [[0] * (n + 1) for _ in range(m + 1)]
        for i in range(1, m + 1):
            ai = a[i - 1]
            row = dp[i]
            prev = dp[i - 1]
            for j in range(1, n + 1):
                if ai == b[j - 1]:
                    row[j] = prev[j - 1] + 1
                else:
                    row[j] = prev[j] if prev[j] >= row[j - 1] else row[j - 1]
        self._dp = dp

    def is_valid_diff(self, diff_commands):
        cmds = diff_commands._cmds
        orig, new = self.original, self.new

        if not cmds:
            return orig == new

        rebuilt = []
        i = 0
        for a, b, op, c, d in cmds:
            target_left = (a - 1) if op != 'a' else a
            while i < target_left:
                if i >= len(orig):
                    return False
                rebuilt.append(orig[i])
                i += 1

            if op == 'd':
                end = b if b is not None else a
                if end > len(orig):
                    return False
                i = end
            elif op == 'a':
                end = d if d is not None else c
                if end > len(new):
                    return False
                rebuilt.extend(new[c - 1:end])
            else:
                o_end = b if b is not None else a
                n_end = d if d is not None else c
                if o_end > len(orig) or n_end > len(new):
                    return False
                i = o_end
                rebuilt.extend(new[c - 1:n_end])

        rebuilt.extend(orig[i:])
        if rebuilt != new:
            return False

        self._build_dp()
        changed = 0
        for a, b, op, _, _ in cmds:
            if op == 'a':
                continue
            end = b if b is not None else a
            changed += end - a + 1
        return len(orig) - changed == self._dp[len(orig)][len(new)]

    def print_diff(self, diff_commands):
        orig, new = self.original, self.new
        for a, b, op, c, d in diff_commands._cmds:
            left = f'{a},{b}' if b is not None else str(a)
            right = f'{c},{d}' if d is not None else str(c)
            print(f'{left}{op}{right}')
            if op == 'd':
                end = b if b is not None else a
                for k in range(a - 1, end):
                    print(f'< {orig[k]}')
            elif op == 'a':
                end = d if d is not None else c
                for k in range(c - 1, end):
                    print(f'> {new[k]}')
            else:
                o_end = b if b is not None else a
                n_end = d if d is not None else c
                for k in range(a - 1, o_end):
                    print(f'< {orig[k]}')
                print('---')
                for k in range(c - 1, n_end):
                    print(f'> {new[k]}')

    def print_unmodified_from_original(self, diff_commands):
        touched = set()
        for a, b, op, _, _ in diff_commands._cmds:
            if op == 'a':
                continue
            end = b if b is not None else a
            touched.update(range(a, end + 1))
        self._print_kept(self.original, touched)

    def print_unmodified_from_new(self, diff_commands):
        touched = set()
        for _, _, op, c, d in diff_commands._cmds:
            if op == 'd':
                continue
            end = d if d is not None else c
            touched.update(range(c, end + 1))
        self._print_kept(self.new, touched)

    @staticmethod
    def _print_kept(lines, touched):
        kept = [k for k in range(1, len(lines) + 1) if k not in touched]
        if not kept:
            return
        if kept[0] > 1:
            print('...')
        prev = None
        for k in kept:
            if prev is not None and k > prev + 1:
                print('...')
            print(lines[k - 1])
            prev = k
        if kept[-1] < len(lines):
            print('...')

    def all_diff_commands(self):
        self._build_dp()
        m, n = len(self.original), len(self.new)
        dp = self._dp
        orig, new = self.original, self.new

        cache = {}

        def walk(i, j):
            if (i, j) in cache:
                return cache[(i, j)]
            if i == 0 or j == 0:
                out = {()}
                cache[(i, j)] = out
                return out
            here = dp[i][j]
            out = set()
            if orig[i - 1] == new[j - 1] and here == dp[i - 1][j - 1] + 1:
                for tail in walk(i - 1, j - 1):
                    out.add(tail + ((i, j),))
            if dp[i - 1][j] == here:
                out.update(walk(i - 1, j))
            if dp[i][j - 1] == here:
                out.update(walk(i, j - 1))
            cache[(i, j)] = out
            return out

        seen = set()
        results = []
        for matches in walk(m, n):
            cmds = self._matches_to_commands(matches, m, n)
            dc = DiffCommands._from_list(cmds)
            key = str(dc)
            if key in seen:
                continue
            seen.add(key)
            results.append(dc)

        results.sort(key=str)
        return results

    @staticmethod
    def _matches_to_commands(matches, m, n):
        cmds = []
        prev_o, prev_n = 0, 0
        for oi, ni in list(matches) + [(m + 1, n + 1)]:
            o_lo, o_hi = prev_o + 1, oi - 1
            n_lo, n_hi = prev_n + 1, ni - 1
            has_o = o_lo <= o_hi
            has_n = n_lo <= n_hi

            if has_o and has_n:
                b = o_hi if o_hi > o_lo else None
                d = n_hi if n_hi > n_lo else None
                cmds.append((o_lo, b, 'c', n_lo, d))
            elif has_o:
                b = o_hi if o_hi > o_lo else None
                cmds.append((o_lo, b, 'd', prev_n, None))
            elif has_n:
                d = n_hi if n_hi > n_lo else None
                cmds.append((prev_o, None, 'a', n_lo, d))

            prev_o, prev_n = oi, ni
        return cmds
