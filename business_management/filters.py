import django_filters
from .models import Business

class BusinessFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(lookup_expr="icontains")  
    owner = django_filters.CharFilter(lookup_expr="icontains") 

    class Meta:
        model = Business
        fields = ["name", "owner__first_name", "owner__last_name"]
