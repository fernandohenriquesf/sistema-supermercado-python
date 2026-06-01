import sys
print(sys.executable)

import os
import shutil
import sqlite3
from datetime import datetime
import customtkinter as ctk
from tkinter import ttk, messagebox

DB_NAME = "supermercado.db"
BACKUP_DIR = "backups"

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")


class Database:

    def __init__(self):
        self.conn = sqlite3.connect(DB_NAME)
        self.conn.row_factory = sqlite3.Row
        self.cursor = self.conn.cursor()

        self.create_tables()
        self.insert_default_data()

    def create_tables(self):

        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS users(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE,
            password TEXT
        )
        """)

        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS products(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            barcode TEXT UNIQUE,
            category TEXT,
            cost_price REAL,
            sale_price REAL,
            stock INTEGER,
            supplier TEXT,
            created_at TEXT
        )
        """)

        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS sales(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            total REAL,
            operator TEXT,
            created_at TEXT
        )
        """)

        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS sale_items(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sale_id INTEGER,
            product_id INTEGER,
            quantity INTEGER,
            price REAL,
            subtotal REAL
        )
        """)

        self.conn.commit()

    def insert_default_data(self):

        self.cursor.execute(
            "SELECT COUNT(*) FROM users"
        )

        if self.cursor.fetchone()[0] == 0:

            self.cursor.execute("""
            INSERT INTO users(username,password)
            VALUES('admin','123')
            """)

        self.cursor.execute(
            "SELECT COUNT(*) FROM products"
        )

        if self.cursor.fetchone()[0] == 0:

            products = [

                ('COCA COLA 2L','7894900011517','BEBIDAS',6.50,9.99,100,'COCA COLA'),
                ('ARROZ 5KG','7896006716112','MERCEARIA',18.00,26.90,50,'TIO JOAO'),
                ('FEIJAO CARIOCA','7891962050015','MERCEARIA',5.00,8.50,70,'KICALDO'),
                ('LEITE INTEGRAL','7891025301515','LATICINIOS',4.00,5.99,80,'PIRACANJUBA'),
                ('CAFE 500G','7896089010015','MERCEARIA',10.00,16.90,60,'PILAO'),
                ('MACARRAO','7896213005184','MASSAS',2.50,4.99,90,'RENATA'),
                ('ACUCAR','7891910000197','MERCEARIA',3.50,5.50,100,'UNIAO'),
                ('OLEO SOJA','7891107101511','MERCEARIA',5.00,7.99,70,'LIZA'),
                ('DETERGENTE','7891022850016','LIMPEZA',1.50,2.99,100,'YPE'),
                ('SABAO EM PO','7891150060018','LIMPEZA',9.00,15.90,40,'OMO'),
                ('PAPEL HIGIENICO','7891172430011','HIGIENE',12.00,19.99,30,'NEVE'),
                ('MARGARINA','7896004000855','LATICINIOS',4.50,7.99,50,'QUALY'),
                ('CHOCOLATE','7891000100101','DOCES',4.00,7.50,45,'LACTA'),
                ('BISCOITO','7892840813011','DOCES',2.00,3.99,150,'TRAKINAS'),
                ('SAL','7896042500010','MERCEARIA',1.00,2.99,100,'CISNE')

            ]

            for p in products:

                self.cursor.execute("""
                INSERT INTO products(
                    name,
                    barcode,
                    category,
                    cost_price,
                    sale_price,
                    stock,
                    supplier,
                    created_at
                )
                VALUES(?,?,?,?,?,?,?,?)
                """, (
                    p[0],
                    p[1],
                    p[2],
                    p[3],
                    p[4],
                    p[5],
                    p[6],
                    datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                ))

        self.conn.commit()

    def login(self, username, password):

        self.cursor.execute("""
        SELECT *
        FROM users
        WHERE username=?
        AND password=?
        """, (username, password))

        return self.cursor.fetchone()

    def get_product_barcode(self, barcode):

        self.cursor.execute("""
        SELECT *
        FROM products
        WHERE barcode=?
        """, (barcode,))

        return self.cursor.fetchone()

    def get_product_name(self, name):

        self.cursor.execute("""
        SELECT *
        FROM products
        WHERE UPPER(name) LIKE ?
        """, (f"%{name.upper()}%",))

        return self.cursor.fetchone()
