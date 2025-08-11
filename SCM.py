import pandas as pd
import networkx as nx
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import streamlit as st
import matplotlib.pyplot as plt

class SupplyChain:
    def __init__(self):
        self.graph = nx.DiGraph()

    def add_edge(self, start, end, cost, route, transport):
        self.graph.add_edge(start, end, cost=cost, route=route, transport=transport)

    def top_supplier(self, start_supplier):
        supply_chain_data = pd.read_csv('supply_chain_data.csv')

        for index, row in supply_chain_data.iterrows():
            supplier = row['Supplier name']
            location = row['Location']
            cost = row['Costs']
            route = row['Routes']
            transport = row['Transportation modes']
            self.add_edge(supplier, location, cost, route, transport)

        lead_time_weight = 0.4
        cost_weight = 0.3
        availability_weight = 0.3

        supply_chain_data['Score'] = (supply_chain_data['Lead times'] * lead_time_weight +
                                      supply_chain_data['Price'] * cost_weight +
                                      supply_chain_data['Availability'] * availability_weight)

        top_supplier = supply_chain_data[supply_chain_data['Supplier name'] == start_supplier].sort_values(
            by='Score').iloc[0]
        st.write("Supplier that is best in supplying product based on score:")
        st.write(top_supplier)

        
                
    def shortest_dist(self, start_supplier):
        supply_chain_data = pd.read_csv('supply_chain_data.csv')

        for index, row in supply_chain_data.iterrows():
            supplier = row['Supplier name']
            location = row['Location']
            cost = row['Costs']
            route = row['Routes']
            transport = row['Transportation modes']
            self.add_edge(supplier, location, cost, route, transport)

        lead_time_weight = 0.4
        cost_weight = 0.3
        availability_weight = 0.3

        supply_chain_data['Score'] = (supply_chain_data['Lead times'] * lead_time_weight +
                                      supply_chain_data['Price'] * cost_weight +
                                      supply_chain_data['Availability'] * availability_weight)

        
        shortest_paths = nx.single_source_dijkstra_path(self.graph, start_supplier, weight='cost')
        shortest_distances = nx.single_source_dijkstra_path_length(self.graph, start_supplier, weight='cost')

        st.write("\nShortest distances, routes, and transportation modes for nodes other than the starting node:")
        for node in shortest_paths:
            if node != start_supplier:
                distance = shortest_distances[node]
                route = shortest_paths[node]
                transport = self.graph.edges[route[0], route[1]]['transport']
                st.write("Location:", node)
                st.write("Shortest distance:", distance)
                st.write("Route:", route)
                st.write("Transportation mode:", transport)
                st.write()

        # nx.write_graphml(self.graph, 'supply_chain_network.graphml')

    def find_max_min(self, values, start, end):
        if start == end:
            return values[start], values[start]

        if end == start + 1:
            return (values[start], values[end]) if values[start] < values[end] else (values[end], values[start])

        mid = (start + end) // 2
        max_left, min_left = self.find_max_min(values, start, mid)
        max_right, min_right = self.find_max_min(values, mid + 1, end)

        max_value = max(max_left, max_right)
        min_value = min(min_left, min_right)

        return max_value, min_value

    def find_max_min_for_supplier(self, data, supplier_name, attribute):
        if supplier_name not in data['Supplier name'].unique():
            st.write(f"Supplier '{supplier_name}' not found in the dataset.")
            return None, None

        supplier_data = data[data['Supplier name'] == supplier_name]

        if attribute not in supplier_data.columns:
            st.write(f"Attribute '{attribute}' not found for supplier '{supplier_name}'.")
            return None, None

        attribute_values = supplier_data[attribute].tolist()

        max_value, min_value = self.find_max_min(attribute_values, 0, len(attribute_values) - 1)

        max_product = supplier_data[supplier_data[attribute] == max_value]
        min_product = supplier_data[supplier_data[attribute] == min_value]

        return max_value, min_value, max_product, min_product

    def send_email_to_industry(self, supplier_name, attribute, threshold):
        supply_chain_data = pd.read_csv('supply_chain_data.csv')
        

        for index, row in supply_chain_data.iterrows():
            avail = row['Availability']

        if supplier_name not in supply_chain_data['Supplier name'].unique():
            st.write(f"Supplier '{supplier_name}' not found in the dataset.")
            return

        supplier_data = supply_chain_data[supply_chain_data['Supplier name'] == supplier_name]

        if attribute not in supplier_data.columns:
            st.write(f"Attribute '{attribute}' not found for supplier '{supplier_name}'.")
            return

        product_avg_availability = supplier_data.groupby('Product type')[attribute].mean()

        low_availability_products = product_avg_availability[product_avg_availability < threshold]

        if not low_availability_products.empty:
            email_content = f"Greetings,\n\nThis is to bring to your kind attention that the availability of products from '{supplier_name}' " \
                            f"is below the threshold ({threshold}).\n\nProducts with low " \
                            f"availability:\n{avail}\n\nRegards,\nSupply chain manager"

            sender_email = "vlekhasri159@gmail.com"
            receiver_email = "shruthijeya7@gmail.com"
            password = "repb czsm cecu tuvp"

            msg = MIMEMultipart()
            msg['From'] = sender_email
            msg['To'] = receiver_email
            msg['Subject'] = "Low Product Availability Alert"

            msg.attach(MIMEText(email_content, 'plain'))

            with smtplib.SMTP('smtp.gmail.com', 587) as smtp_server:
                smtp_server.starttls()
                smtp_server.login(sender_email, password)
                smtp_server.sendmail(sender_email, receiver_email, msg.as_string())

            st.write("Email sent successfully!")
        else:
            st.write(f"No products with availability below the threshold ({threshold}). No email sent.")

    def visualize_data(self):
        # Read supply chain data from CSV
        supply_chain_data = pd.read_csv('supply_chain_data.csv')

        # Plot 1: Distribution of Lead Times
        st.write("Distribution of Lead Times")
        plt.figure(figsize=(8, 6))
        supply_chain_data['Lead times'].plot(kind='hist', bins=20, color='skyblue')
        plt.xlabel('Lead Time')
        plt.ylabel('Frequency')
        plt.title('Distribution of Lead Times')
        st.pyplot(plt)

        # Plot 2: Distribution of Prices
        st.write("Distribution of Prices")
        plt.figure(figsize=(8, 6))
        supply_chain_data['Price'].plot(kind='hist', bins=20, color='orange')
        plt.xlabel('Price')
        plt.ylabel('Frequency')
        plt.title('Distribution of Prices')
        st.pyplot(plt)

        # Plot 3: Scatter plot of Price vs Availability
        st.write("Scatter plot of Price vs Availability")
        plt.figure(figsize=(8, 6))
        plt.scatter(supply_chain_data['Price'], supply_chain_data['Availability'], color='green')
        plt.xlabel('Price')
        plt.ylabel('Availability')
        plt.title('Scatter plot of Price vs Availability')
        st.pyplot(plt)

        # Plot 4: Bar chart of Product Counts by Supplier
        st.write("Bar chart of Product Counts by Supplier")
        supplier_counts = supply_chain_data['Supplier name'].value_counts()
        plt.figure(figsize=(10, 6))
        supplier_counts.plot(kind='bar', color='purple')
        plt.xlabel('Supplier Name')
        plt.ylabel('Number of Products')
        plt.title('Number of Products by Supplier')
        plt.xticks(rotation=45)
        st.pyplot(plt)


