from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.utils import timezone
from datetime import timedelta
import random
import secrets


class CustomUserManager(BaseUserManager):
    """Manager untuk CustomUser dengan email sebagai username"""
    
    def create_user(self, email, password=None, **extra_fields):
        """Membuat dan menyimpan user dengan email"""
        if not email:
            raise ValueError('Email harus diisi')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_superuser(self, email, password=None, **extra_fields):
        """Membuat dan menyimpan superuser"""
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        
        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser harus memiliki is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser harus memiliki is_superuser=True.')
        
        return self.create_user(email, password, **extra_fields)


class CustomUser(AbstractBaseUser):
    """Custom User Model dengan email sebagai username"""
    email = models.EmailField(unique=True, verbose_name='Email')
    is_active = models.BooleanField(default=False, verbose_name='Aktif')
    is_staff = models.BooleanField(default=False, verbose_name='Staff')
    is_superuser = models.BooleanField(default=False, verbose_name='Superuser')
    date_joined = models.DateTimeField(auto_now_add=True, verbose_name='Tanggal Bergabung')
    last_login = models.DateTimeField(null=True, blank=True, verbose_name='Login Terakhir')
    
    objects = CustomUserManager()
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []
    
    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'
    
    def __str__(self):
        return self.email
    
    def has_perm(self, perm, obj=None):
        return self.is_superuser
    
    def has_module_perms(self, app_label):
        return self.is_superuser


class OTP(models.Model):
    """Model untuk menyimpan OTP code"""
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='otps', verbose_name='User')
    otp_code = models.CharField(max_length=6, verbose_name='Kode OTP')
    verification_token = models.CharField(max_length=64, unique=True, null=True, blank=True, verbose_name='Token Verifikasi')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Dibuat Pada')
    is_used = models.BooleanField(default=False, verbose_name='Sudah Digunakan')
    purpose = models.CharField(
        max_length=20,
        choices=[
            ('registration', 'Registrasi'),
            ('login', 'Login'),
            ('password_reset', 'Reset Password'),
        ],
        default='login',
        verbose_name='Tujuan'
    )
    
    class Meta:
        verbose_name = 'OTP'
        verbose_name_plural = 'OTPs'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.email} - {self.otp_code}"
    
    def is_expired(self):
        """Cek apakah OTP sudah expired (lebih dari 5 menit)"""
        expiration_time = self.created_at + timedelta(minutes=5)
        return timezone.now() > expiration_time
    
    def is_valid(self):
        """Cek apakah OTP masih valid (belum digunakan dan belum expired)"""
        return not self.is_used and not self.is_expired()
    
    @staticmethod
    def generate_otp():
        """Generate 6 digit random OTP"""
        return str(random.randint(100000, 999999))
    
    @staticmethod
    def generate_token():
        """Generate token untuk verifikasi via link"""
        return secrets.token_urlsafe(32)


class PPTRegistration(models.Model):
    """Model untuk pendaftaran pembelian PPT"""
    email = models.EmailField(verbose_name='Email')
    nama = models.CharField(max_length=100, verbose_name='Nama Lengkap')
    no_hp = models.CharField(max_length=20, verbose_name='No. HP/WhatsApp', blank=True)
    paket_ppt = models.CharField(
        max_length=50,
        choices=[
            ('basic', 'Paket Basic - Rp 50.000'),
            ('premium', 'Paket Premium - Rp 100.000'),
            ('enterprise', 'Paket Enterprise - Rp 200.000'),
        ],
        default='basic',
        verbose_name='Paket PPT'
    )
    catatan = models.TextField(blank=True, verbose_name='Catatan')
    status = models.CharField(
        max_length=20,
        choices=[
            ('pending', 'Menunggu Konfirmasi'),
            ('confirmed', 'Terkonfirmasi'),
            ('paid', 'Sudah Dibayar'),
            ('completed', 'Selesai'),
        ],
        default='pending',
        verbose_name='Status'
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Tanggal Daftar')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Diperbarui')
    
    class Meta:
        verbose_name = 'Pendaftaran PPT'
        verbose_name_plural = 'Pendaftaran PPT'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.nama} - {self.email} - {self.get_paket_ppt_display()}"
    
    def get_harga(self):
        """Mengembalikan harga berdasarkan paket"""
        harga_map = {
            'basic': 50000,
            'premium': 100000,
            'enterprise': 200000,
        }
        return harga_map.get(self.paket_ppt, 0)

