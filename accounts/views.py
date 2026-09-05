from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.mail import send_mail, send_mass_mail, EmailMultiAlternatives, get_connection
from django.conf import settings
from django.utils import timezone
from django.db.models import Q
from django.template.loader import render_to_string
from django.urls import reverse
from .models import CustomUser, OTP, PPTRegistration
from .forms import RegistrationForm, LoginForm, OTPVerificationForm, PPTRegistrationForm, MassEmailForm, ForgotPasswordForm, ResetPasswordForm


def send_email_safe(msg, request=None):
    """Helper function untuk kirim email dengan fallback ke Console Backend jika SMTP gagal"""
    try:
        msg.send(fail_silently=False)
        return True, None
    except Exception as e:
        # Jika SMTP gagal, coba dengan Console Backend
        if settings.EMAIL_BACKEND != 'django.core.mail.backends.console.EmailBackend':
            try:
                console_connection = get_connection('django.core.mail.backends.console.EmailBackend')
                msg.connection = console_connection
                msg.send(fail_silently=False)
                if request:
                    messages.warning(request, 'Email dikirim ke console/terminal karena SMTP tidak bisa diakses. Cek terminal untuk melihat email dan link verifikasi.')
                return True, 'console'
            except Exception as e2:
                return False, str(e2)
        else:
            return False, str(e)


def register_view(request):
    """View untuk registrasi user baru"""
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            
            # Cek apakah user sudah ada tapi belum aktif
            user, created = CustomUser.objects.get_or_create(email=email)
            
            if created:
                # User baru dibuat
                user.is_active = False
                user.save()
            elif user.is_active:
                # User sudah aktif, redirect ke login
                messages.warning(request, 'Email sudah terdaftar dan aktif. Silakan login.')
                return redirect('login')
            
            # Generate OTP dan Token
            otp_code = OTP.generate_otp()
            verification_token = OTP.generate_token()
            otp_obj = OTP.objects.create(
                user=user,
                otp_code=otp_code,
                verification_token=verification_token,
                purpose='registration'
            )
            
            # Buat link verifikasi
            verification_link = request.build_absolute_uri(
                reverse('verify_otp_token', args=[verification_token])
            )
            
            # Kirim email OTP dengan HTML template
            html_message = render_to_string('accounts/emails/otp_email.html', {
                'otp_code': otp_code,
                'verification_link': verification_link,
                'purpose': 'Registrasi',
                'user': user,
            })
            plain_message = f'''Kode OTP Anda adalah: {otp_code}

Atau klik link berikut untuk verifikasi otomatis:
{verification_link}

Kode ini berlaku selama 5 menit.

Jangan bagikan kode ini kepada siapapun.'''
            
            msg = EmailMultiAlternatives(
                subject='Kode OTP untuk Registrasi',
                body=plain_message,
                from_email=settings.DEFAULT_FROM_EMAIL if hasattr(settings, 'DEFAULT_FROM_EMAIL') else 'noreply@belajarotp.com',
                to=[email],
            )
            msg.attach_alternative(html_message, "text/html")
            success, error_msg = send_email_safe(msg, request)
            
            if not success:
                messages.error(request, f'Gagal mengirim email: {error_msg}. Silakan cek konfigurasi email atau gunakan Console Backend.')
                return redirect('register')
            
            # Simpan email di session untuk verifikasi
            request.session['registration_email'] = email
            if error_msg != 'console':
                messages.success(request, f'Kode OTP telah dikirim ke email {email}. Silakan cek email Anda atau klik link verifikasi di email.')
            return redirect('verify_otp', purpose='registration')
    else:
        form = RegistrationForm()
    
    return render(request, 'accounts/register.html', {'form': form})


