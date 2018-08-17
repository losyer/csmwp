### How to run
- $`cd <PATH_TO_REPOSITORY>`
- $`python bin/solve_copa.py -f data/copa-file.txt -word_comb_file data/word_comb_file_with_mwp.json -json_dic data/freq_dic/c_r_dic_with_mwp.json data/freq_dic/c_dic_with_mwp.json data/freq_dic/r_dic_with_mwp.json -vc data/vocabulary/vocab_c_with_mwp.tsv -vr data/vocabulary/vocab_r_with_mwp.tsv -l 0.7`

### How to use
- $`python solve_copa.py -f copa-file_path -word_comb_file word-comb-file_path -json_dic dic1 dic2 dic3 -vc vocabulary-file_path1 -vr vocabulary-file_path2`

#### Note:
It is impossible to run this code on Python3.

#### Set your files' paths
-f
- Set your copa-file path.
- You can use my file: copa-file.txt

-word_comb_file
- Set your path of word combinations file(JSON).
- You can use my file: word_comb_file.json or word_comb_file_with_mwp.json

-json_dic
- Set your paths of 3 json-dictionary files(cause-result-cooccurence-frequency dic, cause-word-frequency dic, result-word-frequency dic).

-vc
- Set path of sorted vocabulary file for cause word.

-vr
- Set path of sorted vocabulary file for result word.

##### Hyper parameter:
-l
- Set float value for lambda in CS equation.

-a
- Set float value for alpha in CS equation.

-t
- Set int value for threshold for filtering high frequency terms.
- If you filter top-10 frequent words, set this value to be 10.

##### OPTIONAL:
-p
- Option to print results' detail.


### ---JSON DICTIONARY FILE DETAILE
cause-result-cooccurence-frequency dic:
    key = "cause_word:result_word"
    value = frequency of cooccurence

cause(result)-word-frequency dic:
    key = "cause(result)_word"
    value = frequency of occurence


### ---VOCABLARY FILE EXAMPLE
Frequency\tWord
- $cat vocabulary.tsv

16283892        use

14674044        want

13099278        make

12503586        know

...

