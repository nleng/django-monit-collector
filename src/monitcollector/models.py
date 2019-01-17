from django.db import models
from xml.dom import minidom
import json
import time
from django.conf import settings

monit_update_period = getattr(settings, 'MONIT_UPDATE_PERIOD', 60)
maximum_store_days = getattr(settings, 'MAXIMUM_STORE_DAYS', 7)

"""
from the monit source code (monit/contrib/wap.php):
//For conversion of status codes to text
$event[0] = 'OK';
$event[1] = 'Checksum failed';
$event[2] = 'Resource limit matched';
$event[4] = 'Timeout';
$event[8] = 'Timestamp failed';
$event[16] = 'Size failed';
$event[32] = 'Connection failed';
$event[64] = 'Permission failed';
$event[128] = 'UID failed';
$event[256] = 'GID failed';
$event[512] = 'Does not exist';
$event[1024] = 'Invalid type';
$event[2048] = 'Data access error';
$event[4096] = 'Execution failed';
$event[8192] = 'Changed';
$event[16384] = 'ICMP failed';
$monitored[0] = 'No';
$monitored[1] = 'Yes';
$monitored[2] = 'Init';
"""

def collect_data(xml_str):
    # only ready data if it has a monit id
    try:
        xmldoc = minidom.parseString(xml_str)
        monit_id = xmldoc.getElementsByTagName('monit')[0].attributes["id"].value
    except:
        return False
    
    Server.update(xmldoc, monit_id)
    return True

def decode_status(status):
    errors_messages = ['Ok', 'Checksum failed', 'Resource limit matched', 'Timeout', 'Timestamp failed', 'Size failed',
              'Connection failed', 'Permission failed', 'UID failed', 'GID failed', 'Does not exist',
              'Invalid type', 'Data access error', 'Execution failed', 'Changed', 'ICMP failed']
    # choice_monitor = ['No', 'Yes', 'Init']
    # format to a bitarray
    bits = '{0:015b}'.format(status)
    out_str = ''
    ok = True
    for i in range(len(bits)):
        if bits[i] == "1":
            if not ok:
                out_str += ", "
            out_str += errors_messages[-i-1]
            ok = False
    if ok:
        return "running"
    return out_str
    
def get_value(xmldoc, parent_element="", child_element="", attribute=""):
  try:
    if parent_element == "" and attribute == "":
      element = xmldoc.childNodes[0]
    elif parent_element == "":
      element = xmldoc
    elif child_element == "":
      # first index, because there could be multiple Elements with that tag, second index because there could be multiple childNodes
      element = xmldoc.getElementsByTagName(parent_element)[0].childNodes[0]
    else:
      element = xmldoc.getElementsByTagName(parent_element)[0].getElementsByTagName(child_element)[0].childNodes[0]
    if attribute == "":
      return element.nodeValue
    else:
      return element.attributes[attribute].value
  except:
    # monit sometimes does not pass cpu/memory info (e.g. if it sends event messages), so we have to filter it
    return "none"

def json_list_append(json_list, value):
    try:
      new_list = json.loads(json_list)
      new_list.append(value)
    except:
      new_list = [value]
    # maximum allowed table size, if monit reports every monite, this stores data for one week
    maximum_table_length = int(maximum_store_days*24.*60.*60./monit_update_period)
    # just remove the first one, should be better in future
    if len(new_list) > maximum_table_length:
      new_list = new_list[-int(maximum_table_length):]
    return json.dumps(new_list)

def remove_old_services(server, service_list):
    if server.system.name not in service_list:
        server.system.delete()
    processes = server.process_set.all()
    for process in processes:
        if process.name not in service_list:
            process.delete()


