import time

first_order = range(1600)
print(first_order)
second_order = []

for panel_y in range(5):
    for panel_x in range(5):
        for quad_y in range(2):
            for quad_x in range(2):
                for mag_y in range(4):
                    for mag_x in range(4):
                        index = mag_x + mag_y * 40 + quad_x * 4 + quad_y * 160 + panel_x * 8 + panel_y * 320
                        # index = mag_x + mag_y * 40 + quad_x * 4 + quad_y    + panel_x * 4 + panel_y * 320
                        second_order.append(first_order[index])
                        # second_order.append(first_order[index])

print(second_order)
