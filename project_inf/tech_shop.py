import sqlite3
import csv
import os
import tkinter as tk
from tkinter import ttk, messagebox
import datetime as dt

conn = sqlite3.connect('store.db')
cursor = conn.cursor()
cursor.execute("PRAGMA foreign_keys = ON;")

# Создание таблиц
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

cursor.execute("""CREATE TABLE IF NOT EXISTS returns (
    id_return INTEGER PRIMARY KEY NOT NULL UNIQUE,
    id_sale INTEGER NOT NULL,
    return_date REAL NOT NULL,
    quantity_returned REAL NOT NULL,
    reason TEXT,
    FOREIGN KEY(id_sale) REFERENCES sale_items(id_sale));""")

def read_csv(filename):
    if not os.path.exists(filename):
        return []
    with open(filename, 'r', encoding='utf-8-sig') as f:
        reader = csv.reader(f)
        next(reader)
        return list(reader)

def fill_if_empty(table_name, csv_file, columns, converter=None):
    cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
    if cursor.fetchone()[0] == 0:
        rows = read_csv(csv_file)
        for row in rows:
            if converter:
                row = converter(row)
            placeholders = ','.join(['?'] * len(row))
            cursor.execute(f"INSERT INTO {table_name} ({columns}) VALUES ({placeholders})", row)

def convert_prod(row):
    return (int(row[0]), row[1], float(row[2]), int(row[3]), float(row[4]))

fill_if_empty('jobs_titles', 'jobs_titles.csv', 'id_job_title, name')
fill_if_empty('categories', 'categories.csv', 'id_category, name_category')
fill_if_empty('emploees', 'emploees.csv', 'id_employee, name, surname, id_job_title')
fill_if_empty('producrs', 'producrs.csv', 'id_product, name_of_product, price, id_category, quantity_at_storage', convert_prod)

conn.commit()

# Загружаем актуальные товары из БД
cursor.execute("SELECT id_product, name_of_product, price, id_category, quantity_at_storage FROM producrs")
producrs = cursor.fetchall()

# Глобальные переменные интерфейса
basket_list = []
all_sum = 0
basket_labels = []
message_label = None
scrollable_frame = None
basket_window = None
catalog_window = None

def open_basket():
    global basket_window, scrollable_frame, basket_labels, total_lbl, message_label
    if basket_window is not None and basket_window.winfo_exists():
        basket_window.lift()
        return
    # Создаём новое окно корзины
    basket_window = tk.Toplevel(inf)
    basket_window.geometry("500x550")
    basket_window.title("Корзина")
    basket_window.configure(bg="#f0f0f0")
    basket_window.protocol("WM_DELETE_WINDOW", close_basket)
    
    basket_frame = tk.Frame(basket_window, bg="#f0f0f0", padx=15, pady=15)
    basket_frame.pack(fill='both', expand=True)
    tk.Label(basket_frame, text="Корзина", font="Arial 18 bold", bg="#f0f0f0", fg="#2c6e9e").pack()
    
    items_container = tk.Frame(basket_frame, bg="#f0f0f0")
    items_container.pack(fill='both', expand=True, pady=10)
    canvas = tk.Canvas(items_container, bg="#f0f0f0", highlightthickness=0)
    scrollbar = tk.Scrollbar(items_container, orient="vertical", command=canvas.yview)
    scrollable_frame = tk.Frame(canvas, bg="#f0f0f0")
    scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
    canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)
    canvas.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")
    
    bottom_panel = tk.Frame(basket_frame, bg="#f0f0f0")
    bottom_panel.pack(fill='x', pady=10)
    total_lbl = tk.Label(bottom_panel, text=f"Итоговая сумма: {all_sum:.2f} руб.", font="Arial 16 bold", bg="#f0f0f0", fg="#2c6e9e")
    total_lbl.pack(side='left', padx=10)
    btn_buy = tk.Button(bottom_panel, text="Купить", font="Arial 14", bg="#2c6e9e", fg="white", relief="raised", padx=15, pady=5, command=Click_buy)
    btn_buy.pack(side='right', padx=10)
    
    # Восстанавливаем товары из basket_list
    for (prod_id, name, qty, price, total_price) in basket_list:
        lbl = tk.Label(scrollable_frame, text=f"{name} x {qty} = {total_price:.2f} руб.", font="Arial 12", fg="#2c6e9e", bg="#f0f0f0")
        lbl.pack(anchor='w', pady=2)
        basket_labels.append(lbl)

