import sqlite3
import tkinter as tk
import datetime as dt

connection = sqlite3.connect('baza.db')
cursor = connection.cursor()

cursor.execute("""CREATE TABLE IF NOT EXISTS jobs_titles (
    id_job_title INTEGER PRIMARY KEY NOT NULL UNIQUE,
    name TEXT NOT NULL);""")

cursor.execute("""CREATE TABLE IF NOT EXISTS emploees (
    id_employee INTEGER PRIMARY KEY NOT NULL UNIQUE,
    name TEXT NOT NULL,
    surname TEXT NOT NULL,
    id_job_title INTEGER NOT NULL,
    FOREIGN KEY(id_job_title) REFERENCES jobs_titles(id_job_title));""")

cursor.execute("""CREATE TABLE IF NOT EXISTS categories (
    id_category INTEGER PRIMARY KEY NOT NULL UNIQUE,
    name_category TEXT NOT NULL);""")

cursor.execute("""CREATE TABLE IF NOT EXISTS producrs (
    id_product INTEGER PRIMARY KEY NOT NULL UNIQUE,
    name_of_product TEXT NOT NULL,
    price REAL NOT NULL,
    id_category INTEGER NOT NULL,
    quantity_at_storage REAL NOT NULL,
    FOREIGN KEY(id_category) REFERENCES categories(id_category));""")

cursor.execute("""CREATE TABLE IF NOT EXISTS reseipts (
    id_check INTEGER PRIMARY KEY NOT NULL UNIQUE,
    created_at REAL NOT NULL,
    id_cashier INTEGER NOT NULL,
    FOREIGN KEY(id_cashier) REFERENCES emploees(id_employee));""")

cursor.execute("""CREATE TABLE IF NOT EXISTS sale_items (
    id_sale INTEGER PRIMARY KEY NOT NULL UNIQUE,
    id_check INTEGER NOT NULL,
    id_product INTEGER NOT NULL,
    quantity REAL NOT NULL,
    FOREIGN KEY(id_check) REFERENCES reseipts(id_check),
    FOREIGN KEY(id_product) REFERENCES producrs(id_product));""")

cursor.executemany("INSERT OR IGNORE INTO jobs_titles VALUES (?, ?)", [
    (1, 'Кассир'), (2, 'Старший кассир'),
    (3, 'Администратор зала'),
    (4, 'Управляющий магазином'),
    (5, 'Стажёр-кассир')])

cursor.executemany("INSERT OR IGNORE INTO emploees VALUES (?, ?, ?, ?)", [
    (1, 'Анна', 'Иванова', 1),
    (2, 'Мария', 'Петрова', 1),
    (3, 'Елена', 'Сидорова', 2),
    (4, 'Ольга', 'Кузнецова', 1),
    (5, 'Дмитрий', 'Смирнов', 3),
    (6, 'Ирина', 'Васильева', 1),
    (7, 'Сергей', 'Попов', 4),
    (8, 'Татьяна', 'Новикова', 2), 
    (9, 'Алексей', 'Морозов', 3),
    (10, 'Наталья', 'Волкова', 1)])

cursor.executemany("INSERT OR IGNORE INTO categories VALUES (?, ?)", [
    (1, 'Молочные продукты'),
    (2, 'Хлебобулочные изделия'),
    (3, 'Овощи и фрукты'),
    (4, 'Мясо и птица'),
    (5, 'Бакалея'),
    (6, 'Напитки'),
    (7, 'Кондитерские изделия'),
    (8, 'Замороженные продукты'),
    (9, 'Детское питание'),
    (10, 'Бытовая химия')])