def login_view(request):
    """View untuk login user"""
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            
            try:
                user = CustomUser.objects.get(email=email)
                
                if not user.is_active:
                    messages.error(request, 'Akun Anda belum aktif. Silakan verifikasi email terlebih dahulu.')
                    return redirect('register')
                
                # Generate OTP dan Token
                otp_code = OTP.generate_otp()
                verification_token = OTP.generate_token()
                otp_obj = OTP.objects.create(
                    user=user,
                    otp_code=otp_code,
                    verification_token=verification_token,
                    purpose='login'
                )
                
                # Buat link verifikasi
                verification_link = request.build_absolute_uri(
                    reverse('verify_otp_token', args=[verification_token])
                )
                
                # Kirim email OTP dengan HTML template
                html_message = render_to_string('accounts/emails/otp_email.html', {
                    'otp_code': otp_code,
                    'verification_link': verification_link,
                    'purpose': 'Login',
                    'user': user,
                })
                plain_message = f'''Kode OTP Anda adalah: {otp_code}

Atau klik link berikut untuk verifikasi otomatis:
{verification_link}

Kode ini berlaku selama 5 menit.

Jangan bagikan kode ini kepada siapapun.'''
                
                msg = EmailMultiAlternatives(
                    subject='Kode OTP untuk Login',
                    body=plain_message,
                    from_email=settings.DEFAULT_FROM_EMAIL if hasattr(settings, 'DEFAULT_FROM_EMAIL') else 'noreply@belajarotp.com',
                    to=[email],
                )
                msg.attach_alternative(html_message, "text/html")
                success, error_msg = send_email_safe(msg, request)
                
                if not success:
                    messages.error(request, f'Gagal mengirim email: {error_msg}. Silakan cek konfigurasi email atau gunakan Console Backend.')
                    return redirect('login')
                
                # Simpan email di session untuk verifikasi
                request.session['login_email'] = email
                if error_msg != 'console':
                    messages.success(request, f'Kode OTP telah dikirim ke email {email}. Silakan cek email Anda atau klik link verifikasi di email.')
                return redirect('verify_otp', purpose='login')
                
            except CustomUser.DoesNotExist:
                messages.error(request, 'Email tidak terdaftar.')
    else:
        form = LoginForm()
    
    return render(request, 'accounts/login.html', {'form': form})


def verify_otp_view(request, purpose):
    """View untuk verifikasi OTP (registration atau login)"""
    if request.user.is_authenticated and purpose == 'login':
        return redirect('dashboard')
    
    # Ambil email dari session
    if purpose == 'registration':
        email = request.session.get('registration_email')
        if not email:
            messages.error(request, 'Sesi registrasi tidak valid. Silakan registrasi ulang.')
            return redirect('register')
    elif purpose == 'login':
        email = request.session.get('login_email')
        if not email:
            messages.error(request, 'Sesi login tidak valid. Silakan login ulang.')
            return redirect('login')
    else:
        messages.error(request, 'Tujuan tidak valid.')
        return redirect('login')
    
    try:
        user = CustomUser.objects.get(email=email)
    except CustomUser.DoesNotExist:
        messages.error(request, 'User tidak ditemukan.')
        return redirect('login' if purpose == 'login' else 'register')
    
    if request.method == 'POST':
        form = OTPVerificationForm(request.POST)
        if form.is_valid():
            otp_code = form.cleaned_data['otp_code']
            
            # Cari OTP yang valid untuk user ini
            try:
                otp = OTP.objects.filter(
                    user=user,
                    otp_code=otp_code,
                    purpose=purpose,
                    is_used=False
                ).latest('created_at')
                
                # Cek apakah OTP masih valid
                if otp.is_valid():
                    # Mark OTP sebagai used
                    otp.is_used = True
                    otp.save()
                    
                    if purpose == 'registration':
                        # Aktifkan user dan login
                        user.is_active = True
                        user.save()
                        login(request, user)
                        messages.success(request, 'Registrasi berhasil! Akun Anda telah diaktifkan.')
                        # Hapus session
                        if 'registration_email' in request.session:
                            del request.session['registration_email']
                        return redirect('dashboard')
                    
                    elif purpose == 'login':
                        # Login user
                        login(request, user)
                        messages.success(request, 'Login berhasil!')
                        # Hapus session
                        if 'login_email' in request.session:
                            del request.session['login_email']
                        return redirect('dashboard')
                else:
                    if otp.is_expired():
                        messages.error(request, 'Kode OTP sudah kadaluarsa. Silakan request kode baru.')
                    else:
                        messages.error(request, 'Kode OTP tidak valid.')
            except OTP.DoesNotExist:
                messages.error(request, 'Kode OTP tidak valid atau sudah digunakan.')
    else:
        form = OTPVerificationForm()
    
    context = {
        'form': form,
        'purpose': purpose,
        'email': email,
    }
    return render(request, 'accounts/verify_otp.html', context)


@login_required
def dashboard_view(request):
    """View untuk dashboard (hanya untuk user yang sudah login)"""
    # Ambil semua pendaftar PPT
    pendaftar_list = PPTRegistration.objects.all()
    
    # Statistik
    total_pendaftar = pendaftar_list.count()
    pending_count = pendaftar_list.filter(status='pending').count()
    confirmed_count = pendaftar_list.filter(status='confirmed').count()
    paid_count = pendaftar_list.filter(status='paid').count()
    completed_count = pendaftar_list.filter(status='completed').count()
    
    context = {
        'user': request.user,
        'pendaftar_list': pendaftar_list,
        'total_pendaftar': total_pendaftar,
        'pending_count': pending_count,
        'confirmed_count': confirmed_count,
        'paid_count': paid_count,
        'completed_count': completed_count,
    }
    return render(request, 'accounts/dashboard.html', context)


