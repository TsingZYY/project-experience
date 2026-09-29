"""NumPy MARL coursework core, extracted for portfolio code review.

This preserves selected environment, learning and evaluation definitions from
the historical notebook. Importing defines code; it does not train or evaluate.
Matplotlib/imageio rendering hooks, figures, checkpoints and automatic execution
cells are omitted. See ../CODE.md for source provenance and usage boundaries.
"""
import numpy as np


# 历史实验配置
SEED    = 0

CFG = dict(
    gamma=0.98, lam=0.95, clip=0.2,            # discount, GAE-lambda, PPO clip epsilon
    lr_actor=3e-4, lr_critic=1e-3,             # Adam learning rates
    weight_decay=1e-5,                          # Adam weight decay
    rollout=512, minibatch=128, epochs=8,      # rollout length, minibatch size, PPO epochs
    hidden=(64, 64), c1=0.5, c2=0.05,          # MLP hidden sizes, critic & entropy coefficients
    grad_clip=0.5, max_steps=50,               # global grad-norm clip, episode horizon
    use_safety_shield=True,                     # soft boundary+fragile+robot collision prevention
    val_interval=25, val_episodes=64,            # fixed-seed validation checkpoint selection
)

ITERS  = 400

EVAL34 = 300

EVAL5  = 400


# 环境常量与轻量空间接口
GRID_SIZE = 12

N_AGENTS = 3

MAX_STEPS = 50

IDLE, UP, DOWN, LEFT, RIGHT = 0, 1, 2, 3, 4

ACTION_NAMES = {0: "IDLE", 1: "UP", 2: "DOWN", 3: "LEFT", 4: "RIGHT"}

ACTION_DELTA = {IDLE: (0, 0), UP: (-1, 0), DOWN: (1, 0), LEFT: (0, -1), RIGHT: (0, 1)}

N_ACTIONS = 5

N_CHANNELS = 5

def _to0(one_based_coordinates):
    """Convert assignment-table coordinates to internal 0-based tuples."""
    return [(row - 1, col - 1) for row, col in one_based_coordinates]

START_POSITIONS = _to0([(1, 3), (12, 3), (7, 12)])

FRAGILE_CELLS = _to0([
    (2, 2), (4, 4), (6, 6), (7, 2), (8, 4), (10, 6),
    (1, 7), (4, 7), (8, 7), (12, 7),
    (3, 11), (8, 9), (6, 10), (11, 11),
])

LARGE_DIRT_CELLS = _to0([
    (2, 5), (3, 9), (4, 2), (6, 7),
    (8, 8), (9, 4), (10, 11), (12, 2),
])

NORMAL_DIRT_CELLS = _to0([
    (1, 4), (1, 10), (3, 2), (4, 8),
    (5, 9), (7, 3), (9, 11), (12, 6),
])

R_NORMAL_DIRT = 2.0

R_LARGE_DIRT = 4.0

R_EXPLORE = 2.0

R_REVISIT = -1.0

R_IDLE = -0.1

R_TIMESTEP = -0.1

R_COLLISION = -20.0

R_COMPLETE = 20.0

AGENT_COLORS = {0: "#F2C200", 1: "#3FA34D", 2: "#3B7DD8"}

class MultiDiscreteSpace:
    """Small dependency-free equivalent of a joint discrete space."""

    def __init__(self, number_of_actions, seed=None):
        self.nvec = np.asarray(number_of_actions, dtype=np.int64)
        self.shape = self.nvec.shape
        self.dtype = np.dtype(np.int64)
        self.seed(seed)

    def seed(self, seed=None):
        self._rng = np.random.default_rng(seed)
        return [seed]

    def sample(self):
        return np.asarray(
            [self._rng.integers(n) for n in self.nvec], dtype=self.dtype
        )

    def contains(self, actions):
        actions = np.asarray(actions)
        return bool(
            actions.shape == self.shape
            and np.issubdtype(actions.dtype, np.integer)
            and np.all(actions >= 0)
            and np.all(actions < self.nvec)
        )

    def __repr__(self):
        return f"MultiDiscrete({self.nvec.tolist()})"

class BinaryArraySpace:
    """Shape and validity contract for the joint binary observation."""

    def __init__(self, shape, seed=None):
        self.shape = tuple(shape)
        self.dtype = np.dtype(np.float32)
        self.seed(seed)

    def seed(self, seed=None):
        self._rng = np.random.default_rng(seed)
        return [seed]

    def sample(self):
        return self._rng.integers(0, 2, self.shape).astype(self.dtype)

    def contains(self, observation):
        observation = np.asarray(observation)
        return bool(
            observation.shape == self.shape
            and np.all((observation == 0) | (observation == 1))
        )

    def __repr__(self):
        return f"BinaryArray(shape={self.shape}, dtype=float32)"