class Server(models.Model):
    monit_id = models.CharField(max_length=32, unique=True)
    monit_version = models.TextField(null=True)
    localhostname = models.TextField(null=True)
    uptime = models.IntegerField(null=True)
    address = models.TextField(null=True)
    
    @classmethod
    def update(cls, xmldoc, monit_id):
        reporting_services = []
        server, created = cls.objects.get_or_create(monit_id=monit_id)
        server.monit_version = xmldoc.getElementsByTagName('monit')[0].attributes["version"].value
        server.localhostname = get_value(xmldoc, "localhostname", "")
        server.uptime = get_value(xmldoc, "server", "uptime")
        server.address = get_value(xmldoc, "server", "address")
        server.save()
        Platform.update(xmldoc, server)
        for service in xmldoc.getElementsByTagName('services')[0].getElementsByTagName('service'):
            service_type = get_value(service, "type", "")
            service_name = get_value(service, "", "", "name")
            reporting_services.append(service_name)
            # properties for type=5 (system)
            if service_type == '5':
                System.update(xmldoc, server, service)
            # we call everything else a Process, not only type=3
            else:
                Process.update(xmldoc, server, service)
        remove_old_services(server, reporting_services)

class Platform(models.Model):
    server = models.OneToOneField('Server')
    name = models.TextField(null=True)
    release = models.TextField(null=True)
    version = models.TextField(null=True)
    machine = models.TextField(null=True)
    cpu = models.IntegerField(null=True)
    memory = models.IntegerField(null=True)
    swap = models.IntegerField(null=True)
    @classmethod
    def update(cls, xmldoc, server):
        platform, created = Platform.objects.get_or_create(server=server)
        platform.name = get_value(xmldoc, "platform", "name")
        platform.release = get_value(xmldoc, "platform", "release")
        platform.version = get_value(xmldoc, "platform", "version")
        platform.machine = get_value(xmldoc, "platform", "machine")
        platform.cpu = get_value(xmldoc, "platform", "cpu")
        platform.memory = get_value(xmldoc, "platform", "memory")
        platform.swap = get_value(xmldoc, "platform", "swap")
        platform.save()

# Service
class Service(models.Model):
    # not unique since there could be multiple server with service 'nginx', etc.
    name = models.TextField()
    status = models.TextField(null=True)
    status_hint = models.IntegerField(null=True)
    monitor = models.IntegerField(null=True)
    monitormode = models.IntegerField(null=True)
    pendingaction = models.IntegerField(null=True)

# Service type=5
class System(Service):
    server = models.OneToOneField('Server')
    date_last = models.PositiveIntegerField(null=True)
    date = models.TextField(null=True)
    load_avg01_last = models.FloatField(null=True)
    load_avg01 = models.TextField(null=True)
    load_avg05_last = models.FloatField(null=True)
    load_avg05 = models.TextField(null=True)
    load_avg15_last = models.FloatField(null=True)
    load_avg15 = models.TextField(null=True)
    cpu_user_last = models.FloatField(null=True)
    cpu_user = models.TextField(null=True)
    cpu_system_last = models.FloatField(null=True)
    cpu_system = models.TextField(null=True)
    cpu_wait_last = models.FloatField(null=True)
    cpu_wait = models.TextField(null=True)
    memory_percent_last = models.FloatField(null=True)
    memory_percent = models.TextField(null=True)
    memory_kilobyte_last = models.PositiveIntegerField(null=True)
    memory_kilobyte = models.TextField(null=True)
    swap_percent_last = models.FloatField(null=True)
    swap_percent = models.TextField(null=True)
    swap_kilobyte_last = models.PositiveIntegerField(null=True)
    swap_kilobyte = models.TextField(null=True)
    
    @classmethod
    def update(cls, xmldoc, server, service):
        system, created = cls.objects.get_or_create(server=server)
        system.name = get_value(service, "", "", "name")
        system.status = decode_status(int(get_value(service, "status", "")))
        system.status_hint = get_value(service, "status_hint", "")
        system.monitor = get_value(service, "monitor", "")
        system.monitormode = get_value(service, "monitormode", "")
        system.pendingaction = get_value(service, "pendingaction", "")
        if get_value(service, "load", "avg01") != "none":
            system.date_last = int(time.time())
            system.date = json_list_append(system.date, system.date_last)
            system.load_avg01_last = float(get_value(service, "load", "avg01"))
            system.load_avg01 = json_list_append(system.load_avg01, system.load_avg01_last)
            system.load_avg05_last = float(get_value(service, "load", "avg05"))
            system.load_avg05 = json_list_append(system.load_avg05, system.load_avg05_last)
            system.load_avg15_last = float(get_value(service, "load", "avg15"))
            system.load_avg15 = json_list_append(system.load_avg15,  system.load_avg15_last)
            system.cpu_user_last = float(get_value(service, "cpu", "user"))
            system.cpu_user = json_list_append(system.cpu_user, system.cpu_user_last)
            system.cpu_system_last = float(get_value(service, "cpu", "system"))
            system.cpu_system = json_list_append(system.cpu_system, system.cpu_system_last)
            system.cpu_wait_last = float(get_value(service, "cpu", "wait"))
            system.cpu_wait = json_list_append(system.cpu_wait, system.cpu_wait_last)
            system.memory_percent_last = float(get_value(service, "memory", "percent"))
            system.memory_percent = json_list_append(system.memory_percent, system.memory_percent_last)
            system.memory_kilobyte_last = int(get_value(service, "memory", "kilobyte"))
            system.memory_kilobyte = json_list_append(system.memory_kilobyte, system.memory_kilobyte_last)
            system.swap_percent_last = float(get_value(service, "swap", "percent"))
            system.swap_percent = json_list_append(system.swap_percent, system.swap_percent_last)
            system.swap_kilobyte_last = int(get_value(service, "swap", "kilobyte"))
            system.swap_kilobyte = json_list_append(system.swap_kilobyte, system.swap_kilobyte_last)
        system.save()

