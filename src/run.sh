#!/bin/sh

python exp_size_wisconsin.py >& logs/exp_size_wisconsin.log &
python exp_k_wisconsin.py >& logs/exp_k_wisconsin.log &
python exp_error_dis_wisconsin.py >& logs/exp_dis_wisconsin.log &
# python exp_error_attrs_num_wisconsin.py >& logs/exp_error_attrs_num_wisconsin.log &
python exp_epsilon_wisconsin.py >& logs/exp_epsilon_wisconsin.log &
python exp_attrs_wisconsin.py >& logs/exp_attrs_wisconsin.log &