def close_basket():
    global basket_window, scrollable_frame, basket_labels, total_lbl, message_label
    if basket_window:
        basket_window.destroy()
        basket_window = None
        scrollable_frame = None
        total_lbl = None

def open_catalog():
    global catalog_window
    if catalog_window is not None and catalog_window.winfo_exists():
        catalog_window.lift()
        return
    catalog_window = tk.Toplevel(inf)
    catalog_window.geometry("500x750")
    catalog_window.title("Каталог товаров")
    catalog_window.configure(bg="#f0f0f0")
    catalog_window.protocol("WM_DELETE_WINDOW", close_catalog)
    
    catalog_frame = tk.Frame(catalog_window, bg="#f0f0f0", padx=10, pady=10)
    catalog_frame.pack(fill='both', expand=True)
    tk.Label(catalog_frame, text="Каталог товаров", font="Arial 18 bold", bg="#f0f0f0", fg="#2c6e9e").pack(pady=10)
    
    canvas_cat = tk.Canvas(catalog_frame, bg="#f0f0f0", highlightthickness=0)
    scrollbar_cat = tk.Scrollbar(catalog_frame, orient="vertical", command=canvas_cat.yview)
    catalog_scrollable = tk.Frame(canvas_cat, bg="#f0f0f0")
    catalog_scrollable.bind("<Configure>", lambda e: canvas_cat.configure(scrollregion=canvas_cat.bbox("all")))
    canvas_cat.create_window((0, 0), window=catalog_scrollable, anchor="nw")
    canvas_cat.configure(yscrollcommand=scrollbar_cat.set)
    
    for p in producrs:
        tk.Label(catalog_scrollable, text=f"{p[1]} — {p[2]:.2f} руб.", font="Arial 12", bg="#f0f0f0", fg="#333333").pack(anchor='w', pady=2, padx=10)
    
    canvas_cat.pack(side="left", fill="both", expand=True)
    scrollbar_cat.pack(side="right", fill="y")

def close_catalog():
    global catalog_window
    if catalog_window:
        catalog_window.destroy()
        catalog_window = None

def Click():
    global qn, all_sum, basket_labels, scrollable_frame
    open_basket()  # открываем корзину (если не открыта)
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
                conn.commit()
                producrs[i] = (prod[0], prod[1], prod[2], prod[3], new_qty)

                total_price = count * prod[2]
                basket_list.append((prod[0], prod[1], count, prod[2], total_price))

                lbl = tk.Label(scrollable_frame, text=f"{prod[1]} x {count} = {total_price:.2f} руб.", font="Arial 12", fg="#2c6e9e", bg="#f0f0f0")
                lbl.pack(anchor='w', pady=2)
                basket_labels.append(lbl)

                all_sum += total_price
                total_lbl.config(text=f"Итоговая сумма: {all_sum:.2f} руб.")
            else:
                qn.config(text=f"Такого количества нет на складе! Осталось: {current_qty}", fg="red")
            break
    if not flag:
        qn.config(text="Такого товара нет в каталоге!", fg="red")

