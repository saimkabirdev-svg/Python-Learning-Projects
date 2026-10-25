# ------------------------------ Input helpers ------------------------------

def print_line(symbol="-", width=78):
    print(symbol * width)

def show_heading(title):
    print()
    print_line("=")
    print(title.center(78))
    print_line("=")

def get_non_empty_text(prompt):
    while True:
        value = input(prompt).strip()
        if value != "":
            return value
        print("Input cannot be empty. Please try again.")

def get_non_negative_number(prompt, whole_number=False):
    while True:
        value = input(prompt).strip()
        if value == "":
            print("Please enter a value.")
            continue

        # Manually validate input without importing modules.
        if whole_number:
            if value.isdigit():
                return int(value)
            print("Enter a whole number greater than or equal to zero.")
        else:
            try:
                number = float(value)
                if number >= 0:
                    return number
                print("Enter a number greater than or equal to zero.")
            except ValueError:
                print("Enter a valid number.")

def get_positive_whole_number(prompt):
    while True:
        number = get_non_negative_number(prompt, whole_number=True)
        if number > 0:
            return number
        print("Value must be at least 1.")

def get_choice(prompt, valid_choices):
    while True:
        choice = input(prompt).strip()
        if choice in valid_choices:
            return choice
        print("Invalid choice. Valid options:", ", ".join(valid_choices))

def format_money(amount):
    return f"{CURRENCY} {amount:,.2f}"

# ------------------------------ Product utilities ------------------------------

def generate_product_id(products):
    """Generate the next ID using the number of existing products."""
    next_number = len(products) + 1001

    # Check for duplicates in case a product was deleted.
    while find_product(products, "SP" + str(next_number)) is not None:
        next_number += 1

    return "SP" + str(next_number)

def find_product(products, product_id):
    """Return a product dictionary if its ID matches; otherwise return None."""
    for product in products:
        if product["id"].lower() == product_id.strip().lower():
            return product
    return None

def show_product_table(products):
    if len(products) == 0:
        print("There are no products to display.")
        return

    print_line()
    print(f"{'ID':<9} {'PRODUCT':<22} {'CATEGORY':<16} {'QTY':>5} "
          f"{'COST':>11} {'PRICE':>11} {'STATUS':<10}")
    print_line()

    for product in products:
        if product["quantity"] == 0:
            status = "OUT"
        elif product["quantity"] <= product["min_stock"]:
            status = "LOW"
        else:
            status = "OK"

        print(f"{product['id']:<9} "
              f"{product['name'][:21]:<22} "
              f"{product['category'][:15]:<16} "
              f"{product['quantity']:>5} "
              f"{product['cost_price']:>11,.2f} "
              f"{product['selling_price']:>11,.2f} "
              f"{status:<10}")

    print_line()
    print("Products displayed:", len(products))

def show_product_details(product):
    show_heading("PRODUCT DETAILS")
    print("Product ID             :", product["id"])
    print("Name                   :", product["name"])
    print("Category               :", product["category"])
    print("Quantity available     :", product["quantity"])
    print("Low-stock threshold    :", product["min_stock"])
    print("Purchase cost per unit :", format_money(product["cost_price"]))
    print("Selling price per unit :", format_money(product["selling_price"]))
    print("Total inventory cost   :", format_money(product["quantity"] * product["cost_price"]))
    print("Potential sales value  :", format_money(product["quantity"] * product["selling_price"]))
    print("Potential gross profit :", format_money(
        product["quantity"] * (product["selling_price"] - product["cost_price"])
    ))

# ------------------------------ Product management ------------------------------

def add_product(products):
    show_heading("ADD A PRODUCT")

    name = get_non_empty_text("Product name: ")
    category = get_non_empty_text("Category: ")
    cost_price = get_non_negative_number("Purchase cost per unit (PKR): ")
    selling_price = get_non_negative_number("Selling price per unit (PKR): ")
    quantity = get_non_negative_number("Opening stock quantity: ", whole_number=True)
    min_stock = get_non_negative_number("Low-stock warning level: ", whole_number=True)

    product = {
        "id": generate_product_id(products),
        "name": name,
        "category": category,
        "cost_price": round(cost_price, 2),
        "selling_price": round(selling_price, 2),
        "quantity": quantity,
        "min_stock": min_stock
    }

    products.append(product)
    print("\nProduct added successfully!")
    print("Assigned product ID:", product["id"])

    if selling_price < cost_price:
        print("Warning: the selling price is lower than the purchase cost.")
    if quantity <= min_stock:
        print("Low-stock alert: this product is already at or below its warning level.")


