from tkinter import *
from tkinter import filedialog
import datetime
import os
from PIL import Image, ImageTk, ImageGrab
import win32gui
from tkinter import ttk
import time
from mm_util import *

def print_info(info:str):
    now = datetime.datetime.now()
    current_time = now.strftime("%H:%M:%S")
    print(f'[ Info ] {current_time} {info}')

# 数据区
# 当前画布内容
infos_in_canvas_list = []
# 鼠标右键事件触发时， 鼠标位置
mouse_click_x, mouse_click_y = 0, 0
# ControlNet image
controlnet_image = None
# 保留对象size属性的接口
object_size_map = dict({
    'Bird':'small',
    'Sun':'medium-sized',
    'Cloud':'large'
})

# 九大区域 的 坐标:(up_left_x, up_left_y, height, width)
nine_big_area:list = [
    ( 512 // 3 * 0, 512 // 3 * 0, 512 // 3, 512 // 3, "on the top-left"),
    ( 512 // 3 * 1, 512 // 3 * 0, 512 // 3, 512 // 3, "on the top"),
    ( 512 // 3 * 2, 512 // 3 * 0, 512 // 3, 512 // 3, "on the top-right"),
    
    ( 512 // 3 * 0, 512 // 3 * 1, 512 // 3, 512 // 3, "on the left"),
    ( 512 // 3 * 1, 512 // 3 * 1, 512 // 3, 512 // 3, "in the center"),
    ( 512 // 3 * 2, 512 // 3 * 1, 512 // 3, 512 // 3, "on the right"),
    
    ( 512 // 3 * 0, 512 // 3 * 2, 512 // 3, 512 // 3, "on the bottom-left"),
    ( 512 // 3 * 1, 512 // 3 * 2, 512 // 3, 512 // 3, "on the bottom"),
    ( 512 // 3 * 2, 512 // 3 * 2, 512 // 3, 512 // 3, "on the bottom-right")
]

root = Tk()

canvas = Canvas(root, width=512, height=512, background='white')
canvas.pack()

# 定义一个 root 菜单
right_click_menu = Menu(root, tearoff=False)
# add object
add_object_menu = Menu(right_click_menu, tearoff=False)

def menu_add_object(o_name:str):
    print_info(f'menu_add_object( {o_name} )')
    
    # 左上，右下的坐标
    x0, x1 = mouse_click_x - 50,  mouse_click_x + 50
    y0, y1 = mouse_click_y - 25,  mouse_click_y + 25    
    if x0 < 0:
        x0 = 0
        x1 = 100
    if x1 > 512:
        x0 = 412
        x1 = 512
    if y0 < 0:
        y0 = 0
        y1 = 50
    if y1 > 512:
        y1 = 512
        y0 = 412
    
    # canvas.create_rectangle(x0, y0, x1, y1, dash = (4, 4))
    item_id_1 = canvas.create_oval(x0, y0, x1, y1, fill = "pink")
    item_id_2 = canvas.create_text((x0 + x1) // 2, (y0 + y1) // 2, text = o_name)
    
    print_info(f'Before len(infos_in_canvas_list):{len(infos_in_canvas_list)}')
    info = dict({
        'type':'object',
        'mouse_click_xy':[mouse_click_x, mouse_click_y],
        
        'top_left_and_bottom_right':[x0, y0, x1, y1],
        'text':o_name,
        'size':object_size_map[o_name],
        'item_id':[item_id_1, item_id_2]
    })
    infos_in_canvas_list.append(info)
    print_info(f'Add: {info}')
    print_info(f'After len(infos_in_canvas_list):{len(infos_in_canvas_list)}')    
    root.update()
    print_info('Refresh: root.update()!')

add_object_menu.add_command(label='Bird', command=lambda: menu_add_object('Bird'))
add_object_menu.add_command(label='Sun', command=lambda: menu_add_object('Sun'))
add_object_menu.add_command(label='Cloud', command=lambda: menu_add_object('Cloud'))

right_click_menu.add_command(label='Exit', command=root.destroy)

def menu_generate():
    print_info('Generate!')
    if len(infos_in_canvas_list) == 0:
        print_info(' Empty infos_in_canvas_list. Nothing to generate!')
        return
    infos = "Generate infos:"
    for info in infos_in_canvas_list:
        infos =  infos + '\n' + str(info)
    print_info(info=infos)
    
    prompts = ""
    # 生成位置信息
    for info in infos_in_canvas_list:
        o_name = info['text']
        o_type = info['type']
        for x0, y0, h, w, pos in nine_big_area:
            if o_type == 'object':
                iou = calculate_IoU(info['top_left_and_bottom_right'], (x0, y0, x0 + w, y0 + h))
                if iou >= (100 * 50) // 2:                    
                    sub_prompt = f'A {object_size_map[o_name]} {o_name} {pos}. '
                    prompts = prompts + sub_prompt                              
                    break
            elif o_type == 'text':
                if point_in_area(info['mouse_click_xy'], (x0, y0, x0 + w, y0 + h)):
                    sub_prompt = f'A line word "{o_name}" {pos}. '
                    prompts = prompts + sub_prompt                              
                    break
        print_info(f'Finish do: {info}')
        # end for: find area
    # end for: do all object on canvas
        
              
    print_info(f'Prompts:\n{prompts}')  
    
    
    print_info('Generate infos send success!')
right_click_menu.add_command(label='Generate', command=menu_generate)

def menu_clean():
    infos_in_canvas_list.clear()
    print_info('Clean all data in infos_in_canvas_list!')
    
    canvas.delete('all')
    print_info('Clean all shapes in canvas!')
    
    root.update()
    print_info('Refresh: root.update()!')
    
right_click_menu.add_command(label='Clean',command=menu_clean)

def menu_load_gif():
    print_info('Menu: Load gif!')
    filetypes = (
        ('text files', '*.png'), ("all files", "*.*")
    )
    filename = filedialog.askopenfilename(
        title='Open a file',
        initialdir='C:Users/',
        filetypes=filetypes)    
    
    if filename == "":
        print_info(f'Not select an image, filename == ""!')
        return
    
    print_info(f'Load gif from: {filename}')
        
    global controlnet_image
    image = Image.open(filename).resize((512, 512))
    controlnet_image = ImageTk.PhotoImage(image)
    
    item_id = canvas.create_image(0, 0, anchor=NW, image=controlnet_image)
    print_info(f'Before len(infos_in_canvas_list):{len(infos_in_canvas_list)}')
    info = dict({
        'type':'image',
        'position_x':mouse_click_x,
        'position_y':mouse_click_y,
        'path':filename,
        'item_id':[item_id]
    })
    infos_in_canvas_list.append(info)
    print_info(f'Add: {info}')
    print_info(f'After len(infos_in_canvas_list):{len(infos_in_canvas_list)}')    
    
    root.update()
    print_info('Refresh: root.update()!')    
    
right_click_menu.add_command(label='Load gif',command=menu_load_gif)

def menu_add_text():
    print_info('Add text!')
    item_id_1 = canvas.create_text(mouse_click_x, mouse_click_y, text='Hello World!')
    print_info(f'create_text({mouse_click_x}, {mouse_click_y}, text="Hello World!")')
    
    print_info(f'Before len(infos_in_canvas_list):{len(infos_in_canvas_list)}')
    info = dict({
        'type':'text',
        'mouse_click_xy':[mouse_click_x, mouse_click_y],
        'text':'Hello World!',
        'item_id':[item_id_1]
    })
    infos_in_canvas_list.append(info)
    print_info(f'Add: {info}')
    print_info(f'After len(infos_in_canvas_list):{len(infos_in_canvas_list)}')
    
    root.update()
    print_info('Refresh: root.update()!')        
    
right_click_menu.add_command(label='Add text', command=menu_add_text)

right_click_menu.add_cascade(label='Add Object', menu=add_object_menu)

def menu_undo():
    print_info('Undo!')
    if len(infos_in_canvas_list) == 0:
        print_info('len(infos_in_canvas_list) == 0')
        return    
    print_info(f'Before len(infos_in_canvas_list):{len(infos_in_canvas_list)}')
    n1 = infos_in_canvas_list.pop()
    print_info(f'list[-1] info:{n1}')
    print_info(f'After len(infos_in_canvas_list):{len(infos_in_canvas_list)}')
    for item in n1['item_id']:
        canvas.delete(item)  
    
    global controlnet_image
    if n1['type'] == 'image':
        controlnet_image = None    
    
    # root.update()
    # print_info('Refresh: root.update()!')    
       
right_click_menu.add_command(label='Undo', command=menu_undo)

def menu_save():
    HWND = win32gui.GetFocus()  # 获取当前窗口句柄
    rect1 = win32gui.GetWindowRect(HWND)  # 获取当前窗口坐标
    # magic number: 2. From your desktop setting "Scale".
    rect1 = [ p * 2 for p in rect1]
    time.sleep(0.5)
    im=ImageGrab.grab(rect1)
    im.save("canvas.png",'png')

right_click_menu.add_command(label='Save', command=menu_save)


def listen_mouse_right_click(event):
    # 相对于屏幕的位置
    # print(root.winfo_rootx(), root.winfo_rooty())
    # print(event.x_root, event.y_root)
    # 鼠标相对root frame 位置
    # print(event.x, event.y)    
    global mouse_click_x, mouse_click_y
    mouse_click_x, mouse_click_y = event.x, event.y
    right_click_menu.post(event.x_root, event.y_root)
    
root.bind("<Button-3>", listen_mouse_right_click)

root.mainloop()    
