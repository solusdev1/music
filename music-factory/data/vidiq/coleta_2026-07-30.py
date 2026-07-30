import json, sys
sys.path.insert(0,'/workspace/music/music-factory')
from core import db, vidiq, opportunity

conn = db.connect("/workspace/music/music-factory/data/radar.db")

# ── keywords coletadas do MCP VIDIQ (2026-07-30) ──
KW = {
 "country_blues_fe": ("BR", {
  "seedKeyword": {"keyword":"country gospel","volume":83.4,"competition":42.4,"overall":73.1,
                  "estimatedMonthlySearch":387688,"countryVolume":173376},
  "relatedKeywords":[
   {"keyword":"christian country music","volume":68.4,"competition":16.8,"overall":74.3,"estimatedMonthlySearch":38239,"countryVolume":3187},
   {"keyword":"country gospel music","volume":72.0,"competition":24.1,"overall":73.6,"estimatedMonthlySearch":66734,"countryVolume":27300},
   {"keyword":"country gospel songs","volume":73.8,"competition":32.9,"overall":71.1,"estimatedMonthlySearch":87786,"countryVolume":23410},
   {"keyword":"gospel music","volume":82.6,"competition":21.4,"overall":81.0,"estimatedMonthlySearch":340466,"countryVolume":51437},
   {"keyword":"country gospel playlist","volume":52.6,"competition":16.6,"overall":64.9,"estimatedMonthlySearch":3318},
   {"keyword":"relaxing country gospel","volume":74.0,"competition":41.5,"overall":67.8,"estimatedMonthlySearch":90367,"countryVolume":5830},
   {"keyword":"country gospel hymns","volume":61.1,"competition":30.2,"overall":64.6,"estimatedMonthlySearch":12441},
   {"keyword":"sertanejo gospel","volume":78.0,"competition":42.5,"overall":69.8,"estimatedMonthlySearch":169147,"countryVolume":139613},
   {"keyword":"sertanejo gospel raiz","volume":53.2,"competition":33.9,"overall":58.4,"estimatedMonthlySearch":3665},
   {"keyword":"viola caipira gospel","volume":58.4,"competition":22.8,"overall":65.9,"estimatedMonthlySearch":8108},
   {"keyword":"moda de viola cristã","volume":52.9,"competition":16.5,"overall":65.1,"estimatedMonthlySearch":3478},
   {"keyword":"moda de viola evangélica","volume":55.7,"competition":21.5,"overall":64.8,"estimatedMonthlySearch":5351},
   {"keyword":"gospel sertanejo raiz","volume":55.7,"competition":22.6,"overall":64.4,"estimatedMonthlySearch":5421},
   {"keyword":"louvor caipira","volume":54.9,"competition":24.2,"overall":63.3,"estimatedMonthlySearch":4763},
   {"keyword":"louvor sertanejo","volume":59.0,"competition":30.1,"overall":63.4,"estimatedMonthlySearch":9026},
   {"keyword":"música gospel","volume":75.6,"competition":48.5,"overall":66.0,"estimatedMonthlySearch":115704,"countryVolume":67729},
   {"keyword":"traditional country gospel","volume":53.3,"competition":23.5,"overall":62.6,"estimatedMonthlySearch":3700},
   {"keyword":"vintage country gospel","volume":52.9,"competition":25.2,"overall":61.6,"estimatedMonthlySearch":3471},
  ]}),
 "camino_de_la_fe": ("MX", {
  "seedKeyword": {"keyword":"música cristiana","volume":79.1,"competition":44.8,"overall":69.6,
                  "estimatedMonthlySearch":199658,"countryVolume":2570},
  "relatedKeywords":[
   {"keyword":"musica cristiana","volume":88.7,"competition":46.9,"overall":74.5,"estimatedMonthlySearch":880096,"countryVolume":54060},
   {"keyword":"musica para orar","volume":77.9,"competition":28.1,"overall":75.5,"estimatedMonthlySearch":164392,"countryVolume":10780},
   {"keyword":"adoracion cristiana","volume":71.2,"competition":25.3,"overall":72.6,"estimatedMonthlySearch":58623,"countryVolume":12342},
   {"keyword":"alabanzas cristianas","volume":84.6,"competition":50.9,"overall":70.4,"estimatedMonthlySearch":467557,"countryVolume":28194},
   {"keyword":"canciones cristianas","volume":77.1,"competition":38.2,"overall":71.0,"estimatedMonthlySearch":145181,"countryVolume":10957},
   {"keyword":"alabanzas de adoracion","volume":73.0,"competition":35.7,"overall":69.5,"estimatedMonthlySearch":77354,"countryVolume":8925},
   {"keyword":"música cristiana de adoración","volume":64.6,"competition":29.5,"overall":67.0,"estimatedMonthlySearch":21293},
   {"keyword":"música cristiana para danzar","volume":54.6,"competition":21.2,"overall":64.3,"estimatedMonthlySearch":4527},
   {"keyword":"música cristiana para el hogar","volume":55.4,"competition":23.1,"overall":64.0,"estimatedMonthlySearch":5169},
   {"keyword":"música cristiana en español","volume":64.5,"competition":37.7,"overall":63.6,"estimatedMonthlySearch":20983},
   {"keyword":"música cristiana para orar","volume":61.2,"competition":34.9,"overall":62.8,"estimatedMonthlySearch":12576},
   {"keyword":"alabanzas","volume":80.8,"competition":64.4,"overall":62.7,"estimatedMonthlySearch":256725,"countryVolume":86422},
  ]}),
 "southern_country_blues_gospel": ("US", {
  "seedKeyword": {"keyword":"southern gospel","volume":65.5,"competition":42.8,"overall":62.2,
                  "estimatedMonthlySearch":24569,"countryVolume":5985},
  "relatedKeywords":[
   {"keyword":"southern gospel piano","volume":53.9,"competition":12.9,"overall":67.2,"estimatedMonthlySearch":4108},
   {"keyword":"gospel music praise and worship","volume":78.7,"competition":40.8,"overall":70.9,"estimatedMonthlySearch":188001,"countryVolume":29127},
   {"keyword":"gospel worship songs","volume":68.2,"competition":41.7,"overall":64.2,"estimatedMonthlySearch":36902,"countryVolume":3197},
   {"keyword":"southern gospel songs","volume":59.5,"competition":31.4,"overall":63.2,"estimatedMonthlySearch":9715},
   {"keyword":"southern gospel quartets","volume":53.2,"competition":27.6,"overall":60.9,"estimatedMonthlySearch":3673},
   {"keyword":"southern gospel music","volume":60.5,"competition":38.8,"overall":60.8,"estimatedMonthlySearch":11333},
   {"keyword":"praise and worship songs","volume":79.6,"competition":60.9,"overall":63.4,"estimatedMonthlySearch":215831,"countryVolume":54608},
   {"keyword":"southern gospel hymns","volume":53.2,"competition":38.3,"overall":56.6,"estimatedMonthlySearch":3656},
   {"keyword":"southern gospel revival","volume":54.5,"competition":37.2,"overall":57.8,"estimatedMonthlySearch":4501},
  ]}),
}
for niche,(pais,payload) in KW.items():
    n = vidiq.ingest_keywords(conn, niche, payload, pais=pais)
    print(f"  {niche:<32} {n} keywords ({pais})")

