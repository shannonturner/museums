from museums.models import Museum, MuseumType
with open("fixtures/museums.tsv") as museums_file:
    museums = museums_file.read().strip().split("\n")
for index, museum in enumerate(museums):
    museums[index] = museum.split("\t")

for museum in museums[1:]:
    try:
        if museum[4] == 'HSC':
            continue
        mtype = MuseumType.objects.filter(code=museum[4])[0]
        latlong = museum[9][museum[9].rfind("(")+1:-1]
        latitude, longitude = latlong.split(", ")
        latitude = float(latitude)
        longitude = float(longitude)
        m = Museum(**{
            'imls_id': museum[0],
            'name': museum[1],
            'phone': museum[2],
            'url': museum[3],
            'types': mtype,
            'address': museum[5],
            'city': museum[6],
            'state': museum[7],
            'zipcode': museum[8],
            'latitude': latitude,
            'longitude': longitude,
            })
        m.save()
    except Exception:
        print "[ERROR] Failed on ", museum
        raise