def ppt_registration_view(request):
    """View untuk form pendaftaran pembelian PPT"""
    if request.method == 'POST':
        form = PPTRegistrationForm(request.POST)
        if form.is_valid():
            registration = form.save()
            
            # Kirim email konfirmasi ke pendaftar
            try:
                email_msg = EmailMultiAlternatives(
                    subject=f'Terima Kasih! Pendaftaran Paket {registration.get_paket_ppt_display()}',
                    body=f'''Halo {registration.nama},

Terima kasih telah mendaftar untuk pembelian PPT!

Detail Pendaftaran:
- Nama: {registration.nama}
- Email: {registration.email}
- Paket: {registration.get_paket_ppt_display()}
- Harga: Rp {registration.get_harga():,}
- Status: {registration.get_status_display()}

Kami akan segera menghubungi Anda untuk proses selanjutnya.

Salam,
Tim PPT Store''',
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    to=[registration.email],
                )
                success, error_msg = send_email_safe(email_msg, request)
                if success:
                    if error_msg != 'console':
                        messages.success(request, 'Pendaftaran berhasil! Email konfirmasi telah dikirim.')
                    else:
                        messages.success(request, 'Pendaftaran berhasil! Email konfirmasi muncul di terminal.')
                else:
                    messages.warning(request, f'Pendaftaran berhasil, tapi email gagal dikirim: {error_msg}')
            except Exception as e:
                messages.warning(request, f'Pendaftaran berhasil, tapi email gagal dikirim: {str(e)}')
            
            return redirect('ppt_registration_success')
    else:
        form = PPTRegistrationForm()
    
    return render(request, 'accounts/ppt_registration.html', {'form': form})


def ppt_registration_success_view(request):
    """View untuk halaman sukses pendaftaran PPT"""
    return render(request, 'accounts/ppt_registration_success.html')


@login_required
def send_mass_email_view(request):
    """View untuk kirim email massal"""
    if request.method == 'POST':
        form = MassEmailForm(request.POST)
        if form.is_valid():
            subject = form.cleaned_data['subject']
            message = form.cleaned_data['message']
            recipient_type = form.cleaned_data['recipient_type']
            
            # Filter pendaftar berdasarkan recipient_type
            if recipient_type == 'all':
                recipients = PPTRegistration.objects.all()
            else:
                recipients = PPTRegistration.objects.filter(status=recipient_type)
            
            if not recipients.exists():
                messages.warning(request, 'Tidak ada penerima email yang sesuai dengan filter.')
                return redirect('send_mass_email')
            
            # Kirim email ke setiap penerima
            success_count = 0
            failed_count = 0
            
            for recipient in recipients:
                try:
                    personalized_message = f'''Halo {recipient.nama},

{message}

---
Detail Pendaftaran Anda:
- Paket: {recipient.get_paket_ppt_display()}
- Status: {recipient.get_status_display()}

Salam,
Tim PPT Store'''
                    
                    send_mail(
                        subject=subject,
                        message=personalized_message,
                        from_email=settings.DEFAULT_FROM_EMAIL,
                        recipient_list=[recipient.email],
                        fail_silently=False,
                    )
                    success_count += 1
                except Exception as e:
                    failed_count += 1
                    messages.error(request, f'Gagal kirim ke {recipient.email}: {str(e)}')
            
            messages.success(request, f'Email berhasil dikirim ke {success_count} penerima. {failed_count} gagal.')
            return redirect('dashboard')
    else:
        form = MassEmailForm()
    
    return render(request, 'accounts/send_mass_email.html', {'form': form})


def verify_otp_token_view(request, token):
    """View untuk verifikasi OTP via token dari link email"""
    try:
        otp = get_object_or_404(OTP, verification_token=token, is_used=False)
        
        # Cek apakah OTP masih valid
        if not otp.is_valid():
            if otp.is_expired():
                messages.error(request, 'Link verifikasi sudah kadaluarsa. Silakan request kode baru.')
            else:
                messages.error(request, 'Link verifikasi tidak valid.')
            return redirect('login' if otp.purpose == 'login' else 'register')
        
        # Mark OTP sebagai used
        otp.is_used = True
        otp.save()
        
        if otp.purpose == 'registration':
            # Aktifkan user dan login
            otp.user.is_active = True
            otp.user.save()
            login(request, otp.user)
            messages.success(request, 'Registrasi berhasil! Akun Anda telah diaktifkan.')
            return redirect('dashboard')
        
        elif otp.purpose == 'login':
            # Login user
            login(request, otp.user)
            messages.success(request, 'Login berhasil!')
            return redirect('dashboard')
            
    except Exception as e:
        messages.error(request, 'Link verifikasi tidak valid atau sudah digunakan.')
        return redirect('login')


