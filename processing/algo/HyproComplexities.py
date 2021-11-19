import sqlite3, logging, traceback, json, bisect
from numpy import asarray, sum, argmin, where
import time
# This file contains some more of the complicated functions that are required for hypro, namely determining a survey..

def get_max_rp(rosette_positions: list):
    if max(rosette_positions) > 24:
        max_rp = 36
    else:
        max_rp = 24

    return max_rp


def check_hover(event, axes):
    for line in axes.get_lines():
        if line.get_gid() == 'picking_line':
            if line.contains(event)[0]:
                x_point = line.get_xdata(orig=True)
                y_point = line.get_ydata(orig=True)
                xy_points = line.get_xydata()

                return x_point, y_point, xy_points
    return None


def find_closest(picked_xy, plot_xy):
    """
    Find closest
    :param picked_xy:
    :param plot_xy:
    :return:
    """
    nodes = asarray(plot_xy)
    dist_sq = sum((nodes - picked_xy) ** 2, axis=1)
    return argmin(dist_sq)


def update_annotation(anno, new_x, new_y, new_text, axes, canvas):
    xlim = axes.get_xlim()
    xlim_shift_coeff = (xlim[1] - xlim[0]) * 0.05

    anno.xy = (new_x - xlim_shift_coeff, new_y)
    anno.xyann = (new_x - xlim_shift_coeff, new_y)
    anno.set_text(new_text)
    anno.set_visible(True)

    canvas.draw()


def zoom(axes, ad_max=None, ad_min=None, out=None):
    #y_min, y_max = axes.get_ybound()
    #x_min, x_max = axes.get_xbound()
    trace_state = axes.getViewBox().state
    x_min = trace_state['viewRange'][0][0]
    x_max = trace_state['viewRange'][0][1]
    y_min = trace_state['viewRange'][1][0]
    y_max = trace_state['viewRange'][1][1]

    print(y_min)

    y_ten_percent = y_max * 0.1
    x_ten_percent = (x_max - x_min) * 0.15

    if out:
        new_x_min = x_min - x_ten_percent
        new_x_max = x_max + x_ten_percent
        new_y_max = y_max + y_ten_percent
        if y_max < ad_max + 500:
            return new_x_min, new_x_max, y_min, new_y_max
        else:
            if x_min > 0 and x_max < ad_max:
                return new_x_min, new_x_max, y_min, y_max
    else:
        new_x_min = x_min + x_ten_percent
        new_x_max = x_max - x_ten_percent
        new_y_max = y_max - y_ten_percent
        if y_max > ad_min * 2 and x_ten_percent < (x_max - x_min) / 2:
            return new_x_min, new_x_max, y_min, new_y_max


def move_camera_calc(axes, right=None, ad_max=None):

    trace_state = axes.getViewBox().state
    x_min = trace_state['viewRange'][0][0]
    x_max = trace_state['viewRange'][0][1]

    x_difference = x_max - x_min

    movement_amount = (x_max - x_min) * 0.065
    if right:
        if x_max < ad_max + 100:
            new_x_max = x_max + movement_amount
            new_x_min = new_x_max - x_difference
            return new_x_min, new_x_max
    if x_min > 0 - 200:
        new_x_min = x_min - movement_amount
        new_x_max = x_max - movement_amount
        return new_x_min, new_x_max

def match_hover_to_peak(x_time, slk_data, current_nutrient, peak_windows):

    st = time.time()
    hovered_peak_index = [i for i, x in enumerate(peak_windows) if int(x_time) in x]
    #print(f'match hover to peak time taken: {time.time() - st}')
    return True, hovered_peak_index


def match_click_to_peak(x_time, slk_data, current_nutrient, adj_p_s):
    '''

    Finds the closest peak to where was clicked on the trace, returns the index of this peak
    :param x_time:
    :param slk_data:
    :param current_nutrient:
    :return:
    '''
    st = time.time()
    clicked_peak_index = bisect.bisect_left(adj_p_s[current_nutrient], x_time) - 1
    #clicked_peak_index = bisect.bisect_left(slk_data.clean_peak_starts[current_nutrient], x_time) - 1
    if clicked_peak_index == -1:
        clicked_peak_index = 0
    #print(f'match click to peak time taken: {time.time() - st}')
    return True, clicked_peak_index


def load_proc_settings(path, project):
    """
    Read processing parameters from disk of json format
    :param path:
    :param project:
    :return:
    """
    try:
        with open(path + '/' + '%sParams.json' % project, 'r') as file:
            params = json.loads(file.read())
            return params
    except Exception as e:
        logging.error('ERROR: Could not load project parameters file, this should live within the project folder')


def save_proc_settings(path, project, settings):
    """
    Save processing parameters to disk in json file
    :param path:
    :param project:
    :param settings:
    :return:
    """
    try:
        with open(path + '/' + '%sParams.json' % project, 'w') as file:
            json.dump(settings, file)
    except Exception as e:
        logging.error(
            'ERROR: Could not save to project parameters file, this should live within the project folder')

