ssh mcc3 "rm -rf BlindControl && mkdir BlindControl"
cd ../ || exit 1
scp -r experiments jabj22@student.aau.dk@deis-mcc3-fe01.srv.aau.dk:~/BlindControl/
scp -r scripts jabj22@student.aau.dk@deis-mcc3-fe01.srv.aau.dk:~/BlindControl/
scp -r data jabj22@student.aau.dk@deis-mcc3-fe01.srv.aau.dk:~/BlindControl/
scp -r main_train.py jabj22@student.aau.dk@deis-mcc3-fe01.srv.aau.dk:~/BlindControl/