# ── outliers → ideias ──
OUT = {
 "country_blues_fe": [
  ("Melhores Louvores 2026, Top Gospel Mais Tocadas, Louvores De Adoração",314.02,"Luz de Fé",8000),
  ("Louvores De Adoração 2026, Melhores Hinos Evangélicos, Top Gospel",51.47,"Nova Luz Gospel",97100),
  ("Melhores Louvores Gospel 2026, Adoração que Toca a Alma",35.72,"Luz de Fé",8000),
  ("As Mais Tocadas 2026, Hinos Evangélicos Com Letra",35.22,"Nova Luz Gospel",97100),
  ("JOÃO 3:16 - Country Gospel | O Deus Que Amou o Mundo Inteiro",24.89,"Serginho Gospel Music",1950),
  ("PAI NOSSO | Country Gospel",15.84,"Serginho Gospel Music",1950),
  ("À Sombra do Altíssimo | Country Gospel Inspirado no Salmo 91",12.33,"Serginho Gospel Music",1950),
 ],
 "camino_de_la_fe": [
  ("Alabanzas con letra para Orar a Dios | Música Cristiana Profunda | SIN ANUNCIOS",153.22,"Al Oido de Dios",11200),
  ("Líbrame de la Tormenta | Música Cristiana para Orar y Conectar con Dios",84.66,"sara duvall",3530),
  ("PODEROSAS ALABANZAS CRISTIANAS ADORACION PARA ORAR",46.26,"Canciones Católicas",30700),
  ("Estas 5 Alabanzas Llenarán tu Alma de Paz y Esperanza",30.51,"Fortaleza De Música",13100),
  ("MUSICA CRISTIANA PARA SENTIR LA PRESENCIA DE DIOS",17.17,"Canciones Cristianas",9900),
  ("3 HORAS - MUSICA INSTRUMENTAL CRISTIANA PARA ORAR *SIN ANUNCIOS",13.69,"Encontrando la Paz",1120),
  ("Himnos Antiguos Del Himnario | 45 Min ✝️ Cruz & Blues Worship",6.14,"Gospel del Hermano",1100),
 ],
}
for niche, vids in OUT.items():
    payload={"videos":[{"videoTitle":t,"breakoutScore":b,"channelTitle":c,"subscriberCount":s}
                       for t,b,c,s in vids]}
    n = vidiq.ingest_outliers(conn, niche, payload)
    print(f"  {niche:<32} {n} ideias de outlier")