supply_chain = SupplyChain()

# Sidebar layout
#st.sidebar.title("Supply Chain Analysis")

# Center-align the title
st.markdown("<h1 style='text-align: center;'>Supply Chain Analysis</h1><br><br>", unsafe_allow_html=True)

# Sidebar features
feature = st.sidebar.selectbox("Select Feature", ["Find Top Supplied product of the supplier", "Find Shortest Distance", "Find Min and Max", "Send Email", "Visualization"])

if feature == "Find Top Supplied product of the supplier":
    input_supplier = st.text_input("Enter the supplier name:")
    if st.button("Find"):
        supply_chain.top_supplier(input_supplier)

elif feature == "Find Shortest Distance":
    input_supplier = st.text_input("Enter the supplier name:")
    if st.button("Find Shortest Distance"):
        supply_chain.shortest_dist(input_supplier)

elif feature == "Find Min and Max":
    input_supplier = st.text_input("Enter the supplier name:")
    attribute = st.text_input("Enter the attribute for analysis (e.g., Price, Availability, Revenue generated):")
    if st.button("Find Min and Max"):
        max_value, min_value, max_product, min_product = supply_chain.find_max_min_for_supplier(
            pd.read_csv('supply_chain_data.csv'), input_supplier, attribute)

        st.write(f"\nMaximum value for '{attribute}' for supplier '{input_supplier}': {max_value}")
        st.write(f"Minimum value for '{attribute}' for supplier '{input_supplier}': {min_value}")

        if max_product is not None:
            st.write("\nProduct(s) with maximum value:")
            st.write(max_product)

        if min_product is not None:
            st.write("\nProduct(s) with minimum value:")
            st.write(min_product)

elif feature == "Send Email":
    input_supplier = st.text_input("Enter the supplier name:")
    threshold = st.number_input("Enter the threshold for availability:", value=0.0)
    if st.button("Send Email"):
        supply_chain.send_email_to_industry(input_supplier, 'Availability', threshold)

elif feature == "Visualization":
    supply_chain.visualize_data()