# 三机器人清洁环境
class MultiAgentCleaningEnv:
    """Cooperative multi-agent cleaning grid world (Gymnasium-style API)."""

    metadata = {"render_modes": ["human", "rgb_array"], "render_fps": 4}
    _render_hook = None
    _close_hook = None

    def __init__(self, mode="fixed", use_safety_shield=True,
                 max_steps=MAX_STEPS, seed=None, render_mode=None):
        assert mode in ("fixed", "random")
        if render_mode not in (None, *self.metadata["render_modes"]):
            raise ValueError(f"unsupported render_mode: {render_mode!r}")
        self.mode = mode
        self.use_safety_shield = use_safety_shield
        self.max_steps = max_steps
        self.render_mode = render_mode
        self.rng = np.random.default_rng(seed)

        self.n_agents = N_AGENTS
        self.grid_size = GRID_SIZE
        self.n_actions = N_ACTIONS
        self.obs_shape = (GRID_SIZE, GRID_SIZE, N_CHANNELS)
        self.obs_dim = GRID_SIZE * GRID_SIZE * N_CHANNELS
        self.state_dim = self.obs_dim * self.n_agents
        self.action_space = MultiDiscreteSpace([N_ACTIONS] * N_AGENTS, seed)
        self.observation_space = BinaryArraySpace(
            (N_AGENTS, *self.obs_shape), seed
        )

        self.fragile = set(FRAGILE_CELLS)
        self.start = list(START_POSITIONS)
        self._build_static()
        self.reset(seed=seed)

    def _build_static(self):
        self.fragile_map = np.zeros((GRID_SIZE, GRID_SIZE), np.float32)
        for (r, c) in self.fragile:
            self.fragile_map[r, c] = 1.0

    def _sample_dirt(self):
        """Return fixed dirt cells or sample an equally sized random layout."""
        if self.mode == "fixed":
            return set(NORMAL_DIRT_CELLS), set(LARGE_DIRT_CELLS)
        blocked = set(self.fragile) | set(self.start)
        free = [(r, c) for r in range(GRID_SIZE) for c in range(GRID_SIZE)
                if (r, c) not in blocked]
        idx = self.rng.choice(len(free),
                              size=len(NORMAL_DIRT_CELLS) + len(LARGE_DIRT_CELLS),
                              replace=False)
        chosen = [free[i] for i in idx]
        normal = set(chosen[:len(NORMAL_DIRT_CELLS)])
        large = set(chosen[len(NORMAL_DIRT_CELLS):])
        return normal, large

    def reset(self, *, seed=None, options=None):
        """Start a new episode and return all local observations plus info."""
        if seed is not None:
            self.rng = np.random.default_rng(seed)
            self.action_space.seed(seed)
            self.observation_space.seed(seed)
        self.t = 0
        self.positions = [list(p) for p in self.start]
        self.normal_dirt, self.large_dirt = self._sample_dirt()
        self.total_dirt = len(self.normal_dirt) + len(self.large_dirt)
        self.explored = np.zeros((GRID_SIZE, GRID_SIZE), np.float32)
        self.owner = -np.ones((GRID_SIZE, GRID_SIZE), np.int8)
        for i, (r, c) in enumerate(self.positions):
            self.explored[r, c] = 1.0
            self.owner[r, c] = i
        self.visit_map = np.zeros((GRID_SIZE, GRID_SIZE), np.float32)
        self.revisit_map = np.zeros((GRID_SIZE, GRID_SIZE), np.float32)
        self.shield_interventions = 0
        self.action_attempts = 0
        for (r, c) in self.positions:
            self.visit_map[r, c] += 1.0
        self.done = False
        info = {"cleaned": 0, "total_dirt": self.total_dirt}
        return self._all_obs(), info

    def _docking_map(self, i):
        m = np.zeros((GRID_SIZE, GRID_SIZE), np.float32)
        r, c = self.start[i]
        m[r, c] = 1.0
        return m

    def _obs_for(self, i):
        """Build the five-channel partial observation for one agent."""
        self_map = np.zeros((GRID_SIZE, GRID_SIZE), np.float32)
        other_map = np.zeros((GRID_SIZE, GRID_SIZE), np.float32)
        for j, (r, c) in enumerate(self.positions):
            if j == i:
                self_map[r, c] = 1.0
            else:
                other_map[r, c] = 1.0
        obs = np.stack([self.fragile_map, self_map, other_map,
                        self.explored, self._docking_map(i)], axis=-1)
        return obs

    def _all_obs(self):
        return np.stack(
            [self._obs_for(agent_id) for agent_id in range(self.n_agents)],
            axis=0,
        )

    def global_state(self):
        """Flatten all local observations for MAPPO's central critic."""
        return self._all_obs().reshape(-1).copy()

    def _in_bounds(self, r, c):
        return 0 <= r < GRID_SIZE and 0 <= c < GRID_SIZE

    def _targets_conflict(self, first_agent, second_agent, targets):
        """Detect agents entering the same cell or swapping positions."""
        same_target = targets[first_agent] == targets[second_agent]
        swapped_positions = (
            targets[first_agent] == tuple(self.positions[second_agent])
            and targets[second_agent] == tuple(self.positions[first_agent])
        )
        return same_target or swapped_positions

    def step(self, actions):
        """Apply one joint action and return the Gymnasium-style transition.

        ``terminated`` means all dirt was cleaned. ``truncated`` means the
        episode stopped because of a violation or the time horizon.
        """
        assert not self.done, "step() on a finished episode; call reset()."
        if not self.action_space.contains(actions):
            raise ValueError(
                f"joint action must be in {self.action_space}; got {actions!r}"
            )
        actions = np.asarray(actions, dtype=np.int64).tolist()
        self.t += 1
        self.action_attempts += self.n_agents
        rewards = np.zeros(self.n_agents, np.float32)
        info = {"events": [[] for _ in range(self.n_agents)],
                "collision": False, "boundary": False,
                "success": False, "time_limit": False}

        # Phase 1 - propose one target cell for every agent.
        intended = []
        for i, a in enumerate(actions):
            dr, dc = ACTION_DELTA[a]
            r, c = self.positions[i]
            intended.append((r + dr, c + dc))
        eff_actions = list(actions)
        eff_target = list(intended)

        # Phase 2 - turn unsafe proposals into IDLE before execution.
        if self.use_safety_shield:
            shielded_agents = set()
            for i, (r, c) in enumerate(eff_target):
                if not self._in_bounds(r, c) or (r, c) in self.fragile:
                    if eff_actions[i] != IDLE:
                        shielded_agents.add(i)
                    eff_actions[i] = IDLE
                    eff_target[i] = tuple(self.positions[i])
            # Iterate to a fixed point: making one agent IDLE can create a
            # new conflict with another agent targeting its current cell.
            changed = True
            while changed:
                changed = False
                for i in range(self.n_agents):
                    for j in range(i + 1, self.n_agents):
                        if self._targets_conflict(i, j, eff_target):
                            for k in (i, j):
                                if eff_actions[k] != IDLE:
                                    shielded_agents.add(k)
                                    eff_actions[k] = IDLE
                                    eff_target[k] = tuple(self.positions[k])
                                    changed = True
            self.shield_interventions += len(shielded_agents)

        # Phase 3 - with the shield disabled, detect Table-2 violations.
        truncate = False
        for i in range(self.n_agents):
            r, c = eff_target[i]
            if not self._in_bounds(r, c):
                rewards[i] += R_COLLISION
                info["events"][i].append(f"boundary({R_COLLISION:g})")
                info["boundary"] = True
                truncate = True
                continue
            if (r, c) in self.fragile:
                rewards[i] += R_COLLISION
                info["events"][i].append(
                    f"fragile_collision({R_COLLISION:g})"
                )
                info["collision"] = True
                truncate = True
        for i in range(self.n_agents):
            for j in range(i + 1, self.n_agents):
                if not self._in_bounds(*eff_target[i]) or not self._in_bounds(*eff_target[j]):
                    continue
                if self._targets_conflict(i, j, eff_target):
                    rewards[i] += R_COLLISION
                    rewards[j] += R_COLLISION
                    collision_event = f"robot_collision({R_COLLISION:g})"
                    info["events"][i].append(collision_event)
                    info["events"][j].append(collision_event)
                    info["collision"] = True
                    truncate = True

        if truncate:
            rewards += R_TIMESTEP
            self.done = True
            obs = self._all_obs()
            info["cleaned"] = self.total_dirt - (len(self.normal_dirt) + len(self.large_dirt))
            return obs, rewards, False, True, info

        # Phase 4 - execute safe moves and accumulate all triggered rewards.
        for i in range(self.n_agents):
            r, c = eff_target[i]
            self.positions[i] = [r, c]
            if eff_actions[i] == IDLE:
                # IDLE adds its action penalty but skips traversal bookkeeping.
                # The common R_TIMESTEP penalty is still added after this loop.
                rewards[i] += R_IDLE
                info["events"][i].append(f"idle({R_IDLE:g})")
                continue
            # the agent actually moved onto cell (r, c) -> count the traversal
            self.visit_map[r, c] += 1.0
            if self.explored[r, c] == 0.0:
                self.explored[r, c] = 1.0
                self.owner[r, c] = i
                rewards[i] += R_EXPLORE
                info["events"][i].append(f"explore({R_EXPLORE:+g})")
            else:
                self.revisit_map[r, c] += 1.0
                rewards[i] += R_REVISIT
                info["events"][i].append(f"revisit({R_REVISIT:g})")
            if (r, c) in self.normal_dirt:
                self.normal_dirt.discard((r, c))
                rewards[i] += R_NORMAL_DIRT
                info["events"][i].append(
                    f"normal_dirt({R_NORMAL_DIRT:+g})"
                )
            elif (r, c) in self.large_dirt:
                self.large_dirt.discard((r, c))
                rewards[i] += R_LARGE_DIRT
                info["events"][i].append(
                    f"large_dirt({R_LARGE_DIRT:+g})"
                )

        rewards += R_TIMESTEP

        # Phase 5 - decide success termination or time-limit truncation.
        remaining_dirt = len(self.normal_dirt) + len(self.large_dirt)
        cleaned = self.total_dirt - remaining_dirt
        terminated = remaining_dirt == 0
        if terminated:
            rewards += R_COMPLETE
            info["success"] = True
            self.done = True
        truncated = False
        if not terminated and self.t >= self.max_steps:
            truncated = True
            info["time_limit"] = True
            self.done = True
        info["cleaned"] = cleaned
        return self._all_obs(), rewards, terminated, truncated, info

    def render(self):
        """Render through the Matplotlib hook registered in Task 1.2."""
        if self.render_mode is None:
            raise RuntimeError(
                "construct the environment with render_mode='human' "
                "or render_mode='rgb_array'"
            )
        render_hook = type(self)._render_hook
        if render_hook is None:
            raise RuntimeError("run the Task 1.2 visualization cell first")
        return render_hook(self, self.render_mode)

    def close(self):
        """Close a human-rendering figure, if one is open."""
        close_hook = type(self)._close_hook
        if close_hook is not None:
            close_hook(self)

    def weighted_clean_fraction(self):
        """Success-rate metric: fraction of dirt cleaned, large dirt worth 2x."""
        total_weight = len(NORMAL_DIRT_CELLS) + 2 * len(LARGE_DIRT_CELLS)
        remaining_weight = len(self.normal_dirt) + 2 * len(self.large_dirt)
        return (total_weight - remaining_weight) / total_weight


