import tkinter as tk
from tkinter import ttk, messagebox
import mysql.connector
from mysql.connector import Error

class AdminInventoryGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Admin Inventory Management")
        self.root.geometry("1000x700")
        
        # Database connection
        self.db_connection = self.connect_to_db()
        if not self.db_connection:
            self.root.destroy()
            return
        
        # Create GUI elements
        self.create_widgets()
        
        # Load products from database
        self.load_products()

    def connect_to_db(self):
        try:
            config = {
                'host': 'localhost',
                'user': 'root',
                'password': 'Test@123',  # change if needed
                'database': 'shopping_cart_system'
            }
            print("Connecting to DB (admin)...")
            connection = mysql.connector.connect(**config)
            return connection
        except Error as e:
            messagebox.showerror("Database Error", f"Failed to connect: {e}")
            return None

    #End of the DatabaseConnection class

    #Creating the GUI elements
    def create_widgets(self):
        # Main frames
        control_frame = ttk.LabelFrame(self.root, text="Inventory Controls", padding=10)
        control_frame.pack(fill=tk.X, padx=10, pady=5)
        
        display_frame = ttk.LabelFrame(self.root, text="Current Inventory", padding=10)
        display_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Product selection
        ttk.Label(control_frame, text="Select Product:").grid(row=0, column=0, sticky=tk.W)
        self.product_combobox = ttk.Combobox(control_frame, state="readonly")
        self.product_combobox.grid(row=0, column=1, sticky=tk.EW, padx=5)
        self.product_combobox.bind("<<ComboboxSelected>>", self.on_product_select)
        
        # Quantity controls
        ttk.Label(control_frame, text="New Quantity:").grid(row=0, column=2, padx=5)
        self.quantity_entry = ttk.Entry(control_frame, width=10)
        self.quantity_entry.grid(row=0, column=3, padx=5)
        
        # Action buttons
        self.update_btn = ttk.Button(control_frame, text="Update Quantity", command=self.update_quantity)
        self.update_btn.grid(row=0, column=4, padx=5)
        
        self.delete_btn = ttk.Button(control_frame, text="Delete Product", command=self.delete_product)
        self.delete_btn.grid(row=0, column=5, padx=5)
        
        # Add new product frame
        add_frame = ttk.LabelFrame(control_frame, text="Add New Product", padding=10)
        add_frame.grid(row=1, column=0, columnspan=6, sticky=tk.EW, pady=10)
        
        # New product fields
        ttk.Label(add_frame, text="Name:").grid(row=0, column=0)
        self.new_name = ttk.Entry(add_frame)
        self.new_name.grid(row=0, column=1, padx=5)
        
        ttk.Label(add_frame, text="Price:").grid(row=0, column=2)
        self.new_price = ttk.Entry(add_frame)
        self.new_price.grid(row=0, column=3, padx=5)
        
        ttk.Label(add_frame, text="Initial Stock:").grid(row=0, column=4)
        self.new_stock = ttk.Entry(add_frame)
        self.new_stock.grid(row=0, column=5, padx=5)
        
        ttk.Label(add_frame, text="Category:").grid(row=1, column=0)
        self.new_category = ttk.Entry(add_frame)
        self.new_category.grid(row=1, column=1, padx=5)
        
        ttk.Label(add_frame, text="Description:").grid(row=1, column=2)
        self.new_desc = ttk.Entry(add_frame)
        self.new_desc.grid(row=1, column=3, columnspan=3, sticky=tk.EW, padx=5)
        
        self.add_btn = ttk.Button(add_frame, text="Add Product", command=self.add_product)
        self.add_btn.grid(row=2, column=0, columnspan=6, pady=5)
        
        # Inventory display treeview
        self.tree = ttk.Treeview(display_frame, columns=('id', 'name', 'price', 'stock', 'category'), show='headings')
        
        self.tree.heading('id', text='ID')
        self.tree.heading('name', text='Product Name')
        self.tree.heading('price', text='Price')
        self.tree.heading('stock', text='In Stock')
        self.tree.heading('category', text='Category')
        
        self.tree.column('id', width=50, anchor=tk.CENTER)
        self.tree.column('name', width=200)
        self.tree.column('price', width=100, anchor=tk.E)
        self.tree.column('stock', width=100, anchor=tk.CENTER)
        self.tree.column('category', width=150)
        
        self.tree.pack(fill=tk.BOTH, expand=True)
        
        # Refresh button
        ttk.Button(display_frame, text="Refresh", command=self.load_products).pack(anchor=tk.E, pady=5)
    
    def load_products(self):
        try:
            cursor = self.db_connection.cursor(dictionary=True)
            query = """
                SELECT p.product_id, p.name, p.price, p.description, p.category, i.quantity 
                FROM products p 
                JOIN inventory i ON p.product_id = i.product_id
            """
            cursor.execute(query)
            self.products = cursor.fetchall()
            
            # Update combobox
            self.product_combobox['values'] = [f"{p['product_id']} - {p['name']}" for p in self.products]
            if self.products:
                self.product_combobox.current(0)
                self.on_product_select()
            
            # Update treeview
            for item in self.tree.get_children():
                self.tree.delete(item)
                
            for product in self.products:
                self.tree.insert('', 'end', values=(
                    product['product_id'],
                    product['name'],
                    f"${product['price']:.2f}",
                    product['quantity'],
                    product['category']
                ))
                
        except Error as e:
            messagebox.showerror("Database Error", f"Failed to load products: {e}")
    
    def on_product_select(self, event=None):
        if not self.products:
            return
            
        selection = self.product_combobox.current()
        if selection >= 0:
            product = self.products[selection]
            self.quantity_entry.delete(0, tk.END)
            self.quantity_entry.insert(0, str(product['quantity']))
    
    def update_quantity(self): 
        #debugging didn't work here
        #print("Update Quantity button clicked")
        #print(f"Selected product: {self.product_combobox.get()}")
        #print(f"New quantity: {self.quantity_entry.get()}")
        try:
            selection = self.product_combobox.current()
            if selection < 0:
                messagebox.showwarning("Warning", "Please select a product first")
                return
                
            product_id = self.products[selection]['product_id']
            new_quantity = int(self.quantity_entry.get())
            
            if new_quantity < 0:
                messagebox.showwarning("Warning", "Quantity cannot be negative")
                return
                
            cursor = self.db_connection.cursor()
            cursor.execute(
                "UPDATE inventory SET quantity = %s WHERE product_id = %s",
                (new_quantity, product_id)
            )
            self.db_connection.commit()
            
            messagebox.showinfo("Success", "Quantity updated successfully")
            self.load_products()
            
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid number")
        except Error as e:
            messagebox.showerror("Database Error", f"Failed to update quantity: {e}")
            self.db_connection.rollback()
    
    def delete_product(self):
        selection = self.product_combobox.current()
        if selection < 0:
            messagebox.showwarning("Warning", "Please select a product first")
            return
            
        product_id = self.products[selection]['product_id']
        product_name = self.products[selection]['name']
        
        if not messagebox.askyesno("Confirm", f"Delete {product_name} permanently?"):
            return
            
        try:
            cursor = self.db_connection.cursor()
            
            # First delete from inventory
            cursor.execute("DELETE FROM inventory WHERE product_id = %s", (product_id,))
            
            # Then delete from products
            cursor.execute("DELETE FROM products WHERE product_id = %s", (product_id,))
            
            self.db_connection.commit()
            messagebox.showinfo("Success", "Product deleted successfully")
            self.load_products()
            
        except Error as e:
            messagebox.showerror("Database Error", f"Failed to delete product: {e}")
            self.db_connection.rollback()
    
    def add_product(self):
        #debugging
        #print("Add Product button clicked")
        #print(f"Name: {self.new_name.get()}")
        #print(f"Price: {self.new_price.get()}") 
        try:
            name = self.new_name.get().strip()
            price = float(self.new_price.get())
            stock = int(self.new_stock.get())
            category = self.new_category.get().strip()
            description = self.new_desc.get().strip()
            
            if not name or not category:
                messagebox.showwarning("Warning", "Name and category are required")
                return
                
            if price <= 0 or stock < 0:
                messagebox.showwarning("Warning", "Price must be positive and stock cannot be negative")
                return
                
            cursor = self.db_connection.cursor()
            
            # Insert into products
            cursor.execute(
                "INSERT INTO products (name, price, description, category) VALUES (%s, %s, %s, %s)",
                (name, price, description, category)
            )
            
            # Get the new product ID
            product_id = cursor.lastrowid
            
            # Insert into inventory
            cursor.execute(
                "INSERT INTO inventory (product_id, quantity) VALUES (%s, %s)",
                (product_id, stock)
            )
            
            self.db_connection.commit()
            
            # Clear form
            self.new_name.delete(0, tk.END)
            self.new_price.delete(0, tk.END)
            self.new_stock.delete(0, tk.END)
            self.new_category.delete(0, tk.END)
            self.new_desc.delete(0, tk.END)
            
            messagebox.showinfo("Success", "Product added successfully")
            self.load_products()
            
        except ValueError:
            messagebox.showerror("Error", "Please enter valid numbers for price and stock")
        except Error as e:
            messagebox.showerror("Database Error", f"Failed to add product: {e}")
            self.db_connection.rollback()

if __name__ == "__main__":
    root = tk.Tk()
    app = AdminInventoryGUI(root)
    root.mainloop()