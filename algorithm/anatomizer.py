import random, heapq
import pdb

# by Qiyuan Gong
# qiyuangong@gmail.com

# @INPROCEEDINGS{
#   author = {Xiao, Xiaokui and Tao, Yufei},
#   title = {Anatomy: simple and effective privacy preservation},
#   booktitle = {Proceedings of the 32nd international conference on Very large data
#     bases},
#   year = {2006},
#   series = {VLDB '06},
#   pages = {139--150},
#   publisher = {VLDB Endowment},
#   acmid = {1164141},
#   location = {Seoul, Korea},
#   numpages = {12}
# }


_DEBUG = True

class SABucket(object):

    def __init__(self, data_index, index):
        self.member_index = data_index[:]
        self.index = index

    def pop_element(self):
        """pop an element from SABucket
        """
        return self.member_index.pop()


class Group(object):

    def __init__(self):
        self.index = 0
        self.member_index = []
        self.checklist = set()

    def add_element(self, record_index, index):
        """add element pair (record, index) to Group
        """
        self.member_index.append(record_index)
        self.checklist.add(index)

    def check_index(self, index):
        """Check if index is in checklist
        """
        if index in self.checklist:
            return True
        return False


def list_to_str(value_list, sep=';'):
    """covert sorted str list (sorted by default) to str 
    value (splited by sep). This fuction is value safe, which means 
    value_list will not be changed.
    """
    temp = value_list[:]
    return sep.join(temp)


def anatomizer(data, L):
    """
    only one SA is supported in anatomy.
    Separation grouped member into QIT and SAT
    Use heap to get l largest buckets
    L is the denote l in l-diversity.
    data is a list, i.e. [qi1,qi2,sa]
    """
    groups = []
    buckets = {}
    result = []
    suppress = []
    h = []
    if _DEBUG:
        print '*' * 10
        print "Begin Anatomizer!"
    print "L=%d" % L
    # Assign SA into buckets
    for i, temp in enumerate(data):
        # convert list to str
        list_temp = list_to_str(temp[-1])
        try:
            buckets[list_temp].append(i)
        except:
            buckets[list_temp] = [i]
    # group stage
    # use heap to sort buckets
    for i, temp in enumerate(buckets.values()):
        # push to heap reversely
        pos = len(temp) * -1
        if pos == 0:
            continue
        heapq.heappush(h, (pos, SABucket(temp, i)))
    while len(h) >= L:
        newgroup = Group()
        length_list = []
        SAB_list = []
        # chosse l largest buckets
        for i in range(L):
            (length, temp) = heapq.heappop(h)
            length_list.append(length)
            SAB_list.append(temp)
        # pop a element from chosen buckets
        for i in range(L):
            temp = SAB_list[i]
            length = length_list[i]
            newgroup.add_element(temp.pop_element(), temp.index)
            length += 1
            if length == 0:
                continue
            # push new tuple to heap
            heapq.heappush(h, (length, temp))
        groups.append(newgroup)
    # residue-assign stage
    while len(h):
        (length, temp) = heapq.heappop(h)
        index = temp.index
        while temp.member_index:
            for g in groups:
                if g.check_index(index) == False:
                    g.add_element(temp.pop_element(), index)
                    break
            else:
                suppress.extend(temp.member_index[:])
                break
    # transform result
    for i, t in enumerate(groups):
        t.index = i
        result.append(t.member_index[:])
    if _DEBUG:
        print 'NO. of Suppress after anatomy = %d' % len(suppress)
        print 'NO. of groups = %d' % len(result)
    return result