# NumPy 神经网络与 Adam
def orthogonal(shape, std, rng):
    """Orthogonal initialisation (as used by PPO reference implementations)."""
    if len(shape) < 2:
        return (std * rng.standard_normal(shape)).astype(np.float32)
    rows, cols = shape
    a = rng.standard_normal((rows, cols))
    u, _, vt = np.linalg.svd(a, full_matrices=False)   # handles rectangular shapes
    q = u if u.shape == (rows, cols) else vt
    return (std * q).astype(np.float32)

class Linear:
    """Fully connected layer with manually stored parameter gradients."""

    def __init__(self, in_dim, out_dim, std, rng):
        self.W = orthogonal((in_dim, out_dim), std, rng)
        self.b = np.zeros(out_dim, np.float32)
        self.dW = np.zeros_like(self.W)
        self.db = np.zeros_like(self.b)

    def forward(self, x):
        self.x = x
        return x @ self.W + self.b

    def backward(self, g):
        self.dW[...] = self.x.T @ g
        self.db[...] = g.sum(0)
        return g @ self.W.T

    def params(self):
        return [self.W, self.b]

    def grads(self):
        return [self.dW, self.db]

class Tanh:
    """Tanh activation that caches its output for manual backpropagation."""

    def forward(self, x):
        self.y = np.tanh(x)
        return self.y

    def backward(self, g):
        return g * (1.0 - self.y ** 2)

    def params(self):
        return []

    def grads(self):
        return []

class MLP:
    """Linear -> Tanh -> ... -> Linear (final layer is linear)."""
    def __init__(self, in_dim, hidden_sizes, out_dim, out_std, rng, hidden_std=np.sqrt(2)):
        self.layers = []
        d = in_dim
        for h in hidden_sizes:
            self.layers += [Linear(d, h, hidden_std, rng), Tanh()]
            d = h
        self.layers.append(Linear(d, out_dim, out_std, rng))

    def forward(self, x):
        for layer in self.layers:
            x = layer.forward(x)
        return x

    def backward(self, g):
        for layer in reversed(self.layers):
            g = layer.backward(g)
        return g

    def params(self):
        return [parameter for layer in self.layers for parameter in layer.params()]

    def grads(self):
        return [gradient for layer in self.layers for gradient in layer.grads()]

    def n_params(self):
        return int(sum(p.size for p in self.params()))

class Adam:
    """Minimal Adam optimizer with weight decay and global-norm clipping."""

    def __init__(self, params, lr, weight_decay=0.0, betas=(0.9, 0.999), eps=1e-8):
        self.params = params
        self.lr = lr
        self.wd = weight_decay
        self.b1, self.b2 = betas
        self.eps = eps
        self.m = [np.zeros_like(p) for p in params]
        self.v = [np.zeros_like(p) for p in params]
        self.t = 0

    def step(self, grads, max_norm=None):
        """Clip gradients if requested, then apply one Adam update."""
        if max_norm is not None:                    # global grad-norm clipping
            total = np.sqrt(sum(float((g ** 2).sum()) for g in grads)) + 1e-12
            scale = min(1.0, max_norm / total)
            if scale < 1.0:
                grads = [g * scale for g in grads]
        self.t += 1
        for i, (p, g) in enumerate(zip(self.params, grads)):
            if self.wd:
                g = g + self.wd * p
            self.m[i] = self.b1 * self.m[i] + (1 - self.b1) * g
            self.v[i] = self.b2 * self.v[i] + (1 - self.b2) * (g * g)
            mhat = self.m[i] / (1 - self.b1 ** self.t)
            vhat = self.v[i] / (1 - self.b2 ** self.t)
            p -= self.lr * mhat / (np.sqrt(vhat) + self.eps)


# 策略、价值函数、GAE 与 PPO 梯度
def log_softmax(z):
    """Numerically stable row-wise log-softmax."""
    z = z - z.max(axis=1, keepdims=True)
    return z - np.log(np.exp(z).sum(axis=1, keepdims=True))

def softmax(z):
    """Numerically stable row-wise softmax."""
    return np.exp(log_softmax(z))

def categorical_logp_entropy(logits, actions):
    """Return (log_prob(actions), entropy, probs, logprobs)."""
    logp = log_softmax(logits)
    p = np.exp(logp)
    idx = np.arange(len(actions))
    logp_a = logp[idx, actions]
    entropy = -(p * logp).sum(axis=1)
    return logp_a, entropy, p, logp

class PolicyNet:
    """Categorical actor mapping a batch of observations to five actions."""

    def __init__(self, obs_dim, n_actions, hidden, rng, out_std=0.01):
        self.mlp = MLP(obs_dim, hidden, n_actions, out_std, rng)
        self.n_actions = n_actions

    def logits(self, obs):
        return self.mlp.forward(obs)

    def act(self, obs, rng, deterministic=False):
        """Sample (or argmax) actions for a batch of observations."""
        logp_all = log_softmax(self.mlp.forward(obs))
        p = np.exp(logp_all)
        if deterministic:
            actions = p.argmax(axis=1)
        else:
            actions = np.array([rng.choice(self.n_actions, p=pi) for pi in p])
        logp_a = logp_all[np.arange(len(actions)), actions]
        return actions, logp_a, p

class ValueNet:
    """Critic mapping each input state to one scalar value estimate."""

    def __init__(self, in_dim, hidden, rng, out_std=1.0):
        self.mlp = MLP(in_dim, hidden, 1, out_std, rng)

    def value(self, x):
        return self.mlp.forward(x)[:, 0]

def compute_gae(rewards, values, dones, gamma=0.95, lam=0.95, last_value=0.0,
                timeouts=None, bootstrap_values=None):
    """Compute GAE advantages and value targets for one rollout.

    A true terminal state bootstraps with zero. A time-limit truncation uses
    its supplied next-state value, but still stops the GAE recursion so an
    advantage never leaks across the environment reset. ``last_value`` handles
    a rollout that ends part-way through an unfinished episode.
    """
    num_steps = len(rewards)
    timeouts = (
        np.zeros(num_steps, np.float32)
        if timeouts is None else np.asarray(timeouts)
    )
    bootstrap_values = (
        np.zeros(num_steps, np.float32)
        if bootstrap_values is None else np.asarray(bootstrap_values)
    )
    advantages = np.zeros(num_steps, np.float32)
    next_advantage = 0.0
    for step in reversed(range(num_steps)):
        if dones[step]:
            next_value = bootstrap_values[step] if timeouts[step] else 0.0
        else:
            next_value = (
                last_value if step == num_steps - 1 else values[step + 1]
            )
        continuation = 1.0 - dones[step]
        td_error = rewards[step] + gamma * next_value - values[step]
        next_advantage = (
            td_error + gamma * lam * continuation * next_advantage
        )
        advantages[step] = next_advantage
    target_returns = advantages + np.asarray(values, np.float32)
    return advantages.astype(np.float32), target_returns.astype(np.float32)

