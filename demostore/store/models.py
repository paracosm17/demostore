from django.core.validators import validate_email
from django.db import models
from django.utils.safestring import mark_safe
from phonenumber_field.modelfields import PhoneNumberField


class TgUser(models.Model):
    user_id = models.BigIntegerField(unique=True, blank=False, verbose_name='Telegram id')
    first_name = models.CharField(max_length=64, blank=False, verbose_name='Имя')
    last_name = models.CharField(max_length=64, blank=True, default='', verbose_name='Фамилия')
    username = models.CharField(max_length=32, blank=True, default='', verbose_name='Юзернейм')
    balance = models.DecimalField(max_digits=20, decimal_places=2, default=0, blank=False, verbose_name='Баланс')
    language_code = models.CharField(max_length=8, blank=True, verbose_name='Код языка')
    phone = PhoneNumberField(blank=True, null=True, verbose_name='Номер')
    email = models.EmailField(verbose_name='Почта', blank=True, validators=[validate_email])
    added = models.DateTimeField(auto_now_add=True, verbose_name='Добавлен')

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self) -> str:
        return f'{self.id}. {self.first_name} (id{self.user_id})'


class Category(models.Model):
    name = models.CharField(max_length=32, blank=False, unique=True, verbose_name='Категория')

    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'

    def __str__(self) -> str:
        return self.name


class Product(models.Model):
    name = models.CharField(max_length=64, blank=False, verbose_name='Название')
    category = models.ForeignKey(Category, on_delete=models.PROTECT, verbose_name='Категория')
    description = models.TextField(max_length=4000, blank=True, verbose_name='Описание')
    image = models.ImageField(upload_to='products', default='products/default.jpg', blank=False,
                              verbose_name='Картинка')
    price = models.DecimalField(max_digits=16, decimal_places=2, blank=False, verbose_name='Цена')
    quantity = models.PositiveIntegerField(blank=True, default=0, verbose_name='Количество')
    added = models.DateTimeField(auto_now_add=True, verbose_name='Добавлен')

    def image_view(self):
        return mark_safe('<img src="%s" width="50" height="50" />' % self.image.url)

    image_view.short_description = 'Картинка'

    def full_image(self):
        return mark_safe('<img src="%s"/>' % self.image.url)

    full_image.short_description = ''

    class Meta:
        verbose_name = 'Товар'
        verbose_name_plural = 'Товары'

    def __str__(self) -> str:
        return f'{self.name} ({self.category.name})'


class Purchase(models.Model):
    buyer = models.ForeignKey(TgUser, on_delete=models.PROTECT, verbose_name='Покупатель')
    product = models.ForeignKey(Product, on_delete=models.PROTECT, verbose_name='Товар')
    quantity = models.IntegerField(blank=True, verbose_name='Количество')
    status = models.BooleanField(default=False, verbose_name='Оплачено')
    added = models.DateTimeField(auto_now_add=True, verbose_name='Добавлен')

    class Meta:
        verbose_name = 'Покупка'
        verbose_name_plural = 'Покупки'

    def __str__(self) -> str:
        return self.buyer.__str__() + ' | ' + self.product.__str__() + ' ' + f'({self.quantity})'


class Appeal(models.Model):
    user = models.ForeignKey(TgUser, on_delete=models.PROTECT, verbose_name='Пользователь')
    text = models.TextField(blank=False, verbose_name='Текст обращения')
    viewed = models.BooleanField(default=False, verbose_name='Просмотрено')
    status = models.BooleanField(default=False, verbose_name='Закрыто')
    added = models.DateTimeField(auto_now_add=True, verbose_name='Добавлено')

    class Meta:
        verbose_name = 'Обращение в тех. поддержку'
        verbose_name_plural = 'Обращения в тех. поддержку'

    def __str__(self) -> str:
        return f'{self.user} | Обращение от {self.added}'
