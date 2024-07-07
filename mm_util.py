import cv2

def is_object_and_area_overloop(object_rect:list, area_rect:list):
    minx1, miny1, maxx1, maxy1 = object_rect
    minx2, miny2, maxx2, maxy2 = area_rect
    minx = max(minx1, minx2)
    miny = max(miny1, miny2)
    maxx = min(maxx1, maxx2)
    maxy = min(maxy1, maxy2)

    if minx > maxx or miny > maxy:
        return False
    else:
        return True

def calculate_IoU(predicted_bound, ground_truth_bound):
    """
    computing the IoU of two boxes.
    Args:
        box: (x1, y1, x2, y2),通过左上和右下两个顶点坐标来确定矩形
    Return:
        IoU: IoU of box1 and box2.
    """
    px1, py1, px2, py2 = predicted_bound
    # print("预测框P的坐标是：({}, {}, {}, {})".format(px1, py1, px2, py2))

    gx1, gy1, gx2, gy2 = ground_truth_bound
    # print("原标记框G的坐标是：({}, {}, {}, {})".format(gx1, gy1, gx2, gy2))

    parea = (px2 - px1 + 1) * (py2 - py1 + 1)  # 计算P的面积
    garea = (gx2 - gx1 + 1) * (gy2 - gy1 + 1)  # 计算G的面积
    # print("预测框P的面积是：{}；原标记框G的面积是：{}".format(parea, garea))

    # 求相交矩形的左上和右下顶点坐标(x1, y1, x2, y2)
    x1 = max(px1, gx1)  # 得到左上顶点的横坐标
    y1 = max(py1, gy1)  # 得到左上顶点的纵坐标
    x2 = min(px2, gx2)  # 得到右下顶点的横坐标
    y2 = min(py2, gy2)  # 得到右下顶点的纵坐标
    # print(f'pos: {x1, y1, x2, y2}')
    interArea = max(0,x2-x1+1)*max(0,y2-y1+1)
    # print(f'interArea: {interArea}')
    
    # IoU
    # return interArea / (parea + garea - interArea)
    return interArea 

def point_in_area(point, area):
    x, y = point
    x0, y0, x1, y1 = area
    return x >= x0 and x < x1 and y >= y0 and y <= y1
if __name__ == '__main__':
    print()
