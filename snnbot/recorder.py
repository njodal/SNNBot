"""Every spike, as it happens, with the source it came from."""

from collections import Counter


class Recorder:
    def __init__(self):
        self.spikes = []            # (t, source, event)

    def record(self, t, source, events):
        for e in events:
            self.spikes.append((t, source, e))

    def of(self, source):
        return [(t, e) for t, s, e in self.spikes if s == source]

    def counts(self):
        return Counter(s for _, s, _ in self.spikes)

    def __len__(self):
        return len(self.spikes)
