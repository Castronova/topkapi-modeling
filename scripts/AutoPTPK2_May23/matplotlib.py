from matplotlib import pylab
import matplotlib.pyplot as plt

def diff_bar_plot(data_stacked, legend_label_list):

    x = range(len(data_stacked))
    dim = len(data_stacked[0])
    w = 0.75
    dimw = w / dim
    col = ['b', 'r', 'g']
    leg = []
    for i in range(dim):
        y = [item[i] for item in data_stacked]
        xx = [(val+i*dimw) for val in x ]
        a = pylab.bar( xx, y, dimw, bottom=0.001, color = col[i])     #,bottom=0.001)
        leg.append(a)
    x_tick = [(val+dimw) for val in x ]
    pylab.gca().set_xticks(x_tick)
    pylab.xticks(x_tick, ['A', 'B', 'C', 'D', 'E'])
    pylab.legend(leg, legend_label_list)
    return

data_stacked = [[2,3],[4,4], [1,5], [3,4], [3,6]]
diff_bar_plot(data_stacked)


line_up, = plt.plot([1,2,3], label='Line 2')
line_down, = plt.plot([3,2,1], label='Line 1')
plt.legend([line_up, line_down], ['Line Up', 'Line Down'])