def ppo_actor_loss_and_grad(
    policy, observations, actions, old_log_probs, advantages,
    clip_epsilon, entropy_coefficient, norm_adv=True,
):
    """Return PPO actor diagnostics and the hand-derived logits gradient."""
    if norm_adv:
        advantages = (
            (advantages - advantages.mean()) / (advantages.std() + 1e-8)
        )

    # 1. New/old action-probability ratio and clipped surrogate objective.
    logits = policy.logits(observations)
    selected_log_probs, entropy, probabilities, all_log_probs = (
        categorical_logp_entropy(logits, actions)
    )
    probability_ratio = np.exp(selected_log_probs - old_log_probs)
    unclipped_surrogate = probability_ratio * advantages
    clipped_surrogate = (
        np.clip(probability_ratio, 1 - clip_epsilon, 1 + clip_epsilon)
        * advantages
    )
    per_sample_loss = -np.minimum(unclipped_surrogate, clipped_surrogate)
    actor_loss = per_sample_loss.mean()
    entropy_bonus = entropy.mean()
    batch_size = len(actions)

    # 2. Differentiate only through the branch selected by min + clamp.
    unclipped_branch = (
        unclipped_surrogate <= clipped_surrogate
    ).astype(np.float32)
    clamp_has_gradient = (
        (probability_ratio > 1 - clip_epsilon)
        & (probability_ratio < 1 + clip_epsilon)
    ).astype(np.float32)
    loss_gradient_wrt_ratio = (
        -advantages
        * (unclipped_branch + (1 - unclipped_branch) * clamp_has_gradient)
        / batch_size
    )
    loss_gradient_wrt_selected_log_prob = (
        loss_gradient_wrt_ratio * probability_ratio
    )
    one_hot_actions = np.zeros_like(logits)
    one_hot_actions[np.arange(batch_size), actions] = 1.0
    clipped_gradient = loss_gradient_wrt_selected_log_prob[:, None] * (
        one_hot_actions - probabilities
    )

    # 3. Entropy gradient encourages exploration; c2 is applied here once.
    entropy_gradient = (entropy_coefficient / batch_size) * probabilities * (
        all_log_probs + entropy[:, None]
    )
    gradient_logits = (clipped_gradient + entropy_gradient).astype(np.float32)
    stats = dict(
        actor=float(actor_loss),
        entropy=float(entropy_bonus),
        approx_kl=float(np.mean(
            (probability_ratio - 1) - np.log(probability_ratio + 1e-12)
        )),
        clipfrac=float(np.mean(
            np.abs(probability_ratio - 1) > clip_epsilon
        )),
    )
    return actor_loss, entropy_bonus, gradient_logits, stats

def value_loss_and_grad(critic, inputs, target_returns, critic_coefficient):
    """Return unweighted MSE plus its c1-weighted value gradient."""
    predicted_values = critic.value(inputs)
    prediction_error = predicted_values - target_returns
    critic_loss = (prediction_error ** 2).mean()
    batch_size = len(target_returns)
    value_gradient = (
        critic_coefficient * 2.0 * prediction_error / batch_size
    ).astype(np.float32)[:, None]
    return critic_loss, value_gradient


# IPPO 的初始化、采样与更新
def flatten_observations(observations):
    """Flatten one joint observation into a list of local vectors."""
    return [
        observation.reshape(-1).astype(np.float32)
        for observation in observations
    ]

def is_time_limit_truncation(env, terminated, truncated, info):
    """True only for horizon truncation, which may bootstrap V(s')."""
    return bool(
        truncated
        and not terminated
        and info.get("time_limit", False)
    )

class RolloutBuffer:
    """Store per-agent transitions plus computed GAE targets."""

    def __init__(self, n_agents):
        self.n_agents = n_agents
        self.clear()

    def clear(self):
        keys = ("obs", "state", "act", "logp", "rew", "val", "done",
                "timeout", "bootstrap")
        self.data = [
            {field: [] for field in keys} for _ in range(self.n_agents)
        ]
        self.advantages = [None] * self.n_agents
        self.returns = [None] * self.n_agents

    def add(self, agent_id, **transition):
        """Append the named fields of one agent transition."""
        for field, value in transition.items():
            self.data[agent_id][field].append(value)

    def as_arrays(self, agent_id):
        """Return populated fields as arrays, including GAE when ready."""
        arrays = {}
        for field, values in self.data[agent_id].items():
            if len(values):
                arrays[field] = np.array(values)
        if self.advantages[agent_id] is not None:
            arrays["adv"] = self.advantages[agent_id]
            arrays["ret"] = self.returns[agent_id]
        return arrays

def make_ippo(obs_dim, n_actions, cfg, rng):
    """Create one independent actor, critic and optimizer pair per agent."""
    actors = []
    critics = []
    actor_optimizers = []
    critic_optimizers = []
    for _ in range(N_AGENTS):
        actor = PolicyNet(obs_dim, n_actions, cfg["hidden"], rng)
        critic = ValueNet(obs_dim, cfg["hidden"], rng)
        actors.append(actor)
        critics.append(critic)
        actor_optimizers.append(
            Adam(actor.mlp.params(), cfg["lr_actor"], cfg["weight_decay"])
        )
        critic_optimizers.append(
            Adam(critic.mlp.params(), cfg["lr_critic"], cfg["weight_decay"])
        )
    return {
        "actors": actors,
        "critics": critics,
        "actor_optimizers": actor_optimizers,
        "critic_optimizers": critic_optimizers,
    }

