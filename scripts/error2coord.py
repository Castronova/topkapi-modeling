ids = []

with open('C:\error_pytopkapi.txt', "r") as f:
    lines = f.readlines()
    for i in range(1, len(lines)):
        ids.append(int(i))

coords = {}
with open (r'..\simulations\TEST SIMULAITON_RBC_demo\run_the_model\parameter_files\cell_param.dat', "r") as f:
    lines = f.readlines()
    for line in lines:
        elements = line.split(" ")
        coords[int(elements[0])] = [float(elements[1]), float(elements[2])]

with open('coords.txt', "w") as f:
    f.write("X, Y \n")
    for i in ids:
        x,y = coords[i]
        f.write('%3.5f, %3.5f\n' % (x,y))
