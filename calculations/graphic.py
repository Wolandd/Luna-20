import matplotlib.pyplot as plt
import math

w = 2796  # скорость истечения несимметричного диметилгидразина из сопла двигателя
m0 = 673762  # масса ракеты
dry_m0 = 45100
dry_m_final = 1880

y = [m for m in range(dry_m0, dry_m_final + 1, -100)]
x = [w * math.log(m0 / m) for m in range(dry_m0, dry_m_final + 1, -100)]

plt.plot(x, y)
plt.ylabel("Сухая масса ракеты (кг)")
plt.xlabel("Характеристическая скорость (м/с)")
plt.show()
