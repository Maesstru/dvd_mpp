Trebe sa instalezi git local. din cmd verifica daca s-o instalat(ruleaza git -v in terminal)
Fa un folder nou si in el, deschide terminalul(sa fii cu working directory-u in folder)
Fa comenzile astea ca sa-ti tragi proiectu:
+ `git init`
+ `git remote add origin https://github.com/Maesstru/dvd_mpp.git`
+ `git pull origin master`

Trebe sa iti instalezi docker-desktop(necesita un restart la laptop)
Dupa care rulezi pe rand comenzile astea de mai jos.
Trebe sa fii in directorul cu git, adica directorul cu fisierul *Dockerfile.dev*
+ `docker-compose up -d`
+ `docker exec -it parnaie python manage.py makemigrations`
+ `docker exec -it parnaie python manage.py migrate`
### Acum proiectul ruleaza pe `http://localhost:8000/`
