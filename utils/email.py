import smtplib
import threading
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from flask import current_app


# ── Internal sender ───────────────────────────────────────────────────────────

def _send(subject, html, to_email, app):
    """Send email in a background thread — never blocks the request."""
    username = app.config.get('MAIL_USERNAME', '').strip()
    password = app.config.get('MAIL_PASSWORD', '').replace(' ', '').strip()
    if not username or not password:
        return
    msg = MIMEMultipart('alternative')
    msg['Subject'] = subject
    msg['From']    = f'Traveloop <{username}>'
    msg['To']      = to_email
    msg.attach(MIMEText(html, 'html'))
    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            server.login(username, password)
            server.sendmail(username, to_email, msg.as_string())
    except Exception:
        pass


def _fire(subject, html, to_email):
    """Grab app context and dispatch in a thread."""
    app = current_app._get_current_object()
    t = threading.Thread(target=_send, args=(subject, html, to_email, app), daemon=True)
    t.start()


# ── Public API ────────────────────────────────────────────────────────────────

def send_password_reset(to_email, reset_url):
    """Send password reset link email."""
    subject = 'Reset your Traveloop password'
    html = _build_reset_html(reset_url)
    _fire(subject, html, to_email)


def send_trip_created(to_email, user_name, trip):
    """Auto-triggered when a new trip is created."""
    subject = f'✈️ Trip Created: {trip.name}'
    html = _build_created_html(user_name, trip)
    _fire(subject, html, to_email)


def send_trip_summary(to_email, user_name, trip):
    """Manual itinerary email — returns (ok, message) for flash feedback."""
    username = current_app.config.get('MAIL_USERNAME', '').strip()
    password = current_app.config.get('MAIL_PASSWORD', '').replace(' ', '').strip()
    if not username or not password:
        return False, 'Email not configured. Add MAIL_USERNAME and MAIL_PASSWORD to .env'
    subject = f'✈️ Your Traveloop Itinerary: {trip.name}'
    html = _build_itinerary_html(user_name, trip)
    msg = MIMEMultipart('alternative')
    msg['Subject'] = subject
    msg['From']    = f'Traveloop <{username}>'
    msg['To']      = to_email
    msg.attach(MIMEText(html, 'html'))
    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            server.login(username, password)
            server.sendmail(username, to_email, msg.as_string())
        return True, 'Itinerary sent successfully!'
    except smtplib.SMTPAuthenticationError:
        return False, 'Email authentication failed. Check your Gmail App Password.'
    except Exception as e:
        return False, f'Failed to send email: {str(e)}'


# ── Email templates ───────────────────────────────────────────────────────────

_BASE = """<!DOCTYPE html>
<html>
<head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1"></head>
<body style="margin:0;padding:0;background:#f5f4f0;font-family:'Plus Jakarta Sans',-apple-system,BlinkMacSystemFont,sans-serif">
  <div style="max-width:580px;margin:32px auto;background:#fff;border-radius:20px;overflow:hidden;border:1px solid #e8e5df;box-shadow:0 4px 24px rgba(0,0,0,0.07)">

    <!-- Header -->
    <div style="background:#141413;padding:36px 32px;position:relative;overflow:hidden">
      <div style="position:absolute;bottom:0;right:0;width:200px;height:200px;background:radial-gradient(circle at 100%% 100%%,rgba(194,65,12,.35),transparent 70%%);pointer-events:none"></div>
      <div style="position:relative;z-index:1">
        <div style="display:inline-flex;align-items:center;gap:8px;margin-bottom:20px">
          <div style="width:30px;height:30px;background:#fff;border-radius:7px;display:flex;align-items:center;justify-content:center;font-size:15px">✈️</div>
          <span style="color:#fff;font-weight:800;font-size:17px;letter-spacing:-.02em">Traveloop</span>
        </div>
        {header_content}
      </div>
    </div>

    {body}

    <!-- Footer -->
    <div style="padding:20px 32px;text-align:center;border-top:1px solid #f0ede8">
      <p style="color:#c4c1bb;font-size:12px;margin:0">Sent by Traveloop · Plan smarter, travel better.</p>
    </div>
  </div>
</body>
</html>"""


