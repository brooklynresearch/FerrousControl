def test_tile_map(x_idx, y_idx, src_w, src_h):
    # Tests mapping of screen pixels to magnet tile
    # Activates screen area corresponding to given panel

    x0 = 1
    y0 = y_idx
    
    new_array = []
    
    FLUID_W = src_w
    
    for i in range(src_w * src_h):
        new_array.append(0)
    
    for y in range(5):
        for x in range(4):
            idx = 1 + (y_idx + y) * FLUID_W + x + (x_idx * 4)
            new_array[idx] = 1
    
    return new_array

def test_sequence(step, mag_w, mag_h, dens_array, fluid):
    # Moves left to right top to bottom activating the screen pixel for each magnet
    # Params:
    #    step = index from 0 - 1839
    #    mag_w = width of magnet array
    #    mag_h = height of magnet array
    #    dens_array = the 1D density array
    #    fluid = the fluid instance
    # 
    # Call in draw loop, incrementing step


    x_coord = step % mag_w
    y_coord = step / mag_w
    
    if step % mag_w == 0:
        print("*** ROW ***: " + str(1 + y_coord))

    idx = fluid.xy_coordinate(mag_w, x_coord+1, y_coord+1)
    if x_coord == 0:
        # new row. without this, a spot stays active at the end of each row as the test point wraps around to the new one
        dens_array[fluid.xy_coordinate(mag_w, mag_w, y_coord)] = 0
    if y_coord == 0:
        # Set bottom right to 0 when wrapping back around to start
        dens_array[fluid.xy_coordinate(mag_w, mag_w, mag_h)] = 0

    #print("TEST step=" + str(step) + " idx=" + str(idx))
    dens_array[idx] = 1
    dens_array[idx-1] = 0
    
