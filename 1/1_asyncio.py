import asyncio
import time
from concurrent.futures import ThreadPoolExecutor
import random
from typing import List, Tuple

# ========== 1. Асинхронные функции ==========
async def async_task(name: str, delay: float) -> str:
    """Асинхронная задача с задержкой"""
    print(f"[{name}] Начинаю работу (задержка: {delay}с)")
    await asyncio.sleep(delay)  # Асинхронное ожидание
    result = f"Задача {name} завершена за {delay}с"
    print(f"[{name}] Завершено")
    return result

# ========== 2. Синхронный блокирующий код ==========
def blocking_cpu_task(name: str, iterations: int) -> str:
    """Синхронная CPU-интенсивная задача"""
    print(f"[{name}] Начинаю CPU-интенсивную задачу")
    start = time.time()
    
    # Имитация CPU-интенсивной работы
    result = 0
    for i in range(iterations):
        result += i * i * i
        # Небольшая пауза для имитации работы
        time.sleep(0.0001)
    
    duration = time.time() - start
    print(f"[{name}] CPU-задача завершена за {duration:.2f}с")
    return f"CPU-задача {name}: результат = {result}"

async def run_blocking_in_threadpool(name: str, iterations: int) -> str:
    """Запуск блокирующего кода в отдельном потоке"""
    loop = asyncio.get_event_loop()
    
    # Используем ThreadPoolExecutor для блокирующих операций
    result = await loop.run_in_executor(
        None,  # Используем дефолтный executor
        blocking_cpu_task,  # Функция
        name,  # Аргумент 1
        iterations  # Аргумент 2
    )
    return result

# ========== 3. Параллельный запуск функций ==========
async def parallel_execution() -> List[str]:
    """Запуск нескольких задач параллельно"""
    print("\n=== ПАРАЛЛЕЛЬНЫЙ ЗАПУСК ===")
    
    # Создаем задачи (они начинают выполняться сразу)
    tasks = [
        asyncio.create_task(async_task(f"Async-{i}", random.uniform(0.5, 2.0)))
        for i in range(3)
    ]
    
    # Запускаем блокирующие задачи в threadpool
    cpu_tasks = [
        asyncio.create_task(run_blocking_in_threadpool(f"CPU-{i}", 10000))
        for i in range(2)
    ]
    
    # Ждем завершения всех задач
    results = await asyncio.gather(*tasks, *cpu_tasks)
    return results

# ========== 4. Примеры с таймаутами ==========
async def slow_operation(name: str, delay: float) -> str:
    """Медленная операция"""
    await asyncio.sleep(delay)
    return f"{name}: выполнена за {delay}с"

async def timeout_examples():
    """Различные способы работы с таймаутами"""
    print("\n=== ТАЙМАУТЫ ===")
    
    # 4.1. Таймаут на отдельную задачу
    try:
        result = await asyncio.wait_for(
            slow_operation("Task-Timeout", 3.0),
            timeout=1.5
        )
        print(f"1. С таймаутом: {result}")
    except asyncio.TimeoutError:
        print("1. Таймаут: задача не завершилась за 1.5 секунды")
    
    # 4.2. Таймаут на группу задач
    try:
        tasks = [
            slow_operation(f"Group-{i}", random.uniform(0.5, 1.0))
            for i in range(3)
        ]
        results = await asyncio.wait_for(
            asyncio.gather(*tasks),
            timeout=0.8
        )
        print(f"2. Группа задач: {results}")
    except asyncio.TimeoutError:
        print("2. Таймаут для группы задач")
    
    # 4.3. Ожидание с таймаутом и возвратом частичных результатов
    tasks = [
        asyncio.create_task(slow_operation(f"Partial-{i}", delay))
        for i, delay in enumerate([0.5, 1.5, 2.5])
    ]
    
    done, pending = await asyncio.wait(
        tasks,
        timeout=1.0,
        return_when=asyncio.FIRST_COMPLETED
    )
    
    print(f"3. Завершено за 1с: {len(done)} задач")
    print(f"   Ожидают: {len(pending)} задач")
    
    # Отменяем оставшиеся задачи
    for task in pending:
        task.cancel()
    
    # Собираем результаты завершенных задач
    for task in done:
        try:
            result = await task
            print(f"   Результат: {result}")
        except Exception as e:
            print(f"   Ошибка: {e}")


# ========== 5. Основная функция ==========
async def main():
    """Основная функция, демонстрирующая все возможности"""
    print("=" * 50)
    print("ДЕМОНСТРАЦИЯ ВОЗМОЖНОСТЕЙ ASYNCIO")
    print("=" * 50)
    
    # 1. Последовательный запуск асинхронных функций
    print("\n1. ПОСЛЕДОВАТЕЛЬНЫЙ ЗАПУСК:")
    result1 = await async_task("Последовательная-1", 1.0)
    result2 = await async_task("Последовательная-2", 0.5)
    print(f"Результаты: {result1}, {result2}")
    
    # 2. Параллельный запуск
    parallel_results = await parallel_execution()
    print(f"\nИтоги параллельного выполнения: {len(parallel_results)} задач")
    
    # 3. Таймауты
    await timeout_examples()
    
    # 4. Пример с Event и Condition
    print("\n=== SYNCHRONIZATION PRIMITIVES ===")
    
    event = asyncio.Event()
    
    async def waiter(name: str):
        print(f"[{name}] Жду события...")
        await event.wait()
        print(f"[{name}] Событие произошло!")
    
    async def setter():
        await asyncio.sleep(0.5)
        print("[SETTER] Устанавливаю событие")
        event.set()
    
    # Запускаем ожидающих и установщик
    await asyncio.gather(
        waiter("Waiter-1"),
        waiter("Waiter-2"),
        setter()
    )
    
    print("\n" + "=" * 50)
    print("ВСЕ ДЕМОНСТРАЦИИ ЗАВЕРШЕНЫ!")
    print("=" * 50)

# ========== Запуск ==========
if __name__ == "__main__":
    # Проверяем версию Python
    import sys
    if sys.version_info >= (3, 7):
        # Python 3.7+ - используем asyncio.run()
        asyncio.run(main())
    else:
        # Для Python 3.6 и ниже
        loop = asyncio.get_event_loop()
        try:
            loop.run_until_complete(main())
        finally:
            loop.close()