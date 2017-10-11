#coding:utf-8
import argparse, json

# These values don't influence results
M = 2452621694 #ClueWeb12(NotWS)
N = 113209447 #ClueWeb12(NotWS)

def main():
    parser = argparse.ArgumentParser()
    # necessary files
    parser.add_argument('-f', '--copafile', type=str, default="copa-file.txt", help="")
    parser.add_argument('-word_comb_file', type=str, default="word_comb_file.json", help="")
    parser.add_argument('-json_dic', type=str, nargs=3, 
        help="set 3 json-dictionary (cause-effect-cooccurence-frequency dic, cause-word-frequency dic, effect-word-frequency dic)")
    parser.add_argument('-vc', '--c_vocab', type=str, help="sorted vocablary file for cause word")
    parser.add_argument('-vr', '--r_vocab', type=str, help="sorted vocablary file for result word")

    # option
    parser.add_argument('-p', '--Print', action='store_true', help="print result details")

    # hyper parameter
    parser.add_argument('-l', type=float, default=1.0, help="lambda")
    parser.add_argument('-a', '--alpha', type=float, default=0.66, help="alpha")
    parser.add_argument('-t', '--high_freq_threshold', type=int, default=10, help="index point you want to filter")
    args = parser.parse_args()

    print "loading data..."
    solver = Solver(args)
    data = Data(args)
    print '# causal words: {}'.format(len(data.c_dic))
    print '# result words: {}'.format(len(data.r_dic))
    print "___SOLVE COPA___"
    solver.solve_copa(data, args)
    print "___Fin___"

class Data:
    def __init__(self,args):
        self.word_comb = json.load(open(args.word_comb_file,"r"))
        self.copa_f = open(args.copafile,"r")
        self.c_r_dic = json.load(open(args.json_dic[0],"r"))
        self.c_dic = json.load(open(args.json_dic[1],"r"))
        self.r_dic = json.load(open(args.json_dic[2],"r"))

    def cal_cs(self, c_word, r_word, c_idx, r_idx, threshold=10, l=1.0, alpha=0.66):
        if c_idx < threshold or r_idx < threshold:
            return None
        try:
            p_c_r = int(self.c_r_dic["{}:{}".format(c_word, r_word)]) /float(N)
        except:
            cs = 0.0
            return cs
        try:
            p_c = int(self.c_dic[c_word]) /float(M)
            p_r = int(self.r_dic[r_word]) /float(M)
            cs_nec = p_c_r/ (float(pow(p_c, alpha)) * float(p_r))
            cs_suf = p_c_r/ (float(pow(p_r, alpha)) * float(p_c))
            cs = pow(cs_nec, l) * pow(cs_suf, 1-l)
        except:
            cs = 0.0
        return cs