def collect_ippo(env, models, cfg, rng):
    """Collect local IPPO trajectories and compute per-agent GAE targets."""
    rollout_buffer = RolloutBuffer(env.n_agents)
    episode_stats = {
        key: [] for key in ("ret", "team", "length", "success", "violation", "clean")
    }
    observations, _ = env.reset()
    flat_observations = flatten_observations(observations)
    episode_returns = np.zeros(env.n_agents)
    episode_length = 0

    for _ in range(cfg["rollout"]):
        actions = np.zeros(env.n_agents, dtype=int)
        log_probs = np.zeros(env.n_agents)
        values = np.zeros(env.n_agents)
        for agent_id in range(env.n_agents):
            action, log_prob, _ = models["actors"][agent_id].act(
                flat_observations[agent_id][None, :], rng
            )
            value = models["critics"][agent_id].value(
                flat_observations[agent_id][None, :]
            )[0]
            actions[agent_id] = action[0]
            log_probs[agent_id] = log_prob[0]
            values[agent_id] = value

        next_observations, rewards, terminated, truncated, info = env.step(actions)
        episode_done = bool(terminated or truncated)
        next_flat_observations = flatten_observations(next_observations)
        # Only a horizon cutoff may bootstrap; failures and true terminals may not.
        time_limit = is_time_limit_truncation(
            env, terminated, truncated, info
        )
        bootstrap_values = np.zeros(env.n_agents, dtype=np.float32)
        if time_limit:
            bootstrap_values = np.asarray([
                models["critics"][agent_id].value(
                    next_flat_observations[agent_id][None, :]
                )[0]
                for agent_id in range(env.n_agents)
            ], dtype=np.float32)

        for agent_id in range(env.n_agents):
            rollout_buffer.add(
                agent_id,
                obs=flat_observations[agent_id],
                act=int(actions[agent_id]),
                logp=log_probs[agent_id],
                rew=float(rewards[agent_id]),
                val=values[agent_id],
                done=float(episode_done),
                timeout=float(time_limit),
                bootstrap=bootstrap_values[agent_id],
            )

        episode_returns += rewards
        episode_length += 1
        flat_observations = next_flat_observations

        if episode_done:
            episode_stats["ret"].append(episode_returns.copy())
            episode_stats["team"].append(episode_returns.sum())
            episode_stats["length"].append(episode_length)
            episode_stats["success"].append(float(info.get("success", False)))
            episode_stats["violation"].append(float(info.get("collision", False)))
            episode_stats["clean"].append(env.weighted_clean_fraction())
            observations, _ = env.reset()
            flat_observations = flatten_observations(observations)
            episode_returns = np.zeros(env.n_agents)
            episode_length = 0

    # The rollout can end mid-episode, so its final state also supplies V(s').
    for agent_id in range(env.n_agents):
        final_value = models["critics"][agent_id].value(
            flat_observations[agent_id][None, :]
        )[0]
        agent_data = rollout_buffer.as_arrays(agent_id)
        advantages, target_returns = compute_gae(
            agent_data["rew"],
            agent_data["val"],
            agent_data["done"],
            cfg["gamma"],
            cfg["lam"],
            final_value,
            agent_data["timeout"],
            agent_data["bootstrap"],
        )
        rollout_buffer.advantages[agent_id] = advantages
        rollout_buffer.returns[agent_id] = target_returns
    return rollout_buffer, episode_stats

def update_ippo(models, rollout_buffer, cfg, rng):
    """Apply an independent PPO update to each agent's actor/critic pair."""
    loss_by_agent = []
    for agent_id in range(rollout_buffer.n_agents):
        actor = models["actors"][agent_id]
        critic = models["critics"][agent_id]
        actor_optimizer = models["actor_optimizers"][agent_id]
        critic_optimizer = models["critic_optimizers"][agent_id]
        agent_data = rollout_buffer.as_arrays(agent_id)
        observations = agent_data["obs"]
        actions = agent_data["act"]
        old_log_probs = agent_data["logp"]
        advantages = agent_data["adv"]
        target_returns = agent_data["ret"]
        # Normalize once on the complete rollout, never again per minibatch.
        advantages = (advantages - advantages.mean()) / (advantages.std() + 1e-8)

        sample_indices = np.arange(len(actions))
        losses = {key: [] for key in ("total", "actor", "critic", "entropy")}
        for _ in range(cfg["epochs"]):
            rng.shuffle(sample_indices)
            for start in range(0, len(actions), cfg["minibatch"]):
                minibatch = sample_indices[start:start + cfg["minibatch"]]
                actor_loss, entropy, grad_logits, _ = ppo_actor_loss_and_grad(
                    actor,
                    observations[minibatch],
                    actions[minibatch],
                    old_log_probs[minibatch],
                    advantages[minibatch],
                    cfg["clip"],
                    cfg["c2"],
                    norm_adv=False,
                )
                actor.mlp.backward(grad_logits)
                actor_optimizer.step(actor.mlp.grads(), cfg["grad_clip"])

                critic_loss, grad_values = value_loss_and_grad(
                    critic,
                    observations[minibatch],
                    target_returns[minibatch],
                    cfg["c1"],
                )
                critic.mlp.backward(grad_values)
                critic_optimizer.step(critic.mlp.grads(), cfg["grad_clip"])

                losses["actor"].append(actor_loss)
                losses["critic"].append(critic_loss)
                losses["entropy"].append(entropy)
                # c1/c2 are already present in the gradients; this is reporting.
                losses["total"].append(
                    actor_loss + cfg["c1"] * critic_loss - cfg["c2"] * entropy
                )
        loss_by_agent.append({
            key: float(np.mean(values)) for key, values in losses.items()
        })
    return loss_by_agent


# 显式调用的训练函数
def train(algo, mode, cfg, iterations, seed=0, log_every=10, verbose=True):
    """Train one algorithm/mode and retain raw episodes plus best weights."""
    rng = np.random.default_rng(seed)
    env = MultiAgentCleaningEnv(
        mode=mode,
        use_safety_shield=cfg["use_safety_shield"],
        max_steps=cfg["max_steps"],
        seed=seed,
    )
    models = (
        make_ippo(env.obs_dim, env.n_actions, cfg, rng)
        if algo == "ippo"
        else make_mappo(env.obs_dim, env.state_dim, env.n_actions, cfg, rng)
    )
    history = {
        "total": [], "actor": [], "critic": [], "entropy": [],
        # Legacy 'success' stores weighted cleaning, not binary full solve.
        "ret": [], "team": [], "length": [], "success": [],
        "full_success": [], "violation": [],
        "episode_index": [], "episode_return_per_agent": [],
        "episode_team_return": [], "episode_length": [],
        "episode_clean_fraction": [], "episode_full_success": [],
        "episode_violation": [], "update_episode": [],
        "val_iteration": [], "val_clean": [], "val_team": [],
        "val_full_success": [],
    }
    validation_interval = int(cfg.get("val_interval", 0))
    validation_episodes = int(cfg.get("val_episodes", 64))
    best_key = (-1.0, -1.0, -np.inf)
    best_team_return = -np.inf
    best_weights = None
    best_iteration = None

    for iteration in range(iterations):
        # 1. Collect on-policy data, then update the selected PPO variant.
        # Without validation, pre-update weights match the collected outcomes.
        behaviour_weights = (
            get_weights(algo, models) if validation_interval <= 0 else None
        )
        if algo == "ippo":
            rollout_buffer, episode_stats = collect_ippo(env, models, cfg, rng)
            loss_by_agent = update_ippo(models, rollout_buffer, cfg, rng)
        else:
            rollout_buffer, episode_stats = collect_mappo(env, models, cfg, rng)
            loss_by_agent = update_mappo(models, rollout_buffer, cfg, rng)

        # 2. Save update diagnostics and every completed episode separately.
        for loss_name in ("total", "actor", "critic", "entropy"):
            history[loss_name].append([
                loss_by_agent[agent_id][loss_name]
                for agent_id in range(env.n_agents)
            ])

        mean_team_return = float(np.mean(episode_stats["team"]))
        mean_agent_return = np.mean(episode_stats["ret"], axis=0)
        mean_clean_fraction = float(np.mean(episode_stats["clean"]))
        mean_full_success = float(np.mean(episode_stats["success"]))
        mean_episode_length = float(np.mean(episode_stats["length"]))
        mean_violation = float(np.mean(episode_stats["violation"]))
        history["team"].append(mean_team_return)
        history["ret"].append(mean_agent_return)
        history["success"].append(mean_clean_fraction)
        history["full_success"].append(mean_full_success)
        history["length"].append(mean_episode_length)
        history["violation"].append(mean_violation)

        first_episode = len(history["episode_index"]) + 1
        completed_count = len(episode_stats["team"])
        history["episode_index"].extend(
            range(first_episode, first_episode + completed_count)
        )
        history["episode_return_per_agent"].extend(episode_stats["ret"])
        history["episode_team_return"].extend(episode_stats["team"])
        history["episode_length"].extend(episode_stats["length"])
        history["episode_clean_fraction"].extend(episode_stats["clean"])
        history["episode_full_success"].extend(episode_stats["success"])
        history["episode_violation"].extend(episode_stats["violation"])
        history["update_episode"].append(len(history["episode_index"]))

        # 3. Evaluate on fixed seeds instead of selecting a noisy train rollout.
        should_validate = validation_interval > 0 and (
            (iteration + 1) % validation_interval == 0
            or iteration == iterations - 1
        )
        if should_validate:
            validation_summary = summarize_eval(evaluate(
                algo,
                models,
                mode,
                validation_episodes,
                cfg,
                seed=seed + 10000,
                deterministic=False,
            ))
            # Python compares this tuple lexicographically: full solve first,
            # then weighted cleaning, and finally team return as the tie-breaker.
            checkpoint_key = (
                validation_summary["full_success_rate"],
                validation_summary["success_rate"],
                validation_summary["avg_return_team"],
            )
            history["val_iteration"].append(iteration + 1)
            history["val_clean"].append(validation_summary["success_rate"])
            history["val_team"].append(validation_summary["avg_return_team"])
            history["val_full_success"].append(
                validation_summary["full_success_rate"]
            )
            if checkpoint_key > best_key:
                best_key = checkpoint_key
                best_weights = get_weights(algo, models)
                best_iteration = iteration + 1
        elif validation_interval <= 0 and mean_team_return > best_team_return:
            best_team_return = mean_team_return
            best_weights = behaviour_weights
            best_iteration = iteration + 1

        # 4. Keep progress output sparse enough for a readable notebook.
        if verbose and (iteration % log_every == 0 or iteration == iterations - 1):
            print(
                f"[{algo}/{mode}] update {iteration + 1:3d} | "
                f"episodes={history['update_episode'][-1]:4d} | "
                f"team={mean_team_return:7.2f} | clean={mean_clean_fraction:.2f} | "
                f"length={mean_episode_length:.1f} | violation={mean_violation:.2f} | "
                f"loss={np.mean(history['total'][-1]):.3f}"
            )

    if best_weights is None:
        best_weights = get_weights(algo, models)
        best_iteration = iterations
    return {
        "agents": models,
        "history": history,
        "best_weights": best_weights,
        "best_iteration": best_iteration,
        "checkpoint_selection": (
            "lexicographic: full-solve rate, weighted-cleaning rate, team return "
            f"on fixed {validation_episodes}-episode validation seeds"
        ),
        "env": env,
    }


