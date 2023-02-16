def theme_renderer(request):
    if request.user.is_authenticated:
        try:
            colour_theme_preference = request.user.preferences.get('core-user-theme')
        except AttributeError:
            colour_theme_preference = "default-theme"
        return {
            'theme': colour_theme_preference
        }
    else:
        theme = 'default-theme'
        return {'theme': theme}
