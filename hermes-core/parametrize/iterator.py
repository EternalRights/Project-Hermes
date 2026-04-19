import random
from itertools import product


class ParameterIterator:

    STRATEGY_SEQUENTIAL = "sequential"
    STRATEGY_RANDOM = "random"
    STRATEGY_CARTESIAN = "cartesian"

    def __init__(self, data_sources: list[list[dict]], strategy: str = "sequential"):
        self._data_sources = data_sources
        self._strategy = strategy

    def iterate(self):
        if self._strategy == self.STRATEGY_SEQUENTIAL:
            yield from self._iterate_sequential()
        elif self._strategy == self.STRATEGY_RANDOM:
            yield from self._iterate_random()
        elif self._strategy == self.STRATEGY_CARTESIAN:
            yield from self._iterate_cartesian()
        else:
            raise ValueError(f"Unknown strategy: {self._strategy}")

    def _iterate_sequential(self):
        for source in self._data_sources:
            for row in source:
                yield dict(row)

    def _iterate_random(self):
        all_rows = []
        for source in self._data_sources:
            all_rows.extend(source)
        shuffled = list(all_rows)
        random.shuffle(shuffled)
        for row in shuffled:
            yield dict(row)

    def _iterate_cartesian(self):
        if not self._data_sources:
            return
        if len(self._data_sources) == 1:
            for row in self._data_sources[0]:
                yield dict(row)
            return
        for combo in product(*self._data_sources):
            merged = {}
            for row in combo:
                merged.update(row)
            yield merged