# 参数复制与 actor/critic 接口
def get_weights(algo, models):
    """Copy model parameters into a pickle-safe checkpoint dictionary."""
    if algo == "ippo":
        return {
            "algo": "ippo",
            "pol": [
                [parameter.copy() for parameter in actor.mlp.params()]
                for actor in models["actors"]
            ],
            "cri": [
                [parameter.copy() for parameter in critic.mlp.params()]
                for critic in models["critics"]
            ],
        }
    return {
        "algo": "mappo",
        "actor": [
            parameter.copy() for parameter in models["actor"].mlp.params()
        ],
        "critic": [
            parameter.copy() for parameter in models["critic"].mlp.params()
        ],
    }

def validate_checkpoint_identity(checkpoint, expected_algo, expected_mode):
    """Check required checkpoint fields and the requested setting identity."""
    required_fields = {
        "algo", "mode", "cfg", "training_iterations", "history",
        "best_weights", "best_iteration", "eval34", "summary",
    }
    missing_fields = sorted(required_fields - checkpoint.keys())
    if missing_fields:
        raise ValueError(f"checkpoint missing fields: {missing_fields}")
    actual_identity = (checkpoint["algo"], checkpoint["mode"])
    if actual_identity != (expected_algo, expected_mode):
        raise ValueError(
            f"checkpoint identity {actual_identity} does not match "
            f"{(expected_algo, expected_mode)}"
        )

def copy_saved_parameters(parameters, saved_parameters, label):
    """Copy one parameter list after validating its length and shapes."""
    if len(parameters) != len(saved_parameters):
        raise ValueError(
            f"{label}: expected {len(parameters)} arrays, "
            f"checkpoint has {len(saved_parameters)}"
        )
    for index, (parameter, saved_parameter) in enumerate(
        zip(parameters, saved_parameters)
    ):
        if parameter.shape != saved_parameter.shape:
            raise ValueError(
                f"{label}[{index}]: expected shape {parameter.shape}, "
                f"checkpoint has {saved_parameter.shape}"
            )
        parameter[...] = saved_parameter

def set_weights(algo, models, saved_weights):
    """Load a shape-compatible checkpoint into new model objects."""
    if algo == "ippo":
        for agent_id in range(N_AGENTS):
            copy_saved_parameters(
                models["actors"][agent_id].mlp.params(),
                saved_weights["pol"][agent_id],
                f"IPPO actor {agent_id + 1}",
            )
            copy_saved_parameters(
                models["critics"][agent_id].mlp.params(),
                saved_weights["cri"][agent_id],
                f"IPPO critic {agent_id + 1}",
            )
    else:
        copy_saved_parameters(
            models["actor"].mlp.params(), saved_weights["actor"],
            "MAPPO actor",
        )
        copy_saved_parameters(
            models["critic"].mlp.params(), saved_weights["critic"],
            "MAPPO critic",
        )

def act_policy(algo, models, flat_observations, rng, deterministic):
    """Return one decentralized action and distribution per agent."""
    actions = []
    action_distributions = []
    for agent_id in range(N_AGENTS):
        if algo == "ippo":
            action, _, probabilities = models["actors"][agent_id].act(
                flat_observations[agent_id][None, :], rng, deterministic
            )
        else:
            actor_input = append_agent_id(
                flat_observations[agent_id], agent_id
            )[None, :]
            action, _, probabilities = models["actor"].act(
                actor_input, rng, deterministic
            )
        actions.append(int(action[0]))
        action_distributions.append(probabilities[0])
    return actions, action_distributions

def value_of(algo, models, flat_observations, global_state):
    """Return the three local or centralized value estimates."""
    if algo == "ippo":
        return [
            models["critics"][agent_id].value(
                flat_observations[agent_id][None, :]
            )[0]
            for agent_id in range(N_AGENTS)
        ]
    return models["critic"].value(
        agent_conditioned_global_states(global_state)
    ).tolist()


