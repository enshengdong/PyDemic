

directory = "/Users/paul.warren/Documents/ebola/data"
for i in range(0, GRAPH_SIZE):
    if i < 256:
        if i % 256 == 0:
            # leftmost point, connect with +256, +1
            g.add_edge(i, i + 256)
            g.add_edge(i, i + 1)
        elif i % 255 == 0:
            # rightmost point, connect with +256, -1
            g.add_edge(i, i + 256)
            g.add_edge(i, i - 1)
        else: 
            # middle, connect with +256, -1, +1
            g.add_edge(i, i + 256)
            g.add_edge(i, i - 1)
            g.add_edge(i, i + 1)
    elif i >= 65280:
        if i % 256 == 0:
            # leftmost point, connect with -256, +1
            g.add_edge(i, i - 256)
            g.add_edge(i, i + 1)
        elif i % 255 == 0:
            # rightmost point, connect with -256, -1
            g.add_edge(i, i - 256)
            g.add_edge(i, i - 1)

        elif i % 255 != 0:
            # middle, connect with -256, -1, +1
            g.add_edge(i, i - 256)
            g.add_edge(i, i - 1)
            g.add_edge(i, i + 1)
    else:
        if i % 256 == 0:
            # leftmost point, connect with -256, +256, +1
            g.add_edge(i, i - 256)
            g.add_edge(i, i + 256)
            g.add_edge(i, i + 1)
        elif i % 255 == 0: 
            # rightmost point, connect with -256, +256, -1
            g.add_edge(i, i - 256)
            g.add_edge(i, i + 256)
            g.add_edge(i, i - 1)
        else:
            # middle, connect with -256, +256, -1, +1
            g.add_edge(i, i - 256)
            g.add_edge(i, i + 256)
            g.add_edge(i, i - 1)
            g.add_edge(i, i + 1)
