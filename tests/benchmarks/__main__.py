import argparse
import cProfile

from . import benchmarks

if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='Run the benchmark suite')
    parser.add_argument('benchmarks', type=str, nargs='?',
                       help='specific benchmarks to run')

    parser.add_argument('--profile', dest='profile', action='store_const',
        const=True, default=False,
        help='run profiling against the report')
    parser.add_argument('--loops', '-l', dest='loops',
        default=100, type=int,
        help='Number of loops to run for each benchmark')
    args = parser.parse_args()
    benchmarks_to_run = list(benchmarks.values())
    if args.benchmarks:
        benchmarks_to_run = [benchmark for benchmark in benchmarks_to_run if benchmark.code in args.benchmarks]
    print('\nRunning {0} benchmarks...\n'.format(len(benchmarks_to_run)))

    for benchmark in benchmarks_to_run:
        if args.profile:
            setup_data = benchmark.setup()
            cProfile.run('benchmark.lifter_version(setup_data)')
        else:
            benchmark.report(loops=args.loops)