# 评估与指标汇总
def evaluate(
    algo, models, mode, n_episodes, cfg, seed=123,
    deterministic=False, collect_traj=False, obs_cap=1500,
):
    """Evaluate matched episodes and optionally collect Task-5 trajectories.

    ``collect_traj`` additionally stores matched observations, visitation maps
    and episode-summed TD residuals for the RCR/JSD/contribution analyses.
    """
    action_rng = np.random.default_rng(seed)
    # Optional trajectory logging must not perturb the policy's action stream.
    telemetry_rng = np.random.default_rng(seed + 1_000_003)
    results = {
        key: [] for key in (
            "team", "ret", "length", "full_success", "clean",
            "violation", "shield_intervention",
        )
    }
    visit_map = np.zeros((GRID_SIZE, GRID_SIZE), dtype=np.float64)
    revisit_map = np.zeros((GRID_SIZE, GRID_SIZE), dtype=np.float64)
    observation_bank = []
    episode_advantages = []

    for episode_id in range(n_episodes):
        env = MultiAgentCleaningEnv(
            mode=mode,
            use_safety_shield=cfg["use_safety_shield"],
            max_steps=cfg["max_steps"],
            seed=seed + episode_id + 1,
        )
        observations, _ = env.reset()
        flat_observations = flatten_observations(observations)
        global_state = env.global_state()
        episode_returns = np.zeros(N_AGENTS)
        summed_td_advantage = np.zeros(N_AGENTS)
        episode_length = 0
        episode_done = False
        complete_solve = 0
        safety_violation = 0

        while not episode_done:
            current_values = (
                value_of(algo, models, flat_observations, global_state)
                if collect_traj else None
            )
            actions, _ = act_policy(
                algo, models, flat_observations, action_rng, deterministic
            )
            if collect_traj and len(observation_bank) < obs_cap:
                sampled_agent = int(telemetry_rng.integers(N_AGENTS))
                observation_bank.append(
                    flat_observations[sampled_agent].copy()
                )

            next_observations, rewards, terminated, truncated, info = env.step(actions)
            episode_done = bool(terminated or truncated)
            next_flat_observations = flatten_observations(next_observations)
            next_global_state = env.global_state()

            if collect_traj:
                next_values = value_of(
                    algo, models, next_flat_observations, next_global_state
                )
                time_limit = is_time_limit_truncation(
                    env, terminated, truncated, info
                )
                may_bootstrap = (not episode_done) or time_limit
                for agent_id in range(N_AGENTS):
                    next_value = next_values[agent_id] if may_bootstrap else 0.0
                    summed_td_advantage[agent_id] += (
                        rewards[agent_id]
                        + cfg["gamma"] * next_value
                        - current_values[agent_id]
                    )

            episode_returns += rewards
            episode_length += 1
            flat_observations = next_flat_observations
            global_state = next_global_state
            if info.get("success"):
                complete_solve = 1
            if info.get("collision"):
                safety_violation = 1

        results["team"].append(episode_returns.sum())
        results["ret"].append(episode_returns.copy())
        results["length"].append(episode_length)
        results["full_success"].append(complete_solve)
        results["clean"].append(env.weighted_clean_fraction())
        results["violation"].append(safety_violation)
        results["shield_intervention"].append(
            env.shield_interventions / max(1, env.action_attempts)
        )
        episode_advantages.append(summed_td_advantage)
        visit_map += env.visit_map
        revisit_map += env.revisit_map

    output = {key: np.asarray(values) for key, values in results.items()}
    output["visit"] = visit_map
    output["revisit"] = revisit_map
    output["adv_episode"] = np.asarray(episode_advantages, dtype=np.float32)
    output["adv_per_agent"] = output["adv_episode"].mean(axis=0)
    output["obs_bank"] = (
        np.asarray(observation_bank, dtype=np.float32)
        if observation_bank
        else np.zeros((0, GRID_SIZE * GRID_SIZE * N_CHANNELS), dtype=np.float32)
    )
    return output

def summarize_eval(output):
    """Convert raw evaluation arrays into the required Task-3/4 metrics."""
    per_agent_returns = np.stack(output["ret"])
    solved = output["full_success"].astype(bool)
    solved_lengths = output["length"][solved]
    return {
        "avg_return_team": float(output["team"].mean()),
        "avg_return_per_agent": per_agent_returns.mean(axis=0).tolist(),
        "success_rate": float(output["clean"].mean()),
        "full_success_rate": float(output["full_success"].mean()),
        "episode_length": (
            float(solved_lengths.mean()) if solved.any() else None
        ),
        "mean_length_all": float(output["length"].mean()),
        "safety_violation": float(output["violation"].mean()),
        "shield_intervention_rate": float(
            output["shield_intervention"].mean()
        ),
    }


# 共享 actor 与集中 critic 的 MAPPO
def append_agent_id(flat_observation, agent_id):
    """Append one-hot agent identity to one local observation."""
    agent_one_hot = np.zeros(N_AGENTS, dtype=np.float32)
    agent_one_hot[agent_id] = 1.0
    return np.concatenate([flat_observation, agent_one_hot]).astype(np.float32)

def append_agent_id_batch(observation_batch, agent_id):
    """Append the same one-hot identity to every row in a batch."""
    agent_ids = np.zeros((len(observation_batch), N_AGENTS), dtype=np.float32)
    agent_ids[:, agent_id] = 1.0
    return np.concatenate([observation_batch, agent_ids], axis=1)

def agent_conditioned_global_states(global_state):
    """Build global-state inputs for the three agent-specific V_i(s) values."""
    repeated_state = np.repeat(global_state[None, :], N_AGENTS, axis=0)
    agent_ids = np.eye(N_AGENTS, dtype=np.float32)
    return np.concatenate([repeated_state, agent_ids], axis=1)

def make_mappo(obs_dim, state_dim, n_actions, cfg, rng):
    """Create the shared MAPPO actor, centralized critic, and Adam optimizers."""
    actor = PolicyNet(obs_dim + N_AGENTS, n_actions, cfg["hidden"], rng)
    critic = ValueNet(state_dim + N_AGENTS, cfg["hidden"], rng)
    actor_optimizer = Adam(
        actor.mlp.params(), cfg["lr_actor"], cfg["weight_decay"]
    )
    critic_optimizer = Adam(
        critic.mlp.params(), cfg["lr_critic"], cfg["weight_decay"]
    )
    return {
        "actor": actor,
        "critic": critic,
        "actor_optimizer": actor_optimizer,
        "critic_optimizer": critic_optimizer,
    }

def collect_mappo(env, models, cfg, rng):
    """Collect decentralized actions and centralized value estimates."""
    rollout_buffer = RolloutBuffer(env.n_agents)
    episode_stats = {
        key: [] for key in ("ret", "team", "length", "success", "violation", "clean")
    }
    observations, _ = env.reset()
    flat_observations = flatten_observations(observations)
    global_state = env.global_state()
    episode_returns = np.zeros(env.n_agents)
    episode_length = 0

    for _ in range(cfg["rollout"]):
        # CTDE critic: global state + ID produces one value for each agent.
        values = models["critic"].value(
            agent_conditioned_global_states(global_state)
        )
        actions = np.zeros(env.n_agents, dtype=int)
        log_probs = np.zeros(env.n_agents)
        for agent_id in range(env.n_agents):
            # Decentralized actor: only local observation + ID is visible.
            action, log_prob, _ = models["actor"].act(
                append_agent_id(flat_observations[agent_id], agent_id)[None, :], rng
            )
            actions[agent_id] = action[0]
            log_probs[agent_id] = log_prob[0]

        next_observations, rewards, terminated, truncated, info = env.step(actions)
        episode_done = bool(terminated or truncated)
        next_flat_observations = flatten_observations(next_observations)
        next_global_state = env.global_state()
        time_limit = is_time_limit_truncation(
            env, terminated, truncated, info
        )
        bootstrap_values = (
            models["critic"].value(
                agent_conditioned_global_states(next_global_state)
            )
            if time_limit else np.zeros(env.n_agents, dtype=np.float32)
        )

        for agent_id in range(env.n_agents):
            rollout_buffer.add(
                agent_id,
                obs=flat_observations[agent_id],
                # Global state is stored solely for centralized critic training.
                state=global_state,
                act=int(actions[agent_id]),
                logp=log_probs[agent_id],
                rew=float(rewards[agent_id]),
                val=values[agent_id],
                done=float(episode_done),
                timeout=float(time_limit),
                bootstrap=bootstrap_values[agent_id],
            )

        episode_returns += rewards
        episode_length += 1
        flat_observations = next_flat_observations
        global_state = next_global_state

        if episode_done:
            episode_stats["ret"].append(episode_returns.copy())
            episode_stats["team"].append(episode_returns.sum())
            episode_stats["length"].append(episode_length)
            episode_stats["success"].append(float(info.get("success", False)))
            episode_stats["violation"].append(float(info.get("collision", False)))
            episode_stats["clean"].append(env.weighted_clean_fraction())
            observations, _ = env.reset()
            flat_observations = flatten_observations(observations)
            global_state = env.global_state()
            episode_returns = np.zeros(env.n_agents)
            episode_length = 0

    final_values = models["critic"].value(
        agent_conditioned_global_states(global_state)
    )
    for agent_id in range(env.n_agents):
        agent_data = rollout_buffer.as_arrays(agent_id)
        advantages, target_returns = compute_gae(
            agent_data["rew"],
            agent_data["val"],
            agent_data["done"],
            cfg["gamma"],
            cfg["lam"],
            final_values[agent_id],
            agent_data["timeout"],
            agent_data["bootstrap"],
        )
        rollout_buffer.advantages[agent_id] = advantages
        rollout_buffer.returns[agent_id] = target_returns
    return rollout_buffer, episode_stats

