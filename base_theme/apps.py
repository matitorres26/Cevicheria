from tailwind.apps import TailwindConfig

# Esta clase le dice a Django-Tailwind que 'theme' es una app de Tailwind.
class CevicheriaTailwindConfig(TailwindConfig):
    name = 'theme'
    verbose_name = 'Tema Cevichería (Tailwind)'