producrs = [
    (1, 'Молоко 1л', 89.99, 1, 150.0),
    (2, 'Кефир 1л', 79.99, 1, 120.0),
    (3, 'Сметана 400г', 129.99, 1, 80.0),
    (4, 'Творог 400г', 159.99, 1, 60.0),
    (5, 'Хлеб белый 500г', 49.99, 2, 200.0),
    (6, 'Хлеб ржаной 500г', 59.99, 2, 150.0),
    (7, 'Батон нарезной', 45.99, 2, 180.0),
    (8, 'Яблоки 1кг', 119.99, 3, 300.0),
    (9, 'Бананы 1кг', 139.99, 3, 250.0),
    (10, 'Картофель 1кг', 49.99, 3, 500.0),
    (11, 'Куриное филе 1кг', 349.99, 4, 100.0),
    (12, 'Свинина 1кг', 499.99, 4, 80.0),
    (13, 'Говядина 1кг', 699.99, 4, 50.0),
    (14, 'Рис 800г', 89.99, 5, 120.0),
    (15, 'Гречка 800г', 99.99, 5, 100.0),
    (16, 'Макароны 500г', 69.99, 5, 150.0),
    (17, 'Вода питьевая 1.5л', 39.99, 6, 300.0),
    (18, 'Сок яблочный 1л', 129.99, 6, 90.0),
    (19, 'Печенье 200г', 59.99, 7, 130.0), 
    (20, 'Шоколад молочный 100г', 89.99, 7, 110.0),
    (21, 'Мороженое 500г', 199.99, 8, 70.0),
    (22, 'Пельмени 800г', 249.99, 8, 60.0),
    (23, 'Пюре детское 100г', 49.99, 9, 40.0),
    (24, 'Сок детский 0.5л', 79.99, 9, 50.0),
    (25, 'Порошок стиральный 2кг', 399.99, 10, 30.0)
]

cursor.executemany("INSERT OR IGNORE INTO producrs VALUES (?, ?, ?, ?, ?)", producrs)

cursor.executemany("INSERT OR IGNORE INTO reseipts (id_check, created_at, id_cashier) VALUES (?, ?, ?)", [])
cursor.executemany("INSERT OR IGNORE INTO sale_items (id_sale, id_check, id_product, quantity) VALUES (?, ?, ?, ?)", [])
connection.commit()

basket_list = []
all_sum = 0
basket_labels = []         
message_label = None 

def show_receipt(check_id):

    cursor.execute("""
        SELECT p.name_of_product, si.quantity, p.price
        FROM sale_items si
        JOIN producrs p ON si.id_product = p.id_product
        WHERE si.id_check = ?
    """, (check_id,))
    items = cursor.fetchall()
    
    if not items:
        return
    
    total = sum(qty * price for _, qty, price in items)
    
    receipt_text = f"ЧЕК №{check_id}\n"

    for name, qty, price in items:
        receipt_text += f"{name}\n  {qty} x {price:.2f} = {qty*price:.2f}\n"

    receipt_text += f"ИТОГО: {total:.2f} руб.\n"
    
    win = tk.Toplevel()
    win.title("Чек")
    win.geometry("300x400")
    text_widget = tk.Text(win, wrap=tk.WORD)
    text_widget.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
    text_widget.insert(tk.END, receipt_text)
    text_widget.config(state=tk.DISABLED)
    tk.Button(win, text="Закрыть", command=win.destroy).pack(pady=5)

def Click():
    global qn, all_sum, basket_labels
    name = textfield.get().strip()
    try:
        count = float(cnt.get())
    except ValueError:
        qn.config(text="Введите числовое значение!", fg="red")
        return
    if count <= 0:
        qn.config(text="Количество должно быть больше 0!", fg="red")
        return
    qn.config(text="  ")
    flag = False

    for i, prod in enumerate(producrs):
        if name.lower() == prod[1].lower():
            flag = True
            
            cursor.execute("SELECT quantity_at_storage FROM producrs WHERE id_product = ?", (prod[0],))
            current_qty = cursor.fetchone()[0]

            if count <= current_qty:
                new_qty = current_qty - count
                cursor.execute("UPDATE producrs SET quantity_at_storage = ? WHERE id_product = ?", (new_qty, prod[0]))
                connection.commit()
                
                producrs[i] = (prod[0], prod[1], prod[2], prod[3], new_qty)

                basket_list.append((prod[0], prod[1], count, prod[2]))
                lbl = tk.Label(basket, text=f"{prod[1]} x {count}", font="Arial 12", fg="blue")
                lbl.pack()
                basket_labels.append(lbl)
                
                all_sum += count * prod[2]
                total_lbl.config(text=f"Итоговая сумма: {all_sum:.2f}")
            else:
                qn.config(text=f"Такого количества нет на складе! Осталось: {current_qty}", fg="red")
            break

    if not flag:
        qn.config(text="Такого товара нет в каталоге!", fg="red")


