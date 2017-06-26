from Round1.models import SystemClientConfig
from department.models import Department

SystemClientConfig.objects.all().delete()

try:
    config = SystemClientConfig()
    config.key = 'auto_honour_stock_transfer_requests'
    config.value = 'True'
    config.notes = 'Possible values True or False, Defalt: False'
    config.save()
    print('success auto_honour_stock_transfer_requests')
except Exception as e:
    print(e)

try:
    config = SystemClientConfig()
    config.key = 'auto_transfer_produced_items'
    config.value = 'True'
    config.notes = 'Possible values True or False, Defalt: False'
    config.save()
    print('success auto_transfer_produced_items')
except Exception as e:
    print(e)

try:
    config = SystemClientConfig()
    config.key = 'default_sale_department'
    config.value = Department.objects.get(id=1).id # Service
    config.notes = 'Id of the department for sale'
    config.save()
    print('success default_sale_department')
except Exception as e:
    print(e)
    print('add new department from django admin and run script again')

try:
    config = SystemClientConfig()
    config.key = 'default_production_department'
    config.value = Department.objects.get(id=2).id # Kitchen
    config.notes = 'Id of the department for production'
    config.save()
    print('success default_production_department')
except Exception as e:
    print(e)
    print('add new department from django admin and run script again')

