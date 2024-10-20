#! /usr/bin/python3

class Interval:
    def __init__(self, start, end):
        self.start = start
        self.end = end

    def __repr__(self):
        return f"({self.start}, {self.end})"


location_mem = []

def linear_scan(intervals, R):
    # Сортируем интервалы по началу
    intervals.sort(key=lambda x: x.start)

    active_intervals = []
    register = {}
    free_registers = list(range(R))  # Регистрируем регистры от 0 до R-1

    print(f"Исходные интервалы: {intervals}")
    print(f"Количество доступных регистров: {R}\n")
    
    for interval in intervals:
        # Обновление активных интервалов
        print(f"Обрабатываем интервал {interval}")
        print(f"  Before expire: active_intervals = {active_intervals}, ")
        print(f"  free_registers = {free_registers}, registers = {register}\n")
        expire_old_intervals(active_intervals, interval, free_registers, register)

        print(f"  Активные интервалы после удаления завершенных: {active_intervals}")
        print(f"  Свободные регистры: {free_registers}")

        if len(active_intervals) == R:
            print("\n  Doing spill")
            spill_at_interval(interval, active_intervals, register, free_registers)
            print(f"  Проведен спилл для интервала {interval}\n")
        else:
            if free_registers:
                allocated_register = free_registers.pop(0)
                register[interval] = allocated_register
                active_intervals.append(interval)
                active_intervals.sort(key=lambda x: x.end)  # Сортируем по окончанию

                print(f"  Интервал {interval} выделен регистру {allocated_register}\n")
        
        print(f"  Активные интервалы теперь: {active_intervals}")
        print(f"  Текущее назначение регистров: {register}\n")

    return register

def expire_old_intervals(active_intervals, interval, free_registers, register):
    # Удаляем все интервалы, которые закончились до начала текущего интервала
    active_intervals.sort(key=lambda x: x.end)
    for j in active_intervals:
        print(f"  j = {j}, interval = {interval}")
        if j.end >= interval.start:
            print("  j.end >= interval.start so we return")
            return
        print(f"  j.end < interval.start so we remove {j} from active_intervals")
        active_intervals.remove(j)
        reg = register[j]
        print(f"  add register {reg} to free_registers")
        if not reg in free_registers:
            free_registers.append(reg)
        print(f"  free_registers = {free_registers}")

def spill_at_interval(interval, active_intervals, register, free_registers):
    # Находим последний интервал для спилла
    active_intervals.sort(key=lambda x: x.end)
    spill = active_intervals[-1]
    print(f"  current spill = {spill}, current interval = {interval}")
    if spill.end > interval.end:
        # Перемещаем регистр из спилла на новый интервал
        print(f"  spill.end > interval.end so register[{interval}] = register[{spill}]")
        register[interval] = register[spill]
        # Перемещаем спилленный интервал в стек
        print(f"  {spill} is moved to memory")
        location_mem.append(spill)
        print(f"  in memory now = {location_mem}")
        
        active_intervals.remove(spill)
        print(f"  removing {spill} from active_intervals")
        print(f"  active_intervals = {active_intervals}")

        # if not register[spill] in free_registers:
        #     free_registers.append(register[spill])
        register.pop(spill)

        if not interval in active_intervals:
            print(f"  adding {interval} to active_intervals")
            active_intervals.append(interval)  # Заменяем спилленный интервал на текущий
            active_intervals.sort(key=lambda x: x.end)
    else:
        location_mem.append(interval)

    print(f"  spill end: active_intervals = {active_intervals}")

# Пример использования
if __name__ == "__main__":
    intervals = [Interval(1, 8), Interval(2, 8), Interval(3, 10), Interval(4, 6)]
    R = 2  # Количество доступных регистров
    allocation = linear_scan(intervals, R)
    
    print("Конечное распределение регистров:")
    for interval, reg in allocation.items():
        print(f"  Интервал {interval} выделен регистру {reg}")

    print("  in memory:", location_mem)
