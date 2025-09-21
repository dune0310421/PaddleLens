#!/bin/bash

source ./venv/bin/activate


owners=("aaPanel" "PaddlePaddle" "pytorch" "tensorflow")
repos=("BillionMail" "Paddle" "pytorch" "tensorflow")
labels=("enhancement" "type/feature-request" "feature" "type:feature")
days=90

mkdir -p logs

for i in "${!owners[@]}"
do
    echo "=============================="
    echo "Run #$((i+1)) at $(date)"
    echo "Parameters: ${owners[$i]} ${repos[$i]} ${labels[$i]}"
    echo "=============================="
    
    python getdata.py "${owners[$i]}"/"${repos[$i]}" --days $days --label "${labels[$i]}"> logs/run_$((i+1)).log 2>&1

done

echo "All 3 runs finished!"