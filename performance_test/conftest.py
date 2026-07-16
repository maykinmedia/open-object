import pytest


@pytest.fixture
def benchmark_assertions(benchmark):
    """Assert hard upper bounds on benchmark metrics.
    e.g. to assert the median duration per round is less than 1s.

    .. code-block::
        def my_bench(benchmark, benchmark_assertions):
            def addition():
                return 1 + 1
            assert benchmark(addition) == 2

            assert benchmark_assertions(median=1)
    """

    def wrapper(**kwargs):
        stats = benchmark.stats["stats"]
        for name, value in kwargs.items():
            assert getattr(stats, name) < value, (
                f"{name} {getattr(stats, name)}s exceeded {value}s"
            )

    return wrapper
