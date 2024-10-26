from django.template.loader import render_to_string
def welcome_html(user):
    context = {
        'username': user.email,
        'profile_pic_url': user.profile_pic_url,
    }
    
    html_content = render_to_string('welcome_email.html', context)
    return html_content
