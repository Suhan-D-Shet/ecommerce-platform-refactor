# E-Commerce API Endpoints Documentation

## Base URL
```
http://localhost:8000
```

## Authentication
All protected endpoints require an Authorization header:
```
Authorization: Bearer <your_jwt_token>
```

---

## Authentication Endpoints

### Register User
- **POST** `/auth/register`
- **Body:**
  ```json
  {
    "email": "user@example.com",
    "username": "johndoe",
    "password": "password123"
  }
  ```
- **Response:** `TokenResponse` with access_token and user data

### Login
- **POST** `/auth/login`
- **Body:**
  ```json
  {
    "email": "user@example.com",
    "password": "password123"
  }
  ```
- **Response:** `TokenResponse` with access_token and user data

---

## Category Endpoints

### Get All Categories
- **GET** `/categories`
- **Response:** List of categories

### Create Category
- **POST** `/categories`
- **Body:**
  ```json
  {
    "name": "Electronics",
    "description": "Electronic devices"
  }
  ```
- **Response:** Category object

### Get Category by ID
- **GET** `/categories/{category_id}`
- **Response:** Category object

---

## Product Endpoints

### Get Products (with filters)
- **GET** `/products?categoryId=1&minPrice=10&maxPrice=100&q=headphones&skip=0&limit=10`
- **Query Parameters:**
  - `categoryId`: (optional) Filter by category
  - `minPrice`: (optional) Minimum price
  - `maxPrice`: (optional) Maximum price
  - `q`: (optional) Search query
  - `skip`: (default: 0) Pagination offset
  - `limit`: (default: 10, max: 100) Results per page
- **Response:** List of products

### Create Product
- **POST** `/products`
- **Body:**
  ```json
  {
    "name": "Wireless Mouse",
    "description": "Ergonomic wireless mouse",
    "price": 29.99,
    "stock": 50,
    "weight": 0.15,
    "category_id": 1
  }
  ```
- **Response:** Product object

### Get Product by ID
- **GET** `/products/{product_id}`
- **Response:** Product object

### Get Product Reviews
- **GET** `/products/{product_id}/reviews`
- **Response:** List of review objects

### Update Product
- **PUT** `/products/{product_id}`
- **Body:** (all fields optional)
  ```json
  {
    "name": "Updated Name",
    "price": 39.99,
    "stock": 100
  }
  ```
- **Response:** Updated product object

---

## Cart Endpoints

### Get Cart
- **GET** `/cart?userId={user_id}`
- **Response:** CartResponse with items array and total

### Add to Cart
- **POST** `/cart`
- **Headers:** `Authorization: Bearer <token>`
- **Body:**
  ```json
  {
    "product_id": 1,
    "quantity": 2
  }
  ```
- **Response:** CartItemResponse

### Update Cart Item
- **PUT** `/cart/{cart_item_id}`
- **Headers:** `Authorization: Bearer <token>`
- **Body:**
  ```json
  {
    "quantity": 5
  }
  ```
- **Response:** CartItemResponse

### Remove from Cart
- **DELETE** `/cart/{cart_item_id}`
- **Headers:** `Authorization: Bearer <token>`
- **Response:** 204 No Content

### Clear Cart
- **DELETE** `/cart?user_id={user_id}`
- **Headers:** `Authorization: Bearer <token>`
- **Response:** 204 No Content

---

## Order Endpoints

### Checkout
- **POST** `/orders/checkout`
- **Headers:** `Authorization: Bearer <token>`
- **Body:**
  ```json
  {
    "shipping_address": "123 Main St, City, State 12345",
    "coupon_code": "SUMMER20"
  }
  ```
- **Response:** OrderResponse with order details

### Get User Orders
- **GET** `/orders?user_id={user_id}&skip=0&limit=10`
- **Headers:** `Authorization: Bearer <token>`
- **Response:** List of Order objects

### Get Order by ID
- **GET** `/orders/{order_id}`
- **Headers:** `Authorization: Bearer <token>`
- **Response:** Order object

### Update Order Status
- **PUT** `/orders/{order_id}/status`
- **Headers:** `Authorization: Bearer <token>`
- **Body:**
  ```json
  {
    "status": "shipped"
  }
  ```
- **Response:** Order object

---

## Review Endpoints

### Create Review
- **POST** `/products/{product_id}/reviews`
- **Headers:** `Authorization: Bearer <token>`
- **Body:**
  ```json
  {
    "rating": 5,
    "comment": "Excellent product, highly recommended!"
  }
  ```
- **Response:** ReviewResponse

### Get Product Reviews
- **GET** `/products/{product_id}/reviews`
- **Response:** List of ReviewResponse

### Update Review
- **PUT** `/products/{product_id}/reviews/{review_id}`
- **Headers:** `Authorization: Bearer <token>`
- **Body:**
  ```json
  {
    "rating": 4,
    "comment": "Updated comment"
  }
  ```
- **Response:** ReviewResponse

### Delete Review
- **DELETE** `/products/{product_id}/reviews/{review_id}`
- **Headers:** `Authorization: Bearer <token>`
- **Response:** 204 No Content

---

## Coupon Endpoints

### Create Coupon
- **POST** `/coupons`
- **Headers:** `Authorization: Bearer <token>`
- **Body:**
  ```json
  {
    "code": "SUMMER20",
    "discount_percentage": 20,
    "max_uses": 100,
    "expiry_date": "2025-08-31T23:59:59"
  }
  ```
- **Response:** CouponResponse

### Validate Coupon
- **POST** `/coupons/validate?code=SUMMER20`
- **Response:** CouponResponse or error

### Get Coupon
- **GET** `/coupons/{coupon_id}`
- **Response:** CouponResponse

---

## Shipping Endpoints

### Calculate Shipping
- **POST** `/shipping/calculate`
- **Body:**
  ```json
  {
    "address": "123 Main St, City, State 12345",
    "total_weight": 2.5,
    "total_amount": 150.00
  }
  ```
- **Response:**
  ```json
  {
    "shipping_cost": 10.0,
    "estimated_days": 3,
    "method": "Standard Shipping"
  }
  ```

---

## Error Responses

### 400 Bad Request
```json
{
  "detail": "Invalid input or validation error"
}
```

### 401 Unauthorized
```json
{
  "detail": "Invalid or missing authentication token"
}
```

### 403 Forbidden
```json
{
  "detail": "Not authorized to perform this action"
}
```

### 404 Not Found
```json
{
  "detail": "Resource not found"
}
```

### 500 Internal Server Error
```json
{
  "detail": "Internal server error"
}
