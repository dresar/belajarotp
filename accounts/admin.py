from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import CustomUser, OTP, PPTRegistration


@admin.register(CustomUser)
class CustomUserAdmin(BaseUserAdmin):
    list_display = ('email', 'is_active', 'is_staff', 'date_joined')
    list_filter = ('is_active', 'is_staff', 'is_superuser', 'date_joined')
    search_fields = ('email',)
    ordering = ('email',)
    filter_horizontal = ()  # CustomUser tidak memiliki groups dan user_permissions
    
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2', 'is_staff', 'is_superuser', 'is_active'),
        }),
    )


@admin.register(OTP)
class OTPAdmin(admin.ModelAdmin):
    list_display = ('user', 'otp_code', 'purpose', 'created_at', 'is_used', 'is_expired')
    list_filter = ('purpose', 'is_used', 'created_at')
    search_fields = ('user__email', 'otp_code')
    readonly_fields = ('created_at',)
    
    def is_expired(self, obj):
        return obj.is_expired()
    is_expired.boolean = True
    is_expired.short_description = 'Expired'


@admin.register(PPTRegistration)
class PPTRegistrationAdmin(admin.ModelAdmin):
    list_display = ('nama', 'email', 'paket_ppt', 'get_harga_display', 'status', 'created_at')
    list_filter = ('status', 'paket_ppt', 'created_at')
    search_fields = ('nama', 'email', 'no_hp')
    readonly_fields = ('created_at', 'updated_at')
    list_editable = ('status',)
    
    fieldsets = (
        ('Informasi Pendaftar', {
            'fields': ('nama', 'email', 'no_hp')
        }),
        ('Detail Pembelian', {
            'fields': ('paket_ppt', 'catatan')
        }),
        ('Status', {
            'fields': ('status',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at')
        }),
    )
    
    def get_harga_display(self, obj):
        return f"Rp {obj.get_harga():,}"
    get_harga_display.short_description = 'Harga'

