---
description: How to setup and test Postfix email service
---

1. **Install Postfix** (if not already installed):
   ```bash
   sudo apt-get update
   sudo apt-get install postfix
   ```
   - During installation, select "Internet Site".
   - System mail name: `votewise.local` (or your domain).

2. **Configure Postfix** (optional, for send-only):
   - Edit `/etc/postfix/main.cf` and ensure `inet_interfaces = loopback-only` to prevent open relay.
   - Restart Postfix: `sudo systemctl restart postfix`.

3. **Test Email Sending** via Django Shell:
   ```bash
   python manage.py shell
   ```
   ```python
   from django.core.mail import send_mail
   send_mail(
       'Test Subject',
       'This is a test message from VoteWise via Postfix.',
       'noreply@votewise.local',
       ['your-email@example.com'],
       fail_silently=False,
   )
   ```

4. **Verify**: Check your spam folder if not received, or check `/var/log/mail.log` (or `journalctl -u postfix`) for errors.

## Troubleshooting: Emails Bouncing (Gmail/Outlook)

If you see "The IP you're using to send mail is not authorized..." in your logs, your ISP or the recipient is blocking direct mail. To fix this, configure Postfix to relay through a Gmail account:

1.  **Get an App Password**:
    - Go to Google Account > Security > 2-Step Verification > App passwords.
    - Generate a password for "Mail".

2.  **Configure Postfix**:
    Edit `/etc/postfix/main.cf` and add:
    ```
    relayhost = [smtp.gmail.com]:587
    smtp_use_tls = yes
    smtp_sasl_auth_enable = yes
    smtp_sasl_security_options = noanonymous
    smtp_sasl_password_maps = hash:/etc/postfix/sasl_passwd
    ```

3.  **Set Credentials**:
    Create `/etc/postfix/sasl_passwd`:
    ```
    [smtp.gmail.com]:587 your-email@gmail.com:your-app-password
    ```

4.  **Apply Changes**:
    ```bash
    sudo postmap /etc/postfix/sasl_passwd
    sudo chmod 600 /etc/postfix/sasl_passwd /etc/postfix/sasl_passwd.db
    sudo systemctl restart postfix
    ```
