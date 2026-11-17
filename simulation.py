"""Simulation of the scenarios of a model (step 4 of the verification process).

Semantics of Laboratory 5 (core v2.0): every component with a capacity is a single server with
exponential service (capacity = jobs per second) and a FIFO queue; components without capacity
take no time; workloads are Poisson arrivals that follow their path; a component that is down
loses the jobs that reach it, unless the previous component of the path is a store, which holds
them until the fault ends; independent replications with seeds 1..N; 95 % confidence intervals
with Student's t; outcome with a margin of 10 % of the threshold.

Laboratory 5 visits the components in topological order, which needs acyclic paths. The paths of
the FTS pass twice through the Translator (request and response), so the same semantics are
executed here by a small discrete-event engine. Extensions of team E, each used by a property:
  discipline priority   non-preemptive priority queue, FIFO inside a class            (E-QS1)
  via / latency         a hop takes the latency (ms) of the connector it names        (E-QS1)
  count, at, retry      batch released by a rate limiter, one retry at most           (SoS-QS1 M4)
  delay                 time per visit to a component of another owner                (SoS-QS1 M4)
  store + capacity      the server of the store pauses while its next hop is down     (E-QS2)
  store buffer N        the store keeps N jobs at most; the rest are lost             (E-QS2)
  store + period        the store notices that the hop is back at its next probe      (E-QS2)
  fault on a connector  the hops over that connector are down                         (E-QS2, E-QS6)
  period, misses        silence declared `misses` periods after the last signal       (E-QS3, E-QS6)
  standby, switch       the standby serves `switch` ms after the silence is declared  (E-QS3)
  workload on C         one job when C is declared silent (propagation of the notice) (E-QS6)
"""
import heapq
import math
import random
import statistics

# Student t quantiles (0.975) by degrees of freedom, for 95 % confidence intervals
T_975 = {1: 12.71, 2: 4.30, 3: 3.18, 4: 2.78, 5: 2.57, 6: 2.45, 7: 2.36, 8: 2.31,
         9: 2.26, 10: 2.23, 15: 2.13, 20: 2.09, 30: 2.04}
QUANTILE = {'p95_latency': 0.95, 'p99_latency': 0.99, 'p999_latency': 0.999}
DEFAULT_ATTR = {'Workload': 'rate', 'Component': 'capacity', 'Delay': 'time'}


class Job:
    """One request or event that traverses the path of its workload."""
    __slots__ = ('w', 'workload', 'path', 'via', 'priority', 'start', 't', 'lost', 'held', 'again')

    def __init__(self, w, start, again=False):
        self.w, self.workload, self.path, self.via = w, w.name, w.path, w.via
        self.priority, self.start, self.t = w.priority or 1, start, start
        self.lost = self.held = False
        self.again = again