# we call everything else a Process, not only type=3
class Process(Service):
    server = models.ForeignKey('Server')
    date_last = models.PositiveIntegerField(null=True)
    date = models.TextField(null=True)
    pid = models.IntegerField(null=True)
    ppid = models.IntegerField(null=True)
    uptime = models.PositiveIntegerField(null=True)
    children = models.PositiveIntegerField(null=True)
    cpu_percenttotal_last = models.FloatField(null=True)
    cpu_percenttotal = models.TextField(null=True)
    memory_percenttotal_last = models.FloatField(null=True)
    memory_percenttotal = models.TextField(null=True)
    memory_kilobytetotal_last = models.PositiveIntegerField(null=True)
    memory_kilobytetotal = models.TextField(null=True)
    
    @classmethod
    def update(cls, xmldoc, server, service):
        service_name = get_value(service, "", "", "name")
        process, created = cls.objects.get_or_create(server=server,name=service_name)
        process.status = decode_status(int(get_value(service, "status", "")))
        process.status_hint = get_value(service, "status_hint", "")
        process.monitor = get_value(service, "monitor", "")
        process.monitormode = get_value(service, "monitormode", "")
        process.pendingaction = get_value(service, "pendingaction", "")
        if get_value(service, "cpu", "percent") != "none":
            process.pid = get_value(service, "pid")
            process.ppid = get_value(service, "ppid")
            process.uptime = get_value(service, "uptime")
            process.children = get_value(service, "children")
            # needs less characters than datetime.now().ctime() or datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            process.date_last = int(time.time())
            process.date = json_list_append(process.date, process.date_last)
            process.cpu_percenttotal_last = float(get_value(service, "cpu", "percenttotal"))
            process.cpu_percenttotal = json_list_append(process.cpu_percenttotal, process.cpu_percenttotal_last)
            process.memory_percenttotal_last = float(get_value(service, "memory", "percenttotal"))
            process.memory_percenttotal = json_list_append(process.memory_percenttotal, process.memory_percenttotal_last)
            process.memory_kilobytetotal_last = int(get_value(service, "memory", "kilobytetotal"))
            process.memory_kilobytetotal = json_list_append(process.memory_kilobytetotal, process.memory_kilobytetotal_last)
        process.save()

########## who needs groups? ##########

# for servicegroup in xmldoc.getElementsByTagName('servicegroups')[0].getElementsByTagName('servicegroup'):
#   servicegroup_name = get_value(servicegroup, "", "", "name")
#   for service in servicegroup.getElementsByTagName('service'):
#     service_name = get_value(service)
#     print servicegroup_name, service_name