def update_product(products):
    show_heading("UPDATE PRODUCT")

    product_id = input("Enter product ID: ").strip()
    product = find_product(products, product_id)

    if product is None:
        print("Product not found.")
        return

    show_product_details(product)
    print("\nPress Enter to keep an existing value.")

    new_name = input("New name [" + product["name"] + "]: ").strip()
    new_category = input("New category [" + product["category"] + "]: ").strip()

    if new_name != "":
        product["name"] = new_name
    if new_category != "":
        product["category"] = new_category

    choice = get_choice("Update prices too? (y/n): ", ["y", "n"])
    if choice == "y":
        product["cost_price"] = get_non_negative_number("New purchase cost: ")
        product["selling_price"] = get_non_negative_number("New selling price: ")

    product["min_stock"] = get_non_negative_number(
        "New low-stock threshold [" + str(product["min_stock"]) + "]: ",
        whole_number=True
    )

    print("Product details updated successfully.")


def delete_product(products):
    show_heading("DELETE PRODUCT")

    product_id = input("Enter product ID: ").strip()
    product = find_product(products, product_id)

    if product is None:
        print("Product not found.")
        return

    show_product_details(product)
    confirmation = get_choice("Are you sure you want to delete it? (y/n): ", ["y", "n"])

    if confirmation == "y":
        products.remove(product)
        print("Product deleted successfully.")
    else:
        print("Deletion cancelled.")


def search_products(products):
    show_heading("SEARCH PRODUCTS")
    query = get_non_empty_text("Enter an ID, product name, or category: ").lower()
    matches = []

    for product in products:
        if (query in product["id"].lower()
                or query in product["name"].lower()
                or query in product["category"].lower()):
            matches.append(product)

    print("\nSearch results:")
    show_product_table(matches)


# ------------------------------ Stock operations ------------------------------

def receive_stock(products):
    show_heading("RECEIVE STOCK")

    product_id = input("Enter product ID: ").strip()
    product = find_product(products, product_id)

    if product is None:
        print("Product not found.")
        return

    print("Current quantity:", product["quantity"])
    received = get_positive_whole_number("Quantity received: ")
    new_cost = get_non_negative_number("Purchase cost per new unit (PKR): ")

    old_quantity = product["quantity"]
    old_cost = product["cost_price"]
    combined_quantity = old_quantity + received

    # Weighted average cost: a basic business calculation.
    product["cost_price"] = round(
        ((old_quantity * old_cost) + (received * new_cost)) / combined_quantity, 2
    )
    product["quantity"] += received

    print("\nStock received successfully.")
    print("Updated quantity:", product["quantity"])
    print("Updated average purchase cost:", format_money(product["cost_price"]))

    if product["quantity"] <= product["min_stock"]:
        print("Low-stock alert: quantity is still at or below the warning level.")


def record_sale(products):
    show_heading("RECORD A SALE")

    product_id = input("Enter product ID: ").strip()
    product = find_product(products, product_id)

    if product is None:
        print("Product not found.")
        return

    if product["quantity"] == 0:
        print("This product is out of stock. Sale cannot be completed.")
        return

    print("Available quantity:", product["quantity"])
    quantity_sold = get_positive_whole_number("Quantity sold: ")

    if quantity_sold > product["quantity"]:
        print("Sale rejected: requested quantity exceeds available stock.")
        return

    selling_price = get_non_negative_number(
        "Selling price per unit (press 0 to use listed price): "
    )
    if selling_price == 0:
        selling_price = product["selling_price"]

    revenue = quantity_sold * selling_price
    estimated_cost = quantity_sold * product["cost_price"]
    gross_profit = revenue - estimated_cost

    product["quantity"] -= quantity_sold

    print("\nSale recorded successfully.")
    print("Units sold             :", quantity_sold)
    print("Sales revenue          :", format_money(revenue))
    print("Estimated gross profit :", format_money(gross_profit))
    print("Remaining stock        :", product["quantity"])

    if product["quantity"] == 0:
        print("OUT OF STOCK ALERT: this product needs restocking.")
    elif product["quantity"] <= product["min_stock"]:
        print("LOW STOCK ALERT: consider restocking this product.")


