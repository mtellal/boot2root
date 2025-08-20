#!/bin/bash

declare -A fragments

for file in "ft_fun"/*.pcap; do
    last_line=$(tail -n 1 "$file")
    # echo $last_line
    index="${last_line#//file}"
    # echo $index
    content=$(head -n -1 "$file")
    # echo "$index :$content"
    fragments[$index]="$content"
done

for index in $(printf "%s\n" "${!fragments[@]}" | sort -n); do
    echo "${fragments[$index]}" >> "main.c"
done