def Click_buy():
    global basket_list, all_sum, basket_labels, message_label
    if not basket_list:
        return
    
    now = dt.datetime.now().timestamp()
    cursor.execute("INSERT INTO reseipts (created_at, id_cashier) VALUES (?, ?)", (now, 1))
    check_id = cursor.lastrowid
    
    for prod_id, name, qty, price in basket_list:
        cursor.execute("INSERT INTO sale_items (id_check, id_product, quantity) VALUES (?, ?, ?)", (check_id, prod_id, qty))
    connection.commit()
    

    show_receipt(check_id)
    
    for lbl in basket_labels:
        lbl.destroy()
    basket_labels.clear()
    if message_label:
        message_label.destroy()
    basket_list = []
    all_sum = 0
    total_lbl.config(text="Итоговая сумма: 0.00")
    
    message_label = tk.Label(basket, text="Покупка оформлена!", fg="green", font="Arial 14")
    message_label.pack(pady=10)


def add_to_wh():
    global base, text_name_wh, cnt_wh  
    name = text_name_wh.get().strip()
    try:
        count = float(cnt_wh.get())
    except ValueError:
        base.config(text="Введите числовое значение!", fg="red")
        return

    base.config(text="  ")
    flag = False

    for i, prod in enumerate(producrs):
        if name.lower() == prod[1].lower():
            flag = True
            
            cursor.execute("SELECT quantity_at_storage FROM producrs WHERE id_product = ?", (prod[0],))
            current_qty = cursor.fetchone()[0]
            
            new_qty = current_qty + count
            cursor.execute("UPDATE producrs SET quantity_at_storage = ? WHERE id_product = ?", (new_qty, prod[0]))
            connection.commit()
            
            producrs[i] = (prod[0], prod[1], prod[2], prod[3], new_qty)
            
            base.config(text=f"{prod[1]}: +{count} шт. (Всего: {new_qty})", fg="green")
            break
        
    if not flag:
        base.config(text="Такого товара нет в каталоге!", fg="red")

def Open_wh():
    global text_name_wh, cnt_wh, base
    warehouse = tk.Toplevel(inf)
    warehouse.geometry("700x300")
    warehouse.title("Склад")
    
    tk.Label(warehouse, text="Название:", font="Arial 18", fg="blue").pack()
    text_name_wh = tk.Entry(warehouse, font="Arial 18", fg="blue")
    text_name_wh.pack()

    tk.Label(warehouse, text="Кол-во:", font="Arial 18", fg="blue").pack()
    cnt_wh = tk.Entry(warehouse, font="Arial 18", fg="blue", width=5)
    cnt_wh.pack()
    base = tk.Label(warehouse, text="  ", font="Arial 18")
    base.pack()

    tk.Button(warehouse, text="Добавить", font="Arial 18", fg="blue", command=add_to_wh).pack()

inf = tk.Tk()
inf.geometry("700x300")
inf.title("Касса")

input_frame = tk.Frame(inf)
input_frame.pack(pady=10)

tk.Label(input_frame, text="Название:", font="Arial 18", fg="blue").pack(side='left', padx=5)
textfield = tk.Entry(input_frame, font="Arial 18", fg="blue")
textfield.pack(side='left', padx=5)

tk.Label(input_frame, text="Кол-во:", font="Arial 18", fg="blue").pack(side='left', padx=5)
cnt = tk.Entry(input_frame, font="Arial 18", fg="blue", width=5)
cnt.pack(side='left', padx=5)

qn = tk.Label(inf, text="  ", font="Arial 18")
qn.pack()

tk.Button(inf, text="Добавить в корзину", font="Arial 18", fg="blue", command=Click).pack()

tk.Button(inf, text="Добавить на склад", font="Arial 18", fg="blue", command=Open_wh).pack(side='bottom', padx=5)

basket = tk.Toplevel(inf)
basket.geometry("400x400")
basket.title("Корзина")
tk.Label(basket, text="Корзина:", font="Arial 18", fg="blue").pack()
total_lbl = tk.Label(basket, text="Итоговая сумма: 0.00", font="Arial 18", fg="blue")
total_lbl.pack()
tk.Button(basket, text="Купить", font="Arial 18", fg="blue", command=Click_buy).pack(side='bottom')

all_pr = tk.Toplevel(inf)
all_pr.geometry("250x650")
all_pr.title("Каталог")
tk.Label(all_pr, text="Каталог товаров", font="Arial 18", fg="blue").pack()
for p in producrs:
    tk.Label(all_pr, text=p[1], font="Arial 11", fg="blue").pack(anchor='w', padx=10)

inf.mainloop()