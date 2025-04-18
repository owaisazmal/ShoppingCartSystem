import mysql.connector
from mysql.connector import Error


#Establishing the connection ref:https://dev.mysql.com/doc/connector-python/en/connector-python-example-connecting.html
class DatabaseConnection:
    def __init__(self):
        try:
            self.connection = mysql.connector.connect( 
                host='localhost',
                user='root',  
                password='Test@123',  
                database='shopping_cart_system'
            )
            if self.connection.is_connected():
                print("Successfully connected to the database")
        except Error as e:
            print(f"Error connecting to MySQL: {e}")
    
    def close(self):
        if self.connection.is_connected():
            self.connection.close()
            print("Database connection closed")

#End of the DatabaseConnection class

#This class handles the shoping cart operations
class ShoppingCartSystem:
    def __init__(self):
        self.db = DatabaseConnection()
        self.cart = {}

    #This method fetches product detils from the database
    #It takes the product_id as argment & returns the product details
    def get_product(self, product_id):
        """Get product details from database"""
        try:
            cursor = self.db.connection.cursor(dictionary=True) #set dictionary=True to get results as dictionaries
            query = "SELECT * FROM products WHERE product_id = %s"
            cursor.execute(query, (product_id,))
            product = cursor.fetchone()
            return product
        except Error as e:
            print(f"Error fetching product: {e}")
            return None
    
    def check_stock(self, product_id, quantity=1):
        """Check if we have enough stock"""
        try:
            cursor = self.db.connection.cursor()
            query = "SELECT quantity FROM inventory WHERE product_id = %s"
            cursor.execute(query, (product_id,))
            result = cursor.fetchone()
            
            if result and result[0] >= quantity:
                return True
            return False
        except Error as e:
            print(f"Error checking stock: {e}")
            return False
    
    def update_stock(self, product_id, quantity_change):
        """Update inventory after purchase"""
        try:
            cursor = self.db.connection.cursor()
            query = "UPDATE inventory SET quantity = quantity + %s WHERE product_id = %s"
            cursor.execute(query, (quantity_change, product_id))
            self.db.connection.commit()
            return True
        except Error as e:
            print(f"Error updating stock: {e}")
            return False
    
    def add_to_cart(self, product_id, quantity=1):
        """Add an item to the shopping cart"""
        if quantity <= 0:
            print("Quantity must be positive")
            return False
        
        product = self.get_product(product_id)
        if not product:
            print("Product not found")
            return False
        
        if not self.check_stock(product_id, quantity):
            print(f"Not enough stock for {product['name']}")
            return False
        
        if product_id in self.cart:
            self.cart[product_id]['quantity'] += quantity
        else:
            self.cart[product_id] = {
                'name': product['name'],
                'price': product['price'],
                'quantity': quantity
            }
        
        print(f"Added {quantity} {product['name']}(s) to cart")
        return True
    
    def remove_from_cart(self, product_id, quantity=1):
        """Remove an item from the cart"""
        if product_id not in self.cart:
            print("Item not in cart")
            return False
        
        if quantity <= 0:
            print("Quantity must be positive")
            return False
        
        current_quantity = self.cart[product_id]['quantity']
        
        if quantity >= current_quantity:
            del self.cart[product_id]
            print(f"Removed all {self.cart[product_id]['name']} from cart")
        else:
            self.cart[product_id]['quantity'] -= quantity
            print(f"Removed {quantity} {self.cart[product_id]['name']}(s) from cart")
        
        return True
    
    def view_cart(self):
        """Display all items in the cart"""
        if not self.cart:
            print("Your cart is empty")
            return
        
        print("\nYour Shopping Cart:")
        total = 0
        for item in self.cart.values():
            item_total = item['price'] * item['quantity']
            print(f"{item['name']} x{item['quantity']}: ${item_total:.2f}")
            total += item_total
        
        print(f"\nTotal: ${total:.2f}")
    
    def checkout(self):
        """Process the order and update inventory"""
        if not self.cart:
            print("Cannot checkout empty cart")
            return False
        
        # Check stock again in case it changed
        for product_id, item in self.cart.items():
            if not self.check_stock(product_id, item['quantity']):
                print(f"Sorry, {item['name']} is now out of stock")
                return False
        
        # Update inventory
        for product_id, item in self.cart.items():
            if not self.update_stock(product_id, -item['quantity']):
                print(f"Failed to update inventory for {item['name']}")
                return False
        
        # Calculate total
        total = sum(item['price'] * item['quantity'] for item in self.cart.values())
        
        # Clear cart
        self.cart = {}
        
        print("\nCheckout successful!")
        print(f"Your total was: ${total:.2f}")
        print("Thank you for your purchase!")
        return True
    
    def close(self):
        """Close the database connection"""
        self.db.close()

# Example usage
if __name__ == "__main__":
    system = ShoppingCartSystem()
    
    try:
        # Add some items to cart
        system.add_to_cart(1, 2)  # 2 Laptops
        system.add_to_cart(2, 3)  # 3 Mice
        system.add_to_cart(3, 5)  # 5 Notebooks
        
        # View cart
        system.view_cart()
        
        # Try to checkout
        system.checkout()
        
    finally:
        system.close()