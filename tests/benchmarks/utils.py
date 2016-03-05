import time

from .big_fake_data import fake;


class Benchmark(object):
    label = None
    loops = 100

    def get_label(self):
        return self.code

    def setup(self):
        return {'test_data': fake * 100}

    def vanilla_version(self, setup_data):
        raise NotImplemented()

    def lifter_version(self, setup_data):
        raise NotImplemented()

    def run(self):
        setup_data = self.setup()
        data = {}
        data['total_loops'] = self.loops
        data['lifter'] = timer(self.lifter_version, setup_data, number=data['total_loops'])
        data['vanilla'] = timer(self.vanilla_version, setup_data, number=data['total_loops'])

        assert data['lifter']['result'] is not None and data['lifter']['result'] is not None
        assert data['lifter']['result'] == data['vanilla']['result']

        data['benchmark'] = self
        data['source'] = {'total_objs': len(setup_data['test_data'])}
        data['total_time'] = data['lifter']['total_time'] + data['vanilla']['total_time']
        data['speed_ratio'] = data['lifter']['total_time'] / data['vanilla']['total_time']
        return data

    def report(self):
        data = self.run()
        print(report(data))

def timer(func, *args, **kwargs):
    start = time.time()
    data = {}
    loop_times = []
    total_loops = kwargs.pop('number', 100)
    result = None
    for loop in range(total_loops):
        loop_start = time.time()
        r = func(*args, **kwargs)
        loop_times.append(time.time() - loop_start)
        if not result:
            result = r
    end = time.time()

    data['total_time'] = end - start
    data['average_time'] = data['total_time'] / total_loops
    data['min_time'] = min(loop_times)
    data['max_time'] = max(loop_times)
    data['result'] = r
    return data

def report(data):
    rows = []
    rows.append('  {0}'.format('*' * 50))
    rows.append('  {0} benchmark results:'.format(data['benchmark'].get_label()))
    rows.append('  {0}\n'.format('*' * 50))

    for version in ['vanilla', 'lifter']:
        version_data = data[version]
        rows.append('    {0} results:\n'.format(version))
        rows.append('      * {0} loops in {1}s'.format(data['total_loops'], version_data['total_time']))
        rows.append('      * Avg {0}s/loop'.format(version_data['average_time']))
        rows.append('      * Min {0}s/loop'.format(version_data['min_time']))
        rows.append('      * Max {0}s/loop\n'.format(version_data['max_time']))

    rows.append('    lifter/vanilla ratio: {0} times slower\n'.format(data['speed_ratio']))
    return '\n'.join(rows)
