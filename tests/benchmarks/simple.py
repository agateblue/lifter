import lifter

from big_fake_data import fake;
final_data = fake * 100

def vanilla_python():
    len([row for row in final_data if row["age"] == 42 and row["is_active"] and not row["name"] == "Bernard" ])

def lifter_version():
    manager = lifter.load(final_data)
    manager.filter(age=42, is_active=True).exclude(name="Bernard").count()

if __name__ == '__main__':
    import timeit
    print('Vanilla Python', timeit.timeit("vanilla_python()", setup="from __main__ import vanilla_python", number=100))
    print('Lifter', timeit.timeit("lifter_version()", setup="from __main__ import lifter_version", number=100))
