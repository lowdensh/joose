from django.core.management.base import BaseCommand, CommandError
from django.db.models import Q
from products.models import Volume, Strength, Ratio, FlavourCategory, Flavour

class Command(BaseCommand):
    help = 'Quickly create some model instances to play with in the shell or admin site.'

    def add_arguments(self, parser):
        parser.add_argument(
            'app',
            type=str,
            help='The app containing the models to create instances of.')

    def handle(self, *args, **kwargs):
        supported_apps = ['products']
        input_app = kwargs['app']
        if input_app in supported_apps:
            self.create_for(input_app)
            self.stdout.write()
            self.stdout.write('Done.')
        else:
            self.stdout.write(self.style.ERROR(
                f'Unrecognised app: \'{input_app}\''))
    
    def create_for(self, app):
        self.stdout.write(self.style.MIGRATE_HEADING(
            f'Creating model instances for app \'{app}\':'))
        if app == 'products': self.create_for_products()
    
    def create_for_products(self):
        self.create_products_volume()
        self.create_products_strength()
        self.create_products_ratio()
        self.create_products_flavour()
        self.create_products_flavour_category()
        self.manage_products_add_flavours_to_categories()
    
    def create_products_volume(self):
        self.stdout.write(self.style.MIGRATE_LABEL('  Volume:'))
        volumes = [10, 30, 50, 100, 250, 500]
        for v in volumes:
            try:
                obj = Volume.objects.create(volume=v)
                self.stdout.write(f'    Created {obj}')
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'    Error: {e}'))
    
    def create_products_strength(self):
        self.stdout.write(self.style.MIGRATE_LABEL('  Strength:'))
        strengths = [0, 3, 5, 6, 10, 12, 18, 20]
        for s in strengths:
            try:
                obj = Strength.objects.create(strength=s)
                self.stdout.write(f'    Created {obj}')
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'    Error: {e}'))
    
    def create_products_ratio(self):
        self.stdout.write(self.style.MIGRATE_LABEL('  Ratio:'))
        vgs = [0, 10, 20, 30, 40, 50, 60, 65, 70, 80, 90, 100]
        for vg in vgs:
            try:
                obj = Ratio.objects.create(vg=vg)
                self.stdout.write(f'    Created {obj}')
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'    Error: {e}'))
    
    def create_products_flavour(self):
        self.stdout.write(self.style.MIGRATE_LABEL('  Flavour:'))
        flavours = [
            'apple',
            'banana',
            'cherry',
            'strawberry',
            'raspberry',
            'menthol',
            'spearmint',
            'peppermint']
        for f in flavours:
            try:
                obj = Flavour.objects.create(name=f)
                self.stdout.write(f'    Created {obj}')
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'    Error: {e}'))
    
    def create_products_flavour_category(self):
        self.stdout.write(self.style.MIGRATE_LABEL('  FlavourCategory:'))
        categories = ['fruit', 'berry', 'menthol']
        for c in categories:
            try:
                obj = FlavourCategory.objects.create(name=c)
                self.stdout.write(f'    Created {obj}')
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'    Error: {e}'))

    def manage_products_add_flavours_to_categories(self):
        self.stdout.write(self.style.MIGRATE_LABEL(
            '  Add Flavours to Categories:'))
        cat_fruit = FlavourCategory.objects.get(name='fruit')
        cat_berry = FlavourCategory.objects.get(name='berry')
        cat_menthol = FlavourCategory.objects.get(name='menthol')

        fruit_flavours = Flavour.objects.filter(
            Q(name='apple')
            | Q(name='banana')
            | Q(name='cherry')
            | Q(name='strawberry')
            | Q(name='raspberry')
        )
        berry_flavours = Flavour.objects.filter(
            Q(name__icontains='berry')
        )
        menthol_flavours = Flavour.objects.filter(
            Q(name='menthol')
            | Q(name__icontains='mint')
        )

        if (cat_fruit is not None and len(fruit_flavours) > 0):
            for ff in fruit_flavours:
                cat_fruit.flavours.add(ff)
                self.stdout.write(f'    Added {ff} to {cat_fruit}')

        if (cat_berry is not None and len(berry_flavours) > 0):
            for bf in berry_flavours:
                cat_berry.flavours.add(bf)
                self.stdout.write(f'    Added {bf} to {cat_berry}')

        if (cat_menthol is not None and len(menthol_flavours) > 0):
            for mf in menthol_flavours:
                cat_menthol.flavours.add(mf)
                self.stdout.write(f'    Added {mf} to {cat_menthol}')