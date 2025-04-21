Trebe sa instalezi git local. din cmd verifica daca s-o instalat(ruleaza git -v in terminal)
Fa un folder nou si in el, deschide terminalul(sa fii cu working directory-u in folder)
Fa comenzile astea ca sa-ti tragi proiectu:
	git init
	git remote add origin https://github.com/Maesstru/dvd_mpp.git
	git pull origin master




Trebe sa iti instalezi docker-desktop(necesita un restart la laptop)
Dupa care rulezi pe rand comenzile astea de mai jos.
Trebe sa fii in directorul cu git, adica directorul cu fisierul *Dockerfile.dev*



docker build -f Dockerfile.dev -t dvd:dev . #1

docker run --name parnaie -d -p 8000:8000 dvd:dev #2

docker exec -it parnaie python manage.py makemigrations #3

docker exec -it parnaie python manage.py migrate #4