def show_receipt(check_id, items, total_sum):
    receipt_win = tk.Toplevel(inf)
    receipt_win.title(f"Чек №{check_id}")
    receipt_win.geometry("500x400")
    receipt_win.configure(bg="#f0f0f0")
    
    frame = tk.Frame(receipt_win, bg="#f0f0f0", padx=15, pady=15)
    frame.pack(fill='both', expand=True)
    
    tk.Label(frame, text=f"ЧЕК №{check_id}", font="Arial 16 bold", bg="#f0f0f0", fg="#2c6e9e").pack(pady=5)
    now_str = dt.datetime.now().strftime("%d.%m.%Y %H:%M:%S")
    tk.Label(frame, text=now_str, font="Arial 10", bg="#f0f0f0", fg="#555555").pack(pady=2)
    tk.Label(frame, text="-"*40, font="Arial 10", bg="#f0f0f0").pack()
    
    items_frame = tk.Frame(frame, bg="#f0f0f0")
    items_frame.pack(fill='both', expand=True, pady=5)
    
    tk.Label(items_frame, text="Товар", width=25, anchor='w', font="Arial 10 bold", bg="#f0f0f0").grid(row=0, column=0, sticky='w')
    tk.Label(items_frame, text="Кол-во", width=6, anchor='e', font="Arial 10 bold", bg="#f0f0f0").grid(row=0, column=1, padx=5)
    tk.Label(items_frame, text="Цена", width=8, anchor='e', font="Arial 10 bold", bg="#f0f0f0").grid(row=0, column=2, padx=5)
    tk.Label(items_frame, text="Сумма", width=8, anchor='e', font="Arial 10 bold", bg="#f0f0f0").grid(row=0, column=3, padx=5)
    
    for i, (_, name, qty, price, item_total) in enumerate(items, start=1):
        tk.Label(items_frame, text=name[:25], width=25, anchor='w', font="Arial 10", bg="#f0f0f0").grid(row=i, column=0, sticky='w')
        tk.Label(items_frame, text=str(qty), width=6, anchor='e', font="Arial 10", bg="#f0f0f0").grid(row=i, column=1, padx=5)
        tk.Label(items_frame, text=f"{price:.2f}", width=8, anchor='e', font="Arial 10", bg="#f0f0f0").grid(row=i, column=2, padx=5)
        tk.Label(items_frame, text=f"{item_total:.2f}", width=8, anchor='e', font="Arial 10", bg="#f0f0f0").grid(row=i, column=3, padx=5)
    
    tk.Label(frame, text="-"*40, font="Arial 10", bg="#f0f0f0").pack(pady=5)
    tk.Label(frame, text=f"ИТОГО: {total_sum:.2f} руб.", font="Arial 14 bold", bg="#f0f0f0", fg="#2c6e9e").pack(pady=5)
    tk.Button(frame, text="Закрыть", font="Arial 12", bg="#2c6e9e", fg="white", command=receipt_win.destroy).pack(pady=10)

def Click_buy():
    global basket_list, all_sum, basket_labels, message_label, scrollable_frame, basket_window
    if not basket_list:
        return
    now = dt.datetime.now().timestamp()
    cursor.execute("INSERT INTO reseipts (created_at, id_cashier) VALUES (?, ?)", (now, 1))
    check_id = cursor.lastrowid
    for prod_id, name, qty, price, total in basket_list:
        cursor.execute("INSERT INTO sale_items (id_check, id_product, quantity) VALUES (?, ?, ?)", (check_id, prod_id, qty))
    conn.commit()
    
    show_receipt(check_id, basket_list.copy(), all_sum)
    
    # Закрываем окно корзины, если оно открыто
    if basket_window:
        basket_window.destroy()
        basket_window = None
    # Очищаем данные корзины
    for lbl in basket_labels:
        lbl.destroy()
    basket_labels.clear()
    if message_label:
        message_label.destroy()
    basket_list = []
    all_sum = 0
    scrollable_frame = None
    total_lbl = None

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
            conn.commit()
            producrs[i] = (prod[0], prod[1], prod[2], prod[3], new_qty)
            base.config(text=f"{prod[1]}: +{count} шт. (Всего: {new_qty})", fg="green")
            break
    if not flag:
        base.config(text="Такого товара нет в каталоге!", fg="red")