def _build_created_html(user_name, trip):
    trip_dates = ''
    if trip.start_date:
        end = trip.end_date.strftime('%B %d, %Y') if trip.end_date else '?'
        trip_dates = f"{trip.start_date.strftime('%B %d')} – {end}"

    meta_rows = ''
    if trip_dates:
        meta_rows += f'<tr><td style="padding:10px 0;border-bottom:1px solid #f0ede8;font-size:14px;color:#8a8680;width:120px">Dates</td><td style="padding:10px 0;border-bottom:1px solid #f0ede8;font-size:14px;color:#141413;font-weight:600">{trip_dates}</td></tr>'
    if trip.total_days:
        meta_rows += f'<tr><td style="padding:10px 0;border-bottom:1px solid #f0ede8;font-size:14px;color:#8a8680">Duration</td><td style="padding:10px 0;border-bottom:1px solid #f0ede8;font-size:14px;color:#141413;font-weight:600">{trip.total_days} day{"s" if trip.total_days != 1 else ""}</td></tr>'
    if trip.description:
        meta_rows += f'<tr><td style="padding:10px 0;font-size:14px;color:#8a8680;vertical-align:top">Note</td><td style="padding:10px 0;font-size:14px;color:#4b4945;line-height:1.6">{trip.description}</td></tr>'

    header_content = f'''
      <div style="display:inline-block;background:#c2410c;color:#fff;font-size:11px;font-weight:700;letter-spacing:.1em;text-transform:uppercase;padding:4px 12px;border-radius:99px;margin-bottom:10px">Trip Created</div>
      <h1 style="color:#fff;font-size:26px;font-weight:800;margin:0;letter-spacing:-.03em">{trip.name}</h1>
    '''

    body = f'''
    <div style="padding:28px 32px">
      <p style="font-size:15px;color:#4b4945;margin:0 0 20px;line-height:1.6">
        Hey <strong style="color:#141413">{user_name}</strong>, your trip has been created! Start adding cities and activities to build your itinerary.
      </p>

      {'<table style="width:100%;border-collapse:collapse;margin-bottom:24px">' + meta_rows + '</table>' if meta_rows else ''}

      <a href="http://localhost:5000/trips"
         style="display:inline-block;background:#c2410c;color:#fff;font-weight:700;padding:12px 28px;border-radius:10px;text-decoration:none;font-size:14px;letter-spacing:.01em">
        Start Building Your Itinerary →
      </a>
    </div>

    <!-- Tips strip -->
    <div style="padding:20px 32px;background:#f5f4f0;border-top:1px solid #e8e5df">
      <p style="font-size:12px;font-weight:700;color:#8a8680;text-transform:uppercase;letter-spacing:.08em;margin:0 0 12px">Quick tips</p>
      <div style="display:flex;flex-direction:column;gap:8px">
        {''.join(f'<div style="display:flex;align-items:center;gap:10px"><span style="font-size:14px">{e}</span><span style="font-size:13px;color:#4b4945">{t}</span></div>' for e,t in [
            ('📍','Add city stops to plan your route'),
            ('💰','Set a budget target to track spending'),
            ('📝','Use notes to save ideas and reminders'),
            ('✅','Build a packing checklist before you leave'),
        ])}
      </div>
    </div>
    '''

    return _BASE.format(header_content=header_content, body=body)