# ------------------------------ Reports and calculations ------------------------------

def show_dashboard(products):
    show_heading("STOCKPILOT BUSINESS DASHBOARD")

    if len(products) == 0:
        print("No products have been added yet.")
        return

    total_units = 0
    inventory_cost = 0
    potential_sales = 0
    low_stock_count = 0
    out_of_stock_count = 0

    for product in products:
        total_units += product["quantity"]
        inventory_cost += product["quantity"] * product["cost_price"]
        potential_sales += product["quantity"] * product["selling_price"]

        if product["quantity"] <= product["min_stock"]:
            low_stock_count += 1
        if product["quantity"] == 0:
            out_of_stock_count += 1

    print("Unique products             :", len(products))
    print("Total units in stock        :", total_units)
    print("Inventory cost value        :", format_money(inventory_cost))
    print("Potential sales value       :", format_money(potential_sales))
    print("Potential gross profit      :", format_money(potential_sales - inventory_cost))
    print("Products at low-stock level :", low_stock_count)
    print("Out-of-stock products       :", out_of_stock_count)

    print("\nLow-stock products:")
    low_stock_products = []
    for product in products:
        if product["quantity"] <= product["min_stock"]:
            low_stock_products.append(product)

    if len(low_stock_products) == 0:
        print("All products are above their low-stock thresholds.")
    else:
        show_product_table(low_stock_products)


def show_restock_report(products):
    show_heading("RESTOCKING REPORT")

    low_stock_products = []
    for product in products:
        if product["quantity"] <= product["min_stock"]:
            low_stock_products.append(product)

    if len(low_stock_products) == 0:
        print("No products need restocking.")
        return

    print_line()
    print(f"{'PRODUCT':<22} {'CURRENT':>9} {'MINIMUM':>9} "
          f"{'ORDER QTY':>11} {'EST. COST':>14}")
    print_line()

    total_budget = 0

    for product in low_stock_products:
        # Aim to replenish stock to twice its minimum level.
        target_quantity = product["min_stock"] * 2
        if target_quantity <= product["quantity"]:
            target_quantity = product["quantity"] + 1

        order_quantity = target_quantity - product["quantity"]
        estimated_cost = order_quantity * product["cost_price"]
        total_budget += estimated_cost

        print(f"{product['name'][:21]:<22} "
              f"{product['quantity']:>9} "
              f"{product['min_stock']:>9} "
              f"{order_quantity:>11} "
              f"{estimated_cost:>14,.2f}")

    print_line()
    print("Estimated restocking budget:", format_money(total_budget))
    print("Note: this is a suggested plan, not an actual purchase order.")


def show_category_summary(products):
    show_heading("CATEGORY SUMMARY")

    if len(products) == 0:
        print("No products available.")
        return

    categories = []

    for product in products:
        category_found = False

        for category in categories:
            if category["name"].lower() == product["category"].lower():
                category_found = True
                category["product_count"] += 1
                category["units"] += product["quantity"]
                category["cost_value"] += product["quantity"] * product["cost_price"]
                category["sales_value"] += product["quantity"] * product["selling_price"]
                break

        if not category_found:
            categories.append({
                "name": product["category"],
                "product_count": 1,
                "units": product["quantity"],
                "cost_value": product["quantity"] * product["cost_price"],
                "sales_value": product["quantity"] * product["selling_price"]
            })

    print_line()
    print(f"{'CATEGORY':<22} {'PRODUCTS':>9} {'UNITS':>9} "
          f"{'COST VALUE':>16} {'SALES VALUE':>16}")
    print_line()

    for category in categories:
        print(f"{category['name'][:21]:<22} "
              f"{category['product_count']:>9} "
              f"{category['units']:>9} "
              f"{category['cost_value']:>16,.2f} "
              f"{category['sales_value']:>16,.2f}")

    print_line()