def Open_wh():
    global text_name_wh, cnt_wh, base
    warehouse = tk.Toplevel(inf)
    warehouse.geometry("500x300")
    warehouse.title("Склад")
    warehouse.configure(bg="#f0f0f0")
    frame = tk.Frame(warehouse, bg="#f0f0f0", padx=20, pady=20)
    frame.pack(fill="both", expand=True)
    tk.Label(frame, text="Название товара:", font="Arial 12", bg="#f0f0f0", fg="#333333").pack(anchor='w', pady=(0,5))
    text_name_wh = tk.Entry(frame, font="Arial 12", width=30, relief="solid", bd=1)
    text_name_wh.pack(fill='x', pady=(0,15))
    tk.Label(frame, text="Количество:", font="Arial 12", bg="#f0f0f0", fg="#333333").pack(anchor='w', pady=(0,5))
    cnt_wh = tk.Entry(frame, font="Arial 12", width=10, relief="solid", bd=1)
    cnt_wh.pack(anchor='w', pady=(0,20))
    base = tk.Label(frame, text="", font="Arial 12", bg="#f0f0f0")
    base.pack(pady=10)
    btn = tk.Button(frame, text="Добавить на склад", font="Arial 12", bg="#2c6e9e", fg="white", relief="raised", bd=2, padx=10, pady=5, command=add_to_wh)
    btn.pack(pady=10)