def update_mappo(models, rollout_buffer, cfg, rng):
    """Jointly optimize shared networks, then report data-conditioned agent losses."""
    actor_input_batches = []
    action_batches = []
    old_log_prob_batches = []
    normalised_advantage_batches = []
    target_return_batches = []
    critic_input_batches = []

    # Merge all agents' data before updating the single shared actor/critic.
    for agent_id in range(rollout_buffer.n_agents):
        agent_data = rollout_buffer.as_arrays(agent_id)
        actor_input_batches.append(
            append_agent_id_batch(agent_data["obs"], agent_id)
        )
        action_batches.append(agent_data["act"])
        old_log_prob_batches.append(agent_data["logp"])
        advantages = agent_data["adv"]
        # Normalize each agent's complete rollout once before minibatching.
        normalised_advantage_batches.append(
            (advantages - advantages.mean()) / (advantages.std() + 1e-8)
        )
        target_return_batches.append(agent_data["ret"])
        critic_input_batches.append(
            append_agent_id_batch(agent_data["state"], agent_id)
        )

    actor_inputs = np.concatenate(actor_input_batches)
    actions = np.concatenate(action_batches)
    old_log_probs = np.concatenate(old_log_prob_batches)
    normalised_advantages = np.concatenate(normalised_advantage_batches)
    target_returns = np.concatenate(target_return_batches)
    critic_inputs = np.concatenate(critic_input_batches)

    sample_indices = np.arange(len(actions))
    for _ in range(cfg["epochs"]):
        rng.shuffle(sample_indices)
        for start in range(0, len(actions), cfg["minibatch"]):
            minibatch = sample_indices[start:start + cfg["minibatch"]]
            _, _, grad_logits, _ = ppo_actor_loss_and_grad(
                models["actor"],
                actor_inputs[minibatch],
                actions[minibatch],
                old_log_probs[minibatch],
                normalised_advantages[minibatch],
                cfg["clip"],
                cfg["c2"],
                norm_adv=False,
            )
            models["actor"].mlp.backward(grad_logits)
            models["actor_optimizer"].step(
                models["actor"].mlp.grads(), cfg["grad_clip"]
            )

            _, grad_values = value_loss_and_grad(
                models["critic"],
                critic_inputs[minibatch],
                target_returns[minibatch],
                cfg["c1"],
            )
            models["critic"].mlp.backward(grad_values)
            models["critic_optimizer"].step(
                models["critic"].mlp.grads(), cfg["grad_clip"]
            )

    # Per-agent diagnostics use each agent's own slice after the shared update.
    loss_by_agent = []
    for agent_id in range(rollout_buffer.n_agents):
        agent_data = rollout_buffer.as_arrays(agent_id)
        agent_actor_input = append_agent_id_batch(
            agent_data["obs"], agent_id
        )
        agent_critic_input = append_agent_id_batch(
            agent_data["state"], agent_id
        )
        advantages = agent_data["adv"]
        advantages = (advantages - advantages.mean()) / (advantages.std() + 1e-8)
        actor_loss, entropy, _, _ = ppo_actor_loss_and_grad(
            models["actor"],
            agent_actor_input,
            agent_data["act"],
            agent_data["logp"],
            advantages,
            cfg["clip"],
            cfg["c2"],
            norm_adv=False,
        )
        critic_loss, _ = value_loss_and_grad(
            models["critic"], agent_critic_input, agent_data["ret"], cfg["c1"]
        )
        # c1/c2 are already present in gradients; total is a diagnostic scalar.
        loss_by_agent.append({
            "actor": float(actor_loss),
            "critic": float(critic_loss),
            "entropy": float(entropy),
            "total": float(
                actor_loss + cfg["c1"] * critic_loss - cfg["c2"] * entropy
            ),
        })
    return loss_by_agent


# RCR 与 JSD 指标
def global_rcr(visit_counts, revisit_counts):
    """Team-level redundancy = total revisits / total visits."""
    total_visits = max(1.0, visit_counts.sum())
    return float(revisit_counts.sum() / total_visits)

def rcr_map(visit_counts, revisit_counts):
    """Per-cell redundancy = revisit(x,y)/visit(x,y) where visit>0 else 0."""
    redundancy_map = np.zeros_like(visit_counts, dtype=np.float64)
    visited_cells = visit_counts > 0
    redundancy_map[visited_cells] = (
        revisit_counts[visited_cells] / visit_counts[visited_cells]
    )
    return redundancy_map

def agent_action_distributions(algorithm, models, observation_bank):
    """Return (N_AGENTS, M, 5) action-probability arrays: each agent's policy
    evaluated on the SAME bank of observations (identical-observation test)."""
    if observation_bank.shape[0] == 0:
        return np.zeros((N_AGENTS, 0, 5))
    distributions = []
    for agent_id in range(N_AGENTS):
        if algorithm == "ippo":
            logits = models["actors"][agent_id].logits(observation_bank)
        else:
            actor_inputs = append_agent_id_batch(
                observation_bank, agent_id
            )
            logits = models["actor"].logits(actor_inputs)
        distributions.append(softmax(logits))
    return np.stack(distributions)

def _kl_divergence(distribution_p, distribution_q):
    """Base-2 KL term used inside the symmetric JSD calculation."""
    positive = distribution_p > 0
    return np.sum(
        distribution_p[positive]
        * (
            np.log2(distribution_p[positive])
            - np.log2(distribution_q[positive])
        )
    )

def jsd(distribution_p, distribution_q):
    """JS divergence (base-2, bounded in [0,1]) between two distributions."""
    midpoint = 0.5 * (distribution_p + distribution_q)
    return 0.5 * _kl_divergence(distribution_p, midpoint) + 0.5 * (
        _kl_divergence(distribution_q, midpoint)
    )

def jsd_matrix(action_distributions):
    """Pairwise JSD, averaged across the shared observations."""
    number_of_agents, number_of_observations, _ = action_distributions.shape
    pairwise_jsd = np.zeros((number_of_agents, number_of_agents))
    if number_of_observations == 0:
        return pairwise_jsd
    # JSD is symmetric, so compute each unordered pair once and mirror it.
    for first_agent in range(number_of_agents):
        for second_agent in range(first_agent + 1, number_of_agents):
            observation_jsd = [
                jsd(
                    action_distributions[first_agent, observation_id],
                    action_distributions[second_agent, observation_id],
                )
                for observation_id in range(number_of_observations)
            ]
            mean_jsd = np.mean(observation_jsd)
            pairwise_jsd[first_agent, second_agent] = mean_jsd
            pairwise_jsd[second_agent, first_agent] = mean_jsd
    return pairwise_jsd