def _build_itinerary_html(user_name, trip):
    stops_html = ''
    for i, stop in enumerate(trip.stops, 1):
        activities_html = ''
        for sa in stop.stop_activities:
            cat_emoji = {'sightseeing': '📸', 'food': '🍜', 'adventure': '🏔️', 'culture': '🏛️'}.get(
                sa.activity.category, '⭐')
            cost = sa.custom_cost if sa.custom_cost is not None else sa.activity.estimated_cost
            activities_html += f'''
            <tr>
              <td style="padding:10px 12px;border-bottom:1px solid #f0ede8;font-size:14px;color:#4b4945">
                {cat_emoji} {sa.activity.name}
              </td>
              <td style="padding:10px 12px;border-bottom:1px solid #f0ede8;font-size:14px;color:#8a8680;text-align:right;white-space:nowrap">
                ${cost:.0f} · {sa.activity.duration_hours}h
              </td>
            </tr>'''

        dates_str = ''
        if stop.arrival_date:
            end = stop.departure_date.strftime('%b %d, %Y') if stop.departure_date else '?'
            days = stop.days
            dates_str = f"{stop.arrival_date.strftime('%b %d')} – {end} · {days} day{'s' if days != 1 else ''}"

        stops_html += f'''
        <div style="margin-bottom:16px;border-radius:12px;overflow:hidden;border:1px solid #e8e5df">
          <div style="background:#f5f4f0;padding:14px 18px;display:flex;align-items:center;gap:12px">
            <div style="width:28px;height:28px;border-radius:50%;background:#141413;color:#fff;font-weight:800;font-size:13px;display:flex;align-items:center;justify-content:center;flex-shrink:0">{i}</div>
            <div>
              <div style="font-weight:800;color:#141413;font-size:15px">{stop.city.name}, {stop.city.country}</div>
              {'<div style="font-size:12px;color:#8a8680;margin-top:2px">' + dates_str + '</div>' if dates_str else ''}
            </div>
          </div>
          {'<table style="width:100%;border-collapse:collapse">' + activities_html + '</table>' if activities_html else '<div style="padding:12px 18px;font-size:13px;color:#c4c1bb;font-style:italic">No activities planned yet.</div>'}
        </div>'''

    trip_dates = ''
    if trip.start_date:
        end = trip.end_date.strftime('%B %d, %Y') if trip.end_date else '?'
        trip_dates = f"{trip.start_date.strftime('%B %d')} – {end}"

    budget_str = f'${trip.total_budget:.0f} estimated' if trip.total_budget > 0 else ''

    header_content = f'''
      <h1 style="color:#fff;font-size:26px;font-weight:800;margin:0 0 6px;letter-spacing:-.03em">{trip.name}</h1>
      <p style="color:rgba(255,255,255,.45);font-size:14px;margin:0">Your complete trip itinerary</p>
    '''

    meta_items = []
    if trip_dates:
        meta_items.append(f'<span>📅 {trip_dates}</span>')
    meta_items.append(f'<span>📍 {len(trip.stops)} stop{"s" if len(trip.stops) != 1 else ""}</span>')
    if trip.total_days:
        meta_items.append(f'<span>🌟 {trip.total_days} days</span>')
    if budget_str:
        meta_items.append(f'<span>💰 {budget_str}</span>')

    body = f'''
    <div style="padding:20px 32px 8px;background:#f5f4f0;border-bottom:1px solid #e8e5df">
      <p style="font-size:14px;color:#4b4945;margin:0 0 8px">
        Hey <strong style="color:#141413">{user_name}</strong>, here's your full itinerary!
      </p>
      <div style="display:flex;flex-wrap:wrap;gap:16px;font-size:13px;color:#8a8680">
        {''.join(meta_items)}
      </div>
    </div>

    <div style="padding:20px 32px 28px">
      <h2 style="font-size:16px;font-weight:800;color:#141413;margin:0 0 14px;letter-spacing:-.02em">Itinerary</h2>
      {stops_html if stops_html else '<div style="text-align:center;padding:24px;color:#c4c1bb;font-size:14px">No stops added yet.</div>'}
    </div>

    <div style="padding:20px 32px 28px;background:#f5f4f0;border-top:1px solid #e8e5df;text-align:center">
      <a href="http://localhost:5000/trips"
         style="display:inline-block;background:#141413;color:#fff;font-weight:700;padding:12px 28px;border-radius:10px;text-decoration:none;font-size:14px">
        Open in Traveloop →
      </a>
    </div>
    '''

    return _BASE.format(header_content=header_content, body=body)


def _build_reset_html(reset_url):
    header_content = (
        '<div style="display:inline-block;background:#c2410c;color:#fff;font-size:11px;font-weight:700;'
        'letter-spacing:.1em;text-transform:uppercase;padding:4px 12px;border-radius:99px;margin-bottom:10px">'
        'Password Reset</div>'
        '<h1 style="color:#fff;font-size:24px;font-weight:800;margin:0;letter-spacing:-.03em">'
        'Reset your password</h1>'
    )
    body = (
        '<div style="padding:28px 32px">'
        '<p style="font-size:15px;color:#4b4945;margin:0 0 20px;line-height:1.6">'
        'We received a request to reset your Traveloop password. '
        'Click the button below — this link expires in '
        '<strong style="color:#141413">1 hour</strong>.'
        '</p>'
        '<div style="text-align:center;margin:28px 0">'
        f'<a href="{reset_url}" style="display:inline-block;background:#c2410c;color:#fff;font-weight:700;'
        'padding:13px 32px;border-radius:10px;text-decoration:none;font-size:15px">'
        'Reset Password &rarr;</a>'
        '</div>'
        '<div style="border-radius:10px;padding:14px 18px;background:#f5f4f0;border:1px solid #e8e5df">'
        '<p style="font-size:12px;color:#8a8680;margin:0 0 6px;font-weight:600">Or copy this link:</p>'
        f'<p style="font-size:12px;color:#4b4945;margin:0;word-break:break-all">{reset_url}</p>'
        '</div>'
        '</div>'
        '<div style="padding:0 32px 28px">'
        '<p style="font-size:13px;color:#c4c1bb;margin:0;line-height:1.6">'
        'If you did not request this, ignore this email — your password will not change.'
        '</p>'
        '</div>'
    )
    return _BASE.format(header_content=header_content, body=body)
