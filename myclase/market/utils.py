# utils.py
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings

def enviar_presupuesto_email(data_presupuesto, email_destino):
    """
    Genera el cuerpo del correo y lo envía.
    data_presupuesto: Diccionario con items, total, fecha, etc.
    """
    
    subject = f"Presupuesto LocalMarket - {data_presupuesto['date']}"
    
    # Renderizamos un HTML bonito usando un template de Django
    # (Tendrás que crear email_budget.html en tus templates)
    html_content = render_to_string('market/email_budget.html', {
        'data': data_presupuesto
    })
    
    # Configurar el mensaje
    msg = EmailMultiAlternatives(
        subject=subject,
        body="Aquí tienes tu presupuesto en formato HTML.", # Texto plano por si falla HTML
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[email_destino]
    )
    
    msg.attach_alternative(html_content, "text/html")
    
    # Si más adelante generas PDF con WeasyPrint, aquí harías:
    # msg.attach('presupuesto.pdf', pdf_file, 'application/pdf')
    
    return msg.send()


def get_user_avatar(user):
    
    try:
        social_account = user.socialaccount_set.first()
        if social_account:
            
            return social_account.get_avatar_url()
    except:
        pass
 
    return '/static/img/default-avatar.png'  
