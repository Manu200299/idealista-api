from idealista_api import Idealista, Search

idealista = Idealista(
    api_key="xgz27wkan54zkyb5l3pzpzra0o3n1y1b", api_secret="xJ57kvmCyzFs"
)

s = Search(
    country="asd",
    location_id="0-EU-ES-01",
    property_type="homes",
    operation="sale",
    max_items=50,
    num_page=2
)
print(idealista.query(s))
