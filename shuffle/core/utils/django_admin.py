import logging
logger = logging.getLogger(__name__)

from django.apps import apps
from django.conf.urls import url, include

from django.conf import settings
from django.contrib import admin

def get_admin_model_class(using=None, tabular=False):
    BaseAdmin = admin.ModelAdmin
    
    if using is None:
        return BaseAdmin
    
    if tabular is True:
        BaseAdmin = admin.TabularInline
        
        class _MultiDBTabularInline(BaseAdmin):
            def get_queryset(self, request):
                return super(_MultiDBTabularInline, self).get_queryset(request).using(using)

            def formfield_for_foreignkey(self, db_field, request, **kwargs):
                return super(_MultiDBTabularInline, self).formfield_for_foreignkey(db_field, request, using=using, **kwargs)

            def formfield_for_manytomany(self, db_field, request, **kwargs):
                return super(_MultiDBTabularInline, self).formfield_for_manytomany(db_field, request, using=using, **kwargs)

        return _MultiDBTabularInline
    else:
        class _MultiDBModelAdmin(BaseAdmin):
            def save_model(self, request, obj, form, change):
                obj.save(using=using)

            def delete_model(self, request, obj):
                obj.delete(using=using)

            def get_queryset(self, request):
                return super(_MultiDBModelAdmin, self).get_queryset(request).using(using)

            def formfield_for_foreignkey(self, db_field, request, **kwargs):
                return super(_MultiDBModelAdmin, self).formfield_for_foreignkey(db_field, request, using=using, **kwargs)

            def formfield_for_manytomany(self, db_field, request, **kwargs):
                return super(_MultiDBModelAdmin, self).formfield_for_manytomany(db_field, request, using=using, **kwargs)

        return _MultiDBModelAdmin

def setup_admin_models(models, using=None, admin_site=None, tabular=False, overrides=None, list_per_page=35):
    if admin_site is None:
        admin_site = admin.site

    try:
        models = [
            Model 
                for (_, Model) in models.iteritems() 
                    if not admin_site.is_registered(Model) 
        ]
    except:
        models = []

    for Model in models:
        BaseAdminClass = get_admin_model_class(using=using, tabular=tabular)
        _model_name = "%s.%s" % (Model._meta.app_label, Model._meta.object_name)
        
        class ModelAdmin(BaseAdminClass):
            model = Model

        for (model_name, values) in (overrides or {}).iteritems():
            if (model_name == _model_name):
                for (key, value) in values.iteritems():
                    setattr(ModelAdmin, key, value)

        if ModelAdmin is not None:
            admin_site.register(Model, ModelAdmin)

def setup_admin_sites(admin_path, exclude_apps=None, using=None, overrides=None):
    url_patterns = []

    if exclude_apps is None:
        exclude_apps = []

    for (database_config_name, _) in (getattr(settings, 'DATABASES', {})).iteritems():
        if database_config_name is 'default':
            _admin_path = admin_path
        else:
            _admin_path = "%s/%s" % (database_config_name, admin_path)

        admin_site = admin.AdminSite(database_config_name)
        
        for app in apps.get_app_configs():
            if app.label not in exclude_apps:
                setup_admin_models(
                    apps.get_app_config(app.label).models, 
                    using=(using or database_config_name), 
                    admin_site=admin_site,
                    overrides=overrides
                )

        url_patterns.append(
            url(r'^%s/' % _admin_path, admin_site.urls)
        )

    return url_patterns