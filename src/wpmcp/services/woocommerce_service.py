"""WooCommerce domain: products, orders, customers, coupons, reports."""

from __future__ import annotations

from typing import Any

from wpmcp.domain.enums import View
from wpmcp.domain.models import WpResult
from wpmcp.services.base import BaseDomainService
from wpmcp.wordpress.client import WordPressClient

_WC = "/wc/v3"


class WooCommerceService(BaseDomainService):
    domain = "woocommerce"

    def _register(self) -> None:
        reg = self.add

        async def is_active(c: WordPressClient, site: str, p: dict[str, Any]) -> WpResult:
            data = await c.plugin("/woocommerce/active")
            return WpResult.success(action="is_active", domain="woocommerce", site=site, view=View.OPERATION, data=data)

        async def get_products(c: WordPressClient, site: str, p: dict[str, Any]) -> WpResult:
            params = {k: p[k] for k in ("search", "per_page", "page", "sku") if k in p}
            data = await c.get(_WC + "/products", params=params or None)
            return WpResult.success(action="get_products", domain="woocommerce", site=site, view=View.WC_PRODUCTS, data=data, meta={"count": len(data) if isinstance(data, list) else 0})

        async def create_product(c: WordPressClient, site: str, p: dict[str, Any]) -> WpResult:
            body = {"name": p.get("name", ""), "type": p.get("type", "simple"), "regular_price": str(p.get("regular_price", "0"))}
            data = await c.post(_WC + "/products", body)
            return WpResult.success(action="create_product", domain="woocommerce", site=site, view=View.OPERATION, data=data, message="Product created.")

        async def update_product(c: WordPressClient, site: str, p: dict[str, Any]) -> WpResult:
            body = {k: p[k] for k in ("name", "regular_price", "stock_quantity", "status", "manage_stock") if k in p}
            data = await c.post(f"{_WC}/products/{p.get('id')}", body)
            return WpResult.success(action="update_product", domain="woocommerce", site=site, view=View.OPERATION, data=data, message="Product updated.")

        async def delete_product(c: WordPressClient, site: str, p: dict[str, Any]) -> WpResult:
            data = await c.delete(f"{_WC}/products/{p.get('id')}", params={"force": "true"})
            return WpResult.success(action="delete_product", domain="woocommerce", site=site, view=View.OPERATION, data=data, message="Product deleted.")

        async def get_orders(c: WordPressClient, site: str, p: dict[str, Any]) -> WpResult:
            params = {k: p[k] for k in ("status", "per_page", "page", "customer") if k in p}
            data = await c.get(_WC + "/orders", params=params or None)
            return WpResult.success(action="get_orders", domain="woocommerce", site=site, view=View.WC_ORDERS, data=data, meta={"count": len(data) if isinstance(data, list) else 0})

        async def update_order_status(c: WordPressClient, site: str, p: dict[str, Any]) -> WpResult:
            data = await c.post(f"{_WC}/orders/{p.get('id')}", {"status": p.get("status", "")})
            return WpResult.success(action="update_order_status", domain="woocommerce", site=site, view=View.OPERATION, data=data, message="Order status updated.")

        async def get_customers(c: WordPressClient, site: str, p: dict[str, Any]) -> WpResult:
            data = await c.get(_WC + "/customers", params={"search": p.get("search")} if p.get("search") else None)
            return WpResult.success(action="get_customers", domain="woocommerce", site=site, view=View.WC_CUSTOMERS, data=data, meta={"count": len(data) if isinstance(data, list) else 0})

        async def update_stock(c: WordPressClient, site: str, p: dict[str, Any]) -> WpResult:
            data = await c.post(f"{_WC}/products/{p.get('id')}", {"stock_quantity": int(p.get("quantity", 0)), "manage_stock": True})
            return WpResult.success(action="update_stock", domain="woocommerce", site=site, view=View.OPERATION, data=data, message="Stock updated.")

        async def get_coupons(c: WordPressClient, site: str, p: dict[str, Any]) -> WpResult:
            data = await c.get(_WC + "/coupons")
            return WpResult.success(action="get_coupons", domain="woocommerce", site=site, view=View.WC_COUPONS, data=data, meta={"count": len(data) if isinstance(data, list) else 0})

        async def create_coupon(c: WordPressClient, site: str, p: dict[str, Any]) -> WpResult:
            body = {"code": p.get("code", ""), "amount": str(p.get("amount", "0")), "discount_type": p.get("type", "percent")}
            data = await c.post(_WC + "/coupons", body)
            return WpResult.success(action="create_coupon", domain="woocommerce", site=site, view=View.OPERATION, data=data, message="Coupon created.")

        async def get_sales_report(c: WordPressClient, site: str, p: dict[str, Any]) -> WpResult:
            data = await c.get(_WC + "/reports/sales", params={"period": p.get("period", "month")} if p.get("period") else None)
            return WpResult.success(action="get_sales_report", domain="woocommerce", site=site, view=View.WC_REPORT, data=data)

        async def get_top_sellers(c: WordPressClient, site: str, p: dict[str, Any]) -> WpResult:
            data = await c.get(_WC + "/reports/products/top-sellers")
            return WpResult.success(action="get_top_sellers", domain="woocommerce", site=site, view=View.WC_REPORT, data=data)

        async def get_payment_gateways(c: WordPressClient, site: str, p: dict[str, Any]) -> WpResult:
            data = await c.get(_WC + "/payment_gateways")
            return WpResult.success(action="get_payment_gateways", domain="woocommerce", site=site, view=View.OPERATION, data=data)

        async def get_shipping_zones(c: WordPressClient, site: str, p: dict[str, Any]) -> WpResult:
            data = await c.get(_WC + "/shipping/zones")
            return WpResult.success(action="get_shipping_zones", domain="woocommerce", site=site, view=View.OPERATION, data=data)

        async def get_product_categories(c: WordPressClient, site: str, p: dict[str, Any]) -> WpResult:
            data = await c.get(_WC + "/products/categories")
            return WpResult.success(action="get_product_categories", domain="woocommerce", site=site, view=View.TERMS, data=data, meta={"count": len(data) if isinstance(data, list) else 0})

        reg("is_active", "Check if WooCommerce is active.", is_active)
        reg("get_products", "List products.", get_products, params={"search": "str?", "per_page": "int?"})
        reg("create_product", "Create a product.", create_product, params={"name": "str", "type": "str?", "regular_price": "str"}, read_only=False)
        reg("update_product", "Update a product.", update_product, params={"id": "int", "name": "str?", "regular_price": "str?", "stock_quantity": "int?"}, read_only=False)
        reg("delete_product", "Delete a product.", delete_product, params={"id": "int"}, destructive=True, read_only=False)
        reg("get_orders", "List orders.", get_orders, params={"status": "str?", "per_page": "int?"})
        reg("update_order_status", "Update an order's status.", update_order_status, params={"id": "int", "status": "str"}, read_only=False)
        reg("get_customers", "List customers.", get_customers, params={"search": "str?"})
        reg("update_stock", "Update product stock.", update_stock, params={"id": "int", "quantity": "int"}, read_only=False)
        reg("get_coupons", "List coupons.", get_coupons)
        reg("create_coupon", "Create a coupon.", create_coupon, params={"code": "str", "amount": "str", "type": "str?"}, read_only=False)
        reg("get_sales_report", "Get a sales report.", get_sales_report, params={"period": "str?"})
        reg("get_top_sellers", "Get top-selling products.", get_top_sellers)
        reg("get_payment_gateways", "List payment gateways.", get_payment_gateways)
        reg("get_shipping_zones", "List shipping zones.", get_shipping_zones)
        reg("get_product_categories", "List product categories.", get_product_categories)