def forgot_password_view(request):
    """View untuk lupa password"""
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    if request.method == 'POST':
        form = ForgotPasswordForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            
            try:
                user = CustomUser.objects.get(email=email)
                
                # Generate OTP dan Token untuk reset password
                otp_code = OTP.generate_otp()
                verification_token = OTP.generate_token()
                otp_obj = OTP.objects.create(
                    user=user,
                    otp_code=otp_code,
                    verification_token=verification_token,
                    purpose='password_reset'
                )
                
                # Buat link reset password
                reset_link = request.build_absolute_uri(
                    reverse('reset_password_token', args=[verification_token])
                )
                
                # Kirim email reset password dengan HTML template
                html_message = render_to_string('accounts/emails/reset_password_email.html', {
                    'otp_code': otp_code,
                    'reset_link': reset_link,
                    'user': user,
                })
                plain_message = f'''Halo {user.email},

Anda telah meminta reset password untuk akun Anda.

Kode OTP Anda: {otp_code}

Atau klik link berikut untuk reset password:
{reset_link}

Link ini berlaku selama 5 menit.

Jika Anda tidak meminta reset password, abaikan email ini.

Salam,
Tim Support'''
                
                msg = EmailMultiAlternatives(
                    subject='Reset Password - Kode OTP',
                    body=plain_message,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    to=[email],
                )
                msg.attach_alternative(html_message, "text/html")
                success, error_msg = send_email_safe(msg, request)
                
                if not success:
                    messages.error(request, f'Gagal mengirim email: {error_msg}. Silakan cek konfigurasi email atau gunakan Console Backend.')
                    return redirect('forgot_password')
                
                # Simpan email di session
                request.session['reset_password_email'] = email
                if error_msg != 'console':
                    messages.success(request, f'Email reset password telah dikirim ke {email}. Silakan cek email Anda atau klik link verifikasi.')
                else:
                    messages.info(request, 'Email reset password telah dikirim. Cek terminal untuk melihat email dan link verifikasi.')
                return redirect('reset_password')
                
            except CustomUser.DoesNotExist:
                messages.error(request, 'Email tidak terdaftar.')
    else:
        form = ForgotPasswordForm()
    
    return render(request, 'accounts/forgot_password.html', {'form': form})


def reset_password_view(request):
    """View untuk reset password (input password baru)"""
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    email = request.session.get('reset_password_email')
    if not email:
        messages.error(request, 'Sesi reset password tidak valid. Silakan request reset password ulang.')
        return redirect('forgot_password')
    
    if request.method == 'POST':
        form = ResetPasswordForm(request.POST)
        if form.is_valid():
            new_password = form.cleaned_data['new_password']
            
            try:
                user = CustomUser.objects.get(email=email)
                user.set_password(new_password)
                user.save()
                
                # Hapus session
                if 'reset_password_email' in request.session:
                    del request.session['reset_password_email']
                
                messages.success(request, 'Password berhasil direset! Silakan login dengan password baru.')
                return redirect('login')
                
            except CustomUser.DoesNotExist:
                messages.error(request, 'User tidak ditemukan.')
                return redirect('forgot_password')
    else:
        form = ResetPasswordForm()
    
    return render(request, 'accounts/reset_password.html', {'form': form, 'email': email})


def reset_password_token_view(request, token):
    """View untuk reset password via token dari link email"""
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    try:
        otp = get_object_or_404(OTP, verification_token=token, purpose='password_reset', is_used=False)
        
        # Cek apakah token masih valid
        if not otp.is_valid():
            if otp.is_expired():
                messages.error(request, 'Link reset password sudah kadaluarsa. Silakan request reset password baru.')
            else:
                messages.error(request, 'Link reset password tidak valid.')
            return redirect('forgot_password')
        
        # Mark OTP sebagai used
        otp.is_used = True
        otp.save()
        
        # Simpan email di session untuk reset password
        request.session['reset_password_email'] = otp.user.email
        messages.success(request, 'Verifikasi berhasil! Silakan masukkan password baru.')
        return redirect('reset_password')
        
    except Exception as e:
        messages.error(request, 'Link reset password tidak valid atau sudah digunakan.')
        return redirect('forgot_password')


def logout_view(request):
    """View untuk logout"""
    logout(request)
    messages.success(request, 'Anda telah logout.')
    return redirect('login')

