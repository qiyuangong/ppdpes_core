PPDP_Core
===========================

### Motivation 
Researches on data privacy have lasted for more than ten years, lots of great papers have been published. However, only a few open source projects are available on Internet [2-3], most open source projects are using algorithms proposed before 2004! Fewer projects have been used in real life. Worse more, most people even don't hear about it. Such a tragedy! 

I decided to make some effort. Hoping these open source repositories can help researchers and developers on data privacy (privacy preserving data publishing).

### Attention
I used **both adult and INFORMS** dataset in this implementation. For clarification, **we transform NCP to percentage**, making the NCP (information loss) more meaningful (NCP=2000 v.s. NCP=20%, the former one is sensitive to size of dataset, the latter one is suit for any dataset). This NCP percentage (also called GCP[4]) is computed by dividing NCP value with the number of values in dataset (the number of values can be treated as losing all information).


### Usage:
My Implementation is based on Python 2.7 (not Python 3.0). Please make sure your Python environment is collect installed. You can run Mondrian in following steps: 

1) Download (or clone) the whole project.

2) Check datasets and generalization hierarchies

    #dataset
    adult.data
    # gh for qid_index = 1
    adult_1.txt

3) Run "anonymized.py" in root dir with CLI.

	# run Mondrian with default K(K=10)
	python anonymizer.py 
	
	# run Mondrian with K=20
	python anonymized.py 20

4) Run unit test in root dir with CLI.

    # run all test cases ending with "_test.py" in test dir
    python -m unittest discover . "*_test.py"

5) Test Distribution:

    celery -A tasks worker --loglevel=info

6) Parameters

	# default anon
	['dataset', 'algorithm']
	# normal anon
	['dataset', 'algorithm', 'anon', {k:10, data:10000, qi:[1,2,3]}]
	# default eval
	['dataset', 'algorithm', 'eval', 'k']
	# normal eval
	['dataset', 'algorithm', 'eval', 'k', 'd', 'data']
	# algorithms:
	# High: Semi-Partition, NEC_k-member, NEC_OKA
	# Missing: KAIM, Enhanced-Mondrian, Semi-Partition-Incomplete
	# RT: APA, PAA, 1M-Generalization
	# dataset:
	# adult.data, informs.data, musk.data
	
7) JSON for PPDPES

    # anon JSON
	{"anon":{"k":10, "data": 1000, "d":[1,2,3]}}
    #eval JSON
	{"eval":["k", "d", "data"]}


## For more information:
[1] K. LeFevre, D. J. DeWitt, R. Ramakrishnan. Workload-aware Anonymization. Proceedings of the 12th ACM SIGKDD International Conference on Knowledge Discovery and Data Mining, ACM, 2006, 277-286


[2] [UTD Anonymization Toolbox](http://cs.utdallas.edu/dspl/cgi-bin/toolbox/index.php?go=home)

[3] [ARX- Powerful Data Anonymization](https://github.com/arx-deidentifier/arx)

[4] G. Ghinita, P. Karras, P. Kalnis, N. Mamoulis. Fast data anonymization with low information loss. Proceedings of the 33rd international conference on Very large data bases, VLDB Endowment, 2007, 758-769

==========================
by Qiyuan Gong
qiyuangong@gmail.com

2015-12-22
