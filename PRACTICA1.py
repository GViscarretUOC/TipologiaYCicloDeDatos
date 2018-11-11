import requests
from bs4 import BeautifulSoup
import csv

#definimo una función para escribor en fichero
def escribeCSV(row):
    with open('anel.csv',mode="a") as csvfile:            
        writer=csv.writer(csvfile,delimiter=',')
        writer.writerow([row["fecha"],row["Nombre"],row["Domicilio"],row["Poblacion"],row["Web"],row["Correo"],row["Actividad"],row["img"]])
        csvfile.close()
    
#definimos una función que parsea una dirección concreta
def parsea(link):
    from PIL import Image
    #Descargamos la página particular
    particular_page= requests.get(link)
    respuesta= particular_page.status_code
    if respuesta==200:
        particular_soup = BeautifulSoup(particular_page.content)
        #Tenemos un grupo post por cada grupo de datos que queremos recuperar
        for post in particular_soup.find_all(attrs={'class':'post'}):
            #Creamos una lista para guardar informacion
            row={"fecha":"","Nombre":"","Domicilio":"","Poblacion":"","Correo":"","Web":"","Actividad":"","img":""}
            #La fecha está en un primer nivel
            fecha=post.find('small')
            print(fecha.get_text().strip())
            row["fecha"]=(fecha.get_text()).strip().split("|",2)[0].strip()
            #El resto de datos está en el grupo entry
            for entrada in post.find_all(attrs={'class':'entry'}):
                print('*********************')            
                for campo in entrada.find_all('p'):
                    print(campo.get_text())
                    if campo.find('img'):
                         direcc=campo.find('img').get('src')
                         #Guardamos la imagen (logotipo) que acabamos dedetectar
                         imagen=Image.open(requests.get(direcc,stream=True).raw)
                         path=direcc.split("/",-1)
                         imagen.save(path[len(path)-1])
                         #Y las referenciamos en nuestro dataset
                         row["img"]=path[len(path)-1]
                    else:#Resto de campos
                        if "DOMICILIO:" in campo.get_text():
                            row["Domicilio"]=campo.get_text().split(":",2)[1].replace(',',' ').replace('\n','')
                        elif "POBLACION:" in campo.get_text():
                            row["Poblacion"]=campo.get_text().split(":",2)[1].replace(',',' ')
                        elif "Web:" in campo.get_text():
                            row["Web"]=campo.get_text().split(":",2)[1]
                        elif "Correo Electrónico:" in campo.get_text():
                            row["Correo"]=campo.get_text()  .split(":",2)[1]   
                        elif "ACTIVIDAD:" in campo.get_text():
                            row["Actividad"]=campo.get_text().split(":",2)[1].replace(',',' ')
                        else:
                            if bool(campo.get_text().strip()):#evitamos cadenas vacías
                                row["Nombre"]=campo.get_text().replace(',',' ').replace('\n','')  
                #Escribimos los datos recuperados en CSV                
                escribeCSV(row)
    else:
        print("Error de respuesta del servidor")
#seccion inicial
#De la pagina inicial, buscamos los diferentes links dosnde estrá nuestar información

#Buscamos en esta dirección los diferentes enlaces que vamos a buscar, que serán .../empresas-asociadas-Page1, ... Page2, etc
principal_page = requests.get('http://www.anel.es/category/solo-para-empresas/empresas-asociadas/')
#Comprobamos el código de conexión que nos devuelve el servidor
respuesta = principal_page.status_code
if respuesta==200:
#Aplicamos BeautifulShop para poser empezar a parsear
    principal_soup = BeautifulSoup(principal_page.content)
#Imprimos la estructura descargada con prettify
    print(principal_soup.prettify())
#Según hemos visto en la estructura, tenemo sque buscar la clase pages, que es donde tiene luego los enlaces a las diferentes páginas
    seccion=principal_soup.find(attrs={'class':'pages'})
#Dentro de la seccion pages, tenemos los links con la etiqueta a, href (donde se indica el link)
    for links in seccion.find_all('a'):
        parsea(links.get('href'))
else:
    print("Error de respuesta del servidor")
