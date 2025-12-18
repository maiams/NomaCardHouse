from rest_framework.decorators import api_view

from apps.core.exceptions import api_response


@api_view(["GET"])
def api_root(request):
    """
    Return a helpful landing response for the API root.
    """
    base_api_url = request.build_absolute_uri("/api/v1/")

    return api_response(
        data={
            "name": "Noma Card House API",
            "api_base": base_api_url,
            "admin": request.build_absolute_uri("/admin/"),
            "endpoints": {
                "products": request.build_absolute_uri("/api/v1/products/"),
                "skus": request.build_absolute_uri("/api/v1/products/skus/"),
                "cart": request.build_absolute_uri("/api/v1/cart/"),
                "orders": request.build_absolute_uri("/api/v1/orders/"),
                "payments_webhook": request.build_absolute_uri(
                    "/api/v1/payments/webhook/"
                ),
            },
        },
        message="Welcome to the Noma Card House API. Use the links below to explore available endpoints.",
    )
