from celery import Celery, shared_task
from celery.task.http import URL
from anonymizer import universe_anonymizer
import json


__DEBUG = True

if __DEBUG:
    HOST = '223.3.82.45'
else:
    HOST = 'dark.qygong.net'

app = Celery('tasks', backend='amqp' ,broker='amqp://jssec:ibmc51@' + HOST + '//')

# CALL_BACK_URL = 'http://223.3.82.45:8000/PPDP/task_update'
CALL_BACK_URL = 'http://' + HOST + ':8000/PPDP/task_update'

@shared_task(name='PPDP.tasks.eval')
def eval(task_id, eval_parameters):
    result =  universe_anonymizer(eval_parameters)
    # end_time = datetime.datetime.now()
    URL(CALL_BACK_URL).get_async(task_id=task_id, result=json.dumps(result['k']))
    # return json.dumps(result), end_time


@shared_task(name='PPDP.tasks.anon')
def anon(task_id, key, anon_parameters):
    result, eval_r = universe_anonymizer(anon_parameters)
    # end_time = datetime.datetime.now()
    anon_url = "tmp/" + str(key) + ".txt"
    anon_r = dict()
    anon_r['url'] = anon_url
    anon_r['ncp'] = eval_r[0]
    anon_r['time'] = eval_r[1]
    URL(CALL_BACK_URL).get_async(task_id=task_id, result=json.dumps(anon_r))
    # anon_file = open(anon_url, 'w')
    # for record in result:
    #     try:
    #         line = ';'.join(record) + '\n'
    #     except:
    #         line = ';'.join(record[:-1]) + '|' + ';'.join(record[-1]) + '\n'
    #     anon_file.write(line)
    # anon_file.close()
    # anon_result = Anon_Result.objects.get(pk=anon_id)
    # return json.dumps(anon_r), end_time