class Backup:

    @staticmethod
    def create_backup():

        os.makedirs(BACKUP_DIR, exist_ok=True)

        timestamp = datetime.now().strftime(
            "%Y-%m-%d_%H-%M-%S"
        )

        backup_file = os.path.join(
            BACKUP_DIR,
            f"backup_{timestamp}.db"
        )

        shutil.copy2(DB_NAME, backup_file)


class App(ctk.CTk):

    def __init__(self):

        super().__init__()

        self.db = Database()

        self.user = None
        self.cart = []

        self.title("SUPERMERCADO V2")
        self.geometry("1400x850")

        self.show_login()

    def clear_screen(self):

        for widget in self.winfo_children():
            widget.destroy()

    def show_login(self):

        self.clear_screen()

        frame = ctk.CTkFrame(self)
        frame.pack(expand=True)

        title = ctk.CTkLabel(
            frame,
            text="SUPERMERCADO V2",
            font=("Arial", 30, "bold")
        )

        title.pack(pady=30)

        self.username_entry = ctk.CTkEntry(
            frame,
            placeholder_text="Usuario"
        )

        self.username_entry.pack(
            pady=10,
            padx=20
        )

        self.password_entry = ctk.CTkEntry(
            frame,
            placeholder_text="Senha",
            show="*"
        )

        self.password_entry.pack(
            pady=10,
            padx=20
        )

        login_button = ctk.CTkButton(
            frame,
            text="Entrar",
            command=self.login
        )

        login_button.pack(
            pady=20
        )

    def login(self):

        user = self.db.login(
            self.username_entry.get(),
            self.password_entry.get()
        )

        if user:

            self.user = user

            self.show_dashboard()

        else:

            messagebox.showerror(
                "Erro",
                "Login invalido"
            )

    def show_dashboard(self):

        self.clear_screen()

        self.sidebar = ctk.CTkFrame(
            self,
            width=250
        )

        self.sidebar.pack(
            side="left",
            fill="y"
        )

        self.content = ctk.CTkFrame(self)

        self.content.pack(
            side="right",
            fill="both",
            expand=True
        )

        ctk.CTkButton(
            self.sidebar,
            text="PDV",
            command=self.show_pdv
        ).pack(
            fill="x",
            padx=10,
            pady=5
        )

        ctk.CTkButton(
            self.sidebar,
            text="Produtos",
            command=self.show_products
        ).pack(
            fill="x",
            padx=10,
            pady=5
        )

        self.show_pdv()

    def clear_content(self):

        for widget in self.content.winfo_children():
            widget.destroy()
    def show_pdv(self):

        self.clear_content()

        top = ctk.CTkFrame(self.content)
        top.pack(fill="x", padx=10, pady=10)

        self.search_entry = ctk.CTkEntry(
            top,
            placeholder_text="Digite CODIGO ou NOME do produto"
        )

        self.search_entry.pack(
            side="left",
            fill="x",
            expand=True,
            padx=5
        )

        self.search_entry.bind(
            "<Return>",
            self.add_product
        )

        add_button = ctk.CTkButton(
            top,
            text="Adicionar",
            command=self.add_product
        )

        add_button.pack(
            side="left",
            padx=5
        )

        self.total_label = ctk.CTkLabel(
            self.content,
            text="TOTAL: R$ 0.00",
            font=("Arial", 24, "bold")
        )

        self.total_label.pack(
            pady=10
        )

        columns = (
            "Produto",
            "Qtd",
            "Preco",
            "Subtotal",
            "Estoque"
        )

        self.cart_table = ttk.Treeview(
            self.content,
            columns=columns,
            show="headings",
            height=20
        )

        for col in columns:
            self.cart_table.heading(
                col,
                text=col
            )

        self.cart_table.pack(
            fill="both",
            expand=True,
            padx=10,
            pady=10
        )

        buttons = ctk.CTkFrame(
            self.content
        )

        buttons.pack(
            fill="x",
            padx=10,
            pady=10
        )

        ctk.CTkButton(
            buttons,
            text="Finalizar Venda",
            command=self.finish_sale
        ).pack(
            side="left",
            padx=5
        )

        ctk.CTkButton(
            buttons,
            text="Limpar Carrinho",
            command=self.clear_cart
        ).pack(
            side="left",
            padx=5
        )

        ctk.CTkButton(
            buttons,
            text="Backup",
            command=Backup.create_backup
        ).pack(
            side="left",
            padx=5
        )

        self.update_cart()

    def add_product(self, event=None):

        search = self.search_entry.get().strip()

        if not search:
            return

        product = self.db.get_product_barcode(
            search
        )

        if not product:
            product = self.db.get_product_name(
                search
            )

        if not product:

            messagebox.showerror(
                "Erro",
                "Produto nao encontrado"
            )

            return

        found = False

        for item in self.cart:

            if item["id"] == product["id"]:

                item["quantity"] += 1

                item["subtotal"] = (
                    item["quantity"] *
                    item["price"]
                )

                found = True

                break

        if not found:

            self.cart.append({

                "id": product["id"],
                "name": product["name"],
                "barcode": product["barcode"],
                "price": product["sale_price"],
                "quantity": 1,
                "subtotal": product["sale_price"],
                "stock": product["stock"]

            })

        self.search_entry.delete(
            0,
            "end"
        )

        self.update_cart()

    def update_cart(self):

        if not hasattr(
            self,
            "cart_table"
        ):
            return

        for row in self.cart_table.get_children():
            self.cart_table.delete(row)

        total = 0

        for item in self.cart:

            self.cart_table.insert(
                "",
                "end",
                values=(

                    item["name"],
                    item["quantity"],
                    f'R$ {item["price"]:.2f}',
                    f'R$ {item["subtotal"]:.2f}',
                    item["stock"]

                )
            )

            total += item["subtotal"]

        self.total_label.configure(
            text=f"TOTAL: R$ {total:.2f}"
        )

    def clear_cart(self):

        self.cart.clear()

        self.update_cart()

    def finish_sale(self):

        if not self.cart:

            messagebox.showwarning(
                "Aviso",
                "Carrinho vazio"
            )

            return

        total = sum(
            item["subtotal"]
            for item in self.cart
        )

        self.db.cursor.execute(
            """
            INSERT INTO sales(
                total,
                operator,
                created_at
            )
            VALUES(?,?,?)
            """,
            (
                total,
                self.user["username"],
                datetime.now().strftime(
                    "%Y-%m-%d %H:%M:%S"
                )
            )
        )

        sale_id = self.db.cursor.lastrowid

        for item in self.cart:

            self.db.cursor.execute(
                """
                INSERT INTO sale_items(
                    sale_id,
                    product_id,
                    quantity,
                    price,
                    subtotal
                )
                VALUES(?,?,?,?,?)
                """,
                (
                    sale_id,
                    item["id"],
                    item["quantity"],
                    item["price"],
                    item["subtotal"]
                )
            )

            self.db.cursor.execute(
                """
                UPDATE products
                SET stock = stock - ?
                WHERE id = ?
                """,
                (
                    item["quantity"],
                    item["id"]
                )
            )

        self.db.conn.commit()

        Backup.create_backup()

        messagebox.showinfo(
            "Venda",
            f"Venda finalizada\nTotal R$ {total:.2f}"
        )

        self.cart.clear()

        self.update_cart()

    def show_products(self):

        self.clear_content()

        table = ttk.Treeview(
            self.content,
            columns=(
                "ID",
                "Nome",
                "Codigo",
                "Preco",
                "Estoque"
            ),
            show="headings"
        )

        table.pack(
            fill="both",
            expand=True,
            padx=10,
            pady=10
        )

        for col in table["columns"]:

            table.heading(
                col,
                text=col
            )

        self.db.cursor.execute(
            """
            SELECT *
            FROM products
            ORDER BY name
            """
        )

        products = self.db.cursor.fetchall()

        for p in products:

            table.insert(
                "",
                "end",
                values=(

                    p["id"],
                    p["name"],
                    p["barcode"],
                    f'R$ {p["sale_price"]:.2f}',
                    p["stock"]

                )
            )


if __name__ == "__main__":

    app = App()

    app.mainloop()
