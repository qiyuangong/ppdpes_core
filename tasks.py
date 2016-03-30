from celery import Celery
from anonymizer import universe_anonymizer
import json

app = Celery('ppdpes', backend='amqp' ,broker="amqp://jssec:ibmc51@dark.qygong.net//")

@app.task
def eval(eval_parameters):
    result =  universe_anonymizer(eval_parameters)
    # eval_result = Eval_Result.objects.get(pk=eval_id)
    return json.dumps(result)


@app.task
def anon(key, anon_parameters):
    result, eval_r = universe_anonymizer(anon_parameters)
    anon_url = "tmp/" + str(key) + ".txt"
    anon_r = dict()
    anon_r['url'] = anon_url
    anon_r['ncp'] = eval_r[0]
    anon_r['time'] = eval_r[1]
    # anon_file = open(anon_url, 'w')
    # for record in result:
    #     try:
    #         line = ';'.join(record) + '\n'
    #     except:
    #         line = ';'.join(record[:-1]) + '|' + ';'.join(record[-1]) + '\n'
    #     anon_file.write(line)
    # anon_file.close()
    # anon_result = Anon_Result.objects.get(pk=anon_id)
    return json.dumps(anon_r)