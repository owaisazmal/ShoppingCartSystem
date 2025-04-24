import tkinter as tk
from tkinter import ttk, messagebox
import mysql.connector
from mysql.connector import Error

class ShoppingCartGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Shopping Cart System")
        self.root.geometry("800x600")

        # Database connection
        self.db_connection = self.connect_to_db()
        if not self.db_connection:
            self.root.destroy()
            return

        # Create GUI elements
        self.create_widgets()
        self.load_products()

    def connect_to_db(self):
        try:
            config = {
                'host': 'localhost',
                'user': 'root',
                'password': 'Test@123',  # replace if needed
                'database': 'shopping_cart_system'
            }
            print("Attempting connection with:", config)
            connection = mysql.connector.connect(**config)
            return connection
        except Error as e:
            messagebox.showerror("Database Error", f"Failed to connect: {e}")
            return None


    
    def load_products(self):
        try:
            cursor = self.db_connection.cursor(dictionary=True)
            cursor.execute("SELECT * FROM products")
            self.products = cursor.fetchall()
            
            # Clear and populate products list
            self.product_combobox['values'] = [p['name'] for p in self.products]
            if self.products:
                self.product_combobox.current(0)
                self.update_product_details(0)
        except Error as e:
            messagebox.showerror("Error", f"Failed to load products: {e}")
    
    def update_product_details(self, index):
        product = self.products[index]
        self.current_product_id = product['product_id']
        
        # Update labels
        self.price_label.config(text=f"Price: ${product['price']:.2f}")
        self.desc_label.config(text=f"Description: {product['description']}")
        self.category_label.config(text=f"Category: {product['category']}")
        
        # Update stock
        self.update_stock_label()
    
    def update_stock_label(self):
        cursor = self.db_connection.cursor()
        cursor.execute("SELECT quantity FROM inventory WHERE product_id = %s", (self.current_product_id,))
        stock = cursor.fetchone()[0]
        self.stock_label.config(text=f"In Stock: {stock}")
    
    def create_widgets(self):
        # Product Selection Frame
        selection_frame = ttk.LabelFrame(self.root, text="Product Selection", padding=10)
        selection_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # Product Combobox
        ttk.Label(selection_frame, text="Select Product:").grid(row=0, column=0, sticky=tk.W)
        self.product_combobox = ttk.Combobox(selection_frame, state="readonly")
        self.product_combobox.grid(row=0, column=1, sticky=tk.EW, padx=5)
        self.product_combobox.bind("<<ComboboxSelected>>", self.on_product_select)
        
        # Product Details
        details_frame = ttk.LabelFrame(self.root, text="Product Details", padding=10)
        details_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.price_label = ttk.Label(details_frame, text="Price: $0.00")
        self.price_label.pack(anchor=tk.W)
        
        self.desc_label = ttk.Label(details_frame, text="Description: ")
        self.desc_label.pack(anchor=tk.W)
        
        self.category_label = ttk.Label(details_frame, text="Category: ")
        self.category_label.pack(anchor=tk.W)
        
        self.stock_label = ttk.Label(details_frame, text="In Stock: 0")
        self.stock_label.pack(anchor=tk.W)
        
        # Quantity Control
        qty_frame = ttk.Frame(self.root)
        qty_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(qty_frame, text="Quantity:").pack(side=tk.LEFT)
        self.qty_spinbox = ttk.Spinbox(qty_frame, from_=1, to=100, width=5)
        self.qty_spinbox.pack(side=tk.LEFT, padx=5)
        self.qty_spinbox.set(1)
        
        # Action Buttons
        button_frame = ttk.Frame(self.root)
        button_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.add_button = ttk.Button(button_frame, text="Add to Cart", command=self.add_to_cart)
        self.add_button.pack(side=tk.LEFT, padx=5)
        
        self.remove_button = ttk.Button(button_frame, text="Remove from Cart", command=self.remove_from_cart)
        self.remove_button.pack(side=tk.LEFT, padx=5)
        
        self.clear_button = ttk.Button(button_frame, text="Empty Cart", command=self.empty_cart)
        self.clear_button.pack(side=tk.LEFT, padx=5)
        
        self.checkout_button = ttk.Button(button_frame, text="Checkout", command=self.checkout)
        self.checkout_button.pack(side=tk.LEFT, padx=5)
        
        # Cart Display
        cart_frame = ttk.LabelFrame(self.root, text="Your Shopping Cart", padding=10)
        cart_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        self.cart_tree = ttk.Treeview(cart_frame, columns=('name', 'price', 'quantity', 'total'), show='headings')
        self.cart_tree.heading('name', text='Product')
        self.cart_tree.heading('price', text='Price')
        self.cart_tree.heading('quantity', text='Qty')
        self.cart_tree.heading('total', text='Total')
        
        self.cart_tree.column('name', width=200)
        self.cart_tree.column('price', width=100, anchor=tk.E)
        self.cart_tree.column('quantity', width=50, anchor=tk.E)
        self.cart_tree.column('total', width=100, anchor=tk.E)
        
        self.cart_tree.pack(fill=tk.BOTH, expand=True)
        
        # Total Label
        self.total_label = ttk.Label(cart_frame, text="Total: $0.00", font=('Arial', 12, 'bold'))
        self.total_label.pack(anchor=tk.E, pady=5)
        
        # Initialize cart
        self.cart = {}
    
    def on_product_select(self, event):
        selected_index = self.product_combobox.current()
        self.update_product_details(selected_index)
    
    def add_to_cart(self):
        try:
            product_id = self.current_product_id
            quantity = int(self.qty_spinbox.get())
            
            if quantity <= 0:
                messagebox.showwarning("Invalid Quantity", "Quantity must be positive")
                return
            
            # Check stock
            cursor = self.db_connection.cursor()
            cursor.execute("SELECT quantity FROM inventory WHERE product_id = %s", (product_id,))
            stock = cursor.fetchone()[0]
            
            if stock < quantity:
                messagebox.showwarning("Out of Stock", f"Only {stock} available")
                return
            
            # Get product details
            cursor.execute("SELECT name, price FROM products WHERE product_id = %s", (product_id,))
            name, price = cursor.fetchone()
            
            # Add to cart
            if product_id in self.cart:
                self.cart[product_id]['quantity'] += quantity
            else:
                self.cart[product_id] = {
                    'name': name,
                    'price': price,
                    'quantity': quantity
                }
            
            # Update display
            self.update_cart_display()
            self.update_stock_label()
            messagebox.showinfo("Success", f"Added {quantity} {name}(s) to cart")
            
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid quantity")
        except Error as e:
            messagebox.showerror("Database Error", f"Failed to add to cart: {e}")
    
    def remove_from_cart(self):
        if not self.cart:
            messagebox.showinfo("Empty Cart", "Your cart is already empty")
            return
            
        product_id = self.current_product_id
        
        if product_id not in self.cart:
            messagebox.showwarning("Not in Cart", "This product is not in your cart")
            return
            
        try:
            quantity = int(self.qty_spinbox.get())
            current_qty = self.cart[product_id]['quantity']
            
            if quantity <= 0:
                messagebox.showwarning("Invalid Quantity", "Quantity must be positive")
                return
                
            if quantity >= current_qty:
                name = self.cart[product_id]['name']
                del self.cart[product_id]
                message = f"Removed all {name} from cart"
            else:
                self.cart[product_id]['quantity'] -= quantity
                message = f"Removed {quantity} {self.cart[product_id]['name']}(s) from cart"
            
            self.update_cart_display()
            self.update_stock_label()
            messagebox.showinfo("Success", message)
            
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid quantity")
    
    def empty_cart(self):
        if not self.cart:
            messagebox.showinfo("Empty Cart", "Your cart is already empty")
            return
            
        if messagebox.askyesno("Confirm", "Are you sure you want to empty your cart?"):
            self.cart = {}
            self.update_cart_display()
            messagebox.showinfo("Success", "Cart has been emptied")
    
    def checkout(self):
        if not self.cart:
            messagebox.showinfo("Empty Cart", "Your cart is empty")
            return
            
        try:
            # Calculate total
            total = sum(item['price'] * item['quantity'] for item in self.cart.values())
            
            # Update inventory
            cursor = self.db_connection.cursor()
            for product_id, item in self.cart.items():
                cursor.execute(
                    "UPDATE inventory SET quantity = quantity - %s WHERE product_id = %s",
                    (item['quantity'], product_id)
                )
            
            self.db_connection.commit()
            
            # Clear cart
            self.cart = {}
            self.update_cart_display()
            
            messagebox.showinfo("Order Complete", f"Thank you for your purchase!\nTotal: ${total:.2f}")
            
        except Error as e:
            messagebox.showerror("Checkout Error", f"Failed to complete checkout: {e}")
            self.db_connection.rollback()
    
    def update_cart_display(self):
        # Clear current display
        for item in self.cart_tree.get_children():
            self.cart_tree.delete(item)
        
        # Add cart items
        total = 0
        for product_id, item in self.cart.items():
            item_total = item['price'] * item['quantity']
            self.cart_tree.insert('', 'end', values=(
                item['name'],
                f"${item['price']:.2f}",
                item['quantity'],
                f"${item_total:.2f}"
            ))
            total += item_total
        
        # Update total
        self.total_label.config(text=f"Total: ${total:.2f}")

if __name__ == "__main__":
    root = tk.Tk()
    app = ShoppingCartGUI(root)
    root.mainloop()