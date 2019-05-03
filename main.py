from urllib.request import urlopen
from bs4 import BeautifulSoup
from urllib.error import HTTPError
from urllib.error import URLError
import requests
from pprint import pprint as pp
import calendar
import datetime
import pandas as pd



def fix_posicion(pos):
    if pos > 20:
        pos = pos - 20
    if pos%2==0:
        ret = pos + (20-pos)/2
    else:
        ret = pos - (pos-1)/2
    return int(ret)

retorno = {
    'sorteos_total':0,
    'sorteos_nocturna':0,
    'sorteos_vespertina':0,
    'numeros':{},
    'numeros_restantes':[]
}

numeros_posibles = list(str(i).zfill(3) for i in range(1,1000))

primer_ano = 2007
fecha_actual = datetime.date.today()

for ano in range(primer_ano,fecha_actual.year+1):
    for mes in range(1,13):
        for dia in range(1,calendar.monthrange(ano,mes)[1]+1):
            url = "http://www.loteria.gub.uy/ver_resultados.php?vdia={0}&vmes={1}&vano={2}".format(dia,mes,ano)
            fecha = datetime.date(ano, mes, dia)
            if fecha > fecha_actual:
                break
            dia_semana = fecha.weekday()
            if dia_semana == 6:
                continue
            print(fecha)
            r = requests.get(url)
            soup = BeautifulSoup(r.content)
            quiniela = soup.findAll("div", {"class": "text_azul_3"})
            if len(quiniela) == 80 or len(quiniela) == 91 or len(quiniela) == 85 or len(quiniela) == 96:
                quiniela = quiniela[:20] + quiniela[40:60]
                retorno['sorteos_total'] += 2
                retorno['sorteos_nocturna'] += 1
                retorno['sorteos_vespertina'] += 1
            elif len(quiniela) == 40:
                quiniela = quiniela[:20]
                retorno['sorteos_total'] += 1
                retorno['sorteos_nocturna'] += 1
            elif len(quiniela) == 90 or len(quiniela) == 95:
                quiniela = quiniela[10:30] + quiniela[50:70]
                retorno['sorteos_total'] += 2
                retorno['sorteos_nocturna'] += 1
                retorno['sorteos_vespertina'] += 1
            elif len(quiniela) == 0:
                continue
            else:
                print ("otro caso - " + str(fecha) + str(len(quiniela)))
                continue
            for posicion,valor in enumerate(quiniela,1):
                    fix_pos = fix_posicion(posicion)
                    numero = valor.text.strip()
                    retorno['numeros'].setdefault(numero,{'contador':0,'cabeza':0,'fechas':[],'fecha_ultima_vez':'','fecha_ultima_vez_cabeza':'','ultima_posicion':'','info':[]})
                    #retorno[numero].setdefault('contador',0)
                    retorno['numeros'][numero]['contador'] += 1
                    retorno['numeros'][numero]['fechas'].append(str(fecha))
                    retorno['numeros'][numero]['fecha_ultima_vez'] = str(fecha)
                    retorno['numeros'][numero]['ultima_posicion'] = fix_pos
                    retorno['numeros'][numero]['info'].append({'posicion':fix_pos,'fecha':str(fecha),'sorteo':''})
                    if fix_pos == 1:
                        retorno['numeros'][numero]['cabeza'] += 1
                        retorno['numeros'][numero]['fecha_ultima_vez_cabeza'] = str(fecha)
                    if numero in numeros_posibles:
                        numeros_posibles.remove(numero)
retorno['numeros_restantes'] = numeros_posibles

df = pd.DataFrame(retorno['numeros']).T
df.to_csv('fiiile.csv')
df.to_excel('file.xls')


#recorro por año desde el 2007(primer año con info 1/1/2007) hasta dia actual
#recorro por mes del 1 al 12
#recorro por dia del 1 al 31
#fijarme que dia es
#casos especiales: 
#   sabado, solo hay sorteo nocturno
#   feriados y domingo: no hay sorteo
#   tercer viernes de cada mes, hay loteria

#la idea es agregar a un diccionario cada número, 
#agregar dentro de cada número: 
    #contador de cuantas veces salio, 
    #fecha de cada vez que salió, 
    #posición en la que salió, 
    #cantidad de veces que salió a la cabeza, 
    #fecha de ultima vez que salió, 
    #posicion en la que salió por última vez, 
    #fecha de última vez que salió a la cabeza, 
    #guardar si salió en nocturna o vespertina

#cantidad total de sorteos
#cantidad total de sorteos nocturnos y vespertinos

#exportar el resultado a csv

#poder llamarlo entre rango de fechas
#poder llamarlo con numero especifico
#crear una funcion check sorteo que combine el dia y la posicion para devolverme el sorteo que es
