import collections

import lifter

from .utils import Benchmark, report

benchmarks = collections.OrderedDict()

def register(cls):
    benchmarks[cls.code] = cls()
    return cls

@register
class SingleFilterBenchmark(Benchmark):
    code = 'single_filter'

    def vanilla_version(self, setup_data):
        return len([row for row in setup_data['test_data'] if row["age"] == 42])

    def lifter_version(self, setup_data):
        manager = lifter.load(setup_data['test_data'])
        return manager.filter(age=42).count()


@register
class CombinedFilterBenchmark(Benchmark):
    code = 'combined_filter'

    def vanilla_version(self, setup_data):
        return len([row for row in setup_data['test_data'] if row["age"] == 42 and row['is_active']])

    def lifter_version(self, setup_data):
        manager = lifter.load(setup_data['test_data'])
        return manager.filter(age=42, is_active=True).count()


@register
class OrderByBenchmark(Benchmark):
    code = 'order_by'

    def vanilla_version(self, setup_data):
        return list(sorted(setup_data['test_data'], key=lambda v: v['age']))

    def lifter_version(self, setup_data):
        manager = lifter.load(setup_data['test_data'])
        return manager.order_by('age')