def Return_prod():
    ret = tk.Toplevel(inf)
    ret.geometry("600x600")
    ret.title("Возврат товара")
    ret.configure(bg="#f0f0f0")
    main_frame = tk.Frame(ret, bg="#f0f0f0", padx=15, pady=15)
    main_frame.pack(fill='both', expand=True)

    tk.Label(main_frame, text="Номер чека:", font="Arial 12", bg="#f0f0f0", fg="#333333").pack(anchor='w', pady=(0,5))
    check_entry = tk.Entry(main_frame, font="Arial 12", width=20, relief="solid", bd=1)
    check_entry.pack(anchor='w', pady=(0,10))

    def load_check():
        check_id_str = check_entry.get().strip()
        if not check_id_str.isdigit():
            status_label.config(text="Введите корректный номер чека (цифры)", fg="red")
            return
        check_id = int(check_id_str)
        cursor.execute("SELECT id_check FROM reseipts WHERE id_check = ?", (check_id,))
        if not cursor.fetchone():
            status_label.config(text=f"Чек №{check_id} не найден", fg="red")
            listbox.delete(0, tk.END)
            products_data.clear()
            return
        cursor.execute("""
            SELECT si.id_sale, p.name_of_product, si.quantity,
                   COALESCE(SUM(r.quantity_returned), 0) as returned,
                   p.price
            FROM sale_items si
            JOIN producrs p ON si.id_product = p.id_product
            LEFT JOIN returns r ON si.id_sale = r.id_sale
            WHERE si.id_check = ?
            GROUP BY si.id_sale
        """, (check_id,))
        items = cursor.fetchall()
        if not items:
            status_label.config(text="В чеке нет товаров", fg="red")
            listbox.delete(0, tk.END)
            products_data.clear()
            return
        listbox.delete(0, tk.END)
        products_data.clear()
        valid = False
        for sale_id, name, qty_sold, returned, price in items:
            available = qty_sold - returned
            if available > 0:
                display = f"{name} (доступно: {available} шт., цена: {price} руб.)"
                listbox.insert(tk.END, display)
                products_data[display] = (sale_id, name, available, price)
                valid = True
        if not valid:
            status_label.config(text="Все товары из этого чека уже возвращены", fg="red")
        else:
            status_label.config(text=f"Найдено {len(products_data)} позиций. Выберите товар.", fg="green")

    tk.Button(main_frame, text="Загрузить товары из чека", font="Arial 12", bg="#e0e0e0", relief="raised", command=load_check).pack(pady=5)
    tk.Label(main_frame, text="Товары по чеку:", font="Arial 12", bg="#f0f0f0", fg="#333333").pack(anchor='w', pady=(10,5))
    listbox = tk.Listbox(main_frame, font="Arial 12", height=8, bg="white", fg="#333333", relief="solid", bd=1)
    listbox.pack(fill='x', pady=(0,10))
    products_data = {}

    tk.Label(main_frame, text="Количество для возврата:", font="Arial 12", bg="#f0f0f0", fg="#333333").pack(anchor='w', pady=(0,5))
    qty_entry = tk.Entry(main_frame, font="Arial 12", width=10, relief="solid", bd=1)
    qty_entry.pack(anchor='w', pady=(0,10))

    tk.Label(main_frame, text="Причина возврата:", font="Arial 12", bg="#f0f0f0", fg="#333333").pack(anchor='w', pady=(0,5))
    reason_var = tk.StringVar()
    reasons = ["Не подошёл", "Брак", "Передумал", "Другое"]
    reason_menu = ttk.Combobox(main_frame, textvariable=reason_var, values=reasons, state="readonly", font="Arial 12")
    reason_menu.pack(anchor='w', pady=(0,10))
    reason_var.set(reasons[0])

    status_label = tk.Label(main_frame, text="", font="Arial 12", bg="#f0f0f0")
    status_label.pack(pady=5)

    def do_return():
        selection = listbox.curselection()
        if not selection:
            status_label.config(text="Выберите товар из списка", fg="red")
            return
        selected_text = listbox.get(selection[0])
        if selected_text not in products_data:
            status_label.config(text="Ошибка: товар не найден", fg="red")
            return
        sale_id, product_name, max_available, price = products_data[selected_text]
        qty_str = qty_entry.get().strip()
        if not qty_str:
            status_label.config(text="Введите количество", fg="red")
            return
        try:
            qty = float(qty_str)
        except ValueError:
            status_label.config(text="Количество должно быть числом", fg="red")
            return
        if qty <= 0 or qty > max_available:
            status_label.config(text=f"Можно вернуть от 1 до {max_available} шт.", fg="red")
            return
        reason = reason_var.get()
        now = dt.datetime.now().timestamp()
        try:
            cursor.execute("INSERT INTO returns (id_sale, return_date, quantity_returned, reason) VALUES (?, ?, ?, ?)", (sale_id, now, qty, reason))
            cursor.execute("UPDATE producrs SET quantity_at_storage = quantity_at_storage + ? WHERE id_product = (SELECT id_product FROM sale_items WHERE id_sale = ?)", (qty, sale_id))
            conn.commit()
            cursor.execute("SELECT id_product, name_of_product, price, id_category, quantity_at_storage FROM producrs")
            global producrs
            producrs = cursor.fetchall()
            status_label.config(text=f"Успешно возвращено {qty} шт. '{product_name}'", fg="green")
            load_check()
            qty_entry.delete(0, tk.END)
        except Exception as e:
            conn.rollback()
            status_label.config(text=f"Ошибка: {e}", fg="red")

    tk.Button(main_frame, text="Вернуть выбранный товар", font="Arial 12", bg="#2c6e9e", fg="white", relief="raised", padx=10, pady=5, command=do_return).pack(pady=10)

