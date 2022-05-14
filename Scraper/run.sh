#!/bin/bash

:<<'END'

Status Code

0: 정상 종료
1: 예상치 못한 비정상 종료
2: 매개변수 오류
3: 사용자 종료(Keyboard Interrupt)
4: 재실행 가능한 오류
143: kill

END

exitCode=1

echo "Scraper start"

python main.py $@
exitCode=$?

while [ "$exitCode" -eq 4 ]
do
    echo 'Scraper abnormally closed'
    sleep 5
    echo "Scraper restart"
    python main.py $1 "continue"
done

if [ "$exitCode"  -eq 0 ] || [ "$exitCode" -eq 143 ] ; then
    echo "Scraper well Terminated"
    echo 'Thank you!'
else
    echo "Scraper bad Terminated"
    echo "Sorry.."
fi