class Solver:
    def __init__(self,args):
        # word list
        self.fwd_c = [line.strip().split('\t')[1] for line in open(args.c_vocab)] 
        self.fwd_r = [line.strip().split('\t')[1] for line in open(args.r_vocab)]

        # dictionary: key = word, value = index
        self.bwd_c = dict((s, i) for i, s in enumerate(self.fwd_c))
        self.bwd_r = dict((s, i) for i, s in enumerate(self.fwd_r))

    def disp(self, args, i, cols, altcombs1, altcombs2, disp_dic,cause_or_effect, ans,
                  norm1, norm2, cs_score1, cs_score2, sys_ans,data):
        if args.Print:
            print "-"*100
            print "Question {}".format(i+1)
            print "Premise      : {}".format(cols[0])
            print "Alternative 1: {}".format(cols[1])
            print "Alternative 2: {}".format(cols[2])
            print "Question Type: {}".format(cause_or_effect)
            print "Answer       : {}".format(ans)
            print ""
            print "__CAUSE__".ljust(17),"__RESULT__       _CS_      FREQ_C_R FREQ_C   FREQ_R"
            for k,tup in sorted(disp_dic.items()):
                for e in tup:
                    print "{} {} {}    {} {} {}".format(
                        e[0].ljust(17), e[1].ljust(16), str(e[2])[0:5].ljust(6), str(e[3]).ljust(8), str(e[4]).ljust(8), e[5])
                print ""
            print "norm1 = {} norm2 = {}".format(str(norm1).ljust(3), norm2)
            print "score1  = {}   score2  = {}".format(str(cs_score1)[0:6], str(cs_score2)[0:6]),
            print "  cs_gap = {}".format(abs(float(str(cs_score1)[0:6])-float(str(cs_score2)[0:6])))
            print ""
            if sys_ans == ans:
                print "--------correct--------"
 

    def cal_score(self, altcombs, i, data, disp_dic, args,cause_or_effect):
        cs_score = 0.0
        cs_none_count = 0
        for key in altcombs:
            c, r = key.split(":")
            # set frequency
            try:
                freq_c = data.c_dic[c]
            except:
                freq_c = None
            try:
                freq_r = data.r_dic[r]
            except:
                freq_r = None
            try:
                freq_c_r = int(data.c_r_dic[key])
            except:
                freq_c_r = 0

            # set index
            try:
                c_idx = int(self.bwd_c[c])
            except:
                c_idx = -1
            try:
                r_idx = int(self.bwd_r[r])
            except:
                r_idx = -1

            # calculate cs
            cs = data.cal_cs(c, r, c_idx, r_idx, args.high_freq_threshold, args.l, args.alpha)
            if cs == None:
                cs_none_count += 1
            else:
                cs_score += cs
            
            disp_dic["alt{}".format(i)] += [(c, r, cs, freq_c_r, freq_c, freq_r)]

        return cs_score, cs_none_count

    def solve_copa(self, data, args):
        test_count, dev_count, cs_count = 0, 0, 0

        # OPTIONAL:
        cause_dev_correct, cause_test_correct = 0, 0
        cause_dev_count, cause_test_count = 0, 0
        effect_dev_correct, effect_test_correct = 0, 0
        effect_dev_count, effect_test_count = 0, 0

        for i, line in enumerate(data.copa_f):
            disp_dic = {"alt1":[],"alt2":[]}

            # load data
            cols = line.strip().split("\t")
            cause_or_effect, ans = cols[3], int(cols[4])
            altcombs1, altcombs2 = data.word_comb[i][0], data.word_comb[i][1]

            # calculate scores
            cs_score1, cs_none_count1 = self.cal_score(altcombs1, 1, data,disp_dic, args, cause_or_effect)
            cs_score2, cs_none_count2 = self.cal_score(altcombs2, 2, data,disp_dic, args, cause_or_effect)

            # set term of normalization
            norm1, norm2 = len(altcombs1)-cs_none_count1, len(altcombs2)-cs_none_count2 

            # normalization
            if norm1 != 0:
                cs_score1  = cs_score1  / float(norm1)
            if norm2 != 0:
                cs_score2  = cs_score2  / float(norm2)
            score1, score2 = cs_score1, cs_score2

            # choose ansewer
            sys_ans = 1 if score1 > score2 else 2

            # evaluate the ansewer
            if i < 500: # for development set
                if score1 == score2:
                    dev_count += 0.5
                else:
                    if sys_ans == ans:
                        dev_count += 1
                    
            else: # for test set
                if score1 == score2:
                    test_count += 0.5
                else:
                    if sys_ans == ans:
                        test_count += 1

            # OPTIONAL: evaluate the answer according to the question type
            if cause_or_effect == "cause":
                if i < 500: # for cause question of development set
                    cause_dev_count += 1
                    if score1 == score2:
                        cause_dev_correct += 0.5
                    else:
                        if sys_ans == ans:
                            cause_dev_correct += 1

                else: # for cause question of test set
                    cause_test_count += 1
                    if score1 == score2:
                        cause_test_correct += 0.5
                    else:
                        if sys_ans == ans:
                            cause_test_correct += 1

            if cause_or_effect == "effect":
                if i < 500: # for effect question of development set
                    effect_dev_count += 1
                    if score1 == score2:
                        effect_dev_correct += 0.5
                    else:
                        if sys_ans == ans:
                            effect_dev_correct += 1

                else: # for effect question of test set
                    effect_test_count += 1
                    if score1 == score2:
                        effect_test_correct += 0.5
                    else:
                        if sys_ans == ans:
                            effect_test_correct += 1

            # print the results' detail
            self.disp(args, i, cols, altcombs1, altcombs2, disp_dic, cause_or_effect, ans,
                      norm1, norm2, cs_score1, cs_score2, sys_ans, data)

        print "development_set Qtype:cause correct_count = {}, accuracy = {}".format(cause_dev_correct, cause_dev_correct / float(cause_dev_count))
        print "development_set Qtype:effect correct_count = {}, accuracy = {}".format(effect_dev_correct, effect_dev_correct / float(effect_dev_count))
        print "test_set Qtype:cause correct_count = {}, accuracy = {}".format(cause_test_correct, cause_test_correct / float(cause_test_count))
        print "test_set Qtype:effect correct_count = {}, accuracy = {}".format(effect_test_correct, effect_test_correct / float(effect_test_count))
        print ""
        print "dev  total = {} dev  accuracy = {}".format(dev_count, dev_count/500.0)
        print "test total = {} test accuracy = {}".format(test_count, test_count/500.0)

if __name__ == '__main__':
    main()
