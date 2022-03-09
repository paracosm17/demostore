from django.contrib import admin
from store.models import TgUser, Category, Product, Purchase, Basket

class PurchaseAdminInline(admin.TabularInline):
    '''
    Class for viewing user's purchases on the user's page
    '''
    model = Purchase
    fields = ('product', 'quantity', 'get_total_sum', 'status', 'added')
    list_display = ('product', 'quantity', 'get_total_sum', 'status', 'added')
    readonly_fields = ('product', 'quantity', 'get_total_sum', 'added')
    extra = 0
    
    def get_total_sum(self, obj) -> float:
        # Function to get total purchase amount
        return obj.quantity * obj.product.price
    get_total_sum.short_description = "Общая сумма покупки"

class BasketAdminInline(admin.TabularInline):
    '''
    Class for viewing user's purchases on the user's page
    '''
    model = Basket
    fields = ('product', 'quantity', 'get_total_sum', 'added')
    list_display = ('product', 'quantity', 'get_total_sum', 'added')
    readonly_fields = ('product', 'quantity', 'get_total_sum', 'added')
    extra = 0
    
    def get_total_sum(self, obj) -> float:
        user_id = TgUser.objects.get(id=obj.buyer.id)
        prices_list = [p.product.price for p in Basket.objects.get(buyer=user_id)]
        return sum(prices_list)
    get_total_sum.short_description = "Общая сумма корзины"

class ProductAdminInline(admin.TabularInline):
    '''
    Class for viewing products on the category's page
    '''
    model = Product
    fields = ('id', 'name', 'price', 'quantity', 'image_view')
    list_display = ('id', 'name', 'price', 'quantity', 'image_view')
    readonly_fields = ('id', 'name', 'price', 'quantity', 'image_view')
    extra = 0

class TgUserAdmin(admin.ModelAdmin):
    '''
    Class for the Model TgUser
    '''
    fields = ('id', 'user_id', 'first_name', 'username', 'last_name', 'balance', 'phone', 'email', 'language_code', 'added')
    list_display = ('id', 'user_id', 'first_name', 'username', 'last_name', 'balance', 'phone', 'email', 'language_code', 'added')
    readonly_fields = ('id', 'added')
    list_display_links = ('id', 'user_id', 'first_name')
    inlines = (PurchaseAdminInline, BasketAdminInline)
    ordering = ('id', 'added')
    search_fields = ('id', 'user_id', 'first_name', 'username', 'last_name', 'balance', 'phone', 'email', 'language_code', 'added')

class CategoryAdmin(admin.ModelAdmin):
    '''
    Class for the model Category
    '''
    fields = ('id', 'name')
    readonly_fields = ('id', )
    list_display = ('id', 'name', 'get_products')
    list_display_links = ('id', 'name')
    inlines = (ProductAdminInline, )
    ordering = ('id', 'name')
    search_fields = ('id', 'name')

    def get_products(self, obj) -> str:
        # Function to get category's products
        category_id = obj.id
        products = Product.objects.filter(category__id=category_id)
        return ", ".join([p.name for p in products])
    get_products.short_description = "Список товаров" 

class ProductAdmin(admin.ModelAdmin):
    '''
    Class for the model Product
    '''
    fields = ('id', 'name', 'price', 'quantity', 'category', ('image', 'full_image'), 'added')
    list_display = ('id', 'name', 'image_view', 'price', 'quantity', 'category', 'added')
    list_display_links = ('id', 'name', 'image_view')
    readonly_fields = ('id', 'image_view', 'added', 'full_image')
    ordering = ('id', 'name', 'price', 'quantity', 'category')
    search_fields = ('name', 'description', 'price')

class PurchaseAdmin(admin.ModelAdmin):
    def sum(self, obj) -> float:
        return obj.quantity * obj.product.price
    sum.short_description = "Общая сумма покупки"
    
    list_display = ('buyer', 'product', 'quantity', 'sum', 'status', 'added')

admin.site.register(TgUser, TgUserAdmin)
admin.site.register(Product, ProductAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(Purchase, PurchaseAdmin)