def show_top_products(products):
    show_heading("TOP PRODUCTS BY INVENTORY VALUE")

    if len(products) == 0:
        print("No products available.")
        return

    ranked_products = []
    for product in products:
        ranked_products.append({
            "id": product["id"],
            "name": product["name"],
            "value": product["quantity"] * product["cost_price"]
        })

    for i in range(len(ranked_products)):
        highest_index = i
        for j in range(i + 1, len(ranked_products)):
            if ranked_products[j]["value"] > ranked_products[highest_index]["value"]:
                highest_index = j
        ranked_products[i], ranked_products[highest_index] = (
            ranked_products[highest_index], ranked_products[i]
        )

    print_line()
    print(f"{'RANK':<6} {'ID':<9} {'PRODUCT':<30} {'INVENTORY VALUE':>18}")
    print_line()

    limit = min(5, len(ranked_products))
    for i in range(limit):
        product = ranked_products[i]
        print(f"{i + 1:<6} {product['id']:<9} "
              f"{product['name'][:29]:<30} {product['value']:>18,.2f}")


# ------------------------------ Optional demo data ------------------------------

def load_sample_products(products):
    if len(products) > 0:
        print("Sample data can only be loaded into an empty inventory.")
        return

    choice = get_choice("Load sample products to explore StockPilot? (y/n): ", ["y", "n"])
    if choice == "n":
        return

    products.extend([
        {
            "id": "SP1001", "name": "Wireless Mouse", "category": "Electronics",
            "cost_price": 950.0, "selling_price": 1450.0, "quantity": 18, "min_stock": 5
        },
        {
            "id": "SP1002", "name": "USB-C Cable", "category": "Accessories",
            "cost_price": 220.0, "selling_price": 400.0, "quantity": 4, "min_stock": 10
        },
        {
            "id": "SP1003", "name": "Notebook A5", "category": "Stationery",
            "cost_price": 110.0, "selling_price": 180.0, "quantity": 0, "min_stock": 8
        },
        {
            "id": "SP1004", "name": "Keyboard", "category": "Electronics",
            "cost_price": 1800.0, "selling_price": 2600.0, "quantity": 9, "min_stock": 3
        }
    ])

    print("Sample products loaded successfully.")


# ------------------------------ Main program ------------------------------

def show_menu():
    print("""
  STOCKPILOT | INVENTORY INTELLIGENCE SYSTEM
  ──────────────────────────────────────────
  1. Business dashboard
  2. View all products
  3. Add a product
  4. Update product
  5. Delete product
  6. Search products
  7. Receive stock
  8. Record a sale
  9. Restocking report
  10. Category summary
  11. Top products by inventory value
  0. Exit
""")


def main():
    products = []

    print("""
========================================
              STOCKPILOT
       INVENTORY INTELLIGENCE SYSTEM
========================================
""")

    load_sample_products(products)

    while True:
        show_menu()
        choice = get_choice(
            "Choose an option: ",
            ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11"]
        )

        if choice == "0":
            print("Thank you for using StockPilot!")
            print("Reminder: this Programming Fundamentals version does not save data after exit.")
            break
        elif choice == "1":
            show_dashboard(products)
        elif choice == "2":
            show_heading("ALL PRODUCTS")
            show_product_table(products)
        elif choice == "3":
            add_product(products)
        elif choice == "4":
            update_product(products)
        elif choice == "5":
            delete_product(products)
        elif choice == "6":
            search_products(products)
        elif choice == "7":
            receive_stock(products)
        elif choice == "8":
            record_sale(products)
        elif choice == "9":
            show_restock_report(products)
        elif choice == "10":
            show_category_summary(products)
        elif choice == "11":
            show_top_products(products)

        input("\nPress Enter to return to the menu...")


main()
