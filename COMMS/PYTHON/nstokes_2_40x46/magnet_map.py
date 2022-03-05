def map_parser(x_idx, y_idx, src_w, src_h, src_array):

    parser = []
    for y in range(y_idx, y_idx + 5):
        for x in range(x_idx, x_idx + 5):
            parser += map_tile(x, y, src_w, src_h, src_array)

    return parser


def map_tile(x_idx, y_idx, src_w, src_h, src_array):
    # 1 tile = 20 magnets (24 for last row of tiles)

    n_rows = 5
    if (y_idx == 8): # 9th row of tiles has 6 rows of magnets
        n_rows = 6
    
    tile_y = 1 + y_idx * 5

    tile = [0] * 24
    i = 0
    for y in range(n_rows):
        for x in range(4):
            # index = (y_0 + y * 40) + x_0 + x
            index = 1 + x + (x_idx * 4) + (tile_y + y) * src_w 
            tile[i] = src_array[index]
            i += 1

    return tile


def main():
    print("\n== MAGNET TILES ==\n\n")

    src_array = range(1840)

    parser1 = map_parser(0, 0, src_array)
    print("Length: " + str(len(parser1)))
    print("Tile 1: " + str(parser1[0:24]))
    print("Tile 2: " + str(parser1[24:48]))
    print("Tile 5: " + str(parser1[24*4:24*5]))
    print("Tile 15: " + str(parser1[-24*5:-24*4]))
    print("Tile 20: " + str(parser1[-24:]))



if __name__ == "__main__":
    main()