def Create_PC():
    win = tk.Toplevel(inf)
    win.geometry("700x650")
    win.title("Сборка ПК")
    win.configure(bg="#f0f0f0")
    main_frame = tk.Frame(win, bg="#f0f0f0", padx=15, pady=15)
    main_frame.pack(fill='both', expand=True)

    comps = {
        "Процессор": "Процессор",
        "Материнская плата": "Материнская",
        "Видеокарта": "Видеокарта",
        "Оперативная память": "память",
        "Накопитель": "SSD",
        "Блок питания": "Блок питания",
        "Кулер": "Кулер",
        "Корпус": "Корпус"
    }
    vars = {}
    status = tk.Label(main_frame, text="", font="Arial 12", bg="#f0f0f0", fg="red")
    status.pack(pady=5)

    def load_products(keyword):
        cursor.execute("""SELECT id_product, name_of_product, price, quantity_at_storage
                          FROM producrs
                          WHERE id_category = 2 AND quantity_at_storage > 0 AND name_of_product LIKE ?""", (f'%{keyword}%',))
        return cursor.fetchall()

    for name, kw in comps.items():
        frame = tk.Frame(main_frame, bg="#f0f0f0")
        frame.pack(fill='x', pady=6)
        tk.Label(frame, text=name + ":", width=20, anchor='e', font="Arial 12", bg="#f0f0f0", fg="#333333").pack(side='left', padx=5)
        if name == "Накопитель":
            items = []
            for kw2 in ["SSD", "HDD"]:
                items.extend(load_products(kw2))
            uniq = {}
            for it in items:
                uniq[it[0]] = it
            items = list(uniq.values())
        else:
            items = load_products(kw)
        values = [f"{p[1]} - {p[2]} руб. (остаток {p[3]})" for p in items]
        cb = ttk.Combobox(frame, values=values, width=45, state="readonly", font="Arial 12")
        cb.pack(side='left', padx=5)
        if values:
            cb.current(0)
        vars[name] = (cb, items)

    def add_to_basket():
        global all_sum, basket_list, basket_labels, total_lbl, scrollable_frame
        open_basket()
        to_add = []
        for name, (cb, items) in vars.items():
            sel = cb.get()
            if not sel:
                status.config(text=f"Выберите {name.lower()}!", fg="red")
                return
            for p in items:
                if f"{p[1]} - {p[2]} руб. (остаток {p[3]})" == sel:
                    prod_id, prod_name, price, _ = p
                    cursor.execute("SELECT quantity_at_storage FROM producrs WHERE id_product = ?", (prod_id,))
                    current = cursor.fetchone()[0]
                    if current < 1:
                        status.config(text=f"'{prod_name}' закончился!", fg="red")
                        return
                    to_add.append((prod_id, prod_name, price, 1))
                    break
        need_help = messagebox.askyesno("Помощь в сборке", "Нужна ли помощь в сборке ПК?\n(услуга стоит 2000 руб.)")
        try:
            cursor.execute("BEGIN TRANSACTION")
            added_sum = 0
            for prod_id, name, price, qty in to_add:
                cursor.execute("UPDATE producrs SET quantity_at_storage = quantity_at_storage - 1 WHERE id_product = ?", (prod_id,))
                for i, p in enumerate(producrs):
                    if p[0] == prod_id:
                        producrs[i] = (p[0], p[1], p[2], p[3], p[4] - 1)
                        break
                total = price * qty
                basket_list.append((prod_id, name, qty, price, total))
                added_sum += total

                lbl = tk.Label(scrollable_frame, text=f"{name} x {qty} = {total:.2f} руб.", font="Arial 12", fg="#2c6e9e", bg="#f0f0f0")
                lbl.pack(anchor='w', pady=2)
                basket_labels.append(lbl)

            if need_help:
                cursor.execute("SELECT id_product, name_of_product, price, quantity_at_storage FROM producrs WHERE name_of_product = 'Сборка ПК'")
                service = cursor.fetchone()
                if not service:
                    cursor.execute("INSERT INTO producrs (id_product, name_of_product, price, id_category, quantity_at_storage) VALUES (999, 'Сборка ПК', 2000.0, 4, 1000)")
                    conn.commit()
                    cursor.execute("SELECT id_product, name_of_product, price, quantity_at_storage FROM producrs WHERE name_of_product = 'Сборка ПК'")
                    service = cursor.fetchone()
                serv_id, serv_name, serv_price, serv_qty = service
                if serv_qty >= 1:
                    cursor.execute("UPDATE producrs SET quantity_at_storage = quantity_at_storage - 1 WHERE id_product = ?", (serv_id,))
                    for i, p in enumerate(producrs):
                        if p[0] == serv_id:
                            producrs[i] = (p[0], p[1], p[2], p[3], p[4] - 1)
                            break
                    total = serv_price
                    basket_list.append((serv_id, serv_name, 1, serv_price, total))
                    added_sum += total
                    lbl = tk.Label(scrollable_frame, text=f"{serv_name} x 1 = {total:.2f} руб.", font="Arial 12", fg="#2c6e9e", bg="#f0f0f0")
                    lbl.pack(anchor='w', pady=2)
                    basket_labels.append(lbl)
                else:
                    status.config(text="Услуга временно недоступна", fg="red")
            all_sum += added_sum
            total_lbl.config(text=f"Итоговая сумма: {all_sum:.2f} руб.")
            conn.commit()
            status.config(text=f"ПК добавлен! Сумма: {added_sum:.2f} руб.", fg="green")
            win.after(2000, win.destroy)
        except Exception as e:
            conn.rollback()
            status.config(text=f"Ошибка: {e}", fg="red")

    tk.Button(main_frame, text="Добавить ПК в корзину", font="Arial 14", bg="#2c6e9e", fg="white", relief="raised", padx=10, pady=5, command=add_to_basket).pack(pady=20)

