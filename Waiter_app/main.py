# main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import (
    auth, menus, orders, users, admin, health, tables, images,
    simple_login, order_status, promocoes, pizzas
)

app = FastAPI()

# Allow frontend connections (adjust origins in production)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include all routers
app.include_router(auth.router, prefix="/api/auth")
app.include_router(menus.router, prefix="/api/menus")
app.include_router(orders.router, prefix="/api/orders")
app.include_router(users.router, prefix="/api/users")
app.include_router(admin.router, prefix="/api/admin")
app.include_router(health.router, prefix="/api/health")  # Fixed this line
app.include_router(tables.router, prefix="/api/tables")
app.include_router(simple_login.router, prefix="/api/")
app.include_router(images.router, prefix="/api/images")
app.include_router(order_status.router, prefix="/api/order_status")
app.include_router(promocoes.router, prefix="/api/promos")
app.include_router(pizzas.router, prefix="/api/pizzas")

# User roles: admin, waiter, customer, motoboy
