from models.background import Background, BackgroundImage

PLACEHOLDER_BACKGROUNDS = {
    'hero': {
        'sm': '/upload/background/placeholder/hero/hero-512.webp',
        'md': '/upload/background/placeholder/hero/hero-1024.webp',
        'lg': '/upload/background/placeholder/hero/hero-2048.webp',
    },
    'portfolio': {
        'sm': '/upload/background/placeholder/portfolio/portfolio-512.webp',
        'md': '/upload/background/placeholder/portfolio/portfolio-1024.webp',
        'lg': '/upload/background/placeholder/portfolio/portfolio-2048.webp',
    },
    'biography': {
        'sm': '/upload/background/placeholder/biography/biography-512.webp',
        'md': '/upload/background/placeholder/biography/biography-1024.webp',
        'lg': '/upload/background/placeholder/biography/biography-2048.webp',
    }
}


def create_default_background(user):
    if Background.objects(user=user).first():
        return  # Already exists

    Background(
        user=user,
        hero=BackgroundImage(**PLACEHOLDER_BACKGROUNDS['hero']),
        portfolio=BackgroundImage(**PLACEHOLDER_BACKGROUNDS['portfolio']),
        biography=BackgroundImage(**PLACEHOLDER_BACKGROUNDS['biography'])
    ).save()
