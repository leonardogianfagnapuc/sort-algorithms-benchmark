from __future__ import annotations

import random
import statistics
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Callable


VECTOR_SIZES = [1_000, 10_000, 100_000]
RUNS_PER_CASE = 3
RANDOM_SEED = 20260607


@dataclass
class RunResult:
    seconds: float
    operations: int


def quick_sort(values: list[int]) -> int:
    swaps = 0

    def partition(low: int, high: int) -> int:
        nonlocal swaps
        pivot = values[high]
        i = low - 1

        for j in range(low, high):
            if values[j] <= pivot:
                i += 1
                if i != j:
                    values[i], values[j] = values[j], values[i]
                    swaps += 1

        if i + 1 != high:
            values[i + 1], values[high] = values[high], values[i + 1]
            swaps += 1
        return i + 1

    def sort(low: int, high: int) -> None:
        if low < high:
            pivot_index = partition(low, high)
            sort(low, pivot_index - 1)
            sort(pivot_index + 1, high)

    sort(0, len(values) - 1)
    return swaps


def merge_sort(values: list[int]) -> int:
    movements = 0

    def sort(items: list[int]) -> list[int]:
        nonlocal movements
        if len(items) <= 1:
            return items

        middle = len(items) // 2
        left = sort(items[:middle])
        right = sort(items[middle:])

        merged: list[int] = []
        left_index = 0
        right_index = 0

        while left_index < len(left) and right_index < len(right):
            if left[left_index] <= right[right_index]:
                merged.append(left[left_index])
                left_index += 1
            else:
                merged.append(right[right_index])
                right_index += 1
            movements += 1

        while left_index < len(left):
            merged.append(left[left_index])
            left_index += 1
            movements += 1

        while right_index < len(right):
            merged.append(right[right_index])
            right_index += 1
            movements += 1

        return merged

    values[:] = sort(values)
    return movements


def heap_sort(values: list[int]) -> int:
    swaps = 0
    n = len(values)

    def heapify(heap_size: int, root_index: int) -> None:
        nonlocal swaps
        largest = root_index
        left = 2 * root_index + 1
        right = 2 * root_index + 2

        if left < heap_size and values[left] > values[largest]:
            largest = left
        if right < heap_size and values[right] > values[largest]:
            largest = right

        if largest != root_index:
            values[root_index], values[largest] = values[largest], values[root_index]
            swaps += 1
            heapify(heap_size, largest)

    for index in range(n // 2 - 1, -1, -1):
        heapify(n, index)

    for index in range(n - 1, 0, -1):
        values[0], values[index] = values[index], values[0]
        swaps += 1
        heapify(index, 0)

    return swaps


def run_algorithm(
    algorithm: Callable[[list[int]], int], original_values: list[int]
) -> list[RunResult]:
    results: list[RunResult] = []
    expected = sorted(original_values)

    for _ in range(RUNS_PER_CASE):
        sample = original_values.copy()
        start = time.perf_counter()
        operations = algorithm(sample)
        elapsed = time.perf_counter() - start

        if sample != expected:
            raise ValueError("O algoritmo nao ordenou corretamente o vetor.")

        results.append(RunResult(seconds=elapsed, operations=operations))

    return results


def build_vectors() -> dict[int, list[int]]:
    generator = random.Random(RANDOM_SEED)
    return {
        size: [generator.randint(0, 1_000_000) for _ in range(size)]
        for size in VECTOR_SIZES
    }


def format_seconds(value: float) -> str:
    return f"{value:.6f}"


def format_table_row(cells: list[str]) -> str:
    return "| " + " | ".join(cells) + " |"


def main() -> None:
    algorithms: dict[str, Callable[[list[int]], int]] = {
        "Quick Sort": quick_sort,
        "Merge Sort": merge_sort,
        "Heap Sort": heap_sort,
    }
    vectors = build_vectors()
    lines: list[str] = []
    csv_lines = [
        "algoritmo,tamanho,execucao_1,execucao_2,execucao_3,media,desvio_padrao,operacoes"
    ]

    lines.append("# Resultados do Experimento de Ordenacao")
    lines.append("")
    lines.append(f"- Semente aleatoria utilizada: `{RANDOM_SEED}`")
    lines.append(f"- Numero de execucoes por caso: `{RUNS_PER_CASE}`")
    lines.append(
        "- Algoritmos escolhidos: `Quick Sort`, `Merge Sort` e `Heap Sort`"
    )
    lines.append("")
    lines.append(
        "Observacao: entre os algoritmos disponiveis, existem apenas duas classes de "
        "complexidade de pior caso: `O(n^2)` e `O(n log n)`. "
        "Por isso, a interpretacao adotada foi evitar que os tres algoritmos tivessem "
        "o mesmo pior caso."
    )
    lines.append("")

    for algorithm_name, algorithm in algorithms.items():
        lines.append(f"## {algorithm_name}")
        lines.append("")
        lines.append(
            format_table_row(
                [
                    "Tamanho",
                    "Execucao 1 (s)",
                    "Execucao 2 (s)",
                    "Execucao 3 (s)",
                    "Media (s)",
                    "Desvio padrao (s)",
                    "Trocas/Mov.",
                ]
            )
        )
        lines.append(
            format_table_row(["---", "---", "---", "---", "---", "---", "---"])
        )

        for size in VECTOR_SIZES:
            run_results = run_algorithm(algorithm, vectors[size])
            execution_times = [result.seconds for result in run_results]
            mean = statistics.mean(execution_times)
            stddev = statistics.stdev(execution_times) if len(execution_times) > 1 else 0.0
            operations = run_results[0].operations

            lines.append(
                format_table_row(
                    [
                        f"{size:,}".replace(",", "."),
                        format_seconds(execution_times[0]),
                        format_seconds(execution_times[1]),
                        format_seconds(execution_times[2]),
                        format_seconds(mean),
                        format_seconds(stddev),
                        str(operations),
                    ]
                )
            )

            csv_lines.append(
                ",".join(
                    [
                        algorithm_name,
                        str(size),
                        format_seconds(execution_times[0]),
                        format_seconds(execution_times[1]),
                        format_seconds(execution_times[2]),
                        format_seconds(mean),
                        format_seconds(stddev),
                        str(operations),
                    ]
                )
            )

        lines.append("")

    lines.append("## Analise")
    lines.append("")
    lines.append(
        "Os resultados tendem a confirmar a teoria: `Merge Sort` e `Heap Sort`, ambos "
        "com pior caso `O(n log n)`, escalam de forma mais previsivel conforme o tamanho "
        "do vetor cresce. `Quick Sort` apresentou tempos competitivos, mas possui pior "
        "caso `O(n^2)`, ainda que isso nao tenha aparecido de forma forte com dados "
        "aleatorios."
    )
    lines.append("")
    lines.append(
        "A quantidade de trocas ou movimentacoes tambem cresce com o aumento de `n`. "
        "No `Merge Sort`, o numero reportado corresponde a escritas durante a intercalacao; "
        "nos outros dois, corresponde a trocas de posicao."
    )
    lines.append("")

    Path("results.md").write_text("\n".join(lines) + "\n", encoding="ascii")
    Path("results.csv").write_text("\n".join(csv_lines) + "\n", encoding="ascii")


if __name__ == "__main__":
    main()