inf = tk.Tk()
inf.geometry("830x400")
inf.title("Магазин техники")
inf.configure(bg="#f0f0f0")

# Верхняя панель
top_frame = tk.Frame(inf, bg="#f0f0f0", padx=15, pady=15)
top_frame.pack(fill='x')

input_frame = tk.Frame(top_frame, bg="#f0f0f0")
input_frame.pack(fill='x', pady=5)
tk.Label(input_frame, text="Название товара:", font="Arial 14", bg="#f0f0f0", fg="#333333").pack(side='left', padx=5)
textfield = tk.Entry(input_frame, font="Arial 14", width=30, relief="solid", bd=1)
textfield.pack(side='left', padx=5)
tk.Label(input_frame, text="Кол-во:", font="Arial 14", bg="#f0f0f0", fg="#333333").pack(side='left', padx=5)
cnt = tk.Entry(input_frame, font="Arial 14", width=6, relief="solid", bd=1)
cnt.pack(side='left', padx=5)
qn = tk.Label(top_frame, text="", font="Arial 14", bg="#f0f0f0")
qn.pack(pady=5)
btn_add = tk.Button(top_frame, text="Добавить в корзину", font="Arial 14", bg="#2c6e9e", fg="white", relief="raised", padx=10, pady=5, command=Click)
btn_add.pack(pady=5)

# Нижняя панель кнопок
bottom_frame = tk.Frame(inf, bg="#f0f0f0", padx=10, pady=10)
bottom_frame.pack(side='bottom', fill='x')
btn_wh = tk.Button(bottom_frame, text="Добавить на склад", font="Arial 14", bg="#e0e0e0", relief="raised", padx=10, pady=5, command=Open_wh)
btn_wh.pack(side='left', padx=10, expand=True)
btn_return = tk.Button(bottom_frame, text="Вернуть товар", font="Arial 14", bg="#e0e0e0", relief="raised", padx=10, pady=5, command=Return_prod)
btn_return.pack(side='left', padx=10, expand=True)
btn_pc = tk.Button(bottom_frame, text="Собрать ПК", font="Arial 14", bg="#e0e0e0", relief="raised", padx=10, pady=5, command=Create_PC)
btn_pc.pack(side='left', padx=10, expand=True)
# Новые кнопки
btn_basket = tk.Button(bottom_frame, text="Корзина", font="Arial 14", bg="#e0e0e0", relief="raised", padx=10, pady=5, command=open_basket)
btn_basket.pack(side='left', padx=10, expand=True)
btn_catalog = tk.Button(bottom_frame, text="Каталог", font="Arial 14", bg="#e0e0e0", relief="raised", padx=10, pady=5, command=open_catalog)
btn_catalog.pack(side='left', padx=10, expand=True)

inf.mainloop()
conn.close()