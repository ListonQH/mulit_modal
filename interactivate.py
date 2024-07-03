from tkinter import *
from tkinter import filedialog
import datetime
import os
from PIL import Image, ImageTk

from tkinter import ttk

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

root = Tk()

canvas = Canvas(root, width=512, height=512, background='white')
canvas.pack()

# 定义一个 root 菜单
right_click_menu = Menu(root, tearoff=False)
# add object
add_object_menu = Menu(right_click_menu, tearoff=False)

def menu_add_object(o_name:str):
    print_info(f'menu_add_object( {o_name} )')
    
    x0, x1 = mouse_click_x - 50,  mouse_click_x + 50
    y0, y1 = mouse_click_y - 25,  mouse_click_y + 25
    
    # canvas.create_rectangle(x0, y0, x1, y1, dash = (4, 4))
    item_id_1 = canvas.create_oval(x0, y0, x1, y1, fill = "pink")
    item_id_2 = canvas.create_text(mouse_click_x, mouse_click_y, text = o_name)
    
    print_info(f'Before len(infos_in_canvas_list):{len(infos_in_canvas_list)}')
    info = dict({
        'type':'object',
        'position_x':mouse_click_x,
        'position_y':mouse_click_y,
        'text':o_name,
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
right_click_menu.add_command(label='Generate')

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
    image = Image.open(filename)
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
        'position_x':mouse_click_x,
        'position_y':mouse_click_y,
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

def listen_mouse_right_click(event):
    # 相对于屏幕的位置
    # print(event.x_root, event.y_root)
    # 鼠标相对root frame 位置
    # print(event.x, event.y)    
    global mouse_click_x, mouse_click_y
    mouse_click_x, mouse_click_y = event.x, event.y
    right_click_menu.post(event.x_root, event.y_root)
    
root.bind("<Button-3>", listen_mouse_right_click)

root.mainloop()    
