Bu program TCP Socket üzerinden basit düzeyde bir HTTP Server oluşturmaktadır.

## Kodun Çalıştırılması
```bash
python3 server.py
```
Kod çalıştırıldığında 127.0.0.1:8080 üzerinde server aktif hale gelecektir. 8080 üzerinde başka bir servisin çalışmadığına emin olunuz.

## Endpointler

Yanlış bir endpoint veya metod girildiğinde **404 NOT FOUND** hatası alınması olağandır.

### GET /isPrime
**number** parametresi alarak bu sayının asal olup olmadığını geri döner. Number parametresi yoksa veya parametre integer değilse ilgili uyarıyı döndürür.

Örneğin `curl -X GET http://127.0.0.1:8080/isPrime/?number=129` komutuyla (veya Postman üzerinden aynı sorgu ile) 129 sayısının asal olup olmadığı kontrol edilebilir.

### POST /upload
form-data içerisinde verilen dosyayı server'a kaydeder. multipart/form-data verilmediyse veya form-data içerisinde dosya yoksa ilgili uyarıyı döndürür. form-data içerisinde Tek bir dosya verilmesi gerekmektedir.

### PUT /rename
**oldFileName** parametresi ile aldığı isimdeki dosyanın ismini **newName** parametresinde verilen isim olarak değiştirir. Parametre eksik olması veya ismi değişecek dosyanın olmaması durumlarında ilgili uyarıyı döndürür.

Örneğin `curl -X PUT http://127.0.0.1:8080/rename/?oldFileName=hw.pdf&newName=homework.pdf` komutuyla (veya Postman üzerinden aynı sorgu ile) hw.pdf dosyasının adı homework.pdf olarak güncellenebilir.

### DELETE /remove
**fileName** parametresi ile aldığı isimdeki dosyayı siler. Parametre eksik olması veya silinecek dosyanın olmaması durumlarında ilgili uyarıyı döndürür.

Örneğin `curl -X DELETE http://127.0.0.1:8080/remove/?fileName=homework.pdf` komutuyla (veya Postman üzerinden aynı sorgu ile) homework.pdf dosyası silinebilir.

### GET /download
**fileName** parametresi ile aldığı isimdeki dosyayı gönderir. Parametre eksik olması veya gönderilecek dosyanın olmaması durumlarında ilgili uyarıyı döndürür

Örneğin önceden yüklenmiş olan "homework.pdf" dosyasını görüntülemek için tarayıcıya `http://127.0.0.1:8080/download/?filename=homework.pdf`yazarak (veya Postman üzerinden aynı sorgu ile) endpointe sorgu atılabilir ve dosya görüntülenebilir.