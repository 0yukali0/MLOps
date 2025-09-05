import flytekit as fl
import random

@fl.task()
def gen_nums(low: int, high: int, length: int) -> list[int]:
    return [random.randint(low, high) for _ in range(length)]

@fl.task()
def mean(nums: list[int]) -> float:
    return sum(nums) / len(nums)

@fl.workflow()
def mean_val_wf(low: int = 0, high: int = 100, length: int = 100) -> float:
    arr = gen_nums(low, high, length)
    mean_val = mean(arr)
    return mean_val