class Run:
    """One replication of a scenario."""

    def __init__(self, scenario, seed, over=None):
        s, self.over = scenario, over or {}
        self.s, self.rng = s, random.Random(seed)
        self.events, self.n, self.jobs = [], 0, []
        self.queue, self.busy, self.holding, self.wake_at = {}, set(), {}, {}
        self.first, self.again, self.armed, self.next_slot = {}, {}, {}, {}
        self.down, self.cut, self.alt, self.phase = {}, {}, {}, {}
        self.recovery = self.detection = None
        self.restore, self.fault_end, self.signal = 0.0, 0.0, {}
        self.delay = {d.target.name: self.p(d, 'time') / 1000 for d in s.delays}
        for w in s.workloads:                       # arrivals, as in Laboratory 5
            if w.trigger:
                continue
            rate = self.p(w, 'rate')
            if w.count:                             # [E] batch behind a rate limiter
                self.first[w.name], self.again[w.name] = w.count, 0
                self.armed[w.name], self.next_slot[w.name] = True, w.start
                self.push(w.start, 'slot', w)
                continue
            t = self.rng.expovariate(rate) if rate > 0 else s.duration
            while t < s.duration:
                self.push(t, 'arrive', self.job(w, t), 0)
                t += self.rng.expovariate(rate)
        for f in s.faults:
            self.fault(f)
        while self.events:
            t, _, kind, args = heapq.heappop(self.events)
            getattr(self, kind)(*args, t)
        if self.recovery is None and self.down:     # as in Laboratory 5
            self.recovery = s.duration - max(d1 for _, d1 in self.down.values())
        if self.detection is None and s.faults:     # never detected: no bound within the run
            self.detection = s.duration - min(f.start for f in s.faults)

    # ── parameters, events, jobs ────────────────────────────────────────────────────────────
    def p(self, obj, attr):
        value = self.over.get((obj.name, attr), getattr(obj, attr))
        return value or 0

    def push(self, t, kind, *args):
        self.n += 1
        heapq.heappush(self.events, (t, self.n, kind, args))

    def job(self, w, t, again=False):
        j = Job(w, t, again)
        self.jobs.append(j)
        return j

    def lose(self, j, t):
        j.lost, j.t = True, t

    # ── faults, detection of silence, and switchover ────────────────────────────────────────
    def tick(self, c, t, after):
        """Signal of component c nearest to t: the first at or after t, or the last at or before."""
        per = self.p(c, 'period') / 1000
        if c.name not in self.phase:
            self.phase[c.name] = self.rng.uniform(0, per)
        k = (t - self.phase[c.name]) / per
        return self.phase[c.name] + (math.ceil(k) if after else math.floor(k)) * per

    def fault(self, f):
        start, end = f.start, f.start + f.length
        target, restore = f.target, end
        component = target.__class__.__name__ == 'Component'
        for c in ([target] if component else [link.path[0] for link in target.links]):
            if not (self.p(c, 'period') and self.p(c, 'misses')):
                continue
            last = self.tick(c, start, after=False)             # last valid signal
            declared = last + self.p(c, 'misses') * self.p(c, 'period') / 1000
            if declared >= end:
                continue
            notices = [w for w in self.s.workloads if w.trigger is c]
            for w in notices:                                   # [E] the notice of the silence
                j = self.job(w, declared)
                self.signal[id(j)] = last
                self.push(declared, 'arrive', j, 0)
            if not notices:
                self.detection = max(self.detection or 0, declared - last)
            for sb in self.s.parent.elements if component else []:
                if getattr(sb, 'standby', None) is c:           # [E] the standby takes over
                    restore = min(end, declared + sb.switch / 1000)
                    self.alt[c.name] = (restore, end, sb)
        if component:
            self.down[target.name] = (start, restore)
            self.restore = max(self.restore, restore - start)
        else:
            pairs = {(a.name, b.name) for link in target.links
                     for a, b in zip(link.path, link.path[1:])}
            self.cut[target.name] = (start, end, pairs | {(b, a) for a, b in pairs})
        self.fault_end = max(self.fault_end, restore)

    def blocked(self, j, i, t):
        """End of the fault that keeps the hop from path[i] to path[i + 1] down at t, or None."""
        a, b, until = j.path[i].name, j.path[i + 1].name, None
        d = self.down.get(b)
        if d and d[0] <= t < d[1]:
            until = d[1]
        for name, (d0, d1, pairs) in self.cut.items():
            if d0 <= t < d1 and (j.via[i].name == name if j.via else (a, b) in pairs):
                until = max(until or 0, d1)
        return until

    def resume(self, c, until):
        """A store with a period notices at its next probe that the hop is back."""
        return self.tick(c, until, after=True) if self.p(c, 'period') else until

    # ── traversal of the path ────────────────────────────────────────────────────────────────
    def arrive(self, j, i, t):
        c = j.path[i]
        d = self.down.get(c.name)
        if i == 0 and d and d[0] <= t < d[1]:
            return self.lose(j, t)
        if not self.p(c, 'capacity'):
            wait = self.delay.get(c.name, 0)
            return self.push(t + wait, 'leave', j, i) if wait else self.leave(j, i, t)
        q = self.queue.setdefault(c.name, [])
        if d and self.recovery is None and t > d[1] and c.name not in self.busy and not q:
            self.recovery = t - d[1]            # first arrival after the fault that finds no backlog
        size = len(q) + (c.name in self.busy) + self.holding.get(c.name, 0)
        if c.store and c.buffer and size >= self.p(c, 'buffer'):
            return self.lose(j, t)              # [E] the store is full
        self.n += 1
        heapq.heappush(q, (j.priority if c.discipline == 'priority' else 0, self.n, j, i))
        self.start(c, t)

    def start(self, c, t):
        q = self.queue[c.name]
        if c.name in self.busy or not q:
            return
        d = self.down.get(c.name)
        until = d[1] if d and d[0] <= t < d[1] else None        # the server does not work while down
        j, i = q[0][2], q[0][3]
        if until is None and c.store and i < len(j.path) - 1:   # [E] a store does not send into a
            until = self.blocked(j, i, t)                       #     hop that is down
            if until is not None:
                until = self.resume(c, until)
                for entry in q:
                    entry[2].held = True
        if until is not None:
            if self.wake_at.get(c.name) != until:
                self.wake_at[c.name] = until
                self.push(until, 'wake', c)
            return
        heapq.heappop(q)
        self.busy.add(c.name)
        alt = self.alt.get(c.name)
        server = alt[2] if alt and alt[0] <= t < alt[1] else c
        self.push(t + self.rng.expovariate(self.p(server, 'capacity')), 'done', j, i)

    def wake(self, c, t):
        self.start(c, t)

    def done(self, j, i, t):
        c = j.path[i]
        self.busy.discard(c.name)
        self.leave(j, i, t)
        self.start(c, t)

    def leave(self, j, i, t):
        c = j.path[i]
        if i == len(j.path) - 1:
            j.t, w = t, j.w
            if w.count and not j.again and self.rng.random() < self.p(w, 'retry'):
                self.again[w.name] += 1         # [E] the attempt needs its only retry
                if not self.armed[w.name]:
                    self.armed[w.name] = True
                    self.push(max(t, self.next_slot[w.name]), 'slot', w)
            if id(j) in self.signal:
                self.detection = max(self.detection or 0, t - self.signal[id(j)])
            return
        until = self.blocked(j, i, t)
        if until is not None:
            if not c.store or (c.buffer and self.holding.get(c.name, 0) >= self.p(c, 'buffer')):
                return self.lose(j, t)          # nothing holds it: the job is lost
            self.holding[c.name] = self.holding.get(c.name, 0) + 1
            j.held = True
            return self.push(self.resume(c, until), 'release', j, i)
        k = j.via[i] if j.via else None
        self.push(t + (k.latency or 0) / 1000 if k else t, 'arrive', j, i + 1)

    def release(self, j, i, t):
        self.holding[j.path[i].name] -= 1
        self.leave(j, i, t)

    def slot(self, w, t):
        """[E] The rate limiter of a batch releases one attempt: first tries, then retries."""
        again = not self.first[w.name]
        (self.again if again else self.first)[w.name] -= 1
        self.next_slot[w.name] = t + 1 / self.p(w, 'rate')
        self.armed[w.name] = bool(self.first[w.name] or self.again[w.name])
        if self.armed[w.name]:
            self.push(self.next_slot[w.name], 'slot', w)
        self.arrive(self.job(w, t, again), 0, t)


