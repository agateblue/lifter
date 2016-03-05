import argparse


from . import benchmarks

if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='Run the benchmark suite')
    parser.add_argument('benchmarks', metavar='B', type=str, nargs='?',
                       help='specific benchmarks to run')

    args = parser.parse_args()
    benchmarks_to_run = list(benchmarks.values())
    if args.benchmarks:
        benchmarks_to_run = [benchmark for benchmark in benchmarks_to_run if benchmark.code in args.benchmarks]
    print('\nRunning {0} benchmarks...\n'.format(len(benchmarks_to_run)))
    for benchmark in benchmarks_to_run:
        benchmark.report()
