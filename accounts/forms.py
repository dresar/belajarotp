from django import forms
from .models import CustomUser, PPTRegistration


class RegistrationForm(forms.Form):
    """Form untuk registrasi user baru"""
    email = forms.EmailField(
        label='Email',
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Masukkan email Anda',
            'required': True,
        })
    )
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if CustomUser.objects.filter(email=email).exists():
            raise forms.ValidationError('Email ini sudah terdaftar. Silakan gunakan email lain atau login.')
        return email


class LoginForm(forms.Form):
    """Form untuk login user"""
    email = forms.EmailField(
        label='Email',
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Masukkan email Anda',
            'required': True,
        })
    )
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if not CustomUser.objects.filter(email=email).exists():
            raise forms.ValidationError('Email tidak terdaftar. Silakan registrasi terlebih dahulu.')
        return email


class OTPVerificationForm(forms.Form):
    """Form untuk verifikasi OTP"""
    otp_code = forms.CharField(
        label='Kode OTP',
        max_length=6,
        min_length=6,
        widget=forms.TextInput(attrs={
            'class': 'form-control text-center',
            'placeholder': '000000',
            'maxlength': '6',
            'pattern': '[0-9]{6}',
            'required': True,
        })
    )
    
    def clean_otp_code(self):
        otp_code = self.cleaned_data.get('otp_code')
        if not otp_code.isdigit():
            raise forms.ValidationError('Kode OTP harus berupa 6 digit angka.')
        return otp_code


class PPTRegistrationForm(forms.ModelForm):
    """Form untuk pendaftaran pembelian PPT"""
    class Meta:
        model = PPTRegistration
        fields = ['email', 'nama', 'no_hp', 'paket_ppt', 'catatan']
        widgets = {
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'contoh@email.com',
                'required': True,
            }),
            'nama': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nama Lengkap Anda',
                'required': True,
            }),
            'no_hp': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '081234567890',
            }),
            'paket_ppt': forms.Select(attrs={
                'class': 'form-select',
                'required': True,
            }),
            'catatan': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Catatan tambahan (opsional)',
            }),
        }
        labels = {
            'email': 'Email',
            'nama': 'Nama Lengkap',
            'no_hp': 'No. HP/WhatsApp',
            'paket_ppt': 'Pilih Paket PPT',
            'catatan': 'Catatan',
        }


class ForgotPasswordForm(forms.Form):
    """Form untuk lupa password"""
    email = forms.EmailField(
        label='Email',
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Masukkan email Anda',
            'required': True,
        })
    )
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if not CustomUser.objects.filter(email=email).exists():
            raise forms.ValidationError('Email tidak terdaftar.')
        return email


class ResetPasswordForm(forms.Form):
    """Form untuk reset password"""
    new_password = forms.CharField(
        label='Password Baru',
        min_length=8,
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Masukkan password baru (minimal 8 karakter)',
            'required': True,
        })
    )
    
    confirm_password = forms.CharField(
        label='Konfirmasi Password',
        min_length=8,
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Konfirmasi password baru',
            'required': True,
        })
    )
    
    def clean(self):
        cleaned_data = super().clean()
        new_password = cleaned_data.get('new_password')
        confirm_password = cleaned_data.get('confirm_password')
        
        if new_password and confirm_password:
            if new_password != confirm_password:
                raise forms.ValidationError('Password dan konfirmasi password tidak sama.')
        
        return cleaned_data


class MassEmailForm(forms.Form):
    """Form untuk kirim email massal"""
    subject = forms.CharField(
        label='Subject Email',
        max_length=200,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Subject email Anda',
            'required': True,
        })
    )
    
    message = forms.CharField(
        label='Isi Pesan',
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 10,
            'placeholder': 'Tulis pesan email Anda di sini...',
            'required': True,
        })
    )
    
    recipient_type = forms.ChoiceField(
        label='Kirim Ke',
        choices=[
            ('all', 'Semua Pendaftar'),
            ('pending', 'Status: Menunggu Konfirmasi'),
            ('confirmed', 'Status: Terkonfirmasi'),
            ('paid', 'Status: Sudah Dibayar'),
            ('completed', 'Status: Selesai'),
        ],
        widget=forms.Select(attrs={
            'class': 'form-select',
            'required': True,
        })
    )