def simulate(scenario, seed, over=None):
    return Run(scenario, seed, over)


def measure(m, scenario, run):
    """Value of a measure in one replication, in its unit, with a resolution of 1e-6."""
    return round(_measure(m, scenario, run), 6)


def _measure(m, scenario, run):
    k = 1000 if m.unit == 'ms' else 1
    if m.metric in ('recovery', 'detection', 'restore'):
        return (getattr(run, m.metric) or 0) * k
    w = next(w for w in scenario.workloads if w.name == m.workload.name)
    own = [j for j in run.jobs if j.workload == w.name and j.start >= scenario.warmup]
    if m.metric == 'lost':
        return sum(1 for j in own if j.lost)
    done = [j for j in own if not j.lost]
    if m.metric == 'drain':                     # from the end of the fault to the last held job
        held = [j.t for j in done if j.held]
        return (max(held) - run.fault_end) * k if held else 0.0
    if m.metric == 'completion':                # from the start of the batch to its last job
        return (max(j.t for j in done) - w.start) * k if done else 0.0
    times = sorted(j.t - j.start for j in done)
    q = QUANTILE[m.metric]
    return times[max(0, math.ceil(q * len(times)) - 1)] * k if times else 0.0


# ─────────────────────────────────────────────
# Replications, confidence intervals, and outcome (Laboratory 5)
# ─────────────────────────────────────────────
def interval(values):
    mean = statistics.mean(values)
    if len(values) < 2:
        return mean, mean, mean
    df = len(values) - 1
    t = T_975[max(k for k in T_975 if k <= df)]
    half = t * statistics.stdev(values) / math.sqrt(len(values))
    return mean, mean - half, mean + half


def outcome(low, high, threshold):
    """Classification of Unit 6, Reading 2, §4.1, with a margin of 10 % of the threshold."""
    if high <= 0.9 * threshold:
        return 'Satisfied with margin'
    if high <= threshold:
        return 'Satisfied without margin'
    if low > threshold:
        return 'Violated'
    return 'Inconclusive'


def run_scenario(scenario):
    """Nominal point first, then every value of every varied parameter, one at a time.
    Rows: (parameter, value, measure, mean, low, high, outcome)."""
    points = [(None, None, {})]
    for v in scenario.varies:
        attr = v.attr or DEFAULT_ATTR[v.target.__class__.__name__]
        name = v.target.name if not v.attr else f'{v.target.name}.{attr}'
        points += [(name, value, {(v.target.name, attr): value}) for value in v.values]
    rows = []
    for name, value, over in points:
        samples = {m: [] for m in scenario.measures}
        for seed in range(1, scenario.replications + 1):
            run = simulate(scenario, seed, over)
            for m in scenario.measures:
                samples[m].append(measure(m, scenario, run))
        for m in scenario.measures:
            mean, low, high = interval(samples[m])
            rows.append((name, value, m, mean, low, high, outcome(low, high, m.threshold)))
    return rows
