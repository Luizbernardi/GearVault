# Gera um diagrama de classes dos models Django usando graphviz
# Salve este script como gerar_diagrama.py e execute com: python gerar_diagrama.py

import os
from django.conf import settings
from django.apps import apps
from graphviz import Digraph

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
import django
django.setup()

def main():
    dot = Digraph(comment='Diagrama de Models')
    dot.attr(rankdir='LR')
    for model in apps.get_models():
        label = f"{model.__name__}\\n"
        for field in model._meta.fields:
            label += f"{field.name}: {field.get_internal_type()}\\l"
        dot.node(model.__name__, label, shape='box', style='filled', fillcolor='lightyellow')
    for model in apps.get_models():
        for field in model._meta.fields:
            if field.is_relation and field.related_model:
                dot.edge(model.__name__, field.related_model.__name__, label=field.name)
    dot.render('diagrama_models', format='png', view=True)

if __name__ == '__main__':
    main()
