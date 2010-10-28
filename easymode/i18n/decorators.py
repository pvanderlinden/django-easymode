import logging
import os
import sys

from django.conf import settings

from easymode import i18n
from easymode.i18n import meta

MODEL_IMPORTED_TWICE = """\
%s allready has a localized_fields attribute, with
exactly the same values as the fields you are trying to internationalize,

%s

Most likely your models module was imported twice, which could be because
you are in the middle of an exception and the stack is unwinding, Or maybe a
cyclic import. Instead of causing another error, I will simply return the
%s as it was, since it was allready internationalized.

Please report this freak accident to easymode@librelist.com
"""
__all__ = ('I18n',)

class I18n(object):
    """
    Internationalise a model class.
    
    use like this:
    
    >>> from django.db import models
    >>> from easymode.i18n.decorators import I18n
    >>> 
    >>> @I18n('iamatranslatedfield')
    >>> class Bla(models.Model):
    >>>     iamafield = models.CharField(max_length=255)
    >>>     iamatranslatedfield = models.CharField(max_length=255)
    
    Now ``iamatranslatedfield`` it's value can vary by language.
    """
    def __init__(self, *localized_fields):
        """initialize the decorator"""
        self.localized_fields = localized_fields
        
    def __call__(self, cls):
        """Executes the decorator on the cls."""
        
        if hasattr(cls, 'localized_fields'):
            if cls.localized_fields == self.localized_fields:
                logging.error(MODEL_IMPORTED_TWICE % (cls.__name__,
                    cls.localized_fields, cls.__name__))
                return cls
            else:
                logging.warning("%s allready has the following internationalized\
                    fields %s" % (cls.__name__, cls.localized_fields))
        
        cls = meta.localize_fields(cls, self.localized_fields)
        
        if getattr(settings, 'AUTO_CATALOG', False):
            model_dir = os.path.dirname(sys.modules[cls.__module__].__file__) + getattr(settings, 'LOCALE_POSTFIX', '')
            i18n.register(cls, getattr(settings, 'LOCALE_DIR', None) or model_dir )
        
        # add permission for editing the untranslated fields in this model
        cls._meta.permissions.append(
            ("can_edit_untranslated_fields_of_%s" % cls.__name__.lower(), 
            "Can edit untranslated fields")
        )

        return cls
