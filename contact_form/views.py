from django.core.mail import send_mail, BadHeaderError

from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
import requests

CIRCE_SENDER = 'CIRCE Sito <info@circe.cloud>'
CIRCE_RECIPIENT = 'info@circe.cloud'


def get_email_body(cn, ce, cp, m, em_type, spam_info):
    body = 'E\' arrivata una richiesta dal sito.<br><br>' \
           'Nome: {}<br>' \
           'Email: {}<br>' \
           'Telefono: {}<br><br>'.format(cn, ce, cp)

    if em_type == 'demo':
        body = body + '<h3>RICHIESTA VERSIONE DEMO</h3>' \
                      'Messaggio: {}'.format(m)
    elif em_type == 'buy':
        body = body + '<h3>RICHIESTA ACQUISTO CIRCE</h3>'

    elif em_type == 'info':
        body = body + '<h3>RICHIESTA INFORMAZIONI</h3>' \
                      'Messaggio: {}'.format(m)

    if spam_info:
        body = body + '<h3>SPAM INFO</h3>' \
                      '<pre>{}</pre>'.format(spam_info)

    return body


def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def grecaptcha_verified(request):
    if request.method == 'POST':
        recaptcha_response = request.POST.get('recaptchaResponse', '')

        url = "https://www.google.com/recaptcha/api/siteverify"
        params = {
            'secret': '6Ld9toMaAAAAAN0lBMzteDfuBj7MhJGmP8LZ9FHA',
            'response': recaptcha_response,
            'remoteip': get_client_ip(request)
        }
        verify_rs = requests.get(url, params=params, verify=True)
        verify_rs = verify_rs.json()

        return verify_rs


@csrf_exempt
def request_demo(request):
    cust_name = request.POST.get('name', '')
    cust_email = request.POST.get('email', '')
    cust_phone = request.POST.get('phone', '')
    message = request.POST.get('message', '')

    if cust_name and cust_email:
        verify_rs = grecaptcha_verified(request)
        captcha_verified = verify_rs.get("success", False)
        try:
            if captcha_verified:
                subject = '[CIRCE] Richiesta versione demo'
            else:
                subject = '[SPAM-CIRCE: {}] Richiesta versione demo'.format(get_client_ip(request))

            body = get_email_body(cust_name, cust_email, cust_phone, message, 'demo', verify_rs)

            send_mail(subject, '', CIRCE_SENDER, [CIRCE_RECIPIENT], html_message=body)
        except BadHeaderError:
            return HttpResponse('Errore nell\'invio dell\'email', status=500)

        # return HttpResponse('Email inviata', status=200)
        return JsonResponse({'success': 'true'})
    else:
        return HttpResponse('Errore nell\'invio dell\'email. Dati mancanti.', status=500)


@csrf_exempt
def request_buy(request):
    cust_name = request.POST.get('name', '')
    cust_email = request.POST.get('email', '')
    cust_phone = request.POST.get('phone', '')

    if cust_name and cust_email:
        try:
            subject = '[CIRCE] Richiesta di acquisto'
            body = get_email_body(cust_name, cust_email, cust_phone, None, 'buy', None)

            send_mail(subject, '', CIRCE_SENDER, [CIRCE_RECIPIENT], html_message=body)
        except BadHeaderError:
            return HttpResponse('Errore nell\'invio dell\'email', status=500)

        # return HttpResponse('Email inviata', status=200)
        return JsonResponse({'success': 'true'})
    else:
        return HttpResponse('Errore nell\'invio dell\'email. Dati mancanti.', status=500)


@csrf_exempt
def request_info(request):
    cust_name = request.POST.get('name', '')
    cust_email = request.POST.get('email', '')
    cust_phone = request.POST.get('phone', '')
    message = request.POST.get('message', '')
    prodotto = request.POST.get('prodotto', '')

    if cust_name and cust_email and message:
        try:
            if prodotto == 'Poseidone':
                subject = '[POSEIDONE] Richiesta di informazioni'
            else:
                subject = '[CIRCE] Richiesta di informazioni [{}]'.format(prodotto)
            body = get_email_body(cust_name, cust_email, cust_phone, message, 'info', None)

            send_mail(subject, '', CIRCE_SENDER, [CIRCE_RECIPIENT], html_message=body)
        except BadHeaderError:
            return HttpResponse('Errore nell\'invio dell\'email', status=500)

        # return HttpResponse('Email inviata', status=200)
        return JsonResponse({'success': 'true'})
    else:
        return HttpResponse('Errore nell\'invio dell\'email. Dati mancanti.', status=500)
