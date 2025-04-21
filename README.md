Trebe sa iti instalezi docker-desktop(necesita un restart la laptop)
Dupa care rulezi pe rand comenzile astea de mai jos.
Trebe sa fii in directorul cu git, adica directorul cu fisierul *Dockerfile.dev*



docker build -f Dockerfile.dev -t dvd:dev . #1

docker run --name parnaie -d -p 8000:8000 dvd:dev #2

docker exec -it parnaie python manage.py makemigrations #3

docker exec -it parnaie python manage.py migrate #4