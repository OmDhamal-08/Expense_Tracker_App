from rest_framework import generics, permissions, filters
from django.db.models import Q
from core.models import Category, PaymentMethod
from api.serializers import CategorySerializer, PaymentMethodSerializer


class CategoryListCreateView(generics.ListCreateAPIView):
    """GET /api/categories/ — list (user + predefined) | POST — create."""
    serializer_class = CategorySerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.SearchFilter]
    search_fields = ['name']

    def get_queryset(self):
        qs = Category.objects.filter(
            Q(user=self.request.user) | Q(user__isnull=True),
            is_active=True,
        )
        cat_type = self.request.query_params.get('type')
        if cat_type:
            qs = qs.filter(type=cat_type)
        return qs


class CategoryDetailView(generics.RetrieveUpdateDestroyAPIView):
    """GET/PUT/PATCH/DELETE /api/categories/<id>/"""
    serializer_class = CategorySerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Category.objects.filter(
            Q(user=self.request.user) | Q(user__isnull=True)
        )


class PaymentMethodListCreateView(generics.ListCreateAPIView):
    """GET /api/payment-methods/ | POST — create."""
    serializer_class = PaymentMethodSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return PaymentMethod.objects.filter(
            Q(user=self.request.user) | Q(user__isnull=True),
            is_active=True,
        )


class PaymentMethodDetailView(generics.RetrieveUpdateDestroyAPIView):
    """GET/PUT/PATCH/DELETE /api/payment-methods/<id>/"""
    serializer_class = PaymentMethodSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return PaymentMethod.objects.filter(
            Q(user=self.request.user) | Q(user__isnull=True)
        )

