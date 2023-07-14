def map_parser(x_idx, y_idx, src_w, src_h, src_array):

    p_width = 5 # tile columns per parser
    p_height = 5 # tile rows per parser (only need to count upper row of parsers here)

    # index of top left tile for this parser
    tile_x = x_idx * p_width
    tile_y = y_idx * p_height

    parser_cols = 5
    parser_rows = 5
    if y_idx == 1: # lower row of parsers has 4 rows of tiles
        parser_rows = 4

    parser = []
    for y in range(parser_rows):
        for x in range(parser_cols):
            parser += map_tile(tile_x + x, tile_y + y, src_w, src_h, src_array)

    if y_idx == 1:
        parser += [0] * 120

    return parser


def map_tile(x_idx, y_idx, src_w, src_h, src_array):
    # 1 tile = 24 values (only last row of tiles uses all values)

    n_rows = 5
    if (y_idx == 8): # 9th row of tiles has 6 rows of magnets
        n_rows = 6
    
    # top left magnet
    tile_x = 1 + x_idx * 4
    tile_y = 1 + y_idx * 5

    tile = [0] * 24
    i = 0
    for y in range(n_rows):
        for x in range(4):
            # index = (y_0 + y * 40) + x_0 + x
            index = tile_x + x + (tile_y + y) * src_w
            tile[i] = src_array[index]
            i += 1

    return tile


def main():
    print("\n== MAGNET TILES ==\n\n")

    array_w = 40 + 2
    array_h = 46 + 2

    src_array = range(array_w * array_h)

    parser1 = map_parser(0, 1, array_w, array_h, src_array)
    print("Length: " + str(len(parser1)))
    print("Tile 1: " + str(parser1[0:24]))
    print("Tile 2: " + str(parser1[24:48]))
    print("Tile 5: " + str(parser1[24*4:24*5]))
    print("Tile 6: " + str(parser1[24*5:24*6]))
    print("Tile 10: " + str(parser1[24*9:24*10]))
    print("Tile 12: " + str(parser1[24*11:24*12]))
    print("Tile 15: " + str(parser1[-24*5:-24*4]))
    print("Tile 20: " + str(parser1[-24:]))



if __name__ == "__main__":
    main()
