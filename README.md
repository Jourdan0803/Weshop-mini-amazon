# WeShop - Mini Amazon

## Description

This server can be linked with two other servers to simulate an online shopping center in the real world. In this project, you can play the role of both sellers and customers. All requests are integrated with the warehouse and UPS to ensure efficient delivery. The functionalities include:

### User Roles:

Sellers: Can list products, manage inventory, and process orders.
Customers: Can browse products, add items to their cart, and place orders.

### Product Management:

Listing Products: Sellers can add new products with details such as name, description, price, and images.
Inventory Management: Sellers can update stock levels and receive notifications for low stock.
Product Search: Customers can search for products by category, name, or other filters.

### Order Management:

Cart System: Customers can add items to their cart and proceed to checkout.
Order Placement: Customers can place orders, choose delivery options, and make payments.
Order Tracking: Customers can track the status of their orders in real-time.

### Warehouse Integration:

Stock Updates: Automated synchronization of stock levels between the warehouse and the online system.
Order Fulfillment: Warehouse receives order details for picking, packing, and shipping.

### UPS Integration:

Shipping Calculation: Automatic calculation of shipping costs based on the delivery address and package weight.
Shipping Labels: Generation of shipping labels for each order.
Delivery Tracking: Real-time tracking information provided to customers through their account.

### User Accounts:

Registration and Login: Secure user authentication for both sellers and customers.
Profile Management: Users can update their personal information, addresses, and payment methods.

### Notifications:

Shipping Updates: Customers receive notifications about shipping status and delivery estimates.
Promotional Offers: Sellers can send promotional emails and offers to customers.

### Payment Processing:

Secure Payments: Integration with payment gateways for secure transactions.

By integrating these functionalities, the system provides a comprehensive simulation of an online shopping center, ensuring a seamless experience for both sellers and customers.

## Demo

TBD by JingxuanLi

## Usage Instruction

This project is implemented in Docker, so you can use it in an easy way. 

If you did not install docker before, please use 
```
sudo apt-get install docker-compose
```
to install Docker for the following usage.

Now, you can run this server by following:

```
git clone git@github.com:MorganeLu/WeShop-MiniAmazon.git
cd WeShop-MiniAmazo
sudo docker-compose up
```

Just wait for a second, you can see visit our website by localhost:8000.

## Connections and Communication

As we mentioned before, this server can be linked with other servers and the protocol we used can be found at final_proto.pdf file. The following image shows our workflow.

<img src=".\src\workflow.png">  